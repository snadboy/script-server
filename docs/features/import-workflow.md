# Import-Only Architecture & Project Manager

## Overview

Complete redesign to enforce import-only workflow with auto-managed paths and sandboxed execution. Projects are imported via Git/ZIP/Local, with automatic dependency detection, entry point selection, and wrapper script generation.

## Import-Only Architecture (2026-01-31)

**Status:** ✅ Complete - Committed to master

### Goals Achieved

- ✅ Import-only workflow (Git/ZIP/Local)
- ✅ Script path and working directory auto-managed by server
- ✅ Sandboxed execution (scripts confined to their project folders)
- ✅ Hidden complexity from users (no path fields in UI)
- ✅ Removed advanced "Include Config" field

### Changes

#### 1. Backend: Auto-manage Working Directory

**File:** `src/project_manager/project_service.py`

- `generate_runner_config()` now auto-sets `working_directory = "projects/{project_id}"`
- Scripts execute from their project root, access files via relative paths

#### 2. Backend: Sandboxing Validation

**File:** `src/execution/executor.py`

- Enhanced `_normalize_working_dir()` with security validation
- Enforces that `working_directory` must be within `projects/` folder
- Prevents path traversal attacks (resolves `..`, validates against projects_dir)
- Raises `ValueError` if working directory escapes project boundaries
- Tested: blocks `projects/my-project/../../etc` and `/app/projects/../src`

**Security benefits:**
- Scripts cannot escape their project folder via `../` traversal
- Scripts cannot access other projects or server source code
- Path resolution handles symlinks correctly (follows then validates)
- Absolute paths outside projects/ are rejected

#### 3. Frontend: Remove Manual Script Creation

**File:** `web-src/src/admin/components/scripts-config/create-script/CreateScriptModal.vue`

- Removed Source tab (no more import vs manual selection)
- Import-only workflow: Import → Configure → Details → Parameters → Advanced
- Removed `creationMode` state and logic
- Removed `initialMode` prop
- Always uses import path (calls backend wrapper generation API)

#### 4. Frontend: Simplify Script Manager

**File:** `web-src/src/main-app/components/ProjectsModal.vue`

- Removed "Create" tab
- Now only has: Projects, Import, Configure tabs
- Removed CreateScriptModal integration for manual mode
- Removed `openManualScriptCreation` and related methods

#### 5. Frontend: Hide Path Fields Entirely

**Files:** `EditScriptModal.vue`, `DetailsTab.vue`

