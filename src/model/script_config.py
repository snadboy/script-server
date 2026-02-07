import logging
import os
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import List, Optional

from auth.authorization import ANY_USER
from config.exceptions import InvalidConfigException
from model import parameter_config
from model.model_helper import is_empty, read_bool_from_config, InvalidValueException, \
    read_str_from_config, replace_auth_vars, read_list
from model.parameter_config import ParameterModel
from model.server_conf import LoggingConfig
from model.template_property import TemplateProperty
from model.verb_config import VerbsConfiguration
from react.properties import ObservableList, ObservableDict, observable_fields
from utils import file_utils, custom_json
from utils.object_utils import merge_dicts
from utils.process_utils import ProcessInvoker

OUTPUT_FORMAT_TERMINAL = 'terminal'

OUTPUT_FORMATS = [OUTPUT_FORMAT_TERMINAL, 'html', 'html_iframe', 'text']

LOGGER = logging.getLogger('script_server.script_config')


@dataclass
class ShortConfig:
    name: str
    group: str = None
    description: str = None
    allowed_users: List[str] = field(default_factory=list)
    admin_users: List[str] = field(default_factory=list)
    parsing_failed: bool = False
    verbs_config: 'VerbsConfiguration' = None
    shared_parameters: List[str] = field(default_factory=list)
    project_id: str = None


class InstanceConfig:
    """Configuration for a script instance (project-based)."""

    def __init__(self, config_dict: dict):
        """
        Initialize instance configuration.

        Args:
            config_dict: Dictionary with included_parameters, parameter_values, selected_verb
        """
        self.included_parameters = config_dict.get('included_parameters', [])
        self.parameter_values = config_dict.get('parameter_values', {})
        self.selected_verb = config_dict.get('selected_verb')


def create_failed_short_config(path, has_admin_rights):
    name = _build_name_from_path(path)
    if not has_admin_rights:
        file_content = file_utils.read_file(path)
        if '"allowed_users"' in file_content:
            restricted_name = name[:2] + '...' + name[-2:]
            name = restricted_name + ' (restricted)'

    return ShortConfig(name=name, parsing_failed=True)


