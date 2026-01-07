"""
User Management Service for htpasswd-based authentication.
Provides CRUD operations for users and role management.
"""

import json
import logging
import os
import re
import subprocess
from typing import List, Dict, Optional

from utils import file_utils

LOGGER = logging.getLogger('script_server.UserManagement')


class UserManagementService:
    """Manages users in htpasswd file and roles in conf.json"""

    def __init__(self, htpasswd_path: str, conf_path: str):
        self.htpasswd_path = htpasswd_path
        self.conf_path = conf_path

    def _ensure_htpasswd_exists(self):
        """Create htpasswd file if it doesn't exist"""
        if not os.path.exists(self.htpasswd_path):
            os.makedirs(os.path.dirname(self.htpasswd_path), exist_ok=True)
            with open(self.htpasswd_path, 'w') as f:
                pass  # Create empty file

    def _read_htpasswd_users(self) -> List[str]:
        """Read usernames from htpasswd file"""
        if not os.path.exists(self.htpasswd_path):
            return []

        users = []
        with open(self.htpasswd_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and ':' in line:
                    username = line.split(':')[0]
                    users.append(username)
        return users

    def _read_conf(self) -> dict:
        """Read conf.json"""
        if not os.path.exists(self.conf_path):
            return {}

        content = file_utils.read_file(self.conf_path)
        return json.loads(content) if content.strip() else {}

    def _write_conf(self, conf: dict):
        """Write conf.json"""
        os.makedirs(os.path.dirname(self.conf_path), exist_ok=True)
        with open(self.conf_path, 'w') as f:
            json.dump(conf, f, indent=2)

    def _get_access_config(self) -> dict:
        """Get access section from conf.json"""
        conf = self._read_conf()
        return conf.get('access', {})

    def _set_access_config(self, access: dict):
        """Update access section in conf.json"""
        conf = self._read_conf()
        conf['access'] = access
        self._write_conf(conf)

    def get_users(self) -> List[Dict]:
        """Get all users with their roles"""
        htpasswd_users = set(self._read_htpasswd_users())
        access = self._get_access_config()

        admin_users = access.get('admin_users', [])
        allowed_users = access.get('allowed_users', [])
        code_editors = access.get('code_editors', [])

        # Normalize to sets for easier checking
        if admin_users == '*' or '*' in admin_users:
            admin_set = {'*'}
        else:
            admin_set = set(admin_users) if isinstance(admin_users, list) else set()

        if allowed_users == '*' or '*' in allowed_users:
            allowed_set = {'*'}
        else:
            allowed_set = set(allowed_users) if isinstance(allowed_users, list) else set()

        if code_editors == '*' or '*' in code_editors:
            code_editor_set = {'*'}
        else:
            code_editor_set = set(code_editors) if isinstance(code_editors, list) else set()

        users = []
        for username in sorted(htpasswd_users):
            is_admin = '*' in admin_set or username in admin_set
            is_allowed = '*' in allowed_set or username in allowed_set or is_admin
            is_code_editor = '*' in code_editor_set or username in code_editor_set

            users.append({
                'username': username,
                'is_admin': is_admin,
                'is_allowed': is_allowed,
                'is_code_editor': is_code_editor
            })

        return users

    def add_user(self, username: str, password: str, is_admin: bool = False) -> bool:
        """Add a new user"""
        if not username or not password:
            raise ValueError('Username and password are required')

        if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
            raise ValueError('Username can only contain letters, numbers, underscores, dots, and hyphens')

        self._ensure_htpasswd_exists()

        # Check if user exists
        existing_users = self._read_htpasswd_users()
        if username in existing_users:
            raise ValueError(f'User {username} already exists')

        # Add to htpasswd using bcrypt (-B flag)
        try:
            subprocess.run(
                ['htpasswd', '-Bb', self.htpasswd_path, username, password],
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            LOGGER.error(f'Failed to add user {username}: {e.stderr.decode()}')
            raise RuntimeError(f'Failed to add user: {e.stderr.decode()}')
        except FileNotFoundError:
            # htpasswd not installed, use Python fallback
            self._add_user_python(username, password)

        # Update roles in conf.json
        access = self._get_access_config()

        # Ensure allowed_users list exists and add user
        if 'allowed_users' not in access or access['allowed_users'] == '*':
            access['allowed_users'] = ['*']  # Keep wildcard if it was set
        if '*' not in access['allowed_users']:
            if username not in access['allowed_users']:
                access['allowed_users'].append(username)

        # Add to admin_users if admin
        if is_admin:
            if 'admin_users' not in access:
                access['admin_users'] = []
            if access['admin_users'] != '*' and '*' not in access['admin_users']:
                if username not in access['admin_users']:
                    access['admin_users'].append(username)

        self._set_access_config(access)

        LOGGER.info(f'Added user {username} (admin={is_admin})')
        return True

    def _add_user_python(self, username: str, password: str):
        """Add user using Python bcrypt (fallback when htpasswd not installed)"""
        try:
            import bcrypt
        except ImportError:
            raise RuntimeError('Neither htpasswd utility nor bcrypt package is installed')

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        # bcrypt generates $2b$ but htpasswd expects $2y$
        hashed_str = hashed.decode('utf-8').replace('$2b$', '$2y$')

        with open(self.htpasswd_path, 'a') as f:
            f.write(f'{username}:{hashed_str}\n')

    def delete_user(self, username: str) -> bool:
        """Delete a user"""
        if not username:
            raise ValueError('Username is required')

        # Check if this is the last admin user
        users = self.get_users()
        user_to_delete = next((u for u in users if u['username'] == username), None)
        if user_to_delete and user_to_delete['is_admin']:
            admin_count = sum(1 for u in users if u['is_admin'])
            if admin_count <= 1:
                raise ValueError('Cannot delete the last admin user')

        # Remove from htpasswd
        try:
            subprocess.run(
                ['htpasswd', '-D', self.htpasswd_path, username],
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError:
            # User might not exist in htpasswd, continue to remove from roles
            pass
        except FileNotFoundError:
            # htpasswd not installed, use Python fallback
            self._delete_user_python(username)

        # Remove from all role lists in conf.json
        access = self._get_access_config()

        for key in ['allowed_users', 'admin_users', 'code_editors', 'full_history']:
            if key in access and isinstance(access[key], list):
                if username in access[key]:
                    access[key].remove(username)

        self._set_access_config(access)

        LOGGER.info(f'Deleted user {username}')
        return True

    def _delete_user_python(self, username: str):
        """Remove user from htpasswd file using Python"""
        if not os.path.exists(self.htpasswd_path):
            return

        lines = []
        with open(self.htpasswd_path, 'r') as f:
            for line in f:
                if not line.strip().startswith(username + ':'):
                    lines.append(line)

        with open(self.htpasswd_path, 'w') as f:
            f.writelines(lines)

    def update_user_password(self, username: str, password: str) -> bool:
        """Update a user's password"""
        if not username or not password:
            raise ValueError('Username and password are required')

        existing_users = self._read_htpasswd_users()
        if username not in existing_users:
            raise ValueError(f'User {username} does not exist')

        try:
            subprocess.run(
                ['htpasswd', '-Bb', self.htpasswd_path, username, password],
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f'Failed to update password: {e.stderr.decode()}')
        except FileNotFoundError:
            # htpasswd not installed, use Python fallback
            self._delete_user_python(username)
            self._add_user_python(username, password)

        LOGGER.info(f'Updated password for user {username}')
        return True

    def update_user_roles(self, username: str, is_admin: bool, is_code_editor: bool = False) -> bool:
        """Update a user's roles"""
        existing_users = self._read_htpasswd_users()
        if username not in existing_users:
            raise ValueError(f'User {username} does not exist')

        # Check if trying to remove admin from the last admin user
        if not is_admin:
            users = self.get_users()
            current_user = next((u for u in users if u['username'] == username), None)
            if current_user and current_user['is_admin']:
                admin_count = sum(1 for u in users if u['is_admin'])
                if admin_count <= 1:
                    raise ValueError('Cannot remove admin status from the last admin user')

        access = self._get_access_config()

        # Handle admin_users
        if 'admin_users' not in access:
            access['admin_users'] = []

        if access['admin_users'] != '*' and '*' not in access.get('admin_users', []):
            admin_list = access['admin_users'] if isinstance(access['admin_users'], list) else []
            if is_admin and username not in admin_list:
                admin_list.append(username)
            elif not is_admin and username in admin_list:
                admin_list.remove(username)
            access['admin_users'] = admin_list

        # Handle code_editors
        if 'code_editors' not in access:
            access['code_editors'] = []

        if access['code_editors'] != '*' and '*' not in access.get('code_editors', []):
            editor_list = access['code_editors'] if isinstance(access['code_editors'], list) else []
            if is_code_editor and username not in editor_list:
                editor_list.append(username)
            elif not is_code_editor and username in editor_list:
                editor_list.remove(username)
            access['code_editors'] = editor_list

        self._set_access_config(access)

        LOGGER.info(f'Updated roles for user {username}: admin={is_admin}, code_editor={is_code_editor}')
        return True

    def is_auth_enabled(self) -> bool:
        """Check if htpasswd auth is configured"""
        conf = self._read_conf()
        auth = conf.get('auth', {})
        return auth.get('type') == 'htpasswd'

    def enable_auth(self) -> bool:
        """Enable htpasswd authentication.

        Requires at least one admin user to exist before enabling.
        """
        # Check that at least one admin user exists
        users = self.get_users()
        admin_users = [u for u in users if u['is_admin']]

        if not admin_users:
            raise ValueError('Cannot enable authentication without at least one admin user. Add an admin user first.')

        conf = self._read_conf()

        conf['auth'] = {
            'type': 'htpasswd',
            'htpasswd_path': self.htpasswd_path
        }

        # Ensure access section exists with sensible defaults
        if 'access' not in conf:
            conf['access'] = {}

        # Remove wildcard access when enabling auth
        access = conf['access']
        if access.get('allowed_users') == '*' or access.get('allowed_users') == ['*']:
            # Set allowed_users to include all existing htpasswd users
            htpasswd_users = self._read_htpasswd_users()
            access['allowed_users'] = htpasswd_users if htpasswd_users else []
        if access.get('admin_users') == '*' or access.get('admin_users') == ['*']:
            # Set admin_users to include users marked as admin
            access['admin_users'] = [u['username'] for u in admin_users]

        self._write_conf(conf)
        self._ensure_htpasswd_exists()

        LOGGER.info('Enabled htpasswd authentication')
        return True

    def disable_auth(self) -> bool:
        """Disable authentication (everyone has access)"""
        conf = self._read_conf()

        # Remove auth section
        if 'auth' in conf:
            del conf['auth']

        # Set wildcard access
        conf['access'] = {
            'allowed_users': ['*'],
            'admin_users': ['*']
        }

        self._write_conf(conf)

        LOGGER.info('Disabled authentication')
        return True

    def get_auth_status(self) -> dict:
        """Get current authentication status"""
        conf = self._read_conf()
        auth = conf.get('auth', {})
        access = conf.get('access', {})

        return {
            'enabled': auth.get('type') == 'htpasswd',
            'type': auth.get('type'),
            'user_count': len(self._read_htpasswd_users()),
            'everyone_allowed': access.get('allowed_users') in ['*', ['*']],
            'everyone_admin': access.get('admin_users') in ['*', ['*']]
        }