**Fields removed:**
- Script path field (completely gone, not just hidden)
- Working directory field (auto-managed by server)
- Include config field (advanced feature, doesn't fit import-only)

**Details tab now only shows:**
- Name, Group, Description, Output Format, Enable Pseudo-Terminal

### Commits

- `777502a` - feat: Implement import-only architecture with auto-managed paths and sandboxing
- `192f19e` - fix: Hide script path and working directory fields from Edit Script dialog
- `696a26d` - refactor: Remove Include Config field from script dialogs

### Files Modified

- `src/project_manager/project_service.py` (auto-set working_directory)
- `src/execution/executor.py` (sandboxing validation)
- `web-src/src/admin/components/scripts-config/create-script/CreateScriptModal.vue`
- `web-src/src/admin/components/scripts-config/create-script/DetailsTab.vue`
- `web-src/src/main-app/components/scripts/EditScriptModal.vue`
- `web-src/src/main-app/components/ProjectsModal.vue`
- `docs/import-only-architecture.md`

---

## Project Manager & Entry Point Detection (2026-01-18)

**Status:** ✅ Complete - Merged to master

### Features

- Import Python projects via Git/ZIP/Local Path
- Auto-detect dependencies from requirements.txt
- Auto-detect entry points (main.py, __main__.py, CLI scripts)
- Generate wrapper scripts automatically
- Clean entry point UI with toggle for custom input
- Project deletion removes all associated instances

### Entry Point Detection

The system automatically detects entry points in this order:

1. **CLI scripts** from `pyproject.toml` `[project.scripts]`
2. **Standard entry points:** `main.py`, `__main__.py`, `cli.py`, `app.py`, `run.py`
3. **Package __main__.py** (for packages with `python -m package` support)

### Entry Point UI

**ConfigurePanel.vue:**
- Dropdown showing auto-detected entry points
- Each option shows type (CLI Script, Standard, Package)
- "Custom entry point" toggle reveals manual input field
- Clean UX - custom input only shown when needed

### Project Deletion Bug Fix (2026-02-02)

**Issue:** Deleting a project left orphaned instance configs

**Fix:**
- Modified `delete_project()` to scan all `*.json` files in `conf/runners/`
- Deletes all configs with matching `project_id`
- Deletes associated wrapper scripts
- Logs number of instances removed

**Verification:**
- ✅ Created test project with 3 instances (A, B, C)
- ✅ Deleted project successfully removed all 3 instances
- ✅ No orphaned files remain

---

## Unified Create Script Workflow (2026-01-18)

**Status:** ✅ Complete - Merged to master

### Features

Single modal combining Project Manager and Add Script functionality:

**CreateScriptModal.vue** - Orchestrator component with adaptive tabs:
- **Source tab** - Select import vs manual mode
- **Import tab** - Git/ZIP/Local import (only shown in import mode)
- **Configure tab** - Dependencies & entry point (only shown in import mode)
- **Details tab** - Name, group, description, output format
- **Parameters tab** - Parameter configuration
- **Advanced tab** - Access control, scheduling, verbs

### Reusable Components

| Component | Purpose |
|-----------|---------|
| SourceSelector.vue | Import vs manual selection |
| ImportPanel.vue | Git/ZIP/Local import forms |
| ConfigurePanel.vue | Dependency & entry point configuration |
| DetailsTab.vue | Script details form |
| AdvancedTab.vue | Access/scheduling/verbs combined |

### Integration

**ProjectsModal.vue** - Renamed to "Script Manager":
- Projects tab - View and delete imported projects
- Import tab - Import Python projects
- Configure tab - Entry point configuration

**MainAppSidebar.vue:**
- Single "Script Manager" button (description icon)
- Opens unified modal instead of separate dialogs

---

## Venv Package Management (2026-01-18)

**Status:** ✅ Complete

### Features

- Admin UI for managing Python packages in common venv
- Auto-creates venv if missing
- Install/uninstall packages via pip
- Real-time package list updates
- Error handling for failed installations

### Backend

**VenvService** (`src/venv_manager/venv_service.py`):
- `ensure_venv()` - Creates venv if missing
- `list_packages()` - Lists installed packages with versions
- `install_package()` - Installs package via pip
- `uninstall_package()` - Uninstalls package via pip
- Auto-detects project dependencies from imports

### Frontend

**PackagesModal.vue:**
- Shows installed packages with versions
- Add package button with package name input
- Remove button for each package
- Real-time updates after install/uninstall

### API Endpoints

- `GET /admin/venv/packages` - List installed packages
- `POST /admin/venv/packages` - Install package
- `DELETE /admin/venv/packages/{name}` - Uninstall package

---

## Files Created

**Import-Only Architecture:**
- `docs/import-only-architecture.md`

**Project Manager:**
- `src/project_manager/__init__.py`
- `src/project_manager/project_service.py`
- `web-src/src/admin/components/scripts-config/create-script/CreateScriptModal.vue`
- `web-src/src/admin/components/scripts-config/create-script/SourceSelector.vue`
- `web-src/src/admin/components/scripts-config/create-script/ImportPanel.vue`
- `web-src/src/admin/components/scripts-config/create-script/ConfigurePanel.vue`
- `web-src/src/admin/components/scripts-config/create-script/DetailsTab.vue`
- `web-src/src/admin/components/scripts-config/create-script/AdvancedTab.vue`
- `web-src/src/main-app/components/ProjectsModal.vue`

**Venv Management:**
- `src/venv_manager/__init__.py`
- `src/venv_manager/venv_service.py`
- `web-src/src/main-app/components/PackagesModal.vue`

---

## Testing

- ✅ Sandboxing tests passing (path traversal blocked)
- ✅ Frontend builds successfully
- ✅ Server validates scripts correctly
- ✅ Entry point detection working
- ✅ Project deletion removes all instances
- ✅ Venv creation and package management working
- ✅ UI verified: path fields removed from dialogs

## Benefits

- **Security:** Scripts cannot escape their sandbox
- **Simplicity:** Users don't manage paths manually
- **Portability:** No hardcoded paths in configs
- **Maintainability:** Auto-managed paths reduce errors
- **Flexibility:** Import from Git, ZIP, or local filesystem
- **Dependency Management:** Auto-detect and install requirements
