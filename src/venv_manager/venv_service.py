"""
Venv Package Management Service.
Manages Python packages in the project's venv directory.
"""

import json
import logging
import os
import subprocess
import sys
from typing import List, Dict, Optional

LOGGER = logging.getLogger('script_server.VenvService')


class VenvService:
    """Manages packages in the project venv"""

    def __init__(self, project_root: str):
        self.project_root = project_root
        self.venv_path = os.path.join(project_root, 'venv')
        self.pip_path = self._get_pip_path()
        self.python_path = self._get_python_path()

    def _get_pip_path(self) -> str:
        """Get path to pip in venv"""
        if sys.platform == 'win32':
            return os.path.join(self.venv_path, 'Scripts', 'pip')
        return os.path.join(self.venv_path, 'bin', 'pip')

    def _get_python_path(self) -> str:
        """Get path to python in venv"""
        if sys.platform == 'win32':
            return os.path.join(self.venv_path, 'Scripts', 'python')
        return os.path.join(self.venv_path, 'bin', 'python')

    def venv_exists(self) -> bool:
        """Check if venv exists"""
        return os.path.exists(self.pip_path)

    def create_venv(self) -> bool:
        """Create venv if it doesn't exist"""
        if self.venv_exists():
            return True

        try:
            LOGGER.info(f'Creating venv at {self.venv_path}')
            subprocess.run(
                [sys.executable, '-m', 'venv', self.venv_path],
                check=True,
                capture_output=True
            )
            LOGGER.info(f'Successfully created venv at {self.venv_path}')
            return True
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            LOGGER.error(f'Failed to create venv: {error_msg}')
            raise RuntimeError(f'Failed to create venv: {error_msg}')

    def get_status(self) -> Dict:
        """Get venv status including Python version"""
        if not self.venv_exists():
            return {
                'exists': False,
                'python_version': None,
                'path': self.venv_path
            }

        try:
            result = subprocess.run(
                [self.python_path, '--version'],
                capture_output=True,
                text=True
            )
            version = result.stdout.strip() or result.stderr.strip()
        except Exception:
            version = 'Unknown'

        return {
            'exists': True,
            'python_version': version,
            'path': self.venv_path
        }

    def list_packages(self) -> List[Dict]:
        """List installed packages with versions"""
        if not self.venv_exists():
            return []

        try:
            result = subprocess.run(
                [self.pip_path, 'list', '--format=json'],
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            LOGGER.error(f'Failed to list packages: {error_msg}')
            raise RuntimeError(f'Failed to list packages: {error_msg}')
        except json.JSONDecodeError as e:
            LOGGER.error(f'Failed to parse package list: {e}')
            raise RuntimeError(f'Failed to parse package list: {e}')

    def install_package(self, package: str, version: Optional[str] = None) -> Dict:
        """Install a package. Auto-creates venv if needed."""
        if not package or not package.strip():
            raise ValueError('Package name is required')

        package = package.strip()

        # Auto-create venv if needed
        if not self.venv_exists():
            self.create_venv()

        package_spec = f'{package}=={version}' if version else package

        try:
            LOGGER.info(f'Installing package: {package_spec}')
            result = subprocess.run(
                [self.pip_path, 'install', package_spec],
                capture_output=True,
                text=True,
                check=True
            )
            LOGGER.info(f'Successfully installed package: {package_spec}')
            return {
                'success': True,
                'package': package,
                'version': version,
                'output': result.stdout
            }
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            LOGGER.error(f'Failed to install {package_spec}: {error_msg}')
            raise RuntimeError(f'Failed to install package: {error_msg}')

    def uninstall_package(self, package: str) -> Dict:
        """Uninstall a package"""
        if not package or not package.strip():
            raise ValueError('Package name is required')

        package = package.strip()

        if not self.venv_exists():
            raise RuntimeError('Venv does not exist')

        try:
            LOGGER.info(f'Uninstalling package: {package}')
            result = subprocess.run(
                [self.pip_path, 'uninstall', '-y', package],
                capture_output=True,
                text=True,
                check=True
            )
            LOGGER.info(f'Successfully uninstalled package: {package}')
            return {
                'success': True,
                'package': package,
                'output': result.stdout
            }
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            LOGGER.error(f'Failed to uninstall {package}: {error_msg}')
            raise RuntimeError(f'Failed to uninstall package: {error_msg}')
