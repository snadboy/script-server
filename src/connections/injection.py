"""Connection credential injection for script execution."""

import logging
from typing import Dict, List, Optional

from connections.connection_service import get_connection_service
from connections.connection_types import get_connection_type

LOGGER = logging.getLogger('script_server.ConnectionInjection')


def inject_connection_credentials(
    connection_ids: List[str],
    env_variables: Dict[str, str]
) -> Dict[str, str]:
    """
    Inject connection credentials into environment variables.

    Args:
        connection_ids: List of connection IDs to inject
        env_variables: Existing environment variables dict (will be copied)

    Returns:
        New dict with connection credentials added as environment variables

    Example:
        connection "home-plex" of type "plex" with url="http://plex:32400" and token="abc123"
        will inject:
            PLEX_URL=http://plex:32400
            PLEX_TOKEN=abc123
    """
    if not connection_ids:
        return env_variables

    # Create a copy to avoid modifying the original
    result = dict(env_variables)

    connection_service = get_connection_service()
    if not connection_service:
        LOGGER.warning('Connection service not initialized, skipping credential injection')
        return result

    for connection_id in connection_ids:
        try:
            # Resolve connection
            connection = connection_service.get_connection(connection_id)
            if not connection:
                LOGGER.warning(f'Connection "{connection_id}" not found, skipping')
                continue

            # Get connection type definition
            conn_type = get_connection_type(connection['type'])
            if not conn_type:
                LOGGER.warning(f'Unknown connection type "{connection["type"]}" for connection "{connection_id}", skipping')
                continue

            # Get injection mode and env prefix
            injection_mode = conn_type.injection_mode
            env_prefix = conn_type.env_prefix

            if injection_mode != 'env':
                LOGGER.warning(f'Connection "{connection_id}" has injection_mode="{injection_mode}", only "env" is currently supported')
                continue

            # Inject each field as an environment variable
            for field_def in conn_type.fields:
                field_name = field_def.name
                field_value = connection['fields'].get(field_name)

                if field_value is None:
                    continue

                # Build environment variable name: PREFIX_FIELD_NAME (e.g., PLEX_URL)
                env_var_name = f'{env_prefix}_{field_name.upper()}'

                # Inject into environment
                result[env_var_name] = str(field_value)

                LOGGER.debug(f'Injected {env_var_name} from connection "{connection_id}"')

            LOGGER.info(f'Injected credentials from connection "{connection_id}" (type: {connection["type"]})')

        except Exception as e:
            LOGGER.error(f'Failed to inject connection "{connection_id}": {e}', exc_info=True)
            continue

    return result


def get_connection_env_vars(connection_ids: List[str]) -> Dict[str, str]:
    """
    Get environment variables for given connections without merging with existing env.

    Args:
        connection_ids: List of connection IDs

    Returns:
        Dict of environment variables from connections only
    """
    return inject_connection_credentials(connection_ids, {})
