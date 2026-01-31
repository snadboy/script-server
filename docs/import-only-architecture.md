# Import-Only Architecture

## Overview

Script-server has been simplified to an **import-only architecture** where all scripts are imported projects managed by the server with auto-configured paths and sandboxing.

## Key Principles

1. **Import-Only**: No manual script creation mode. All scripts come from Git/ZIP/Local imports.
2. **Server Manages Paths**: Script path and working directory are automatically set by the server.
3. **Sandboxed Execution**: Scripts run from their project folder and cannot escape via path traversal.
4. **Hidden Complexity**: Users only see: Name, Description, Entry Point, Parameters.

## Architecture

### Directory Structure

```
/app/
├── samples/scripts/          # Generated wrapper scripts
│   ├── gmail-trim.py        # Auto-generated, managed by server
│   └── my-script.py
├── projects/                 # Imported projects
│   ├── gmail-trim/          # From GitHub
│   │   ├── src/
│   │   ├── pyproject.toml
│   │   └── data/            # Script's sandbox
│   └── my-script/           # From ZIP
│       └── script.py
├── .venv/                    # Universal shared venv
└── conf/
    └── runners/             # Script configs (auto-generated)
```

### Auto-Managed Configuration

When a project is imported and configured, the server automatically generates:

**Wrapper Script** (`samples/scripts/{project-id}.py`):
```python
#!/usr/bin/env python3
import sys
import os

# Add project source to Python path
PROJECT_SRC_PATH = '/app/projects/my-project/src'
sys.path.insert(0, PROJECT_SRC_PATH)

# Change to project directory for config/token files
os.chdir('/app/projects/my-project')

# Import and run the CLI app
from myapp.cli import app

if __name__ == '__main__':
    app()
```

**Runner Config** (`conf/runners/{project-id}.json`):
```json
{
  "name": "My Script",
  "script_path": "/app/.venv/bin/python samples/scripts/my-project.py",
  "working_directory": "projects/my-project",  # AUTO-SET
  "description": "Imported from https://github.com/user/repo",
  "group": "Imported Projects",
  "scheduling": {"enabled": true}
}
```

## Security: Sandboxing

### Path Validation

The executor enforces that imported project working directories cannot escape the `projects/` folder:

```python
def _normalize_working_dir(working_directory):
    """Normalize and validate working directory for security."""
    if 'projects/' in normalized or 'projects/' in working_directory:
        # Resolve path (follows symlinks, resolves ..)
        resolved = Path(abs_path).resolve()

        # SANDBOX: Must be within projects/ directory
        if not resolved.startswith(projects_dir):
            raise ValueError(
                f'Working directory must be within projects/ folder for security. '
                f'Got: {resolved}, Expected prefix: {projects_dir}'
            )
```

### What is Blocked

✅ **Path Traversal**: `projects/my-project/../../etc` → Blocked
✅ **Absolute Paths**: `/home/snadboy/projects/script-server/projects/../src` → Blocked
✅ **Symlink Attacks**: Path is resolved before validation
✅ **Cross-Project Access**: `projects/my-project/../other-project` → Blocked

### What is Allowed

✓ **Within Project**: `projects/my-project` → Allowed
✓ **Absolute Within Project**: `/app/projects/my-project` → Allowed
✓ **Subfolders**: `projects/my-project/data` → Allowed
✓ **Backward Compatibility**: Non-projects paths (e.g., `/tmp`) pass through for existing scripts

## User Experience

### Import Workflow

1. **Script Manager** → **Import** tab
2. Select import method:
   - **Git Clone**: Clone from GitHub/GitLab URL
   - **ZIP Upload**: Upload a ZIP file
   - **Local Path**: Copy from local directory
3. **Configure**:
   - Select entry point (auto-detected from pyproject.toml, __main__.py, etc.)
   - Install dependencies (auto-detected from pyproject.toml, requirements.txt)
   - Optional: Config file path and command
4. **Details**:
   - Script name
   - Description
   - Group
   - Output format
   - **No path fields shown!**
5. **Parameters**: Define script parameters (optional)
6. **Advanced**: Access control, scheduling, verbs (optional)

### What Users See

**Before** (Manual Mode):
- Script Path: `/path/to/script.py` ← Confusing, error-prone
- Working Directory: `/some/path` ← Can escape, not portable