@observable_fields(
    'script_command',
    'description',
    'requires_terminal',
    'working_directory',
    'output_format',
    'output_files',
    'schedulable',
    'preload_script',
    '_included_config',
    'verbs_config',
)
class ConfigModel:

    def __init__(self,
                 config_object,
                 path,
                 username,
                 audit_name,
                 group_by_folders: bool,
                 script_configs_folder: str,
                 process_invoker: ProcessInvoker,
                 pty_enabled_default=True):
        super().__init__()

        short_config = read_short(path, config_object, group_by_folders, script_configs_folder)
        self.name = short_config.name
        self._pty_enabled_default = pty_enabled_default
        self._config_folder = script_configs_folder
        self._process_invoker = process_invoker

        self._username = username
        self._audit_name = audit_name
        self.schedulable = False
        self.scheduling_auto_cleanup = True

        self.parameters = ObservableList()
        self.parameter_values = ObservableDict()

        self._original_config = config_object
        self._included_config_paths = TemplateProperty(read_list(config_object, 'include'),
                                                       parameters=self.parameters,
                                                       value_wrappers=self.parameter_values)
        self._included_config_prop.bind(self._included_config_paths, self._read_and_merge_included_paths)

        self._reload_config()

        self.parameters.subscribe(self)

        # Check if this is a project-based instance
        project_id = config_object.get('project_id')
        if project_id:
            self.project_id = project_id  # Store for API response
            self._load_from_project(project_id, config_object, username, audit_name)
        else:
            # Legacy standalone script
            self.project_id = None
            self._init_parameters(username, audit_name)

        for parameter in self.parameters:
            self.parameter_values[parameter.name] = parameter.create_value_wrapper_for_default()

        self._included_config_prop.subscribe(lambda old, new: self._reload(old))

    def set_param_value(self, param_name, value):
        parameter = self.find_parameter(param_name)
        if parameter is None:
            LOGGER.warning('Parameter ' + param_name + ' does not exist in ' + self.name)
            return
        normalized_value = parameter.normalize_user_value(value)
        value_wrapper = parameter.create_value_wrapper(normalized_value)
        validation_error = parameter.validate_value(value_wrapper, ignore_required=True)

        if validation_error is not None:
            self.parameter_values[param_name] = parameter.create_value_wrapper(None)
            raise InvalidValueException(param_name, validation_error)

        self.parameter_values[param_name] = value_wrapper

    def set_all_param_values(self, param_values, skip_invalid_parameters=False):
        original_values = dict(self.parameter_values)
        processed = {}

        anything_changed = True

        def get_sort_key(parameter):
            if parameter.name in self._included_config_paths.required_parameters:
                return len(parameter.get_required_parameters())
            return 100 + len(parameter.get_required_parameters())

        sorted_parameters = sorted(self.parameters, key=get_sort_key)

        while (len(processed) < len(self.parameters)) and anything_changed:
            anything_changed = False

            parameters = sorted_parameters + [p for p in self.parameters if p not in sorted_parameters]
            for parameter in parameters:
                if parameter.name in processed:
                    continue

                required_parameters = parameter.get_required_parameters()
                if required_parameters and any(r not in processed for r in required_parameters):
                    continue

                if parameter.constant:
                    value_wrapper = parameter.create_value_wrapper_for_default()
                else:
                    value = parameter.normalize_user_value(param_values.get(parameter.name))
                    value_wrapper = parameter.create_value_wrapper(value)

                validation_error = parameter.validate_value(value_wrapper)
                if validation_error:
                    if skip_invalid_parameters:
                        logging.warning('Parameter ' + parameter.name + ' has invalid value, skipping')
                        value_wrapper = parameter.create_value_wrapper(parameter.normalize_user_value(None))
                    else:
                        self.parameter_values.set(original_values)
                        raise InvalidValueException(parameter.name, validation_error)

                self.parameter_values[parameter.name] = value_wrapper
                processed[parameter.name] = parameter
                anything_changed = True

            if not anything_changed:
                remaining = [p.name for p in self.parameters if p.name not in processed]
                self.parameter_values.set(original_values)
                raise Exception('Could not resolve order for dependencies. Remaining: ' + str(remaining))

        # Handle verb parameter value (if verbs are configured)
        if self.verbs_config and self.verbs_config.enabled:
            verb_param_name = self.verbs_config.parameter_name
            if verb_param_name in param_values:
                # Store verb value directly without parameter validation
                # since verb parameters don't have parameter definitions
                verb_value = param_values[verb_param_name]
                from model.value_wrapper import ScriptValueWrapper
                verb_wrapper = ScriptValueWrapper(
                    user_value=verb_value,
                    mapped_script_value=verb_value,
                    script_arg=verb_value
                )
                self.parameter_values[verb_param_name] = verb_wrapper

        for key, value in param_values.items():
            if self.find_parameter(key) is None:
                # Skip warning for verb parameter - it's expected to not have a parameter definition
                if self.verbs_config and self.verbs_config.enabled and key == self.verbs_config.parameter_name:
                    continue
                LOGGER.warning('Incoming value for unknown parameter ' + key)

    def list_files_for_param(self, parameter_name, path):
        parameter = self.find_parameter(parameter_name)
        if not parameter:
            raise ParameterNotFoundException(parameter_name)

        return parameter.list_files(path)

    def _load_from_project(self, project_id: str, config_object: dict, username: str, audit_name: str):
        """
        Load parameters and verbs from project metadata.

        Args:
            project_id: Project identifier
            config_object: Script instance configuration
            username: Current username
            audit_name: Audit name for logging
        """
        import os
        from project_manager.project_service import ProjectService

        # ProjectService needs the root directory, not the config folder
        # config_folder is typically 'conf/runners', we need the parent directory
        project_root = os.path.dirname(os.path.dirname(self._config_folder))
        if not project_root:
            project_root = '.'

        project_service = ProjectService(project_root)
        project_meta = project_service.get_project(project_id)

        if not project_meta:
            raise Exception(f'Project {project_id} not found')

        # Parse instance config
        instance_config_data = config_object.get('instance_config', {})
        self.instance_config = InstanceConfig(instance_config_data)

        # Load parameter DEFINITIONS from project
        project_parameters = project_meta.get('parameters', [])

        # Filter to included parameters only
        included_names = set(self.instance_config.included_parameters)
        for param_config in project_parameters:
            if param_config['name'] in included_names:
                parameter = ParameterModel(
                    param_config, username, audit_name,
                    lambda: self.parameters,
                    self._process_invoker,
                    self.parameter_values,
                    self.working_directory
                )
                self.parameters.append(parameter)

        # Override defaults with instance values
        for param_name, value in self.instance_config.parameter_values.items():
            param = self.find_parameter(param_name)
            if param:
                # Set the default value from instance config
                param._default = value

        # Load verb config from project
        project_verbs = project_meta.get('verbs')
        if project_verbs:
            self.verbs_config = VerbsConfiguration(project_verbs)
            self.shared_parameters = project_meta.get('shared_parameters', [])

            # Set selected verb if specified
            if self.instance_config.selected_verb:
                verb_param_name = self.verbs_config.parameter_name
                # Create a pseudo-parameter wrapper for the verb value
                from model.value_wrapper import ScriptValueWrapper
                verb_value = self.instance_config.selected_verb
                self.parameter_values[verb_param_name] = ScriptValueWrapper(
                    user_value=verb_value,
                    mapped_script_value=verb_value,
                    script_arg=verb_value
                )

        self._reload_parameters({})
        self._validate_parameter_configs()

    def _init_parameters(self, username, audit_name):
        original_parameter_configs = self._original_config.get('parameters', [])
        for parameter_config in original_parameter_configs:
            parameter = ParameterModel(parameter_config, username, audit_name,
                                       lambda: self.parameters,
                                       self._process_invoker,
                                       self.parameter_values,
                                       self.working_directory)
            self.parameters.append(parameter)

        self._reload_parameters({})

        self._validate_parameter_configs()

    def _reload(self, old_included_config):
        self._reload_config()
        self._reload_parameters(old_included_config)

    def _reload_config(self):
        if self._included_config is None:
            config = self._original_config
        else:
            config = merge_dicts(self._original_config, self._included_config, ignored_keys=['parameters'])

        self.script_command = config.get('script_path')
        self.description = replace_auth_vars(config.get('description'), self._username, self._audit_name)
        self.working_directory = config.get('working_directory')

        required_terminal = read_bool_from_config('requires_terminal', config, default=self._pty_enabled_default)
        self.requires_terminal = required_terminal

        self.access = config.get('access', {})

        self.output_format = read_output_format(config)

        self.output_files = config.get('output_files', [])

        scheduling_config = config.get('scheduling')
        if scheduling_config:
            self.schedulable = read_bool_from_config('enabled', scheduling_config, default=False)
            self.scheduling_auto_cleanup = read_bool_from_config(
                'auto_cleanup', scheduling_config, default=not bool(self.output_files))

        self.logging_config = LoggingConfig.from_json(config.get('logging'))

        self.preload_script = self._read_preload_script_conf(config.get('preload_script'))

        # Parse verbs configuration
        verbs_config = config.get('verbs')
        self.verbs_config = VerbsConfiguration(verbs_config)

        # Also read shared_parameters list for verbs
        self.shared_parameters = read_list(config, 'shared_parameters') or []

        # Read supported connections list
        self.supported_connections = read_list(config, 'supported_connections') or []

        if not self.script_command:
            raise Exception('No script_path is specified for ' + self.name)

    def _reload_parameters(self, old_included_config):
        original_parameters_names = {p.get('name') for p in self._original_config.get('parameters', [])}

        if old_included_config and old_included_config.get('parameters'):
            old_included_param_names = {p.get('name') for p in old_included_config.get('parameters', [])}
            for param_name in old_included_param_names:
                if param_name in original_parameters_names:
                    continue

                parameter = self.find_parameter(param_name)
                self.parameters.remove(parameter)

        if self._included_config is not None:
            included_parameter_configs = self._included_config.get('parameters', [])
            for parameter_config in included_parameter_configs:
                parameter_name = parameter_config.get('name')
                parameter = self.find_parameter(parameter_name)
                if parameter is None:
                    parameter = ParameterModel(parameter_config, self._username, self._audit_name,
                                               lambda: self.parameters,
                                               self._process_invoker,
                                               self.parameter_values,
                                               self.working_directory)
                    self.parameters.append(parameter)

                    if parameter.name not in self.parameter_values:
                        self.parameter_values[parameter.name] = parameter.create_value_wrapper_for_default()
                    continue
                else:
                    LOGGER.warning('Parameter ' + parameter_name + ' exists in original and included file. '
                                   + 'This is now allowed! Included parameter is ignored')
                    continue

    def find_parameter(self, param_name) -> Optional[ParameterModel]:
        for parameter in self.parameters:
            if parameter.name == param_name:
                return parameter
        return None

    def on_add(self, parameter, index):
        if self.schedulable and parameter.secure:
            LOGGER.warning(
                'Disabling schedulable functionality, because parameter ' + parameter.str_name() + ' is secure')
            self.schedulable = False

    def on_remove(self, parameter):
        pass

    def get_visible_parameters_for_verb(self, verb_name: str) -> List[str]:
        """Get list of visible parameter names for a specific verb.

        If no verbs are configured, returns all parameter names.
        Includes shared_parameters that apply to all verbs.
        """
        if not self.verbs_config or not self.verbs_config.enabled:
            return [p.name for p in self.parameters]

        verb_params = self.verbs_config.get_visible_parameters(verb_name)
        shared_params = getattr(self, 'shared_parameters', [])

        return list(set(verb_params + shared_params))

    def get_required_parameters_for_verb(self, verb_name: str) -> List[str]:
        """Get list of required parameter names for a specific verb."""
        if not self.verbs_config or not self.verbs_config.enabled:
            return [p.name for p in self.parameters if p.required]

        return self.verbs_config.get_required_parameters(verb_name)

    def _validate_parameter_configs(self):
        for parameter in self.parameters:
            parameter.validate_parameter_dependencies(self.parameters)

    def _read_and_merge_included_paths(self, paths):
        if is_empty(paths):
            return None

        merged_dict = {}
        merged_params = []
        merged_param_names = set()

        for path in paths:
            path = file_utils.normalize_path(path, self._config_folder)

            if os.path.exists(path):
                try:
                    included_json = custom_json.loads(file_utils.read_file(path))
                    merged_dict = merge_dicts(merged_dict, included_json, ignored_keys=['parameters'])

                    parameters = included_json.get('parameters')
                    if parameters:
                        for param in parameters:
                            param_name = param.get('name')
                            if not param_name:
                                continue

                            if param_name in merged_param_names:
                                continue

                            merged_params.append(param)
                            merged_param_names.add(param_name)
                except Exception as e:
                    LOGGER.exception('Failed to load included file %s: %s', path, e)
                    continue
            else:
                LOGGER.warning('Failed to load included file, path does not exist: ' + path)
                continue

        if merged_params:
            merged_dict['parameters'] = merged_params
        return merged_dict

    def _read_preload_script_conf(self, config):
        if config is None:
            return None

        error_message = 'Failed to load preload script for ' + self.name + ': '

        if not isinstance(config, dict):
            logging.warning(error_message + 'should be dict')
            return None

        script = config.get('script')
        if is_empty(script):
            logging.warning(error_message + 'missing "script" field')
            return

        try:
            format = read_output_format(config)
        except InvalidConfigException:
            LOGGER.warning(error_message + 'invalid format specified')
            format = OUTPUT_FORMAT_TERMINAL

        return {'script': script, 'output_format': format}

    def run_preload_script(self):
        if not self.preload_script:
            raise Exception('Cannot run preload script for ' + self.name + ': no preload_script is specified')

        return self._process_invoker.invoke(self.preload_script.get('script'))

    def get_preload_script_format(self):
        if not self.preload_script:
            return OUTPUT_FORMAT_TERMINAL

        return self.preload_script.get('output_format')


