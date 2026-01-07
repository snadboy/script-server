"""
Authentication Initialization Module.

Ensures authentication is always enabled with a default admin user
if no users exist. This provides a secure-by-default setup similar
to routers and NAS devices.
"""

import json
import logging
import os
from typing import Optional

LOGGER = logging.getLogger('script_server.AuthInitialization')

DEFAULT_ADMIN_USERNAME = 'admin'
DEFAULT_ADMIN_PASSWORD = 'changeme'
DEFAULT_PASSWORD_MARKER_FILE = '.default_password_active'


class AuthInitializer:
    """Initializes authentication on first run with default admin user."""

    def __init__(self, config_folder: str):
        self.config_folder = config_folder
        self.conf_path = os.path.join(config_folder, 'conf.json')
        self.htpasswd_path = os.path.join(config_folder, 'htpasswd')
        self.marker_path = os.path.join(config_folder, DEFAULT_PASSWORD_MARKER_FILE)

    def initialize(self) -> bool:
        """
        Initialize authentication if needed.

        - If no users exist, creates a default admin account
        - Always ensures htpasswd auth is enabled in conf.json

        Returns True if a new default admin was created.
        """
        created_default_admin = False

        if not self._has_users():
            LOGGER.info('No users found - initializing default admin account')

            # Create default admin user
            self._create_default_admin()

            # Create marker file to indicate default password is active
            self._create_default_password_marker()

            LOGGER.info(f'Default admin account created: {DEFAULT_ADMIN_USERNAME}/{DEFAULT_ADMIN_PASSWORD}')
            LOGGER.warning('Please change the default password immediately!')
            created_default_admin = True

        # Always ensure htpasswd auth is enabled
        if self._ensure_htpasswd_auth_enabled():
            LOGGER.info('Enabled htpasswd authentication')

        return created_default_admin

    def _has_users(self) -> bool:
        """Check if any users exist in htpasswd file."""
        if not os.path.exists(self.htpasswd_path):
            return False

        with open(self.htpasswd_path, 'r') as f:
            for line in f:
                if line.strip() and ':' in line:
                    return True
        return False

    def _create_default_admin(self):
        """Create default admin user in htpasswd file."""
        os.makedirs(os.path.dirname(self.htpasswd_path), exist_ok=True)

        # Try using htpasswd command first
        try:
            import subprocess
            subprocess.run(
                ['htpasswd', '-Bbc', self.htpasswd_path, DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD],
                check=True,
                capture_output=True
            )
            return
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        # Fall back to Python bcrypt
        try:
            import bcrypt
            hashed = bcrypt.hashpw(DEFAULT_ADMIN_PASSWORD.encode('utf-8'), bcrypt.gensalt())
            # bcrypt generates $2b$ but htpasswd expects $2y$
            hashed_str = hashed.decode('utf-8').replace('$2b$', '$2y$')

            with open(self.htpasswd_path, 'w') as f:
                f.write(f'{DEFAULT_ADMIN_USERNAME}:{hashed_str}\n')
        except ImportError:
            raise RuntimeError('Neither htpasswd utility nor bcrypt package is installed')

    def _ensure_htpasswd_auth_enabled(self) -> bool:
        """
        Ensure conf.json has htpasswd auth configured.

        Returns True if configuration was changed.
        """
        conf = {}
        if os.path.exists(self.conf_path):
            with open(self.conf_path, 'r') as f:
                content = f.read().strip()
                if content:
                    conf = json.loads(content)

        # Check if auth is already properly configured
        auth = conf.get('auth', {})
        if auth.get('type') == 'htpasswd':
            return False  # Already configured

        # Set up htpasswd authentication
        conf['auth'] = {
            'type': 'htpasswd',
            'htpasswd_path': self.htpasswd_path
        }

        # Set up access config - preserve existing users or use htpasswd users
        if 'access' not in conf:
            conf['access'] = {}

        access = conf['access']

        # Get existing htpasswd users
        htpasswd_users = self._get_htpasswd_users()

        # For admin_users: if wildcard, set to htpasswd users; otherwise preserve
        if access.get('admin_users') in ['*', ['*'], None]:
            # Default: first user is admin, or all users if no clear choice
            access['admin_users'] = htpasswd_users if htpasswd_users else []
        elif isinstance(access.get('admin_users'), list):
            # Preserve existing list but filter to only htpasswd users
            access['admin_users'] = [u for u in access['admin_users'] if u in htpasswd_users]

        # For allowed_users: if wildcard, set to htpasswd users; otherwise preserve
        if access.get('allowed_users') in ['*', ['*'], None]:
            access['allowed_users'] = htpasswd_users if htpasswd_users else []
        elif isinstance(access.get('allowed_users'), list):
            # Preserve existing list but ensure htpasswd users are included
            existing = set(access['allowed_users'])
            existing.update(htpasswd_users)
            access['allowed_users'] = list(existing)

        # Write updated config
        os.makedirs(os.path.dirname(self.conf_path), exist_ok=True)
        with open(self.conf_path, 'w') as f:
            json.dump(conf, f, indent=2)

        return True

    def _get_htpasswd_users(self) -> list:
        """Get list of usernames from htpasswd file."""
        users = []
        if os.path.exists(self.htpasswd_path):
            with open(self.htpasswd_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and ':' in line:
                        users.append(line.split(':')[0])
        return users

    def _create_default_password_marker(self):
        """Create marker file indicating default password is still active."""
        with open(self.marker_path, 'w') as f:
            f.write(DEFAULT_ADMIN_USERNAME)

    def is_using_default_password(self) -> bool:
        """Check if the default admin password is still in use."""
        return os.path.exists(self.marker_path)

    def clear_default_password_marker(self):
        """Clear the marker file when password is changed."""
        if os.path.exists(self.marker_path):
            os.remove(self.marker_path)
            LOGGER.info('Default password marker cleared')

    def get_default_password_user(self) -> Optional[str]:
        """Get the username that still has the default password, if any."""
        if not os.path.exists(self.marker_path):
            return None
        with open(self.marker_path, 'r') as f:
            return f.read().strip() or None


def initialize_auth(config_folder: str) -> AuthInitializer:
    """
    Initialize authentication and return the initializer instance.

    This should be called early in server startup, before conf.json is loaded.
    """
    initializer = AuthInitializer(config_folder)
    initializer.initialize()
    return initializer
