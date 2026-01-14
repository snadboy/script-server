# Wrapping External Python Projects for Script-Server

This guide explains how to integrate external Python projects with script-server using the common venv approach.

---

## Overview

Script-server can run any executable, but Python projects often have dependencies that need to be managed. The **common venv** approach:

1. Creates a single virtual environment at `{script-server}/venv`
2. Installs all required dependencies into this venv
3. Uses wrapper scripts that import from external project source directories
4. Runs scripts using the venv's Python interpreter

**Benefits:**
- Centralized dependency management via Package Manager UI
- No need to modify the original project
- Scripts can be scheduled and monitored through script-server
- Consistent execution environment

---

## Prerequisites

1. **Script-server** with the venv management feature (Package Manager)
2. **External Python project** with:
   - Source code accessible on the filesystem
   - Known dependencies (usually in `requirements.txt` or `pyproject.toml`)
   - A CLI entry point or importable module

---

## Step-by-Step Process

### 1. Identify Dependencies

Check the external project's dependency file:

```bash
# For pyproject.toml
cat /path/to/project/pyproject.toml | grep -A 20 "dependencies"

# For requirements.txt
cat /path/to/project/requirements.txt
```

**Example (gmail-cleanup project):**
```
google-api-python-client>=2.100.0
google-auth-oauthlib>=1.1.0
google-auth>=2.23.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
structlog>=23.2.0
typer[all]>=0.9.0
pyyaml>=6.0.1
```

### 2. Install Dependencies

Use the Package Manager UI (click the inventory icon in sidebar) or install directly:

```bash
cd /home/snadboy/projects/script-server
./venv/bin/pip install package1 package2 package3
```

**Tip:** If the common venv doesn't exist yet, installing the first package will auto-create it.

### 3. Create a Wrapper Script

Create a wrapper in `samples/scripts/` that:
- Adds the external project's source to `sys.path`
- Changes to the project directory (for config/token files)
- Imports and runs the CLI entry point

**Template:**
```python
#!/usr/bin/env python3
"""
Wrapper script for [PROJECT_NAME] - runs via script-server common venv.

Required packages: [list dependencies]
"""

import sys
import os

# Configuration
PROJECT_SRC_PATH = '/path/to/project/src'      # Where the Python source lives
PROJECT_ROOT = '/path/to/project'               # Working directory for configs
CONFIG_PATH = '/path/to/project/config.yaml'    # Optional: default config file

# Add project source to Python path
sys.path.insert(0, PROJECT_SRC_PATH)

# Change to project directory (for relative config/token paths)
os.chdir(PROJECT_ROOT)

# Optional: Auto-inject config path for specific commands
if len(sys.argv) >= 2 and sys.argv[1] == 'run' and '--config' not in sys.argv:
    sys.argv.insert(2, '--config')
    sys.argv.insert(3, CONFIG_PATH)

# Import and run the CLI app
from project_module.main import app  # Adjust import path as needed

if __name__ == '__main__':
    app()
```

**Real Example (gmail_cleanup.py):**
```python
#!/usr/bin/env python3
"""
Gmail Auto-Cleanup wrapper script for script-server.
"""

import sys
import os

GM_PROJECT_PATH = '/home/snadboy/projects/gm/src'
GM_CONFIG_PATH = '/home/snadboy/projects/gm/config/config.yaml'
sys.path.insert(0, GM_PROJECT_PATH)

os.chdir('/home/snadboy/projects/gm')

if len(sys.argv) >= 2 and sys.argv[1] == 'run' and '--config' not in sys.argv:
    sys.argv.insert(2, '--config')
    sys.argv.insert(3, GM_CONFIG_PATH)

from gmail_cleanup.main import app

if __name__ == '__main__':
    app()
```

### 4. Create Script-Server Config

Create a JSON config in `conf/runners/`:

**Template:**
```json
{
  "name": "Script Display Name",
  "script_path": "/absolute/path/to/script-server/venv/bin/python /absolute/path/to/script-server/samples/scripts/wrapper.py",
  "description": "What this script does",
  "group": "Category Name",
  "scheduling": {
    "enabled": true
  },
  "parameters": [
    {
      "name": "Parameter Name",
      "param": "--flag-name",
      "type": "list|text|int|no_value",
      "required": false,
      "default": "default_value",
      "description": "What this parameter does",
      "values": ["option1", "option2"]
    }
  ]
}
```

**Key Points:**
- Use **absolute paths** for `script_path` - relative paths may not resolve correctly
- The format is: `/path/to/venv/bin/python /path/to/wrapper.py`
- Parameters with `"no_value": true` are boolean flags (present or absent)
- Parameters without `"param"` are positional arguments