def _read_name(file_path, json_object):
    name = json_object.get('name')
    if not name:
        name = _build_name_from_path(file_path)

    return name.strip()


def _build_name_from_path(file_path):
    filename = os.path.basename(file_path)
    name = os.path.splitext(filename)[0]
    return name.strip()


def read_short(file_path, json_object, group_by_folders: bool, script_configs_folder: str):
    name = _read_name(file_path, json_object)
    allowed_users = json_object.get('allowed_users')
    admin_users = json_object.get('admin_users')
    description = read_str_from_config(json_object, 'description', blank_to_none=True)
    group = read_str_from_config(json_object, 'group', blank_to_none=True)
    if ('group' not in json_object) and group_by_folders:
        relative_path = file_utils.relative_path(file_path, script_configs_folder)
        while os.path.dirname(relative_path):
            relative_path = os.path.dirname(relative_path)
            group = relative_path

    hidden = read_bool_from_config('hidden', json_object, default=False)
    if hidden:
        return None

    if allowed_users is None:
        allowed_users = ANY_USER
    elif (allowed_users == '*') or ('*' in allowed_users):
        allowed_users = ANY_USER

    if admin_users is None:
        admin_users = ANY_USER
    elif (admin_users == '*') or ('*' in admin_users):
        admin_users = ANY_USER

    # Parse verbs configuration for short config
    verbs_config_data = json_object.get('verbs')
    verbs_config = VerbsConfiguration(verbs_config_data)
    shared_parameters = read_list(json_object, 'shared_parameters') or []

    # Extract project_id for project-based instances
    project_id = json_object.get('project_id')

    return ShortConfig(
        name=name,
        group=group,
        description=description,
        allowed_users=allowed_users,
        admin_users=admin_users,
        verbs_config=verbs_config,
        shared_parameters=shared_parameters,
        project_id=project_id
    )


class ParameterNotFoundException(Exception):
    def __init__(self, param_name) -> None:
        self.param_name = param_name


def get_sorted_config(config):
    key_order = ['name', 'script_path',
                 'working_directory',
                 'hidden',
                 'description',
                 'group',
                 'allowed_users',
                 'admin_users',
                 'access',
                 'schedulable',
                 'include',
                 'output_files',
                 'requires_terminal',
                 'output_format',
                 'scheduling',
                 'verbs',
                 'shared_parameters',
                 'parameters']

    def get_order(key):
        if key == 'parameters':
            return 99
        elif key in key_order:
            return key_order.index(key)
        else:
            return 50

    sorted_config = OrderedDict(sorted(config.items(), key=lambda item: get_order(item[0])))
    if config.get('parameters'):
        for i, param in enumerate(config['parameters']):
            config['parameters'][i] = parameter_config.get_sorted_config(param)

    return sorted_config


def read_output_format(config):
    output_format = config.get('output_format')
    if not output_format:
        output_format = OUTPUT_FORMAT_TERMINAL

    output_format = output_format.strip().lower()
    if output_format not in OUTPUT_FORMATS:
        raise InvalidConfigException('Invalid output format, should be one of: ' + str(OUTPUT_FORMATS))

    return output_format
