"""
Connection type registry and field definitions.

Defines available connection types (Plex, Sonarr, Google, etc.) and their
field schemas for the admin UI and credential injection.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ConnectionField:
    """Definition of a single field in a connection type."""

    name: str  # Internal field name (e.g., "api_key")
    label: str  # Display label for UI (e.g., "API Key")
    field_type: str  # "text" | "password" | "textarea" | "url"
    required: bool  # Whether the field is required
    secret: bool  # Whether to encrypt at rest and mask in UI
    help_text: str = ""  # Optional help text for the field
    placeholder: str = ""  # Optional placeholder text


@dataclass
class ConnectionType:
    """Definition of a connection type."""

    type_id: str  # Unique identifier (e.g., "plex")
    display_name: str  # Human-readable name (e.g., "Plex Media Server")
    icon: str  # Material icon name for UI
    description: str  # Brief description for type selector
    fields: List[ConnectionField]  # Field definitions
    injection_mode: str  # "env" | "file" | "both"
    env_prefix: str  # Prefix for environment variables (e.g., "PLEX")
    file_templates: Dict[str, str] = field(default_factory=dict)  # filename → template


# Connection type definitions
TYPE_REGISTRY: Dict[str, ConnectionType] = {}


def register_type(conn_type: ConnectionType):
    """Register a connection type in the global registry."""
    TYPE_REGISTRY[conn_type.type_id] = conn_type


# ============================================================================
# Plex Media Server
# ============================================================================

register_type(ConnectionType(
    type_id='plex',
    display_name='Plex Media Server',
    icon='live_tv',
    description='Plex media server for content management and playback',
    injection_mode='env',
    env_prefix='PLEX',
    fields=[
        ConnectionField(
            name='url',
            label='Server URL',
            field_type='url',
            required=True,
            secret=False,
            help_text='Full URL including port (e.g., http://192.168.1.50:32400)',
            placeholder='http://localhost:32400'
        ),
        ConnectionField(
            name='token',
            label='Authentication Token',
            field_type='password',
            required=True,
            secret=True,
            help_text='X-Plex-Token from account settings',
            placeholder=''
        ),
    ]
))

# ============================================================================
# Sonarr
# ============================================================================

register_type(ConnectionType(
    type_id='sonarr',
    display_name='Sonarr',
    icon='tv',
    description='TV series management and automation',
    injection_mode='env',
    env_prefix='SONARR',
    fields=[
        ConnectionField(
            name='url',
            label='Server URL',
            field_type='url',
            required=True,
            secret=False,
            help_text='Full URL including port',
            placeholder='http://localhost:8989'
        ),
        ConnectionField(
            name='api_key',
            label='API Key',
            field_type='password',
            required=True,
            secret=True,
            help_text='API key from Sonarr settings',
            placeholder=''
        ),
    ]
))

# ============================================================================
# Radarr
# ============================================================================

register_type(ConnectionType(
    type_id='radarr',
    display_name='Radarr',
    icon='movie',
    description='Movie management and automation',
    injection_mode='env',
    env_prefix='RADARR',
    fields=[
        ConnectionField(
            name='url',
            label='Server URL',
            field_type='url',
            required=True,
            secret=False,
            help_text='Full URL including port',
            placeholder='http://localhost:7878'
        ),
        ConnectionField(
            name='api_key',
            label='API Key',
            field_type='password',
            required=True,
            secret=True,
            help_text='API key from Radarr settings',
            placeholder=''
        ),
    ]
))

# ============================================================================
# SABnzbd
# ============================================================================

register_type(ConnectionType(
    type_id='sabnzbd',
    display_name='SABnzbd',
    icon='download',
    description='Usenet download client',
    injection_mode='env',
    env_prefix='SABNZBD',
    fields=[
        ConnectionField(
            name='url',
            label='Server URL',
            field_type='url',
            required=True,
            secret=False,
            help_text='Full URL including port',
            placeholder='http://localhost:8080'
        ),
        ConnectionField(
            name='api_key',
            label='API Key',
            field_type='password',
            required=True,
            secret=True,
            help_text='API key from SABnzbd settings',
            placeholder=''
        ),
    ]
))

# ============================================================================
# Home Assistant
# ============================================================================

register_type(ConnectionType(
    type_id='homeassistant',
    display_name='Home Assistant',
    icon='home',
    description='Home automation platform',
    injection_mode='env',
    env_prefix='HA',
    fields=[
        ConnectionField(
            name='url',
            label='Instance URL',
            field_type='url',
            required=True,
            secret=False,
            help_text='Full URL to your Home Assistant instance',
            placeholder='http://homeassistant.local:8123'
        ),
        ConnectionField(
            name='token',
            label='Long-Lived Access Token',
            field_type='password',
            required=True,
            secret=True,
            help_text='Generated from your user profile',
            placeholder=''
        ),
    ]
))

# ============================================================================
# Google (Gmail, Drive, Contacts, etc.)
# ============================================================================

register_type(ConnectionType(
    type_id='google',
    display_name='Google Account',
    icon='cloud',
    description='Google services (Gmail, Drive, Contacts, Calendar)',
    injection_mode='file',
    env_prefix='GOOGLE',
    fields=[
        ConnectionField(
            name='client_id',
            label='Client ID',
            field_type='text',
            required=True,
            secret=True,
            help_text='OAuth client ID from Google Cloud Console',
            placeholder=''
        ),
        ConnectionField(
            name='client_secret',
            label='Client Secret',
            field_type='password',
            required=True,
            secret=True,
            help_text='OAuth client secret from Google Cloud Console',
            placeholder=''
        ),
        ConnectionField(
            name='refresh_token',
            label='Refresh Token',
            field_type='password',
            required=True,
            secret=True,
            help_text='OAuth refresh token (obtain via initial auth flow)',
            placeholder=''
        ),
        ConnectionField(
            name='token_data',
            label='Token Data (JSON)',
            field_type='textarea',
            required=False,
            secret=True,
            help_text='Complete token.json content (auto-refreshed during execution)',
            placeholder='{"token": "...", "refresh_token": "...", ...}'
        ),
        ConnectionField(
            name='scopes',
            label='OAuth Scopes',
            field_type='text',
            required=False,
            secret=False,
            help_text='Comma-separated list of OAuth scopes',
            placeholder='https://www.googleapis.com/auth/gmail.modify'
        ),
    ],
    file_templates={
        'credentials.json': '''{
  "installed": {
    "client_id": "{{client_id}}",
    "client_secret": "{{client_secret}}",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token"
  }
}''',
        'token.json': '{{token_data}}'
    }
))

# ============================================================================
# Generic (User-Defined)
# ============================================================================

register_type(ConnectionType(
    type_id='generic',
    display_name='Generic Connection',
    icon='settings_ethernet',
    description='Custom connection with user-defined fields',
    injection_mode='env',
    env_prefix='CUSTOM',
    fields=[
        ConnectionField(
            name='prefix',
            label='Environment Variable Prefix',
            field_type='text',
            required=True,
            secret=False,
            help_text='Prefix for environment variables (e.g., MYSERVICE)',
            placeholder='MYSERVICE'
        ),
        # Note: Generic connections allow dynamic fields added via UI
        # The fields list here is just the base configuration
    ]
))


# ============================================================================
# Helper Functions
# ============================================================================

def get_connection_type(type_id: str) -> Optional[ConnectionType]:
    """
    Get a connection type by ID.

    Args:
        type_id: Connection type identifier

    Returns:
        ConnectionType or None if not found
    """
    return TYPE_REGISTRY.get(type_id)


def list_connection_types() -> List[ConnectionType]:
    """
    Get all registered connection types.

    Returns:
        List of all ConnectionType definitions
    """
    return list(TYPE_REGISTRY.values())


def get_connection_type_schema(type_id: str) -> Optional[Dict]:
    """
    Get the JSON schema for a connection type (for API responses).

    Args:
        type_id: Connection type identifier

    Returns:
        Dictionary with type metadata and field definitions
    """
    conn_type = get_connection_type(type_id)
    if not conn_type:
        return None

    return {
        'type_id': conn_type.type_id,
        'display_name': conn_type.display_name,
        'icon': conn_type.icon,
        'description': conn_type.description,
        'injection_mode': conn_type.injection_mode,
        'env_prefix': conn_type.env_prefix,
        'fields': [
            {
                'name': f.name,
                'label': f.label,
                'field_type': f.field_type,
                'required': f.required,
                'secret': f.secret,
                'help_text': f.help_text,
                'placeholder': f.placeholder,
            }
            for f in conn_type.fields
        ]
    }


def list_connection_type_schemas() -> List[Dict]:
    """
    Get JSON schemas for all connection types.

    Returns:
        List of connection type schemas
    """
    return [get_connection_type_schema(t.type_id) for t in list_connection_types()]