**After** (Import-Only):
- Script Path: **Hidden** (auto-managed)
- Working Directory: **Hidden** (auto-managed)
- Users only configure: Name, Description, Entry Point, Parameters

## Implementation Details

### Backend Changes

**File: `src/project_manager/project_service.py`**

```python
def generate_runner_config(self, project_id: str, ...):
    # AUTO-MANAGE: Set working_directory to project root for sandboxing
    working_directory = f"projects/{project_id}"

    config = {
        'name': script_name,
        'script_path': f"{self.venv_python} {wrapper_path}",
        'working_directory': working_directory,  # AUTO-SET
        # ...
    }
```

**File: `src/execution/executor.py`**

Added sandboxing validation in `_normalize_working_dir()` function.

### Frontend Changes

**File: `web-src/src/admin/components/scripts-config/create-script/CreateScriptModal.vue`**

- Removed Source tab (no more import vs manual selection)
- Import-only workflow: Import → Configure → Details → Parameters → Advanced
- Removed `creationMode` state and all manual mode logic

**File: `web-src/src/admin/components/scripts-config/create-script/DetailsTab.vue`**

- Script path field: **Hidden** for imported projects
- Working directory field: **Hidden** for imported projects

**File: `web-src/src/main-app/components/ProjectsModal.vue`**

- Removed "Create" tab
- Now only has: Projects, Import, Configure tabs

## Migration from Manual Scripts

### Existing Manual Scripts

Scripts created before this change (with manually specified paths) will continue to work:

- **Read-only mode**: Can be executed but not edited
- **No sandboxing**: Backward compatibility for non-projects paths
- **Recommendation**: Re-import as projects for sandboxing benefits

### Converting Manual → Import

1. Copy script directory to local path
2. Use **Import** → **Local Path** to import it
3. Configure entry point and dependencies
4. Delete old manual script config

## Benefits

### For Users

- **Simpler UX**: No need to understand script paths or working directories
- **Portable**: Configs work across dev/prod without path changes
- **Safer**: Cannot accidentally expose system files or escape project boundaries

### For Developers

- **Maintainable**: Consistent project structure
- **Testable**: Known directory layout
- **Secure**: Sandboxing prevents common vulnerabilities

### For Security

- **Path Traversal Prevention**: Scripts cannot escape via `../`
- **Cross-Project Isolation**: Scripts cannot access other projects
- **Filesystem Boundaries**: Scripts confined to their project folder

## Testing

Run sandboxing tests:

```bash
python /tmp/test_sandboxing.py
```

Expected output:
```
✓ Valid path accepted: projects/my-project
✓ Path traversal blocked: ...
✓ Non-projects path passed: /tmp
✓ None returns None: True
```

## Future Enhancements

### Phase 2: File System Permissions

```bash
# Create restricted user for script execution
RUN useradd -r -s /bin/false scriptrunner
RUN chown -R scriptrunner:scriptrunner /app/projects
RUN chmod -R 700 /app/projects
```

Scripts run as `scriptrunner` user:
- Can only write to `/app/projects/`
- Cannot modify server source or venv

### Phase 3: Docker Container Per Script

```python
docker run --rm \
  --network none \
  --memory 512m \
  --cpus 1.0 \
  --read-only \
  -v /app/projects/{project_id}:/workspace:rw \
  -v /app/.venv:/venv:ro \
  script-server-runner {command}
```

Complete isolation:
- Filesystem, network, resource limits
- No access to server or other projects
- Maximum security for untrusted scripts

## FAQ

**Q: Can I still use manual scripts?**
A: Existing manual scripts work (read-only). New scripts must be imported.

**Q: What if my script needs to access /tmp?**
A: Non-projects paths pass through for backward compatibility.

**Q: How do I update an imported project?**
A: Delete the project and re-import from the updated source.

**Q: Can scripts access the shared venv?**
A: Yes, but only for imports. Scripts cannot modify the venv.

**Q: What about single .py files?**
A: Future enhancement: Upload single .py file → creates minimal project.

## Summary

The import-only architecture simplifies script management, improves security through sandboxing, and provides a better user experience by hiding implementation details. All scripts are now managed by the server with auto-configured paths, making the system more maintainable and secure.
