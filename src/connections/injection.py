"""Connection credential injection for script execution."""

import logging
import os
import re
import shutil
import stat
import tempfile
from typing import Dict, List, Optional, Tuple

from connections.connection_service import get_connection_service
from connections.connection_types import get_connection_type

LOGGER = logging.getLogger('script_server.ConnectionInjection')


class _CredentialFileCleanup:
    """Finish listener that removes temporary credential files."""

    def __init__(self, temp_dirs: List[str]):
        self._temp_dirs = temp_dirs

    def finished(self):
        for temp_dir in self._temp_dirs:
            try:
                shutil.rmtree(temp_dir)
                LOGGER.debug(f'Cleaned up credential temp dir: {temp_dir}')
            except Exception as e:
                LOGGER.warning(f'Failed to clean up credential temp dir {temp_dir}: {e}')


def _filename_to_env_suffix(filename: str) -> str:
    """Convert a filename to an environment variable suffix.

    Examples:
        'credentials.json' -> 'CREDENTIALS'
        'token.json' -> 'TOKEN'
        'my-config.yaml' -> 'MY_CONFIG'
    """
    stem = os.path.splitext(filename)[0]
    return re.sub(r'[^a-zA-Z0-9]', '_', stem).upper()


def _render_template(template: str, field_values: Dict[str, str]) -> str:
    """Replace {{field_name}} placeholders in a template with field values."""
    result = template
    for field_name, field_value in field_values.items():
        result = result.replace('{{' + field_name + '}}', str(field_value) if field_value else '')
    return result


def _write_credential_files(
    conn_type,
    field_values: Dict[str, str],
    connection_id: str
) -> Tuple[Dict[str, str], str]:
    """Write credential files from templates to a temporary directory.

    Returns:
        Tuple of (env_vars dict mapping PREFIX_STEM_PATH to file path, temp_dir path)
    """
    temp_dir = tempfile.mkdtemp(prefix=f'scriptserver_creds_{connection_id}_')
    env_vars = {}

    for filename, template in conn_type.file_templates.items():
        content = _render_template(template, field_values)

        file_path = os.path.join(temp_dir, filename)
        with open(file_path, 'w') as f:
            f.write(content)

        # Set restrictive permissions (owner read/write only)
        os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)

        # Build env var: PREFIX_STEM_PATH (e.g., GOOGLE_CREDENTIALS_PATH)
        suffix = _filename_to_env_suffix(filename)
        env_var_name = f'{conn_type.env_prefix}_{suffix}_PATH'
        env_vars[env_var_name] = file_path

        LOGGER.debug(f'Wrote credential file {filename} -> {env_var_name} for connection "{connection_id}"')

    return env_vars, temp_dir


def inject_connection_credentials(
    connection_ids: List[str],
    env_variables: Dict[str, str]
) -> Tuple[Dict[str, str], Optional[_CredentialFileCleanup]]:
    """
    Inject connection credentials into environment variables and/or temp files.

    Args:
        connection_ids: List of connection IDs to inject
        env_variables: Existing environment variables dict (will be copied)

    Returns:
        Tuple of:
            - New dict with connection credentials added as environment variables
            - Optional cleanup handler (call .finished() to remove temp files)

    Example:
        connection "home-plex" of type "plex" (injection_mode='env') with
        url="http://plex:32400" and token="abc123" will inject:
            PLEX_URL=http://plex:32400
            PLEX_TOKEN=abc123

        connection "home-google" of type "google" (injection_mode='file') with
        client_id and client_secret will write credentials.json and token.json
        to a temp dir and inject:
            GOOGLE_CREDENTIALS_PATH=/tmp/scriptserver_creds_.../credentials.json
            GOOGLE_TOKEN_PATH=/tmp/scriptserver_creds_.../token.json
    """
    if not connection_ids:
        return env_variables, None

    # Create a copy to avoid modifying the original
    result = dict(env_variables)
    temp_dirs = []

    connection_service = get_connection_service()
    if not connection_service:
        LOGGER.warning('Connection service not initialized, skipping credential injection')
        return result, None

    for connection_id in connection_ids:
        try:
            # Resolve connection with decrypted secrets
            connection = connection_service.get_connection(connection_id, mask_secrets=False)
            if not connection:
                LOGGER.warning(f'Connection "{connection_id}" not found, skipping')
                continue

            # Get connection type definition
            conn_type = get_connection_type(connection['type'])
            if not conn_type:
                LOGGER.warning(f'Unknown connection type "{connection["type"]}" for connection "{connection_id}", skipping')
                continue

            injection_mode = conn_type.injection_mode
            field_values = connection['fields']

            # Env injection (mode='env' or 'both')
            if injection_mode in ('env', 'both'):
                env_prefix = conn_type.env_prefix
                for field_def in conn_type.fields:
                    field_name = field_def.name
                    field_value = field_values.get(field_name)

                    if field_value is None:
                        continue

                    env_var_name = f'{env_prefix}_{field_name.upper()}'
                    result[env_var_name] = str(field_value)
                    LOGGER.debug(f'Injected {env_var_name} from connection "{connection_id}"')

            # File injection (mode='file' or 'both')
            if injection_mode in ('file', 'both') and conn_type.file_templates:
                file_env_vars, temp_dir = _write_credential_files(conn_type, field_values, connection_id)
                result.update(file_env_vars)
                temp_dirs.append(temp_dir)

            LOGGER.info(f'Injected credentials from connection "{connection_id}" (type: {connection["type"]}, mode: {injection_mode})')

        except Exception as e:
            LOGGER.error(f'Failed to inject connection "{connection_id}": {e}', exc_info=True)
            continue

    cleanup = _CredentialFileCleanup(temp_dirs) if temp_dirs else None
    return result, cleanup


def get_connection_env_vars(connection_ids: List[str]) -> Dict[str, str]:
    """
    Get environment variables for given connections without merging with existing env.

    Args:
        connection_ids: List of connection IDs

    Returns:
        Dict of environment variables from connections only
    """
    result, _cleanup = inject_connection_credentials(connection_ids, {})
    return result
