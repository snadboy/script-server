# Script Server Architecture

> **Fork:** snadboy/script-server (based on bugy/script-server)
> **Last Updated:** 2026-02-05

This document provides a comprehensive architectural overview of the Script Server fork, focusing on the project-level parameters, CLI verbs, and import-only workflow enhancements.

---

## Table of Contents

1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Architecture Components](#architecture-components)
4. [Key Subsystems](#key-subsystems)
5. [Data Flow](#data-flow)
6. [Directory Structure](#directory-structure)
7. [Technology Stack](#technology-stack)
8. [Feature Deep Dives](#feature-deep-dives)

---

## Overview

### What is Script Server?

Script Server is a web UI for executing and scheduling scripts (Python, Bash, etc.) with parameter inputs, authentication, and logging. This fork extends the original with:

- **Project-Level Parameters** - Define parameters once, create multiple instances with different values
- **CLI Verb/Subcommand Support** - Git-style commands (e.g., `script.py run`, `script.py auth`)
- **Import-Only Workflow** - Auto-managed sandboxed execution from Git/ZIP/Local sources
- **Unified Activity UI** - Single view for Running, Scheduled, and Completed executions
- **Enhanced Scheduling** - Auto-cleanup for one-time schedules, edit schedules
- **Package Management** - Admin UI for Python package installation

### Key Architectural Principles

1. **Import Over Edit** - Scripts are imported from external sources, not edited in-place
2. **Sandboxed Execution** - Each project runs in its own directory with controlled access
3. **Configuration as Code** - All settings stored in JSON with Git-friendly format
4. **Instance Model** - Projects define structure, instances provide values
5. **Clean Separation** - Backend (Python/Tornado) and Frontend (Vue.js) are decoupled

---

## Core Concepts

### Projects

A **project** is an imported Python application or script collection with:

- **Source** - Git repository, ZIP file, or local directory
- **Entry Points** - Callable functions or CLI commands (e.g., `main.py:app`, `script.py`)
- **Parameters** - Reusable parameter definitions (name, type, description, validation)
- **Verbs** - CLI subcommands with parameter associations (optional)
- **Dependencies** - Python packages required by the project

**Example Project Structure:**
```
projects/gmail-trim/
├── .project-meta.json       # Project metadata
├── src/
│   └── gmail_cleanup/
│       ├── main.py           # Entry point
│       └── ...
└── pyproject.toml
```

### Instances

An **instance** is a configured runnable script created from a project:

- **Based On** - A project with defined parameters/verbs
- **Values** - Specific parameter value overrides
- **Verb Selection** - Which subcommand to execute (if project has verbs)
- **Runner Config** - JSON file in `conf/runners/` with instance settings

**Example Instance Config:**
```json
{
  "name": "Gmail Trim A",
  "project_id": "gmail-trim",
  "script_path": "/path/to/venv/python /path/to/wrapper.py",
  "working_directory": "projects/gmail-trim",
  "instance_config": {
    "included_parameters": ["days", "dry_run", "verbose"],
    "parameter_values": { "days": 14 },
    "selected_verb": "run"
  }
}
```

### Parameters

**Parameters** define script inputs with:

- **Type** - text, int, list, file_upload, server_file, bool, bool_dual_flag
- **Validation** - min/max, required, allowed_values
- **Defaults** - Default values for optional parameters
- **CLI Mapping** - How parameter maps to command-line argument

**Parameter Types:**
- `text` - Single-line string input
- `int` - Integer with optional min/max
- `list` - Multi-select dropdown
- `file_upload` - Upload file from user's machine
- `server_file` - Select file from server filesystem
- `bool` - Single flag (e.g., `--verbose`)
- `bool_dual_flag` - Opposing flags (e.g., `--verbose` / `--quiet`)

### Verbs

**Verbs** are CLI subcommands with:

- **Name** - Command name (e.g., `run`, `auth`, `config`)
- **Label** - Display name in UI
- **Description** - What the command does
- **Parameters** - Which project parameters this verb accepts
- **Required Parameters** - Parameters that must have values

**Example Verb Configuration:**
```json
{
  "parameter_name": "command",
  "required": true,
  "default": "run",
  "param": "",
  "verb_position": "after_verb",
  "options": [
    {
      "name": "run",
      "label": "Run Cleanup",
      "description": "Execute email cleanup",
      "parameters": ["days", "dry_run", "verbose"],
      "required_parameters": []
    },
    {
      "name": "auth",
      "label": "Authenticate",
      "description": "Authorize API access",
      "parameters": ["verbose"],
      "required_parameters": []
    }
  ]
}
```

---

## Architecture Components

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Web Browser                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Index.html  │  │  Admin.html  │  │  Login.html  │ │
│  │   (Vue.js)   │  │   (Vue.js)   │  │   (Vue.js)   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP/WebSocket
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Tornado Web Server (Python)                │
│  ┌────────────────────────────────────────────────────┐│
│  │              Request Handlers                       ││
│  │  /scripts │ /execute │ /schedules │ /admin/*       ││
│  └────────────────────────────────────────────────────┘│
│  ┌────────────────────────────────────────────────────┐│
│  │              Core Services                          ││
│  │  • ConfigService    • ExecutionService             ││
│  │  • ProjectService   • ScheduleService              ││
│  │  │  ScriptValidator  • VenvService                 ││
│  └────────────────────────────────────────────────────┘│
│  ┌────────────────────────────────────────────────────┐│
│  │              Data Layer                             ││
│  │  • JSON Configs     • Execution Logs               ││
│  │  • Project Metadata • Schedule Persistence         ││
│  └────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                 Script Execution Layer                  │
│  ┌────────────────────────────────────────────────────┐│
│  │  Subprocess Executor                                ││
│  │  • Environment Setup (working_dir, env vars)       ││
│  │  │  Command Building (params → CLI args)           ││
│  │  • Stream Handling (stdout/stderr capture)         ││
│  │  • Exit Code Handling                              ││
│  └────────────────────────────────────────────────────┘│
│  ┌────────────────────────────────────────────────────┐│
│  │  Project Sandbox                                    ││
│  │  projects/{project-id}/                            ││
│  │  • Isolated working directory per project          ││
│  │  • Relative path access only                       ││
│  └────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

### Frontend (Vue.js SPA)

**Structure:**
- **Main App** (`index.html`) - Script execution, scheduling, activity view
- **Admin App** (`admin.html`) - Script configuration, project management
- **Login App** (`login.html`) - Authentication

**Key Components:**
- `MainAppSidebar.vue` - Script list, search, navigation
- `ActivityPage.vue` - Unified view of running/scheduled/completed executions
- `ExecuteModal.vue` - Script execution dialog with parameter inputs
- `ScheduleModal.vue` - Schedule configuration
- `ProjectsModalPlayground.vue` - Project manager (import/configure)
- `ProjectConfigModal.vue` - Parameter/verb configuration for projects

**State Management (Vuex):**
- `scripts` - Available scripts and selection state
- `executions` - Running/completed execution state
- `schedules` - Active schedules
- `adminScripts` - Admin-only script management state
- `auth` - Authentication state

### Backend (Python/Tornado)

**Entry Point:** `launcher.py`

**Core Modules:**

1. **Web Server** (`src/web/server.py`)
   - Request routing and handlers
   - WebSocket for real-time execution updates
   - Authentication/authorization middleware

2. **Config Service** (`src/config/config_service.py`)
   - Load/save/validate script configurations
   - Merge project metadata with instance configs
   - Config migration and versioning

3. **Project Service** (`src/project_manager/project_service.py`)
   - Import projects (Git/ZIP/Local)
   - Detect entry points and dependencies
   - Generate wrapper scripts and runner configs
   - Manage project metadata

4. **Execution Service** (`src/execution/executor.py`)
   - Build command from config + parameters
   - Launch subprocess in sandboxed environment
   - Stream output to WebSocket clients
   - Track execution state and history

5. **Schedule Service** (`src/scheduling/schedule_service.py`)
   - Persistent schedule storage (JSON)
   - APScheduler integration for cron/interval triggers
   - Auto-cleanup for completed one-time schedules
   - Schedule editing and deletion

6. **Script Validator** (`src/script_validator.py`)
   - Validate script configs on startup
   - Check for missing files, invalid syntax
   - Cache validation results
   - Provide warnings in UI

7. **Venv Service** (`src/venv_manager/venv_service.py`)
   - Manage shared Python virtual environment
   - Install/uninstall packages via pip
   - Detect package dependencies from projects
   - Package listing by script usage

---

## Key Subsystems

### Project Import Workflow

**Goal:** Allow users to import Python projects without manual config editing.

**Flow:**

1. **User Initiates Import**
   - Provides Git URL, ZIP file, or local path
   - Optionally specifies branch (Git only)

2. **Project Service Clones/Copies**
   - Git: `git clone` into `projects/{sanitized-name}/`
   - ZIP: Extract into `projects/{sanitized-name}/`
   - Local: Symlink or copy into `projects/{sanitized-name}/`

3. **Auto-Detection**
   - **Entry Points:** Scan for `main.py`, `__main__.py`, CLI commands (Typer/Click)
   - **Dependencies:** Parse `pyproject.toml`, `requirements.txt`, `setup.py`
   - **Parameters:** Detect CLI arguments (future: parse argparse/Typer decorators)

4. **Metadata Storage**
   - Create `.project-meta.json` with detected info
   - Store: project ID, source URL, entry points, dependencies

5. **Wrapper Generation**
   - Generate Python wrapper script in `samples/scripts/{project-id}_{script-name}.py`
   - Wrapper sets up environment, changes to project dir, calls entry point

6. **Instance Creation**
   - User creates instances via "Configure Project" dialog
   - Selects entry point, parameters, verb (if applicable)
   - Generates runner config in `conf/runners/{script-name}.json`

**Key Files:**
- `projects/{project-id}/.project-meta.json` - Project metadata
- `samples/scripts/{project-id}_{script-name}.py` - Wrapper script
- `conf/runners/{script-name}.json` - Instance configuration

### Parameter Resolution

**Goal:** Merge project-level parameters with instance-specific values.

**Resolution Order:**

1. **Project Parameter Definition** (from `.project-meta.json`)
   ```json
   {
     "name": "days",
     "type": "int",
     "default": 30,
     "min": 1,
     "max": 365
   }
   ```

2. **Instance Config** (from `conf/runners/{name}.json`)
   ```json
   {
     "instance_config": {
       "included_parameters": ["days", "dry_run"],
       "parameter_values": { "days": 14 }
     }
   }
   ```

3. **User Input** (from execution dialog)
   - User provides values via UI form
   - Overrides instance defaults

4. **Effective Values**
   - `days`: 14 (from instance) or user input
   - `dry_run`: default from project (if user doesn't change)

**Implementation:**
- `script_config.py:_load_from_project()` - Merges project params with instance config
- `parameter_config.py` - Individual parameter logic and validation
- `verb_config.py` - Verb-specific parameter filtering

### Command Building

**Goal:** Convert parameters + values into CLI arguments.

**Process:**

1. **Base Command**
   - From `script_path` in config: `/path/to/venv/python /path/to/wrapper.py`

2. **Verb Insertion** (if project has verbs)
   - Append selected verb name: `python wrapper.py run`

3. **Parameter Mapping**
   - For each parameter with a value:
     - Boolean: Add flag if true (e.g., `--dry-run`)
     - Dual-flag: Add positive or negative flag (e.g., `--verbose` or `--quiet`)
     - Other: Add `--param-name value`

4. **Final Command**
   - Example: `/path/to/venv/python /path/to/wrapper.py run --days 14 --dry-run --verbose`

**Key Code:**
- `executor.py:_build_command_args()` - Main command builder
- `parameter_config.py` - Parameter-specific CLI formatting

### Execution Flow

**Goal:** Execute scripts with real-time output streaming.

**Steps:**

1. **Validate Inputs**
   - Check required parameters have values
   - Validate types (int ranges, allowed values, etc.)

2. **Build Command**
   - Merge parameters into CLI command (see Command Building)

3. **Setup Environment**
   - Set `working_directory` (e.g., `projects/gmail-trim`)
   - Set environment variables (if configured)

4. **Launch Subprocess**
   - `subprocess.Popen()` with `stdout=PIPE`, `stderr=PIPE`
   - Non-blocking I/O for streaming

5. **Stream Output**
   - Read stdout/stderr line-by-line
   - Send to WebSocket clients in real-time
   - Store in execution log file

6. **Track State**
   - Update execution state: `running` → `finished` or `error`
   - Store exit code, duration, output
   - Notify UI via WebSocket

7. **Cleanup**
   - Close subprocess handles
   - Finalize logs
   - Update execution history

**Key Code:**
- `executor.py:start_script()` - Main execution orchestration
- `execution_service.py` - Execution state management
- `server.py:ScriptStreamSocket` - WebSocket handler for streaming

### Schedule Management

**Goal:** Persistent scheduling with cron/interval triggers.

**Architecture:**

1. **Schedule Storage**
   - JSON files in `conf/schedules/{name}_{user}_{id}.json`
   - Contains: script name, schedule config, parameter values, enabled state

2. **APScheduler Integration**
   - Python APScheduler library for trigger management
   - Supports: cron expressions, intervals, one-time (date triggers)

3. **Schedule Lifecycle**
   - **Create:** User configures via ScheduleModal → saved to JSON → added to APScheduler
   - **Execute:** APScheduler triggers → calls ExecutionService → runs script
   - **Complete:** One-time schedules auto-delete after success
   - **Edit/Delete:** Modify JSON → reload APScheduler jobs

4. **Cleanup Task**
   - Background task runs every minute
   - Deletes completed one-time schedules older than retention period (default 60 min)

**Key Code:**
- `schedule_service.py` - Schedule CRUD and APScheduler integration
- `conf/schedules/` - Schedule persistence directory

---

## Data Flow

### Script Execution Request

```
User clicks "Run" → Frontend
                     ↓
                  ExecuteModal collects parameters
                     ↓
                  POST /executions/start
                     ↓
              ExecutionService.start_script()
                     ↓
              Build command from config + params
                     ↓
              Launch subprocess in project dir
                     ↓
              Stream stdout/stderr → WebSocket
                     ↓
              Update execution state
                     ↓
              Frontend displays live output
```

### Project Import Request

```
User selects import type → Frontend
                            ↓
                     ProjectsModalPlayground
                            ↓
                     POST /admin/projects/import
                            ↓
                  ProjectService.import_from_{git|zip|local}()
                            ↓
                  Clone/extract to projects/{id}/
                            ↓
                  Detect entry points + dependencies
                            ↓
                  Save .project-meta.json
                            ↓
                  Return project info → Frontend
                            ↓
                  User configures instances
                            ↓
                  POST /admin/projects/{id}/wrapper
                            ↓
                  Generate wrapper + runner config
                            ↓
                  Script appears in sidebar
```

### Schedule Execution

```
APScheduler timer fires
         ↓
ScheduleService.execute_schedule()
         ↓
Load schedule JSON
         ↓
ExecutionService.start_script(schedule.params)
         ↓
Script executes (same as manual execution)
         ↓
If one-time schedule:
  - Mark as completed
  - Auto-delete after retention period
```

---

## Directory Structure

```
script-server/
├── src/                              # Backend Python code
│   ├── web/
│   │   └── server.py                 # Tornado request handlers
│   ├── config/
│   │   └── config_service.py         # Config loading/saving
│   ├── project_manager/
│   │   └── project_service.py        # Project import and management
│   ├── execution/
│   │   └── executor.py               # Script execution
│   ├── scheduling/
│   │   └── schedule_service.py       # Schedule management
│   ├── venv_manager/
│   │   └── venv_service.py           # Python package management
│   ├── model/
│   │   ├── script_config.py          # Script config model
│   │   ├── parameter_config.py       # Parameter definitions
│   │   └── verb_config.py            # Verb/subcommand config
│   └── ...
│
├── web-src/                          # Frontend Vue.js source
│   ├── src/
│   │   ├── main-app/                 # Main application (index.html)
│   │   │   ├── components/
│   │   │   │   ├── activity/         # Activity page components
│   │   │   │   ├── scripts/          # Script list components
│   │   │   │   ├── schedule/         # Schedule components
│   │   │   │   ├── MainAppSidebar.vue
│   │   │   │   ├── ProjectsModalPlayground.vue
│   │   │   │   └── ...
│   │   │   └── store/                # Vuex state management
│   │   ├── admin/                    # Admin application
│   │   │   └── components/
│   │   │       ├── projects/         # Project management
│   │   │       └── scripts-config/   # Script configuration
│   │   └── common/                   # Shared components
│   └── package.json
│
├── web/                              # Built frontend (generated)
│   ├── index.html
│   ├── admin.html
│   ├── login.html
│   └── js/
│
├── conf/                             # Configuration storage
│   ├── runners/                      # Script instance configs
│   │   ├── {script-name}.json
│   │   └── ...
│   ├── schedules/                    # Schedule persistence
│   │   ├── {name}_{user}_{id}.json
│   │   └── ...
│   └── config.json                   # Server settings
│
├── projects/                         # Imported projects
│   ├── {project-id}/
│   │   ├── .project-meta.json        # Project metadata
│   │   ├── src/                      # Project source code
│   │   └── ...
│   └── ...
│
├── samples/                          # Generated wrapper scripts
│   └── scripts/
│       ├── {project-id}_{script}.py  # Wrapper scripts
│       └── ...
│
├── logs/                             # Execution logs
│   └── processes/
│       ├── {execution-id}.log
│       └── ...
│
├── docs/                             # Documentation
│   ├── ARCHITECTURE.md               # This file
│   ├── features/                     # Feature-specific docs
│   └── ...
│
└── .venv/                            # Shared Python virtual environment
    └── ...
```

---

## Technology Stack

### Backend

- **Python 3.8+** - Primary language
- **Tornado 6.x** - Async web framework and WebSocket server
- **APScheduler** - Job scheduling library
- **pip** - Package management

### Frontend

- **Vue.js 2.x** - UI framework
- **Vuex** - State management
- **Vue Router** - Client-side routing
- **Materialize CSS** - UI component library (customized)
- **Webpack** - Build tooling

### Data Storage

- **JSON Files** - Script configs, schedules, project metadata
- **File System** - Execution logs, project sources

### Build & Deploy

- **npm** - Frontend dependency management
- **webpack** - Frontend bundling
- **GitHub Actions** - CI/CD (auto-build Docker images)
- **Docker** - Containerized deployment

---

## Feature Deep Dives

### Project-Level Parameters

**Problem:** Users had to define parameters separately for each script, even when running the same code with different values.

**Solution:** Define parameters once at the project level, create multiple instances with different value overrides.

**Key Files:**
- `docs/features/project-parameters.md` - Full implementation details
- `src/model/script_config.py:_load_from_project()` - Parameter loading
- `web-src/src/admin/components/projects/ProjectConfigModal.vue` - UI

**Benefits:**
- DRY (Don't Repeat Yourself) - Define parameters once
- Consistency - All instances use same parameter definitions
- Easy updates - Change project parameters, all instances inherit

### CLI Verb Support

**Problem:** Many CLI tools have subcommands (e.g., `git commit`, `docker run`), but Script Server treated everything as flags.

**Solution:** Add verb configuration to projects, allow verb selection per instance.

**Key Files:**
- `docs/features/verbs.md` - Implementation guide
- `src/model/verb_config.py` - Verb configuration model
- `src/execution/executor.py` - Verb injection into command

**Example:**
```bash
# Without verbs: python script.py --action=auth --verbose
# With verbs:    python script.py auth --verbose
```

### Import-Only Architecture

**Problem:** Users had to manually create configs, specify paths, and manage script locations.

**Solution:** Import projects from Git/ZIP/Local, auto-detect structure, generate configs automatically.

**Key Files:**
- `docs/import-only-architecture.md` - Original design doc
- `docs/features/import-workflow.md` - Complete guide
- `src/project_manager/project_service.py` - Import implementation

**Workflow:**
1. Import project (one-time)
2. Configure parameters/verbs (one-time)
3. Create instances (as needed)
4. Run instances (daily use)

### Unified Activity Page

**Problem:** Users had to switch between "Running", "Scheduled", and "Completed" tabs to see execution status.

**Solution:** Single-page view with all execution states, auto-refresh, inline actions.

**Key Files:**
- `docs/features/ui-ux.md` - UI improvements doc
- `web-src/src/main-app/components/activity/ActivityPage.vue` - Implementation

**Features:**
- Live updates (WebSocket + polling)
- Inline stop/kill/schedule/edit actions
- Date/time grouping
- State-based button visibility

---

## Security Considerations

### Sandboxed Execution

- Scripts execute in their project directory (`projects/{project-id}/`)
- No access to parent directories or other projects
- Working directory enforcement prevents path traversal

### Authentication & Authorization

- User authentication via htpasswd or LDAP
- Admin-only operations (import, config, package management)
- Script-level access control (allowed_users, admin_users)

### Input Validation

- Parameter type validation (int ranges, allowed values)
- File upload restrictions (size, allowed paths)
- Script config validation on load

### Process Isolation

- Each execution runs in separate subprocess
- Resource limits (optional: memory, CPU)
- Timeout enforcement

---

## Extending the Architecture

### Adding a New Parameter Type

1. Define type in `parameter_config.py:ParameterModel`
2. Add UI component in `web-src/src/common/components/parameters/`
3. Add CLI mapping logic in `executor.py:_build_command_args()`
4. Update parameter editor in admin UI

### Adding a New Import Source

1. Add handler in `project_service.py:import_from_{source}()`
2. Add UI form in `ProjectsModalPlayground.vue`
3. Add API endpoint in `server.py:ImportProjectHandler`
4. Implement auto-detection for source-specific structure

### Adding Real-Time Features

1. Add WebSocket handler in `server.py`
2. Implement message protocol (JSON over WebSocket)
3. Add Vuex action to connect and listen
4. Update relevant components to display real-time data

---

## Performance Considerations

### Config Loading

- Configs cached in memory after first load
- Validation results cached (ScriptValidator)
- Config reloading only on change detection

### Execution Streaming

- Non-blocking I/O for subprocess output
- Chunked WebSocket messages (not line-by-line)
- Client-side buffering in UI

### Frontend Build

- Code splitting (admin vs main app)
- Lazy-loaded routes
- Minified production builds

---

## Testing Strategy

### Backend Tests

- Unit tests for individual services
- Integration tests for API endpoints
- Execution tests with sample scripts

### Frontend Tests

- Component unit tests (Vue Test Utils)
- E2E tests for critical workflows
- Visual regression tests

### Manual Testing

- Test project import from various sources
- Test execution with different parameter types
- Test schedule creation and triggering
- Test permission boundaries

---

## Deployment

### Local Development

```bash
# Backend
python launcher.py

# Frontend (dev server)
cd web-src && npm run serve
```

### Production (Docker)

```bash
# Build
docker build -t script-server:latest .

# Run
docker run -p 5000:5000 -v ./conf:/app/conf -v ./logs:/app/logs script-server:latest
```

### GitHub Actions

- Auto-builds Docker image on push to master
- Pushes to `ghcr.io/snadboy/script-server:latest`
- No manual deployment needed

---

## References

- **Feature Documentation:** `docs/features/`
- **CLAUDE.md:** Session notes and recent changes
- **Upstream Docs:** https://github.com/bugy/script-server/wiki

---

## Glossary

- **Project** - An imported Python application with parameters and optional verbs
- **Instance** - A configured runnable script based on a project
- **Verb** - A CLI subcommand (e.g., `run`, `auth`)
- **Parameter** - A configurable input to a script (e.g., `--days 30`)
- **Runner Config** - JSON file defining an instance's configuration
- **Wrapper Script** - Auto-generated Python script that calls project entry point
- **Execution** - A single run of a script with specific parameter values
- **Schedule** - A recurring or one-time trigger for script execution

---

**Last Updated:** 2026-02-05
**Maintainer:** snadboy
**Questions?** Open an issue on GitHub
