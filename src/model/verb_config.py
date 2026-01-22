import logging
from typing import List, Optional, Dict, Any

from model.model_helper import read_bool_from_config, read_str_from_config, read_list

LOGGER = logging.getLogger('script_server.verb_config')


class VerbOption:
    """Represents a single verb/subcommand option."""

    def __init__(self, config: Dict[str, Any]):
        self.name = config.get('name')  # CLI value: "run", "stop"
        self.label = config.get('label', self.name)  # UI display: "Run Container"
        self.description = config.get('description', '')  # Help text
        self.parameters = read_list(config, 'parameters') or []  # Visible params for this verb
        self.required_parameters = read_list(config, 'required_parameters') or []  # Required when verb selected

        if not self.name:
            raise ValueError('Verb option must have a "name" field')


class VerbsConfiguration:
    """Configuration for verb/subcommand support in a script."""

    def __init__(self, config: Optional[Dict[str, Any]]):
        if config is None:
            self.enabled = False
            self.parameter_name = None
            self.required = False
            self.default = None
            self.options = []
            return

        self.enabled = True
        self.parameter_name = read_str_from_config(config, 'parameter_name', default='verb')
        self.required = read_bool_from_config('required', config, default=True)
        self.default = config.get('default')

        options_config = config.get('options', [])
        self.options: List[VerbOption] = []

        for option_config in options_config:
            try:
                self.options.append(VerbOption(option_config))
            except ValueError as e:
                LOGGER.warning(f'Failed to parse verb option: {e}')

        # Build lookup dictionaries for fast access
        self._options_by_name: Dict[str, VerbOption] = {opt.name: opt for opt in self.options}

        # Validate default
        if self.default and self.default not in self._options_by_name:
            LOGGER.warning(f'Default verb "{self.default}" not found in options, ignoring')
            self.default = None

    def get_option(self, verb_name: str) -> Optional[VerbOption]:
        """Get a verb option by name."""
        return self._options_by_name.get(verb_name)

    def get_visible_parameters(self, verb_name: str) -> List[str]:
        """Get list of visible parameter names for a specific verb."""
        option = self.get_option(verb_name)
        if option:
            return option.parameters
        return []

    def get_required_parameters(self, verb_name: str) -> List[str]:
        """Get list of required parameter names for a specific verb."""
        option = self.get_option(verb_name)
        if option:
            return option.required_parameters
        return []

    def get_verb_names(self) -> List[str]:
        """Get all verb names."""
        return [opt.name for opt in self.options]

    def get_default_verb(self) -> Optional[str]:
        """Get the default verb name."""
        if self.default:
            return self.default
        if self.options:
            return self.options[0].name
        return None

    def to_dict(self) -> Optional[Dict[str, Any]]:
        """Serialize to dictionary for API response."""
        if not self.enabled:
            return None

        return {
            'parameterName': self.parameter_name,
            'required': self.required,
            'default': self.default or self.get_default_verb(),
            'options': [
                {
                    'name': opt.name,
                    'label': opt.label,
                    'description': opt.description,
                    'parameters': opt.parameters,
                    'requiredParameters': opt.required_parameters
                }
                for opt in self.options
            ]
        }