**Real Example (gmail_cleanup.json):**
```json
{
  "name": "Gmail Cleanup",
  "script_path": "/home/snadboy/projects/script-server/venv/bin/python /home/snadboy/projects/script-server/samples/scripts/gmail_cleanup.py",
  "description": "Auto-delete old Gmail emails while preserving those with KEEP labels or from contact groups",
  "group": "Maintenance",
  "scheduling": {
    "enabled": true
  },
  "parameters": [
    {
      "name": "Command",
      "param": "",
      "type": "list",
      "required": true,
      "default": "run",
      "description": "Action to perform",
      "values": ["run", "labels", "groups", "config"],
      "values_ui_mapping": {
        "run": "Run Cleanup",
        "labels": "List Gmail Labels",
        "groups": "List Contact Groups",
        "config": "Show Configuration"
      }
    },
    {
      "name": "Dry Run",
      "param": "--dry-run",
      "no_value": true,
      "default": true,
      "description": "Preview what would be deleted without actually deleting"
    },
    {
      "name": "Verbose",
      "param": "--verbose",
      "no_value": true,
      "default": false,
      "description": "Enable verbose logging output"
    }
  ]
}
```

### 5. Test the Wrapper

Before using through script-server, test directly:

```bash
# Test with venv python
./venv/bin/python ./samples/scripts/wrapper.py --help

# Test a specific command
./venv/bin/python ./samples/scripts/wrapper.py run --dry-run
```

### 6. Verify in Script-Server

1. The script should auto-appear in the UI (script-server watches `conf/runners/`)
2. If not, restart script-server
3. Run with safe options first (e.g., `--dry-run`)
4. Check execution output by clicking on the completed execution card

---

## Handling Authentication

Some projects require one-time authentication (OAuth, API keys, etc.).

### OAuth-based Projects (like Gmail)

1. **Run auth once manually** from the original project's venv:
   ```bash
   cd /path/to/project
   source .venv/bin/activate
   project-cli auth --credentials creds.json --token token.json
   ```

2. **Token files** are typically saved in the project directory
3. **Wrapper script** changes to project directory so tokens are found
4. **Token refresh** happens automatically during subsequent runs

### API Key-based Projects

1. Store keys in the project's config file
2. Or use environment variables in the script-server config:
   ```json
   {
     "parameters": [
       {
         "name": "API_KEY",
         "env_var": "PROJECT_API_KEY",
         "secure": true
       }
     ]
   }
   ```

---

## Parameter Types Reference

| Type | Description | Example |
|------|-------------|---------|
| `text` | Free-form text input | `--name "value"` |
| `int` | Integer input | `--count 5` |
| `list` | Dropdown selection | `--mode fast` |
| `multiselect` | Multiple selections | `--flags a --flags b` |
| `no_value` | Boolean flag (present/absent) | `--verbose` |
| `file_upload` | Upload a file | `--input file.txt` |
| `server_file` | Select file from server | `--config /path/file` |

---

## Troubleshooting

### Script exits immediately with no output

- **Cause:** Missing dependencies or import error
- **Fix:** Test wrapper directly: `./venv/bin/python ./samples/scripts/wrapper.py`

### "Module not found" errors

- **Cause:** `sys.path` not set correctly or dependencies not installed
- **Fix:**
  1. Verify the source path exists
  2. Check all dependencies are installed: `./venv/bin/pip list`

### Script uses wrong Python interpreter

- **Cause:** Relative path in `script_path` not resolving
- **Fix:** Use absolute paths for both Python and script

### Config file not found

- **Cause:** Working directory not set in wrapper
- **Fix:** Add `os.chdir('/path/to/project')` in wrapper

### Authentication errors

- **Cause:** Token file not found or expired
- **Fix:**
  1. Check wrapper changes to correct directory
  2. Re-run authentication manually if token expired

---

## File Locations Summary

| Item | Location |
|------|----------|
| Common venv | `{script-server}/venv/` |
| Wrapper scripts | `{script-server}/samples/scripts/` |
| Script configs | `{script-server}/conf/runners/` |
| External project source | `/path/to/project/src/` |
| External project config | `/path/to/project/config/` |

---

## Example: Complete Gmail Cleanup Integration

```
script-server/
├── venv/                           # Common venv with dependencies
├── samples/scripts/
│   └── gmail_cleanup.py            # Wrapper script
├── conf/runners/
│   └── gmail_cleanup.json          # Script config (gitignored)
└── ...

/home/user/projects/gm/             # External project (unchanged)
├── src/gmail_cleanup/              # Python source
├── config/config.yaml              # Project config
├── token.json                      # OAuth token
└── ...
```

**Dependencies installed:** google-api-python-client, google-auth-oauthlib, google-auth, pydantic, pydantic-settings, structlog, typer, pyyaml
