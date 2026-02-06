"""
Project Manager Service for importing external Python projects.

Handles Git cloning, ZIP extraction, dependency detection, entry point scanning,
and wrapper script generation for use with script-server.
"""

import json
import logging
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

try:
    import tomllib
except ImportError:
    # Python < 3.11 fallback
    tomllib = None

LOGGER = logging.getLogger('script_server.project_manager')

# Wrapper script template
WRAPPER_TEMPLATE = '''#!/usr/bin/env python3
"""
Auto-generated wrapper script for {project_name}.

This script runs the project using the script-server common venv.
Required packages: {dependencies}
"""

import sys
import os

# Add project source to Python path
PROJECT_SRC_PATH = '{src_path}'
sys.path.insert(0, PROJECT_SRC_PATH)

# Change to project directory for config/token files
os.chdir('{project_root}')

{config_injection}

# Import and run the CLI app
{import_statement}

if __name__ == '__main__':
    {run_statement}
'''


class ProjectService:
    """Service for managing imported Python projects."""

    def __init__(self, project_root: str):
        """
        Initialize the ProjectService.

        Args:
            project_root: Path to script-server root directory
        """
        self.project_root = Path(project_root)
        # Use /app/projects in Docker, {project_root}/projects locally
        if os.path.exists('/app'):
            self.projects_dir = Path('/app/projects')
        else:
            self.projects_dir = self.project_root / 'projects'
        self.scripts_dir = self.project_root / 'samples' / 'scripts'
        self.runners_dir = self.project_root / 'conf' / 'runners'
        self.venv_python = self.project_root / '.venv' / 'bin' / 'python'

    def _ensure_projects_dir(self) -> None:
        """Create projects directory if it doesn't exist."""
        self.projects_dir.mkdir(parents=True, exist_ok=True)

    def _get_meta_path(self, project_path: Path) -> Path:
        """Get path to project metadata file."""
        return project_path / '.project-meta.json'

    def _load_meta(self, project_path: Path) -> dict:
        """Load project metadata from JSON file."""
        meta_path = self._get_meta_path(project_path)
        if meta_path.exists():
            with open(meta_path, 'r') as f:
                return json.load(f)
        return {}

    def _save_meta(self, project_path: Path, meta: dict) -> None:
        """Save project metadata to JSON file."""
        meta_path = self._get_meta_path(project_path)
        with open(meta_path, 'w') as f:
            json.dump(meta, f, indent=2, default=str)

    def _sanitize_project_id(self, name: str) -> str:
        """Convert a name to a safe project ID."""
        # Remove .git suffix if present
        name = re.sub(r'\.git$', '', name)
        # Replace non-alphanumeric with hyphens
        project_id = re.sub(r'[^a-zA-Z0-9]+', '-', name.lower())
        # Remove leading/trailing hyphens
        project_id = project_id.strip('-')
        return project_id or 'project'

    def _ensure_unique_name(self, proposed_name: str) -> str:
        """
        Ensure a project name is unique by appending a counter if needed.

        Args:
            proposed_name: The desired project name

        Returns:
            A unique project name (e.g., "Gmail Trim" or "Gmail Trim 2")
        """
        existing_projects = self.list_projects()
        existing_names = {p['name'].lower() for p in existing_projects}

        # If name is unique, return as-is
        if proposed_name.lower() not in existing_names:
            return proposed_name

        # Find next available number
        counter = 2
        while True:
            candidate = f"{proposed_name} {counter}"
            if candidate.lower() not in existing_names:
                return candidate
            counter += 1

    def list_projects(self) -> list[dict]:
        """
        List all imported projects.

        Returns:
            List of project metadata dictionaries
        """
        self._ensure_projects_dir()
        projects = []

        for item in self.projects_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                meta = self._load_meta(item)
                if meta:
                    projects.append(meta)
                else:
                    # Directory exists but no metadata - create minimal info
                    projects.append({
                        'id': item.name,
                        'name': item.name,
                        'import_type': 'unknown',
                        'imported_at': None
                    })

        return sorted(projects, key=lambda x: x.get('name', ''))

    def get_project(self, project_id: str) -> Optional[dict]:
        """
        Get a single project's details.

        Args:
            project_id: The project identifier

        Returns:
            Project metadata dictionary or None if not found
        """
        project_path = self.projects_dir / project_id
        if not project_path.exists():
            return None
        return self._load_meta(project_path)

    @staticmethod
    def _validate_git_url(url: str) -> None:
        """
        Validate Git URL to prevent SSRF attacks.

        Args:
            url: Git repository URL

        Raises:
            ValueError: If URL is invalid or uses disallowed protocol/host
        """
        if not url or not url.strip():
            raise ValueError('URL cannot be empty')

        url = url.strip()

        # Parse URL
        try:
            parsed = urlparse(url)
        except ValueError as e:
            raise ValueError(f'Invalid URL: {e}') from e

        # Only allow https:// protocol (not http, git, ssh, file, etc.)
        if parsed.scheme != 'https':
            raise ValueError(f'Only HTTPS URLs are allowed. Got: {parsed.scheme}://')

        # Validate hostname exists
        if not parsed.netloc:
            raise ValueError('URL must include a hostname')

        # Optional: Restrict to known Git hosting providers
        # Uncomment to enable allowlist
        # allowed_hosts = ['github.com', 'gitlab.com', 'bitbucket.org']
        # if not any(parsed.netloc.endswith(host) for host in allowed_hosts):
        #     raise ValueError(f'Git cloning is restricted to: {", ".join(allowed_hosts)}')

    def import_from_git(self, url: str, branch: Optional[str] = None) -> dict:
        """
        Import a project by cloning a Git repository.

        Args:
            url: Git repository URL
            branch: Optional branch to clone

        Returns:
            Project metadata dictionary

        Raises:
            Exception: If clone fails
        """
        # Validate URL to prevent SSRF attacks
        self._validate_git_url(url)

        self._ensure_projects_dir()

        # Extract repo name from URL
        repo_name = url.rstrip('/').split('/')[-1]
        project_id = self._sanitize_project_id(repo_name)

        # Ensure unique project ID
        base_id = project_id
        counter = 1
        while (self.projects_dir / project_id).exists():
            project_id = f"{base_id}-{counter}"
            counter += 1

        project_path = self.projects_dir / project_id

        # Build git clone command
        cmd = ['git', 'clone', '--depth', '1']
        if branch:
            cmd.extend(['-b', branch])
        cmd.extend([url, str(project_path)])

        LOGGER.info(f"Cloning {url} to {project_path}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"Git clone failed: {result.stderr}")

        # Detect dependencies and entry points
        dependencies = self.detect_dependencies(project_path)
        entry_points = self.detect_entry_points(project_path)

        # Create metadata with unique name
        base_name = repo_name.replace('-', ' ').replace('_', ' ').title()
        unique_name = self._ensure_unique_name(base_name)

        meta = {
            'id': project_id,
            'name': unique_name,
            'import_type': 'git',
            'source_url': url,
            'branch': branch,
            'imported_at': datetime.now().isoformat(),
            'entry_points': entry_points,
            'dependencies': dependencies,
            'wrapper_script': None,
            'runner_config': None
        }
        self._save_meta(project_path, meta)

        return meta

    def import_from_zip(self, file_data: bytes, filename: str) -> dict:
        """
        Import a project from a ZIP file.

        Args:
            file_data: ZIP file content as bytes
            filename: Original filename

        Returns:
            Project metadata dictionary

        Raises:
            Exception: If extraction fails
        """
        self._ensure_projects_dir()

        # Extract project name from filename
        base_name = filename.rsplit('.', 1)[0] if '.' in filename else filename
        project_id = self._sanitize_project_id(base_name)

        # Ensure unique project ID
        base_id = project_id
        counter = 1
        while (self.projects_dir / project_id).exists():
            project_id = f"{base_id}-{counter}"
            counter += 1

        project_path = self.projects_dir / project_id

        # Extract ZIP to temporary directory first
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / 'upload.zip'
            with open(zip_path, 'wb') as f:
                f.write(file_data)

            with zipfile.ZipFile(zip_path, 'r') as zf:
                # Check for single top-level directory
                names = zf.namelist()
                top_dirs = set(n.split('/')[0] for n in names if '/' in n)

                extract_path = Path(tmpdir) / 'extracted'
                extract_path.mkdir(parents=True, exist_ok=True)

                # Safely extract all files with zip-slip protection
                for member in zf.namelist():
                    # Validate path doesn't escape extraction directory
                    member_path = (extract_path / member).resolve()
                    if not str(member_path).startswith(str(extract_path.resolve())):
                        raise ValueError(f'Invalid ZIP entry (path traversal): {member}')

                    # Extract individual file
                    zf.extract(member, extract_path)

                # If single top-level dir, use its contents
                if len(top_dirs) == 1:
                    source_path = extract_path / list(top_dirs)[0]
                else:
                    source_path = extract_path

                # Move to final location
                shutil.move(str(source_path), str(project_path))

        # Detect dependencies and entry points
        dependencies = self.detect_dependencies(project_path)
        entry_points = self.detect_entry_points(project_path)

        # Create metadata with unique name
        display_name = base_name.replace('-', ' ').replace('_', ' ').title()
        unique_name = self._ensure_unique_name(display_name)

        meta = {
            'id': project_id,
            'name': unique_name,
            'import_type': 'zip',
            'source_url': None,
            'imported_at': datetime.now().isoformat(),
            'entry_points': entry_points,
            'dependencies': dependencies,
            'wrapper_script': None,
            'runner_config': None
        }
        self._save_meta(project_path, meta)

        return meta

    def import_from_local(self, local_path: str) -> dict:
        """
        Import a project from a local directory.

        Args:
            local_path: Path to the local project directory

        Returns:
            Project metadata dictionary

        Raises:
            Exception: If path doesn't exist or copy fails
        """
        self._ensure_projects_dir()

        source_path = Path(local_path).resolve()

        # Validate source path
        if not source_path.exists():
            raise FileNotFoundError(f"Path does not exist: {local_path}")
        if not source_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {local_path}")

        # Extract project name from directory name
        dir_name = source_path.name
        project_id = self._sanitize_project_id(dir_name)

        # Ensure unique project ID
        base_id = project_id
        counter = 1
        while (self.projects_dir / project_id).exists():
            project_id = f"{base_id}-{counter}"
            counter += 1

        project_path = self.projects_dir / project_id

        # Copy directory to projects folder
        LOGGER.info(f"Copying {source_path} to {project_path}")
        shutil.copytree(str(source_path), str(project_path))

        # Detect dependencies and entry points
        dependencies = self.detect_dependencies(project_path)
        entry_points = self.detect_entry_points(project_path)

        # Create metadata with unique name
        display_name = dir_name.replace('-', ' ').replace('_', ' ').title()
        unique_name = self._ensure_unique_name(display_name)

        meta = {
            'id': project_id,
            'name': unique_name,
            'import_type': 'local',
            'source_url': str(source_path),
            'imported_at': datetime.now().isoformat(),
            'entry_points': entry_points,
            'dependencies': dependencies,
            'wrapper_script': None,
            'runner_config': None
        }
        self._save_meta(project_path, meta)

        return meta

    def delete_project(self, project_id: str) -> bool:
        """
        Delete an imported project and its generated files.

        Args:
            project_id: The project identifier

        Returns:
            True if deleted, False if not found
        """
        project_path = self.projects_dir / project_id
        if not project_path.exists():
            return False

        # Load metadata to find generated files
        meta = self._load_meta(project_path)

        # Delete legacy wrapper script if exists (backward compatibility)
        if meta.get('wrapper_script'):
            wrapper_path = Path(meta['wrapper_script'])
            if wrapper_path.exists():
                wrapper_path.unlink()
                LOGGER.info(f"Deleted legacy wrapper: {wrapper_path}")

        # Delete legacy runner config if exists (backward compatibility)
        if meta.get('runner_config'):
            config_path = Path(meta['runner_config'])
            if config_path.exists():
                config_path.unlink()
                LOGGER.info(f"Deleted legacy config: {config_path}")

        # Find and delete ALL runner configs that reference this project
        deleted_configs = 0
        deleted_wrappers = set()

        if self.runners_dir.exists():
            for config_file in self.runners_dir.glob('*.json'):
                try:
                    with open(config_file, 'r') as f:
                        config_data = json.load(f)

                    # Check if this config references the project being deleted
                    if config_data.get('project_id') == project_id:
                        # Extract wrapper script path before deleting config
                        script_path = config_data.get('script_path', '')
                        # Extract the actual wrapper path from script_path
                        # Format: "/path/to/python /path/to/wrapper.py"
                        if script_path:
                            parts = script_path.split()
                            if len(parts) >= 2:
                                wrapper_file = Path(parts[-1])
                                deleted_wrappers.add(wrapper_file)

                        # Delete the config file
                        config_file.unlink()
                        deleted_configs += 1
                        LOGGER.info(f"Deleted instance config: {config_file.name}")

                except (OSError, json.JSONDecodeError, KeyError) as e:
                    LOGGER.warning(f"Failed to process config {config_file}: {e}")
                    continue

        # Delete all wrapper scripts for this project
        for wrapper_path in deleted_wrappers:
            if wrapper_path.exists():
                wrapper_path.unlink()
                LOGGER.info(f"Deleted wrapper script: {wrapper_path}")

        # Delete project directory
        shutil.rmtree(project_path)
        LOGGER.info(f"Deleted project {project_id}: {deleted_configs} instance(s) removed")

        return True

    def detect_dependencies(self, project_path: Path) -> list[str]:
        """
        Detect project dependencies from pyproject.toml or requirements.txt.

        Args:
            project_path: Path to the project directory

        Returns:
            List of dependency package names
        """
        dependencies = []
        project_path = Path(project_path)

        # Try pyproject.toml first
        pyproject_path = project_path / 'pyproject.toml'
        if pyproject_path.exists() and tomllib:
            try:
                with open(pyproject_path, 'rb') as f:
                    data = tomllib.load(f)

                # Standard [project.dependencies]
                deps = data.get('project', {}).get('dependencies', [])
                for dep in deps:
                    # Extract package name (before any version specifier)
                    name = re.split(r'[<>=\[!~]', dep)[0].strip()
                    if name:
                        dependencies.append(name)

                # Poetry [tool.poetry.dependencies]
                poetry_deps = data.get('tool', {}).get('poetry', {}).get('dependencies', {})
                for name in poetry_deps:
                    if name.lower() != 'python':
                        dependencies.append(name)

            except (OSError, KeyError, TypeError) as e:
                LOGGER.warning(f"Failed to parse pyproject.toml: {e}")

        # Try requirements.txt
        requirements_path = project_path / 'requirements.txt'
        if requirements_path.exists() and not dependencies:
            try:
                with open(requirements_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and not line.startswith('-'):
                            # Extract package name
                            name = re.split(r'[<>=\[!~]', line)[0].strip()
                            if name:
                                dependencies.append(name)
            except OSError as e:
                LOGGER.warning(f"Failed to parse requirements.txt: {e}")

        return list(set(dependencies))

    def detect_entry_points(self, project_path: Path) -> list[str]:
        """
        Detect CLI entry points in the project.

        Args:
            project_path: Path to the project directory

        Returns:
            List of entry point strings (e.g., "module.main:app")
        """
        entry_points = []
        project_path = Path(project_path)

        # Find source directory
        src_dir = None
        if (project_path / 'src').is_dir():
            src_dir = project_path / 'src'
        else:
            src_dir = project_path

        # 1. Check pyproject.toml for declared entry points
        pyproject_path = project_path / 'pyproject.toml'
        if pyproject_path.exists() and tomllib:
            try:
                with open(pyproject_path, 'rb') as f:
                    data = tomllib.load(f)

                # Standard [project.scripts]
                scripts = data.get('project', {}).get('scripts', {})
                for name, entry in scripts.items():
                    entry_points.append(entry)

                # Poetry [tool.poetry.scripts]
                poetry_scripts = data.get('tool', {}).get('poetry', {}).get('scripts', {})
                for name, entry in poetry_scripts.items():
                    entry_points.append(entry)

            except (OSError, KeyError, TypeError) as e:
                LOGGER.warning(f"Failed to parse pyproject.toml for entry points: {e}")

        # 2. Scan for __main__.py files
        for main_file in src_dir.rglob('__main__.py'):
            # Get module path relative to src_dir
            rel_path = main_file.parent.relative_to(src_dir)
            module_name = str(rel_path).replace(os.sep, '.')
            if module_name and module_name != '.':
                entry_points.append(f"{module_name}.__main__")

        # 3. Scan Python files for CLI patterns
        for py_file in src_dir.glob('**/*.py'):
            if py_file.name.startswith('_') and py_file.name != '__main__.py':
                continue

            try:
                content = py_file.read_text()
                rel_path = py_file.relative_to(src_dir)
                module_name = str(rel_path.with_suffix('')).replace(os.sep, '.')

                # Look for typer app
                if 'typer.Typer()' in content or 'typer.Typer(' in content:
                    match = re.search(r'(\w+)\s*=\s*typer\.Typer\(', content)
                    if match:
                        entry_points.append(f"{module_name}:{match.group(1)}")
                    else:
                        entry_points.append(f"{module_name}:app")

                # Look for click app
                elif '@click.command' in content or '@click.group' in content:
                    if 'def main(' in content:
                        entry_points.append(f"{module_name}:main")
                    elif 'def cli(' in content:
                        entry_points.append(f"{module_name}:cli")

                # Look for standard Python CLI pattern: if __name__ == "__main__" with main()
                elif "if __name__" in content and "__main__" in content:
                    if 'def main(' in content:
                        entry_points.append(f"{module_name}:main")
                    # Also check for direct script execution pattern
                    elif re.search(r'if\s+__name__\s*==\s*["\']__main__["\']\s*:', content):
                        # This file can be run directly, add as module entry
                        entry_points.append(f"{module_name}")

            except (OSError, UnicodeDecodeError) as e:
                LOGGER.warning(f"Failed to scan {py_file} for entry points: {e}")

        # 4. If no entry points found, list root-level .py files as potential entries
        if not entry_points:
            for py_file in src_dir.glob('*.py'):
                if py_file.name.startswith('_'):
                    continue
                module_name = py_file.stem
                # Prefer main.py, cli.py, app.py
                if module_name in ('main', 'cli', 'app'):
                    entry_points.insert(0, f"{module_name}:main")
                else:
                    entry_points.append(f"{module_name}")

        return list(dict.fromkeys(entry_points))  # Remove duplicates, preserve order

    def generate_wrapper(
        self,
        project_id: str,
        entry_point: str,
        config_path: Optional[str] = None,
        config_cmd: Optional[str] = None,
        script_name: Optional[str] = None
    ) -> str:
        """
        Generate a wrapper script for the project.

        Args:
            project_id: The project identifier
            entry_point: Entry point string (e.g., "module.main:app")
            config_path: Optional path to config file
            config_cmd: Optional command that uses config (e.g., "run")
            script_name: Optional script name to make wrapper filename unique

        Returns:
            Path to the generated wrapper script
        """
        project_path = self.projects_dir / project_id
        meta = self._load_meta(project_path)

        # Determine source path
        if (project_path / 'src').is_dir():
            src_path = project_path / 'src'
        else:
            src_path = project_path

        # Parse entry point
        if ':' in entry_point:
            module_path, obj_name = entry_point.rsplit(':', 1)
        else:
            module_path = entry_point
            obj_name = 'main'

        # Build import statement
        import_statement = f"from {module_path} import {obj_name}"

        # Build run statement
        if obj_name in ('app', 'cli'):
            run_statement = f"{obj_name}()"
        else:
            run_statement = f"{obj_name}()"

        # Build config injection
        config_injection = ''
        if config_path and config_cmd:
            config_injection = f'''# Inject --config if running '{config_cmd}' command and not already specified
if len(sys.argv) >= 2 and sys.argv[1] == '{config_cmd}' and '--config' not in sys.argv:
    sys.argv.insert(2, '--config')
    sys.argv.insert(3, '{config_path}')
'''

        # Generate wrapper content
        wrapper_content = WRAPPER_TEMPLATE.format(
            project_name=meta.get('name', project_id),
            dependencies=', '.join(meta.get('dependencies', [])),
            src_path=str(src_path),
            project_root=str(project_path),
            config_injection=config_injection,
            import_statement=import_statement,
            run_statement=run_statement
        )

        # Write wrapper script
        self.scripts_dir.mkdir(parents=True, exist_ok=True)

        # Use script_name in filename if provided to allow multiple scripts per project
        if script_name:
            # Sanitize script name for filesystem (replace spaces/special chars with underscores)
            safe_name = ''.join(c if c.isalnum() or c in ('-', '_') else '_' for c in script_name)
            wrapper_filename = f"{project_id}_{safe_name}.py"
        else:
            wrapper_filename = f"{project_id}.py"

        wrapper_path = self.scripts_dir / wrapper_filename

        with open(wrapper_path, 'w') as f:
            f.write(wrapper_content)

        # Make executable
        wrapper_path.chmod(0o755)

        # Update metadata (keep as single wrapper_script for backward compatibility)
        meta['wrapper_script'] = str(wrapper_path)
        self._save_meta(project_path, meta)

        LOGGER.info(f"Generated wrapper: {wrapper_path}")
        return str(wrapper_path)

    def update_project_parameters(self, project_id: str, parameters: list[dict]) -> dict:
        """
        Update parameter definitions for a project.

        Args:
            project_id: The project identifier
            parameters: List of parameter definition dictionaries

        Returns:
            Updated project metadata

        Raises:
            ValueError: If parameter validation fails
        """
        from model.parameter_config import ParameterModel

        project_path = self.projects_dir / project_id
        if not project_path.exists():
            raise FileNotFoundError(f"Project {project_id} not found")

        meta = self._load_meta(project_path)

        # Validate each parameter (static validation only)
        for param in parameters:
            if not param.get('name'):
                raise ValueError("Parameter must have a 'name' field")
            # Additional validation can be added here

        meta['parameters'] = parameters
        self._save_meta(project_path, meta)

        LOGGER.info(f"Updated parameters for project {project_id}")
        return meta

    def update_project_verbs(
        self,
        project_id: str,
        verbs_config: Optional[dict],
        shared_params: Optional[list[str]] = None
    ) -> dict:
        """
        Update verb configuration for a project.

        Args:
            project_id: The project identifier
            verbs_config: Verb configuration dictionary (or None to remove verbs)
            shared_params: List of shared parameter names (optional)

        Returns:
            Updated project metadata

        Raises:
            ValueError: If verb validation fails
        """
        from model.verb_config import VerbsConfiguration

        project_path = self.projects_dir / project_id
        if not project_path.exists():
            raise FileNotFoundError(f"Project {project_id} not found")

        meta = self._load_meta(project_path)

        # Validate verb config if provided
        if verbs_config:
            VerbsConfiguration(verbs_config)  # Will raise if invalid

        meta['verbs'] = verbs_config
        meta['shared_parameters'] = shared_params or []
        self._save_meta(project_path, meta)

        LOGGER.info(f"Updated verbs for project {project_id}")
        return meta

    def update_project_supported_connections(
        self,
        project_id: str,
        supported_connections: list[str]
    ) -> dict:
        """
        Update supported connection types for a project.

        Args:
            project_id: The project identifier
            supported_connections: List of connection type identifiers

        Returns:
            Updated project metadata
        """
        project_path = self.projects_dir / project_id
        if not project_path.exists():
            raise FileNotFoundError(f"Project {project_id} not found")

        meta = self._load_meta(project_path)
        meta['supported_connections'] = supported_connections
        self._save_meta(project_path, meta)

        LOGGER.info(f"Updated supported_connections for project {project_id}")
        return meta

    def get_project_parameters(self, project_id: str) -> list[dict]:
        """
        Get parameter definitions from project.

        Args:
            project_id: The project identifier

        Returns:
            List of parameter definition dictionaries
        """
        meta = self.get_project(project_id)
        if not meta:
            raise FileNotFoundError(f"Project {project_id} not found")
        return meta.get('parameters', [])

    def get_project_verbs(self, project_id: str) -> Optional[dict]:
        """
        Get verb configuration from project.

        Args:
            project_id: The project identifier

        Returns:
            Verb configuration dictionary or None
        """
        meta = self.get_project(project_id)
        if not meta:
            raise FileNotFoundError(f"Project {project_id} not found")
        return meta.get('verbs')

    def generate_runner_config(
        self,
        project_id: str,
        script_name: str,
        description: Optional[str] = None,
        group: str = 'Imported Projects',
        parameters: Optional[list[dict]] = None,
        included_parameters: Optional[list[str]] = None,
        parameter_values: Optional[dict] = None,
        selected_verb: Optional[str] = None
    ) -> str:
        """
        Generate a script-server runner configuration.

        Args:
            project_id: The project identifier
            script_name: Display name for the script
            description: Optional description
            group: Script group (default: 'Imported Projects')
            parameters: Optional list of parameter definitions (LEGACY - will be ignored if included_parameters is provided)
            included_parameters: List of parameter names to include from project (NEW)
            parameter_values: Dictionary of parameter value overrides (NEW)
            selected_verb: Selected verb name if project has verbs (NEW)

        Returns:
            Path to the generated config file
        """
        project_path = self.projects_dir / project_id
        meta = self._load_meta(project_path)

        wrapper_path = meta.get('wrapper_script')
        if not wrapper_path:
            raise RuntimeError("Wrapper script not generated yet")

        # Build script_path using venv python
        script_path = f"{self.venv_python} {wrapper_path}"

        # AUTO-MANAGE: Set working_directory to project root for sandboxing
        # Scripts execute from their project folder and access files via relative paths
        working_directory = f"projects/{project_id}"

        # Build config
        config: dict[str, Any] = {
            'name': script_name,
            'project_id': project_id,  # Always set project_id for instance tracking
            'script_path': script_path,
            'working_directory': working_directory,
            'description': description or f"Imported from {meta.get('source_url', 'ZIP upload')}",
            'group': group,
            'scheduling': {'enabled': True}
        }

        # NEW FORMAT: Use project_id and instance_config
        if included_parameters is not None:
            config['instance_config'] = {
                'included_parameters': included_parameters,
                'parameter_values': parameter_values or {},
                'selected_verb': selected_verb
            }
        # LEGACY FORMAT: Direct parameter definitions
        elif parameters:
            config['parameters'] = parameters

        # Write config file
        self.runners_dir.mkdir(parents=True, exist_ok=True)

        # Use script_name for filename to allow multiple scripts per project
        # Sanitize script name for filesystem
        safe_name = ''.join(c if c.isalnum() or c in ('-', '_', ' ') else '_' for c in script_name)
        config_filename = f"{safe_name}.json"
        config_path = self.runners_dir / config_filename

        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        # Update metadata (keep as single runner_config for backward compatibility)
        meta['runner_config'] = str(config_path)
        self._save_meta(project_path, meta)

        LOGGER.info(f"Generated config: {config_path}")
        return str(config_path)

    def get_wrapper_preview(
        self,
        project_id: str,
        entry_point: str,
        config_path: Optional[str] = None,
        config_cmd: Optional[str] = None
    ) -> str:
        """
        Get a preview of what the wrapper script would look like.

        Args:
            project_id: The project identifier
            entry_point: Entry point string
            config_path: Optional config path
            config_cmd: Optional config command

        Returns:
            Wrapper script content as string
        """
        project_path = self.projects_dir / project_id
        meta = self._load_meta(project_path)

        # Determine source path
        if (project_path / 'src').is_dir():
            src_path = project_path / 'src'
        else:
            src_path = project_path

        # Parse entry point
        if ':' in entry_point:
            module_path, obj_name = entry_point.rsplit(':', 1)
        else:
            module_path = entry_point
            obj_name = 'main'

        import_statement = f"from {module_path} import {obj_name}"
        run_statement = f"{obj_name}()"

        config_injection = ''
        if config_path and config_cmd:
            config_injection = f'''# Inject --config if running '{config_cmd}' command and not already specified
if len(sys.argv) >= 2 and sys.argv[1] == '{config_cmd}' and '--config' not in sys.argv:
    sys.argv.insert(2, '--config')
    sys.argv.insert(3, '{config_path}')
'''

        return WRAPPER_TEMPLATE.format(
            project_name=meta.get('name', project_id),
            dependencies=', '.join(meta.get('dependencies', [])),
            src_path=str(src_path),
            project_root=str(project_path),
            config_injection=config_injection,
            import_statement=import_statement,
            run_statement=run_statement
        )
