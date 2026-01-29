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

    def _get_requirements_file_path(self) -> str:
        """Get path to requirements.txt in conf directory"""
        return os.path.join(self.project_root, 'conf', 'requirements.txt')

    def read_requirements(self) -> str:
        """Read requirements.txt file content"""
        requirements_path = self._get_requirements_file_path()

        if not os.path.exists(requirements_path):
            return ''

        try:
            with open(requirements_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            LOGGER.error(f'Failed to read requirements.txt: {e}')
            raise RuntimeError(f'Failed to read requirements.txt: {str(e)}')

    def write_requirements(self, content: str) -> Dict:
        """Write requirements.txt file content"""
        requirements_path = self._get_requirements_file_path()

        # Create conf directory if it doesn't exist
        conf_dir = os.path.dirname(requirements_path)
        os.makedirs(conf_dir, exist_ok=True)

        try:
            with open(requirements_path, 'w', encoding='utf-8') as f:
                f.write(content)
            LOGGER.info(f'Successfully wrote requirements.txt')
            return {
                'success': True,
                'path': requirements_path,
                'lines': len(content.strip().split('\n')) if content.strip() else 0
            }
        except Exception as e:
            LOGGER.error(f'Failed to write requirements.txt: {e}')
            raise RuntimeError(f'Failed to write requirements.txt: {str(e)}')

    def sync_requirements(self) -> Dict:
        """Install all packages from requirements.txt"""
        requirements_path = self._get_requirements_file_path()

        if not os.path.exists(requirements_path):
            raise RuntimeError('requirements.txt not found')

        # Auto-create venv if needed
        if not self.venv_exists():
            self.create_venv()

        try:
            LOGGER.info(f'Installing packages from requirements.txt')
            result = subprocess.run(
                [self.pip_path, 'install', '-r', requirements_path],
                capture_output=True,
                text=True,
                check=True
            )
            LOGGER.info(f'Successfully installed packages from requirements.txt')
            return {
                'success': True,
                'output': result.stdout
            }
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            LOGGER.error(f'Failed to sync requirements: {error_msg}')
            raise RuntimeError(f'Failed to sync requirements: {error_msg}')

    def get_requirements_status(self) -> Dict:
        """Compare installed packages vs requirements.txt"""
        requirements_content = self.read_requirements()
        installed_packages = {pkg['name'].lower(): pkg['version'] for pkg in self.list_packages()}

        # Parse requirements.txt
        required = []
        for line in requirements_content.split('\n'):
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue

            # Parse package name and version
            # Handle formats: package, package==version, package>=version, etc.
            package_name = line.split('==')[0].split('>=')[0].split('<=')[0].split('>')[0].split('<')[0].strip()
            version_spec = line[len(package_name):].strip() if len(line) > len(package_name) else ''

            required.append({
                'name': package_name,
                'spec': version_spec,
                'installed': package_name.lower() in installed_packages,
                'installed_version': installed_packages.get(package_name.lower())
            })

        # Find extra installed packages (not in requirements)
        required_names = {pkg['name'].lower() for pkg in required}
        extra = [
            {'name': name, 'version': version}
            for name, version in installed_packages.items()
            if name not in required_names and name not in ['pip', 'setuptools', 'wheel']
        ]

        missing_count = sum(1 for pkg in required if not pkg['installed'])

        return {
            'required': required,
            'extra': extra,
            'missing_count': missing_count,
            'extra_count': len(extra),
            'total_required': len(required)
        }
