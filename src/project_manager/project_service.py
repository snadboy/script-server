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

    def _ensure_projects_dir(self):
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

    def _save_meta(self, project_path: Path, meta: dict):
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

    def _validate_git_url(self, url: str) -> None:
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
        except Exception as e:
            raise ValueError(f'Invalid URL: {e}')

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

    def import_from_git(self, url: str, branch: str = None) -> dict:
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
            raise Exception(f"Git clone failed: {result.stderr}")

        # Detect dependencies and entry points
        dependencies = self.detect_dependencies(project_path)
        entry_points = self.detect_entry_points(project_path)

        # Create metadata
        meta = {
            'id': project_id,
            'name': repo_name.replace('-', ' ').replace('_', ' ').title(),
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

        # Create metadata
        meta = {
            'id': project_id,
            'name': base_name.replace('-', ' ').replace('_', ' ').title(),
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
            raise Exception(f"Path does not exist: {local_path}")
        if not source_path.is_dir():
            raise Exception(f"Path is not a directory: {local_path}")

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

        # Create metadata
        meta = {
            'id': project_id,
            'name': dir_name.replace('-', ' ').replace('_', ' ').title(),
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

        # Delete wrapper script if exists
        if meta.get('wrapper_script'):
            wrapper_path = Path(meta['wrapper_script'])
            if wrapper_path.exists():
                wrapper_path.unlink()
                LOGGER.info(f"Deleted wrapper: {wrapper_path}")

        # Delete runner config if exists
        if meta.get('runner_config'):
            config_path = Path(meta['runner_config'])
            if config_path.exists():
                config_path.unlink()
                LOGGER.info(f"Deleted config: {config_path}")

        # Delete project directory
        shutil.rmtree(project_path)
        LOGGER.info(f"Deleted project: {project_path}")

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

            except Exception as e:
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
            except Exception as e:
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

            except Exception as e:
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

            except Exception as e:
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
        config_path: str = None,
        config_cmd: str = None
    ) -> str:
        """
        Generate a wrapper script for the project.

        Args:
            project_id: The project identifier
            entry_point: Entry point string (e.g., "module.main:app")
            config_path: Optional path to config file
            config_cmd: Optional command that uses config (e.g., "run")

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
        wrapper_filename = f"{project_id}.py"
        wrapper_path = self.scripts_dir / wrapper_filename

        with open(wrapper_path, 'w') as f:
            f.write(wrapper_content)

        # Make executable
        wrapper_path.chmod(0o755)

        # Update metadata
        meta['wrapper_script'] = str(wrapper_path)
        self._save_meta(project_path, meta)

        LOGGER.info(f"Generated wrapper: {wrapper_path}")
        return str(wrapper_path)

    def generate_runner_config(
        self,
        project_id: str,
        script_name: str,
        description: str = None,
        group: str = 'Imported Projects',
        parameters: list[dict] = None
    ) -> str:
        """
        Generate a script-server runner configuration.

        Args:
            project_id: The project identifier
            script_name: Display name for the script
            description: Optional description
            group: Script group (default: 'Imported Projects')
            parameters: Optional list of parameter definitions

        Returns:
            Path to the generated config file
        """
        project_path = self.projects_dir / project_id
        meta = self._load_meta(project_path)

        wrapper_path = meta.get('wrapper_script')
        if not wrapper_path:
            raise Exception("Wrapper script not generated yet")

        # Build script_path using venv python
        script_path = f"{self.venv_python} {wrapper_path}"

        # Build config
        config = {
            'name': script_name,
            'script_path': script_path,
            'description': description or f"Imported from {meta.get('source_url', 'ZIP upload')}",
            'group': group,
            'scheduling': {'enabled': True}
        }

        if parameters:
            config['parameters'] = parameters

        # Write config file
        self.runners_dir.mkdir(parents=True, exist_ok=True)
        config_filename = f"{project_id}.json"
        config_path = self.runners_dir / config_filename

        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        # Update metadata
        meta['runner_config'] = str(config_path)
        self._save_meta(project_path, meta)

        LOGGER.info(f"Generated config: {config_path}")
        return str(config_path)

    def get_wrapper_preview(
        self,
        project_id: str,
        entry_point: str,
        config_path: str = None,
        config_cmd: str = None
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
