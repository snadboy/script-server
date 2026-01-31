"""
Venv Package Management Service.
Manages Python packages in the project's venv directory.
"""

import ast
import json
import logging
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Optional, Set

LOGGER = logging.getLogger('script_server.VenvService')

# PEP 508 compliant package name pattern
# Package names can only contain alphanumerics, hyphens, underscores, and periods
PACKAGE_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9._-]+$')
# Version pattern (basic semver + extras)
VERSION_PATTERN = re.compile(r'^[a-zA-Z0-9._+\-]+$')


class VenvService:
    """Manages packages in the project venv"""

    def __init__(self, project_root: str):
        self.project_root = project_root
        self.venv_path = os.path.join(project_root, '.venv')
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

    def _validate_package_name(self, package: str) -> None:
        """
        Validate package name to prevent command injection.

        Raises:
            ValueError: If package name contains invalid characters or pip options
        """
        if not package or not package.strip():
            raise ValueError('Package name cannot be empty')

        package = package.strip()

        # Check for pip options (anything starting with -)
        if package.startswith('-'):
            raise ValueError(f'Invalid package name: {package}. Package names cannot start with "-"')

        # Check for spaces (could allow multiple arguments)
        if ' ' in package:
            raise ValueError(f'Invalid package name: {package}. Package names cannot contain spaces')

        # Validate against PEP 508 pattern
        if not PACKAGE_NAME_PATTERN.match(package):
            raise ValueError(f'Invalid package name: {package}. Only alphanumerics, hyphens, underscores, and periods are allowed')

    def _validate_version(self, version: str) -> None:
        """
        Validate version string to prevent command injection.

        Raises:
            ValueError: If version contains invalid characters
        """
        if not version or not version.strip():
            return  # Version is optional

        version = version.strip()

        # Check for spaces or pip options
        if ' ' in version or version.startswith('-'):
            raise ValueError(f'Invalid version: {version}')

        # Validate version pattern
        if not VERSION_PATTERN.match(version):
            raise ValueError(f'Invalid version: {version}. Only alphanumerics, dots, hyphens, underscores, and plus signs are allowed')

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

        # Validate package name and version to prevent command injection
        self._validate_package_name(package)
        if version:
            version = version.strip()
            self._validate_version(version)

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

        # Validate package name to prevent command injection
        self._validate_package_name(package)

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

    def _get_stdlib_modules(self) -> Set[str]:
        """Get set of Python stdlib module names"""
        # Python 3.10+ has stdlib_module_names
        if hasattr(sys, 'stdlib_module_names'):
            return sys.stdlib_module_names

        # Fallback for older Python versions - common stdlib modules
        return {
            'abc', 'aifc', 'argparse', 'array', 'ast', 'asynchat', 'asyncio', 'asyncore',
            'atexit', 'audioop', 'base64', 'bdb', 'binascii', 'binhex', 'bisect', 'builtins',
            'bz2', 'calendar', 'cgi', 'cgitb', 'chunk', 'cmath', 'cmd', 'code', 'codecs',
            'codeop', 'collections', 'colorsys', 'compileall', 'concurrent', 'configparser',
            'contextlib', 'contextvars', 'copy', 'copyreg', 'cProfile', 'crypt', 'csv',
            'ctypes', 'curses', 'dataclasses', 'datetime', 'dbm', 'decimal', 'difflib',
            'dis', 'distutils', 'doctest', 'email', 'encodings', 'enum', 'errno', 'faulthandler',
            'fcntl', 'filecmp', 'fileinput', 'fnmatch', 'formatter', 'fractions', 'ftplib',
            'functools', 'gc', 'getopt', 'getpass', 'gettext', 'glob', 'grp', 'gzip',
            'hashlib', 'heapq', 'hmac', 'html', 'http', 'imaplib', 'imghdr', 'imp', 'importlib',
            'inspect', 'io', 'ipaddress', 'itertools', 'json', 'keyword', 'lib2to3', 'linecache',
            'locale', 'logging', 'lzma', 'mailbox', 'mailcap', 'marshal', 'math', 'mimetypes',
            'mmap', 'modulefinder', 'msilib', 'msvcrt', 'multiprocessing', 'netrc', 'nis',
            'nntplib', 'numbers', 'operator', 'optparse', 'os', 'ossaudiodev', 'parser',
            'pathlib', 'pdb', 'pickle', 'pickletools', 'pipes', 'pkgutil', 'platform',
            'plistlib', 'poplib', 'posix', 'posixpath', 'pprint', 'profile', 'pstats',
            'pty', 'pwd', 'py_compile', 'pyclbr', 'pydoc', 'queue', 'quopri', 'random',
            're', 'readline', 'reprlib', 'resource', 'rlcompleter', 'runpy', 'sched',
            'secrets', 'select', 'selectors', 'shelve', 'shlex', 'shutil', 'signal',
            'site', 'smtpd', 'smtplib', 'sndhdr', 'socket', 'socketserver', 'spwd',
            'sqlite3', 'ssl', 'stat', 'statistics', 'string', 'stringprep', 'struct',
            'subprocess', 'sunau', 'symbol', 'symtable', 'sys', 'sysconfig', 'syslog',
            'tabnanny', 'tarfile', 'telnetlib', 'tempfile', 'termios', 'test', 'textwrap',
            'threading', 'time', 'timeit', 'tkinter', 'token', 'tokenize', 'trace',
            'traceback', 'tracemalloc', 'tty', 'turtle', 'types', 'typing', 'unicodedata',
            'unittest', 'urllib', 'uu', 'uuid', 'venv', 'warnings', 'wave', 'weakref',
            'webbrowser', 'winreg', 'winsound', 'wsgiref', 'xdrlib', 'xml', 'xmlrpc',
            'zipapp', 'zipfile', 'zipimport', 'zlib'
        }

    def _extract_imports_from_file(self, filepath: str) -> Set[str]:
        """Extract top-level import names from a Python file"""
        imports = set()

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=filepath)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # Get root module (e.g., 'requests' from 'requests.auth')
                        root = alias.name.split('.')[0]
                        imports.add(root)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        # Get root module
                        root = node.module.split('.')[0]
                        imports.add(root)
        except Exception as e:
            LOGGER.debug(f'Failed to parse imports from {filepath}: {e}')

        return imports

    def _get_script_dependencies(self) -> Dict[str, Set[str]]:
        """
        Scan all scripts and return mapping of script_name -> set of imported packages
        """
        script_dependencies = {}

        # Get samples/scripts directory
        scripts_dir = os.path.join(self.project_root, 'samples', 'scripts')
        if not os.path.exists(scripts_dir):
            return script_dependencies

        # Find all .py files
        for py_file in Path(scripts_dir).rglob('*.py'):
            script_name = py_file.stem
            imports = self._extract_imports_from_file(str(py_file))

            if imports:
                script_dependencies[script_name] = imports

        return script_dependencies

    def get_requirements_with_dependencies(self) -> Dict:
        """
        Get all installed packages with script dependency information and missing packages.
        Returns dict with:
        - requirements: list of installed packages with name, version, is_stdlib, used_by
        - missing_packages: list of packages imported but not installed with name, needed_by
        - script_dependencies: dict mapping script_name -> list of package names
        """
        if not self.venv_exists():
            return {
                'requirements': [],
                'missing_packages': [],
                'script_dependencies': {}
            }

        # Get stdlib modules
        stdlib = self._get_stdlib_modules()

        # Get script dependencies (imports found in scripts)
        script_deps = self._get_script_dependencies()

        # Build reverse mapping: package -> list of scripts that use it
        package_usage = {}
        for script_name, imports in script_deps.items():
            for pkg in imports:
                if pkg not in package_usage:
                    package_usage[pkg] = []
                package_usage[pkg].append(script_name)

        # Get installed packages using pip freeze (name==version format)
        try:
            result = subprocess.run(
                [self.pip_path, 'freeze'],
                capture_output=True,
                text=True,
                check=True
            )

            # Build set of installed package names (normalized)
            installed_packages = set()
            requirements = []

            for line in result.stdout.strip().split('\n'):
                if not line or line.startswith('#') or line.startswith('-'):
                    continue

                # Parse name==version or name @ url
                if '==' in line:
                    name, version = line.split('==', 1)
                elif ' @ ' in line:
                    # Handle editable installs like "package @ file://..."
                    name = line.split(' @ ')[0]
                    version = 'editable'
                else:
                    # Handle other formats
                    name = line
                    version = 'unknown'

                name = name.strip()

                # Add to installed set with various normalizations
                installed_packages.add(name.lower())
                installed_packages.add(name.replace('-', '_').lower())
                installed_packages.add(name.replace('_', '-').lower())

                # Normalize package name (pip uses dashes, imports use underscores)
                # Example: google-api-python-client imports as googleapiclient
                import_name = name.replace('-', '_').lower()

                # Check if it's stdlib
                is_stdlib = name.lower() in stdlib or import_name in stdlib

                # Get scripts that use this package
                used_by = package_usage.get(name, [])
                if not used_by:
                    # Try with underscores
                    used_by = package_usage.get(import_name, [])
                if not used_by:
                    # Try common variations (e.g., google-api-python-client -> google)
                    for pkg_name in package_usage.keys():
                        if pkg_name.startswith(name.split('-')[0].lower()):
                            used_by.extend(package_usage[pkg_name])

                requirements.append({
                    'name': name,
                    'version': version,
                    'is_stdlib': is_stdlib,
                    'used_by': sorted(list(set(used_by)))
                })

            # Find missing packages (imported but not installed)
            missing_packages = []
            all_imports = set()
            for imports in script_deps.values():
                all_imports.update(imports)

            for import_name in all_imports:
                # Skip stdlib modules
                if import_name in stdlib:
                    continue

                # Check if installed (try various normalizations)
                normalized = import_name.lower()
                if normalized not in installed_packages:
                    # Find which scripts need this package
                    needed_by = [script for script, imports in script_deps.items()
                                if import_name in imports]

                    missing_packages.append({
                        'name': import_name,
                        'needed_by': sorted(needed_by)
                    })

            return {
                'requirements': requirements,
                'missing_packages': sorted(missing_packages, key=lambda x: x['name']),
                'script_dependencies': {k: sorted(list(v)) for k, v in script_deps.items()}
            }

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            LOGGER.error(f'Failed to get requirements: {error_msg}')
            raise RuntimeError(f'Failed to get requirements: {error_msg}')
