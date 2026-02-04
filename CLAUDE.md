# Script Server Fork - Project Context

> **Important:** Keep this file updated throughout each session. When completing significant work (features, bug fixes, refactors), update the relevant sections immediately so context is preserved for future sessions.

---

## Repository

- **Fork:** https://github.com/snadboy/script-server
- **Upstream:** https://github.com/bugy/script-server
- **Local Path:** `/home/snadboy/projects/script-server`

---

## Current State

**Branch:** `master`
**Latest Commit:** `4cf99d0` - Updated session notes (4 commits pushed)
**Last Updated:** 2026-02-03 22:15
**Docker Image:** `ghcr.io/snadboy/script-server:latest` (building via GitHub Actions)
**Local Server:** ✅ Running on http://localhost:5000 (PID 2703032)

### Recent Session (2026-02-03): Project-Level Parameters Complete - All Phases + Documentation

**Completed Phases 1-5: Full implementation of project-level parameters & verbs architecture, comprehensive documentation, and UX redesign with master-detail pattern.**

**Status:** ✅ **ALL PHASES COMMITTED & PUSHED** - Ready for Phase 6 Manual UI Testing

**What was completed in this session:**

1. **Test Project Structure Created**
   - Created `projects/gmail-trim-3/` directory with demo script
   - Added comprehensive `.project-meta.json` with 4 parameters and 5 verbs
   - Created `gmail_trim_demo.py` CLI script for testing

2. **Instance Configurations Created**
   - `Gmail Trim A.json` - 14-day retention (run verb)
   - `Gmail Trim B.json` - 60-day retention (run verb)
   - `Gmail List Labels.json` - labels verb with verbose only

3. **Backend Tests Passing**
   - All 4 automated tests verify correct loading
   - Parameters filtered by included_parameters
   - Value overrides working (days: 30→14, 30→60)
   - Verb configuration loaded from project

4. **UX Redesign: Master-Detail Pattern**
   - **Problem solved:** ProjectConfigModal footer buttons disappeared off-screen when adding parameters/verbs
   - **Solution:** Implemented master-detail pattern with fixed-height scrollable tables
   - **ProjectParametersEditor.vue** (complete rewrite, 1076→1142 lines):
     - Fixed-height table (300px) showing parameter summary
     - Edit panel below (400px max) with full form for selected parameter
     - Auto-selects newly added parameters
   - **VerbConfigEditor.vue** (complete rewrite, 565→1163 lines):
     - Fixed-height table (250px) showing verb summary
     - Edit panel below (400px max) with parameter selection checkboxes
     - Shared parameters shown with green styling
   - **Result:** Modal never grows, footer always visible, can display 50+ items

5. **Frontend Build Verified**
   - Build completed successfully with `NODE_OPTIONS=--openssl-legacy-provider npm run build`
   - All Vue components compile without errors
   - Output: 2.9 MB assets (909 KB gzipped)

**Implementation Status:**
- ✅ Phase 1: Backend Foundation (ProjectService CRUD, API endpoints) - COMMITTED
- ✅ Phase 2: Config Loading (InstanceConfig, _load_from_project) - COMMITTED
- ✅ Phase 3: Frontend Project Config UI (ProjectConfigModal, ProjectParametersEditor) - COMMITTED
- ✅ Phase 4: Frontend Instance Config UI (ConfigurePanel with instance config) - COMMITTED
- ✅ Phase 5: Test setup, UX redesign, documentation (ALL TESTS PASSING) - COMMITTED
- ⏳ Phase 6: Manual UI testing (server running and ready)

**Files created:**
- `projects/gmail-trim-3/.project-meta.json` - Project metadata with params/verbs
- `projects/gmail-trim-3/gmail_trim_demo.py` - Demo CLI script
- `conf/runners/Gmail Trim A.json` - Instance config (14 days)
- `conf/runners/Gmail Trim B.json` - Instance config (60 days)
- `conf/runners/Gmail List Labels.json` - Instance config (labels verb)
- `samples/scripts/gmail-trim-3_Gmail_List_Labels.py` - Wrapper script
- `docs/PHASE_5_COMPLETE.md` - Comprehensive phase 5 documentation

**Files modified (UX redesign):**
- `web-src/src/admin/components/projects/ProjectParametersEditor.vue` - Complete rewrite with master-detail pattern (1076→1142 lines)
- `web-src/src/admin/components/scripts-config/VerbConfigEditor.vue` - Complete rewrite with master-detail pattern (565→1163 lines)

**Testing:**
- ✅ Frontend builds successfully
- ✅ Backend tests: 4/4 passing (100%)
- ✅ Parameter loading verified
- ✅ Value overrides verified
- ✅ Verb filtering verified
- ✅ Local server restarted with latest build

**Commits Created (4 total):**
1. `419c899` - feat: Implement Phases 1-4 - Project-Level Parameters & Verbs
2. `5c31122` - docs: Add comprehensive documentation for Phases 1-4
3. `acb4bf2` - feat: Complete Phase 5 - Project-Level Parameters with Master-Detail UX
4. `4cf99d0` - docs: Update CLAUDE.md with latest commit info

**Deployment:**
- ✅ All commits pushed to GitHub (origin/master)
- ✅ GitHub Actions Docker build triggered automatically
- ✅ Image will be available at: `ghcr.io/snadboy/script-server:latest`
- ✅ Local server running with latest build: http://localhost:5000

**Next steps:**
- Phase 6: Manual UI testing (server ready)
  1. Open http://localhost:5000
  2. Click "Script Manager" → Projects tab
  3. Find "Gmail Trim" (gmail-trim-3) → Configure tab
  4. Click "Configure Parameters & Verbs" button
  5. **Verify master-detail UX:**
     - Parameters tab: fixed-height table (300px) + edit panel
     - Verbs tab: fixed-height table (250px) + edit panel
     - Footer buttons always visible
  6. Test adding/editing parameters and verbs
  7. Test instance creation with parameter selection
  8. Verify execution with different verbs

### Previous Session (2026-02-02) - Part 2: Bug Fix Verification

**Fixed and verified: Project deletion now removes all associated instances**

**Issue reported:** User deleted a project that had two instances. Project was deleted but instances remained orphaned.

**Root cause:** The `delete_project()` method only deleted the single legacy wrapper/config stored in project metadata, but didn't scan for all instances with matching `project_id`.

**Fix implemented:**
- Modified `delete_project()` in `src/project_manager/project_service.py`
- Now scans all `*.json` files in `conf/runners/` directory
- Checks each config for matching `project_id`
- Deletes all matching instance configs and their wrapper scripts
- Logs number of instances removed

**Verification test:**
- Created test project with 3 instances (A, B, C)
- All 3 instances had `project_id="test-deletion"`
- Called `delete_project('test-deletion')`
- **Result:** ✅ SUCCESS
  - Project directory deleted
  - All 3 instance configs deleted
  - All 3 wrapper scripts deleted
  - No orphaned files remain

**Files modified:**
- `src/project_manager/project_service.py:425-465` - Enhanced deletion logic

**Testing:**
- ✅ Unit test created and passed (`test_deletion.py`)
- ✅ Manual verification confirmed all files deleted
- ✅ Server running without errors

### Recent Session (2026-02-02) - Part 1: Project-Level Parameters & Verbs Architecture (Phase 1-4)

**Major architectural change: Moving parameter and verb definitions from script-instance level to project level.**

**Status:** ✅ Phase 1 Backend Foundation Complete

**Goals achieved:**
- ✅ Project metadata schema extended with `parameters`, `verbs`, `shared_parameters` fields
- ✅ New instance config format with `project_id` and `instance_config` (included_parameters, parameter_values, selected_verb)
- ✅ ProjectService CRUD methods for project-level parameters and verbs
- ✅ ConfigModel now supports project-based parameter loading
- ✅ API endpoints for managing project configuration
- ✅ 100% backward compatible with legacy configs

**Key Changes:**

1. **Project Metadata Extension:**
   - `.project-meta.json` now stores canonical parameter definitions
   - Added `parameters` array with full parameter specs
   - Added `verbs` object for verb configuration
   - Added `shared_parameters` list for cross-verb parameters

2. **Instance Config Format (NEW):**
   ```json
   {
     "project_id": "gmail-trim-3",
     "instance_config": {
       "included_parameters": ["days", "dry_run"],
       "parameter_values": {"days": 14},
       "selected_verb": "run"
     }
   }
   ```

3. **Backend Changes:**
   - `ProjectService` - Added `update_project_parameters()`, `update_project_verbs()`, `get_project_parameters()`, `get_project_verbs()`
   - `ProjectService.generate_runner_config()` - Now accepts instance config parameters
   - `script_config.InstanceConfig` - New class for instance configuration
   - `ConfigModel._load_from_project()` - New method to load from project metadata

4. **API Endpoints (NEW):**
   - `GET /admin/projects/{id}/config` - Get project parameters and verbs
   - `PUT /admin/projects/{id}/parameters` - Update project parameters
   - `PUT /admin/projects/{id}/verbs` - Update project verb configuration

**Benefits:**
- ✅ **DRY Principle** - Define parameters once, use many times
- ✅ **Consistency** - All instances share parameter definitions
- ✅ **Maintainability** - Update in one place → all instances updated
- ✅ **Clear Separation** - Project = capabilities, Instance = configuration
- ✅ **Reduced Duplication** - Eliminates ~100-200 lines per instance config

**Files modified:**
- `src/project_manager/project_service.py` - Added CRUD methods, modified generate_runner_config
- `src/model/script_config.py` - Added InstanceConfig class, project-based loading
- `src/web/server.py` - Added 3 new API handlers and routes

**Files created:**
- `docs/project-level-parameters-phase1-complete.md` - Comprehensive Phase 1 documentation
- `docs/backend-test-results.md` - Complete test results with verification details
- `test_project_level_params.py` - Backend test suite (4 tests, all passing)
- `conf/runners/Gmail Trim Test Instance.json` - Test instance config using new format
- Updated `projects/gmail-trim-3/.project-meta.json` - Added parameters and verbs

**Testing:**
- ✅ Backend imports successful
- ✅ **All backend tests passed (4/4)**
  - ✅ ProjectService loads project metadata with parameters/verbs
  - ✅ ConfigModel loads instance configs with project_id
  - ✅ Parameter filtering works (only included params loaded)
  - ✅ Value overrides work (instance values override defaults)
- ✅ Real project tested: gmail-trim-3 with 4 parameters and 5 verbs
- ⏳ Manual API testing via HTTP endpoints pending
- ⏳ Full integration testing with UI pending

**Implementation Status:**
- ~~Phase 1: Backend Foundation~~ ✅ COMPLETE (tested 4/4 tests passed)
- ~~Phase 2: Config Loading~~ ✅ COMPLETE (tested with gmail-trim-3)
- ~~Phase 3: Frontend Project Config UI~~ ✅ COMPLETE (awaiting manual testing)
- ~~Phase 4: Frontend Instance Config UI~~ ✅ COMPLETE (awaiting manual testing)
- Phase 5: Migration tooling and documentation - 📋 TODO
- Phase 6: EditScriptModal integration - 📋 TODO
- Phase 7: Full integration testing - 📋 TODO

**Next steps:**
- Manual UI testing of entire workflow
- Test instance creation with parameters/verbs
- Documentation and migration guide
- Consider EditScriptModal enhancements

---

### Recent Session (2026-02-02 cont.) - Phase 4: Frontend Instance Config UI

**Status:** ✅ Complete - Ready for Manual Testing

**Goals achieved:**
- ✅ Added instance configuration section to ConfigurePanel
- ✅ Verb selection dropdown with description display
- ✅ Parameter selection with checkboxes (verb-filtered)
- ✅ Parameter value override inputs (type-specific)
- ✅ "Select All" / "Deselect All" quick actions
- ✅ Smart default value handling
- ✅ Updated API call to send instance config
- ✅ Frontend builds successfully

**Key Features:**

1. **Instance Configuration Section:**
   - Highlighted section when project has parameters/verbs
   - Info message explaining workflow
   - Clean, user-friendly layout

2. **Verb Selection:**
   - Dropdown for selecting verb/command
   - Shows description below selection
   - Filters available parameters based on verb
   - Resets parameter selection on verb change

3. **Parameter Selection:**
   - Checkboxes for each available parameter
   - Shows type, description, required status
   - Filtered by selected verb (verb params + shared params)
   - Quick select all/deselect all actions

4. **Value Overrides:**
   - Type-specific inputs (checkbox, number, text)
   - Shows default value as hint/placeholder
   - Only sends values that differ from defaults
   - Auto-initializes with project defaults

**User Workflow:**
```
Import Project → Configure Dependencies & Entry Point
→ Select Verb (if applicable)
→ Check Parameters to include
→ Override Values (optional)
→ Create Script Instance
```

**Files modified:**
- `web-src/src/admin/components/scripts-config/create-script/ConfigurePanel.vue` (+200 lines)
  - Added instance configuration UI
  - Added data properties, computed properties, methods
  - Added comprehensive CSS styling
- `web-src/src/admin/components/scripts-config/create-script/CreateScriptModal.vue` (+15 lines)
  - Updated API call to include instance config

**Files created:**
- `docs/phase4-instance-config-complete.md` - Complete Phase 4 documentation

**Testing:**
- ✅ Frontend builds successfully
- ⏳ Manual UI testing required
- ⏳ End-to-end instance creation testing

**Next steps:**
- Manual UI testing with gmail-trim-3
- Test all parameter types and verb filtering
- Verify instance creation with overridden values
- Test generated config files

---

### Previous Session (2026-02-02 cont.) - Phase 3: Frontend Project Config UI

**Status:** 🚧 In Progress - Core Components Complete, Awaiting Manual Testing

**Goals achieved:**
- ✅ Created ProjectConfigModal.vue - Main configuration modal with Parameters and Verbs tabs
- ✅ Created ProjectParametersEditor.vue - CRUD interface for parameter definitions
- ✅ Integrated into ProjectsModal - Added "Configure Parameters & Verbs" button
- ✅ API integration complete - GET/PUT endpoints wired up
- ✅ Frontend builds successfully - No compilation errors
- ✅ CSS styling complete - Consistent with existing design

**Key Components:**

1. **ProjectConfigModal.vue** (334 lines)
   - Two-tab interface: Parameters and Verbs
   - Loads/saves configuration via API
   - Unsaved changes detection
   - Error/success messaging

2. **ProjectParametersEditor.vue** (452 lines)
   - Add/edit/delete parameters
   - Reorder with up/down arrows
   - Type selection (text, int, bool, list)
   - Type-specific constraints (min/max, length)
   - Default value configuration
   - CLI flag specification

3. **ProjectsModal Integration:**
   - New "Project Configuration" section in Configure tab
   - Shows parameter/verb counts from metadata
   - Opens ProjectConfigModal on button click

**User Workflow:**
1. Open Script Manager
2. Select project → Configure tab
3. Click "Configure Parameters & Verbs"
4. Add/edit parameters in Parameters tab
5. Configure verbs in Verbs tab (reuses VerbConfigEditor)
6. Save configuration

**Files created:**
- `web-src/src/admin/components/projects/ProjectConfigModal.vue` - Main modal
- `web-src/src/admin/components/projects/ProjectParametersEditor.vue` - Parameter editor
- `docs/phase3-frontend-progress.md` - Comprehensive Phase 3 documentation

**Files modified:**
- `web-src/src/main-app/components/ProjectsModal.vue` - Added integration

**Testing:**
- ✅ Frontend builds successfully
- ⏳ Manual UI testing required
- ⏳ Parameter CRUD operations
- ⏳ Verb configuration
- ⏳ Save/load persistence

**Next steps:**
- Manual UI testing with gmail-trim-3 project
- Verify VerbConfigEditor integration works correctly
- Test error handling and edge cases
- Then proceed to Phase 4 (Instance Config UI)

**Documentation:**
- See `docs/project-level-parameters-phase1-complete.md` for detailed implementation notes
- See original plan in session transcript for full architecture

### Previous Session (2026-02-01) - Part 2: Dual-Flag Boolean Parameters

**Added support for boolean parameters with different flags for true vs false values.**

**Goals achieved:**
- ✅ Backend support for dual-flag configuration
- ✅ Frontend UI for dual-flag mode selection
- ✅ Executor logic to use correct flag based on value
- ✅ 100% backward compatible with existing boolean parameters
- ✅ Comprehensive documentation and test config

**Key Changes:**

1. **Backend - Parameter Model** (`src/model/parameter_config.py`):
   - Added `dual_flags`, `param_true`, `param_false` observable fields
   - Parse dual-flag config from JSON
   - Validate that both flags are provided when dual_flags=true
   - Added fields to sorted config key order

2. **Backend - Executor** (`src/execution/executor.py`):
   - Updated `_build_param_args()` to check for dual_flags first
   - Use `param_true` when value is true, `param_false` when false
   - Skip value passing (just add the flag)

3. **Frontend - ParameterConfigForm** (`web-src/src/admin/components/scripts-config/ParameterConfigForm.vue`):
   - Added data properties: `boolFlagMode`, `paramTrue`, `paramFalse`
   - Added "Boolean flag mode" radio buttons (single/dual)
   - Show dual-flag input fields when mode is "dual"
   - Disable "Combine param with value" checkbox in dual-flag mode
   - Updated `syncToBackend()` to serialize dual-flag config
   - Updated `fromBackendConfig()` to detect and load dual-flag bools
   - Added watchers for new fields

**Example use cases:**
- `--verbose` (if true) / `--quiet` (if false)
- `--enable-cache` (if true) / `--disable-cache` (if false)
- `--color` (if true) / `--no-color` (if false)

**Files modified:**
- `src/model/parameter_config.py` - Added dual-flag fields and validation
- `src/execution/executor.py` - Updated _build_param_args for dual flags
- `web-src/src/admin/components/scripts-config/ParameterConfigForm.vue` - Added dual-flag UI

**Files created:**
- `docs/dual-flag-boolean-parameters.md` - Comprehensive feature documentation
- `conf/runners/dual_flag_test.json` - Test config with dual-flag examples
- `samples/scripts/dual_flag_demo.sh` - Test script for manual verification

**Testing:**
- ✅ Frontend builds successfully
- ✅ Backend executor logic tested (all tests pass)
- ✅ Manual script execution verified
- ⏳ Full UI testing recommended

**Benefits:**
- More flexible boolean parameter configuration
- Support for CLI tools with opposing flag patterns
- Cleaner command-line output (flags only, no values)
- Intuitive UI for choosing flag mode

**Next steps:**
- Test dual-flag UI in admin interface
- Verify config editing and saving
- Commit changes to master branch
- Consider PR to upstream

### Recent Session (2026-02-01) - Part 1: Simplified Parameter Configuration UI

**Complete redesign of parameter configuration form to reduce complexity and improve usability.**

**Goals achieved:**
- ✅ Reduced parameter types from 11 to 6 essential types
- ✅ Removed redundant checkboxes (converted to types)
- ✅ Organized form into 3 clear sections (Basic, Behavior, Constraints)
- ✅ Type-specific constraint visibility
- ✅ 100% backward compatible with existing configs

**Key Changes:**

1. **Simplified Type System:**
   - Reduced from 11 types to 6: `text`, `int`, `bool`, `list`, `flag`, `constant`
   - Removed specialized types: `ip`, `ip4`, `ip6`, `file_upload`, `server_file`, `multiline_text`, `editable_list`, `multiselect`
   - New types: `bool` (radio buttons), `flag` (replaces "Without value" checkbox), `constant` (replaces "Constant" checkbox)

2. **Form Redesign (`ParameterConfigForm.vue`):**
   - **Section 1 - Basic:** Name, Description, Type dropdown, Required checkbox
   - **Section 2 - Parameter Behavior:** Param (CLI flag), Pass as, Combine checkbox
   - **Section 3 - Constraints (bold header):** Type-specific validation fields
   - Removed clutter: "Secret value", "Env var", "Stdin expected text" fields

3. **Type-Specific Constraints:**
   - **Text:** Min/max length (always visible), RegExp pattern + description, Default value
   - **Int:** Min/max value, Default value
   - **Bool:** Radio buttons for true/false default
   - **List:** Selection mode, Two-column value/UI mapping table, Multiselect format options
   - **Flag:** Info box explaining usage (no constraints)
   - **Constant:** Constant value field + info box

4. **Automatic Migration:**
   - `no_value: true` → `flag` type
   - `constant: true` → `constant` type
   - `type: "multiselect"` → `list` (multiple selection mode)
   - `type: "editable_list"` → `list`
   - `type: "multiline_text"/"ip"/"ip4"/"ip6"` → `text`
   - List with `['true', 'false']` → `bool` type

5. **Visual Improvements:**
   - Section dividers for clear separation
   - Bold "Constraints" header for visibility
   - Blue info boxes for flag and constant types
   - Two-column table for list values (Value | UI Display)
   - Clean input styling with focus highlighting

**Files modified:**
- `web-src/src/admin/components/scripts-config/ParameterConfigForm.vue` - Complete redesign (815 lines)
- `web-src/src/admin/components/scripts-config/parameter-fields.js` - Updated typeField
- `docs/simplified-parameter-ui.md` - Comprehensive documentation
- `conf/runners/param_ui_test.json` - Test config with all parameter types

**Bug Fix (List Parameter Reactivity Loop):**
- **Issue:** Selecting "list" type froze the dialog due to infinite reactivity loop
- **Root cause:** Watchers triggering each other (type → syncToBackend → value → fromBackendConfig → listValues → syncToBackend)
- **Solution:** Added `isLoading` flag to prevent re-entrant watcher execution
- **Changes:**
  - Added `isLoading` data property
  - Guarded all field watchers with `if (!this.isLoading)` check
  - Set flag in `value` watcher before `fromBackendConfig()`, clear in `$nextTick`
  - Initialize `listValues` with one empty row when switching to list type
  - Created `listValuesForDropdown` computed property for safe dropdown rendering

**Testing:**
- ✅ Frontend builds successfully
- ✅ Server running on http://localhost:5000
- ✅ Test config created with all 6 parameter types
- ✅ List type reactivity loop fixed
- ✅ All parameter types working correctly
- ⏳ Full manual UI testing recommended

**Benefits:**
- 45% fewer parameter types (6 vs 11)
- 5 fewer form fields (cleaner UI)
- Constraints section now prominent (bold header)
- Type-specific fields reduce confusion
- Better list editing with two-column table
- Info boxes explain special types

**Next steps:**
- Test all parameter types in admin UI
- Verify migration of existing scripts
- Commit changes to master branch
- Update user documentation

### Previous Session (2026-01-31) - Part 3: Import-Only Architecture with Auto-Managed Paths

**Major architectural simplification: removed manual script creation, auto-manage paths, and enforce sandboxing.**

**Goals achieved:**
- ✅ Import-only workflow (Git/ZIP/Local)
- ✅ Script path and working directory auto-managed by server
- ✅ Sandboxed execution (scripts confined to their project folders)
- ✅ Hidden complexity from users (no path fields in UI)
- ✅ Removed advanced "Include Config" field (doesn't fit import-only model)

**Changes:**

1. **Backend: Auto-manage working directory** (`project_service.py`):
   - `generate_runner_config()` now auto-sets `working_directory = "projects/{project_id}"`
   - Scripts execute from their project root, access files via relative paths

2. **Backend: Sandboxing validation** (`executor.py`):
   - Enhanced `_normalize_working_dir()` with security validation
   - Enforces that `working_directory` must be within `projects/` folder
   - Prevents path traversal attacks (resolves `..`, validates against projects_dir)
   - Raises `ValueError` if working directory escapes project boundaries
   - Tested: blocks `projects/my-project/../../etc` and `/app/projects/../src`

3. **Frontend: Remove manual script creation** (`CreateScriptModal.vue`):
   - Removed Source tab (no more import vs manual selection)
   - Import-only workflow: Import → Configure → Details → Parameters → Advanced
   - Removed `creationMode` state and logic
   - Removed `initialMode` prop
   - Always uses import path (calls backend wrapper generation API)

4. **Frontend: Simplify Script Manager** (`ProjectsModal.vue`):
   - Removed "Create" tab
   - Now only has: Projects, Import, Configure tabs
   - Removed CreateScriptModal integration
   - Removed `openManualScriptCreation` and related methods

5. **Frontend: Hide path fields entirely** (`EditScriptModal.vue`, `DetailsTab.vue`):
   - **Script path field: REMOVED** (not just hidden - completely gone)
   - **Working directory field: REMOVED** (auto-managed by server)
   - **Include config field: REMOVED** (advanced feature, doesn't fit import-only)
   - Details tab now only shows: Name, Group, Description, Output Format, Enable Pseudo-Terminal

**Security benefits:**
- Scripts cannot escape their project folder via `../` traversal
- Scripts cannot access other projects or server source code via working_directory
- Path resolution handles symlinks correctly (follows then validates)
- Absolute paths outside projects/ are rejected

**UX benefits:**
- Cleaner UI: removed 3 confusing/advanced fields
- Users only see what they need to configure
- Import-only workflow is clear and straightforward
- No manual path management (error-prone, not portable)

**Commits:**
- `777502a` - feat: Implement import-only architecture with auto-managed paths and sandboxing
- `192f19e` - fix: Hide script path and working directory fields from Edit Script dialog
- `696a26d` - refactor: Remove Include Config field from script dialogs

**Files modified:**
- `src/project_manager/project_service.py` (auto-set working_directory)
- `src/execution/executor.py` (sandboxing validation in _normalize_working_dir)
- `web-src/src/admin/components/scripts-config/create-script/CreateScriptModal.vue` (import-only workflow)
- `web-src/src/admin/components/scripts-config/create-script/DetailsTab.vue` (hide path/include fields)
- `web-src/src/main-app/components/scripts/EditScriptModal.vue` (hide path/include fields)
- `web-src/src/main-app/components/ProjectsModal.vue` (remove Create tab)
- `docs/import-only-architecture.md` (comprehensive documentation)

**Testing performed:**
- ✅ Sandboxing tests passing (path traversal blocked)
- ✅ Frontend builds successfully
- ✅ Server starts and validates scripts correctly
- ✅ UI verified: path fields completely removed from Edit/Create dialogs

**Deployment:**
- Pushed to GitHub: triggers Docker build
- Image: `ghcr.io/snadboy/script-server:latest`
- Ready to deploy to utilities host

### Recent Session (2026-01-31) - Part 2: Code Quality Improvements

**Comprehensive code quality refactoring to fix warnings and improve maintainability.**

**Issues fixed:**
- 6 bare `except:` clauses (catches `KeyboardInterrupt` and `SystemExit`)
- 8 overly broad exception catches
- 4 generic `Exception` raises
- Missing type hints across scheduling and project modules

**Changes:**

1. **Bare exceptions → specific types:**
   - `schedule_service.py`: restore_jobs, _execute_job, get_jobs, get_job
   - `server.py`: ScriptStreamSocket.open, intercept_stop_when_running_scripts

2. **Narrowed exception catches:**
   - `venv_service.py`: OSError for file I/O, SyntaxError for AST parsing
   - `project_service.py`: OSError, KeyError, TypeError for config parsing

3. **Specific exception types:**
   - RuntimeError for git clone failures
   - FileNotFoundError for missing paths
   - NotADirectoryError for invalid directories

4. **Type hints added:**
   - `scheduling_job.py`: All methods and parameters
   - `schedule_config.py`: All functions and return types
   - `schedule_service.py`: All ScheduleService methods
   - `project_service.py`: Optional parameters, staticmethod decorator

**Commits:**
- `fd0b312` - Initial code quality improvements (6 files)
- `e4d4fe4` - Fix all warnings in process_pty.py (bare excepts, type hints)
- `f97d7b0` - Add type narrowing assertions (eliminates 'Argument of type' warnings)
- `8ee414e` - Simplify encoding fallback to satisfy type checker
- `ace566d` - Initialize encoding with default value instead of None (line 174)

**Files modified:**
- src/project_manager/project_service.py (41 changes)
- src/scheduling/schedule_config.py (47 changes)
- src/scheduling/schedule_service.py (34 changes)
- src/scheduling/scheduling_job.py (35 changes)
- src/venv_manager/venv_service.py (8 changes)
- src/web/server.py (4 changes)
- src/execution/process_pty.py (16 changes - 2 bare excepts, comprehensive type hints)

### Recent Session (2026-01-31) - Part 1: Icon Visibility Fix

**Fixed admin buttons appearing invisible due to Material Icons compatibility issues.**

**Issue:**
- User reported Requirements button was missing from sidebar
- All 5 buttons existed in DOM but only 4 icons were visually distinguishable
- Material Icons "storage" (Python Packages) and "list_alt" (Requirements) rendered as nearly identical list icons
- Second issue: `inventory_2` icon doesn't exist in the Material Icons version bundled with the app

**Solution (Final):**
- Changed Python Packages icon: `storage` → `extension` (puzzle piece 🧩)
- Changed Requirements icon: `list_alt` → `assignment` (clipboard 📋)

**Final icon set:**
- Script Manager: `description` (document 📄)
- Python Packages: `extension` (puzzle piece 🧩)
- Requirements: `assignment` (clipboard 📋)
- Server Logs: `subject` (lines ☰)
- Settings: `settings` (gear ⚙️)

**Commits:**
- `a9d99fb` - Initial fix attempt with inventory_2 and assignment icons
- `2f43fd0` - Final fix using extension icon (inventory_2 not available in Material Icons v1)

**Files modified:**
- `web-src/src/main-app/components/MainAppSidebar.vue` (lines 19, 22)

### Recent Session (2026-01-29) - Part 3: Release & Integration

**Merged verb branch to master and set up project integrations.**

**Actions completed:**

1. **Cleaned up verb branch:**
   - Reverted test schedules, local development artifacts
   - Removed test schedule files (Test Script_admin_*.json)
   - Committed staged changes with verb filtering + script descriptions

2. **Merged to master and triggered build:**
   - Fast-forward merge of verb branch to master
   - Pushed to origin master
   - GitHub Actions workflow triggered: Docker build → ghcr.io/snadboy/script-server:latest

3. **Set up gmail-trim on GitHub:**
   - Already pushed to https://github.com/snadboy/gmail-trim
   - Added topics: gmail, automation, cleanup, python, cli
   - Latest commit: c6497b4 - Code quality improvements

4. **Set up upcoming-episodes on GitHub:**
   - Created initial commit (15d9b43) with FastAPI service
   - Created public repository: https://github.com/snadboy/upcoming-episodes
   - Added topics: plex, sonarr, metadata, fastapi, webhook
   - 14 files committed (1,297 lines)

5. **Created script-server integration:**
   - **Wrapper scripts** (committed to repo):
     - `samples/scripts/gmail_trim.py` - Wrapper for gmail-cleanup CLI
     - `samples/scripts/upcoming_episodes_sync.py` - HTTP client for sync service
   - **Config files** (local only, in .gitignore):
     - `conf/runners/gmail_trim.json` - Verb-based config with run/auth/labels/groups/config commands
     - `conf/runners/upcoming_episodes.json` - Simple sync trigger with scheduling enabled

**Next steps:**
- Wait for Docker build to complete
- Deploy projects to /opt/ on utilities host
- Set up systemd service for upcoming-episodes
- Install Python dependencies and test wrappers

### Recent Session (2026-01-29) - Part 2

Consolidated Create Script and Manage Projects buttons into a unified "Script Manager" with 3-tab modal interface.

**What was changed:**

- **Unified Script Manager Button** - Single entry point in sidebar (description icon) for all script-related actions
- **3-Tab Modal System:**
  - **Projects tab** - View and delete imported Python projects (existing ProjectsModal functionality)
  - **Import tab** - Import Python projects via Git/ZIP/Local (existing ProjectsModal functionality)
  - **Create tab** - NEW - Opens CreateScriptModal in manual mode for creating script configs
- **Create Tab UI:**
  - Centered card with code icon
  - "Create Manual Script" button
  - Opens CreateScriptModal with `initialMode='manual'` prop
  - Automatically skips Source tab, goes directly to Details tab
- **InitialMode Prop:**
  - Added to CreateScriptModal to support launching in specific mode
  - When set to 'manual', automatically sets creationMode and activeTab to skip Source selection
- **Axios Import Fix:**
  - Fixed incorrect default imports to use named import: `import {axiosInstance} from '@/common/utils/axios_utils'`
  - Affected CreateScriptModal, ImportPanel, ConfigurePanel

**Files modified:**
- `web-src/src/main-app/components/MainAppSidebar.vue`
  - Removed separate "Create Script" and "Manage Projects" buttons
  - Added single "Script Manager" button (description icon)
  - Opens ProjectsModal instead of CreateScriptModal
- `web-src/src/main-app/components/SidebarBottomNav.vue`
  - Removed "Add Script" button from bottom navigation
  - Bottom nav now only shows Activity and Users tabs
- `web-src/src/main-app/components/ProjectsModal.vue`
  - Renamed title to "Script Manager"
  - Added "Create" tab with centered card UI
  - Integrated CreateScriptModal with `initialMode='manual'`
  - Added CSS for create-section, create-card, create-icon, create-btn
- `web-src/src/admin/components/scripts-config/create-script/CreateScriptModal.vue`
  - Added `initialMode` prop (validates 'import'|'manual')
  - Modified `watch.visible` to handle initialMode and skip Source tab
  - Fixed axios import to named import
- `web-src/src/admin/components/scripts-config/create-script/ImportPanel.vue`
  - Fixed axios import to named import
- `web-src/src/admin/components/scripts-config/create-script/ConfigurePanel.vue`
  - Fixed axios import to named import

**Testing:**
- Frontend rebuilt successfully
- Server restarted on http://localhost:5000
- Verified all three tabs work correctly:
  - Projects tab shows imported projects with configure/delete actions
  - Import tab provides Git/ZIP/Local import options
  - Create tab opens manual script creation modal in correct mode
- Verified CreateScriptModal initialMode prop works - skips Source tab and starts at Details

**Next steps:**
- Update CLAUDE.md with this session's changes
- Consider committing these UI improvements to the verb branch

### Recent Session (2026-01-29) - Part 1

Fixed parameter filtering in execution cards and added script description to script view header.

**Issues fixed:**

1. **Parameter Filtering by Verb** - Execution cards were showing all parameters instead of just those relevant to the verb that was used.
   - **Root cause:** The `/scripts` API endpoint only returned "short configs" without verb configuration
   - **Solution:** Extended ShortConfig dataclass and API response to include verb configuration
   - Now properly filters parameters to show only:
     - The verb parameter itself (e.g., `command=labels`)
     - Parameters specific to the selected verb
     - Shared parameters (e.g., `verbose`)

2. **Script Description in Header** - Added script description display in the header area above the Running section on script view pages.

**Backend changes:**
- `src/model/script_config.py`:
  - Extended `ShortConfig` dataclass to include `verbs_config` and `shared_parameters` fields
  - Modified `read_short()` function to parse and include verb configuration
- `src/web/server.py`:
  - Modified `GetScripts` handler to serialize verb config in API response
  - Uses `verbs_config.to_dict()` for proper camelCase serialization

**Frontend changes:**
- `web-src/src/main-app/utils/executionFormatters.js`:
  - Added `getScriptConfig()` utility to find script config by name
  - Added `filterParametersByVerb()` utility to filter parameters based on verb
  - Fixed to use camelCase `parameterName` (not snake_case `parameter_name`)
- `web-src/src/main-app/components/common/RunningSection.vue`:
  - Integrated verb-aware parameter filtering
  - Updated `getVerbParameterName()` to use camelCase
- `web-src/src/main-app/components/common/CompletedSection.vue`:
  - Integrated verb-aware parameter filtering
  - Updated `getVerbParameterName()` to use camelCase
- `web-src/src/main-app/components/scripts/script-view.vue`:
  - Added script description header with styled container

**Example result:**
- **Before:** `days=14, dry_run=true, verbose=false, command=labels`
- **After:** `command=labels, verbose=false` (for "labels" verb with no specific parameters)

**Testing:**
- Frontend rebuilt successfully
- Server running on http://localhost:5000
- Parameter filtering verified working via Chrome DevTools
- Script description displays in header when present

### Previous Session (2026-01-28)

Added verb/subcommand configuration UI to the admin interface.

**What was added:**
- New **"Verbs"** tab (Tab 5) in Add/Edit Script Modal
- `VerbConfigEditor.vue` - Main component for managing verb configuration
- `VerbOptionEditor.vue` - Component for editing individual verb options
- Enable/disable verb support with checkbox
- Configure verb parameter name, default verb, and required flag
- Define shared parameters (visible for all verbs)
- Add/edit/delete/reorder verb options
- For each verb: set name, label, description, visible parameters, and required parameters
- Real-time parameter filtering based on verb selection
- Full integration with existing script config save/load system

**Files created:**
- `web-src/src/admin/components/scripts-config/VerbConfigEditor.vue`
- `web-src/src/admin/components/scripts-config/VerbOptionEditor.vue`

**Files modified:**
- `web-src/src/admin/components/scripts-config/AddScriptModal.vue` - Added Verbs tab, integrated VerbConfigEditor

**Testing:**
- Frontend rebuilt successfully with `npm run build`
- Server restarted and running on http://localhost:5000
- Verbs tab now accessible in admin UI at http://localhost:5000/admin.html

**Next steps:**
- Test the new Verbs UI by creating/editing a script
- Consider adding verb editing to existing EditScriptModal as well
- Merge to master when ready

### Previous Session (2026-01-22)

Tested and verified CLI verb/subcommand feature is fully working after frontend rebuild.

**Testing performed:**
- Rebuilt frontend (`npm run build`) to include VerbSelector component
- Restarted server to pick up new build (build 0122-0716)
- Verified VerbSelector renders correctly above parameters panel
- Tested all three verbs in `verb_demo.json`:

| Verb | Description | Parameters Shown |
|------|-------------|------------------|
| List Items | List all items with optional filtering | format, all, verbose |
| Create Item | Create a new item with the given name | name, type, verbose |
| Delete Item | Delete an item by its ID | item_id, force, verbose |

**Verified functionality:**
- ✅ VerbSelector dropdown renders with "Command" label
- ✅ Verb descriptions update dynamically when switching
- ✅ Parameter filtering works - only relevant parameters shown per verb
- ✅ Shared parameters (`verbose`) appear for all verbs
- ✅ Verb-specific parameters correctly hidden/shown on switch

**Note:** Initial test showed all parameters visible because server was running old frontend build. After rebuild + restart, feature works correctly.

### Previous Session (2026-01-21)

Implemented CLI verb/subcommand support where scripts can define multiple verbs (like `git clone`, `docker run`), each with their own set of required/optional parameters.

**Features added:**

| Feature | Description |
|---------|-------------|
| Verb Configuration | New `verbs` section in script config to define subcommands |
| VerbOption Model | Defines name, label, description, parameters, and required_parameters per verb |
| Verb-aware Command Building | Executor places verb first, then positional `after_verb` params, then flagged params, then `end` positional params |
| verb_position Parameter | New parameter field: `after_verb` (positional after verb) or `end` (positional at end) |
| shared_parameters | Parameters visible across all verbs (e.g., `--verbose`) |
| VerbSelector.vue | Frontend dropdown component for selecting verb/subcommand |
| Parameter Filtering | Only parameters for selected verb are shown in UI |
| Verb-specific Required | Parameters can be required only for certain verbs |
| ExecuteModal Support | Verb selector integrated into Execute dialog with parameter filtering |
| API Extension | `verbs` and `sharedParameters` serialized in config API response |

**Example config format:**
```json
{
  "verbs": {
    "parameter_name": "action",
    "default": "list",
    "options": [
      {
        "name": "create",
        "label": "Create Item",
        "parameters": ["name", "type"],
        "required_parameters": ["name"]
      }
    ]
  },
  "shared_parameters": ["verbose"],
  "parameters": [
    {"name": "name", "verb_position": "after_verb"},
    {"name": "verbose", "param": "-v", "no_value": true}
  ]
}
```

**Files created/modified:**
- `src/model/verb_config.py` (new)
- `src/model/script_config.py` (modified)
- `src/model/parameter_config.py` (modified)
- `src/execution/executor.py` (modified)
- `src/model/external_model.py` (modified)
- `web-src/src/main-app/components/scripts/VerbSelector.vue` (new)
- `web-src/src/main-app/components/scripts/script-parameters-view.vue` (modified)
- `web-src/src/main-app/components/scripts/ExecuteModal.vue` (modified)
- `web-src/src/main-app/store/scriptSetup.js` (modified)
- `conf/runners/verb_demo.json` (new - test config)

### Previous Session (2026-01-20)

Implemented auto-cleanup of completed one-time scheduled tasks:

| Commit | Description |
|--------|-------------|
| `b476b53` | Add auto-cleanup of non-recurring scheduled tasks |
| `bcf1371` | Add retention setting to Settings Modal (admin only) |
| `7ee892e` | Fix: Use auth store for admin check in SettingsModal |
| `5dffc67` | Fix: Override Materialize red validation border on settings inputs |
| `b018d7b` | Fix: Force override Materialize input border styles with !important |
| `72ee089` | Fix: Clean up legacy one-time schedules without completion_time |

**Features added:**

| Feature | Description |
|---------|-------------|
| Completion Time Tracking | Non-recurring schedules record `completion_time` when executed |
| Configurable Retention | Default 60 min, 0 = immediate, -1 = never delete |
| Background Cleanup | Runs every 5 minutes + on startup to delete expired schedules |
| Expired Status API | GET /schedules returns `expired` and `auto_delete_at` fields |
| Visual Distinction | Green "Completed" badge, reduced opacity, auto-delete countdown in UI |
| Settings Modal | Admins can configure retention via Settings (gear icon) in sidebar |
| Runtime API | GET/PUT /schedules/settings endpoint for retention config |

### Previous Session (2026-01-18)

Tested entry point detection and fixed several UI issues:

| Commit | Description |
|--------|-------------|
| `18e93d6` | Fix entry point dropdown selection timing |
| `7d8313d` | Fix Entry Point dropdown visibility (Materialize CSS override) |
| `df82969` | Prevent modal from closing on outside click |
| `b14c4f2` | Hide custom entry point behind toggle for cleaner UI |
| `e8eb328` | Instance name on new line; show script names in Scheduled section |
| `6e65e47` | Update session notes |
| `f6bdf74` | Fix schedule edit: combine DELETE and PUT into single handler |
| `cd86463` | Fix schedule edit: parse camelCase to snake_case |

**Merged to master** - Docker build triggered automatically via GitHub Actions

### Completed Features

| Feature | Status | Notes |
|---------|--------|-------|
| Schedule List API | Done | GET /schedules, DELETE /schedules/{id} |
| Schedule List UI | Done | ScheduleList.vue component |
| Schedule Modal | Done | Replaced inline panel with modal dialog |
| Schedule Description | Done | Optional description field for schedules |
| Multi-Schedule Support | Done | Modal stays open after scheduling |
| Execute/Stop Button Merge | Done | Single button with state-based behavior |
| Stop Buttons (History) | Done | Stop/kill running scripts from History page |
| Stop Buttons (Scheduled) | Done | Stop/kill running scripts from Scheduled page |
| Add Script Modal | Done | Tabbed wizard with 4 tabs |
| User Management Modal | Done | Modal for user admin |
| Header Consistency | Done | History/Scheduled headers match |
| History Section Fix | Done | Running tasks excluded from Completed section |
| Edit Script Modal | Done | Tabbed wizard modal matching Add Script UX |
| Script Executions Panel | Done | Replaced log panel with Running/Scheduled + History sections |
| Unified Activity Page | Done | Combined Running, Scheduled, Completed into single page |
| Base UI Components | Done | CollapsibleSection, ExecutionCard, StopButton components |
| Live List Updates | Done | Running/Scheduled/Completed lists auto-refresh when executions start/complete |
| Schedule Last Run | Done | Shows last execution time for recurring schedules in lists |
| Sidebar Version Move | Done | Version/build number moved to bottom of sidebar |
| Sidebar Icon Alignment | Done | Fixed nav icon alignment (override global min-height CSS) |
| Scheduled Badge on Running | Done | Purple "Scheduled" badge shown on running executions triggered by schedules |
| Remove Parameter History | Done | Removed history button from script header |
| Simplify Schedule Modal | Done | Removed schedule list from Schedule Execution dialog |
| Execute Modal | Done | Modal dialog for script execution with instance name and parameters |
| Error Message Display | Done | Backend errors now show actual message instead of generic "Failed to save" |
| Collapsed State Persistence | Done | Running/Scheduled/Completed sections remember collapsed state via localStorage |
| Settings Modal | Done | Configurable completed executions limit via gear icon in sidebar |
| Schedule Enable/Disable | Done | Toggle button on schedule rows, checkbox in Schedule modal for recurring schedules |
| Unified Section Components | Done | Single implementation for Running/Scheduled/Completed sections used by both Activity and Script views |
| Schedule Editing | Done | PUT /schedules/{id} endpoint, edit button on schedule cards opens ScheduleModal in edit mode |
| Execution Finish Time | Done | Tracks finish_time in logs, shows Started/Completed times on completed execution cards |
| Instance Name Tracking | Done | Optional instance name for executions, stored in logs, displayed in Running/Completed sections |
| Unified Date Format | Done | Consistent M/D/YYYY @ HH:MM format across all date displays |
| Accurate Last Run Time | Done | Records actual execution time instead of calculated from schedule math |
| Log Size Limit Setting | Done | Configurable limit (max 250) for fetched execution history entries |
| Activity Completed Limit | Done | ActivityPage now uses completedExecutionsLimit setting (was missing) |
| UI/UX Consistency | Done | Unified modal patterns, CSS variables for colors/radius/shadows, standardized inputs |
| Consistent Title Format | Done | Running and Completed sections use same "ScriptName (Execution ID: nnn)" format |
| Card Layout Consistency | Done | Badges on left, schedule timing shown, increased badge visibility (opacity 0.35) |
| Script/Instance Descriptions | Done | All cards show script description + instance name; /scripts API includes description; uses computed scriptsMap for reactivity |
| GitHub Actions Docker Build | Done | Auto-builds and pushes to ghcr.io/snadboy/script-server on push to master |
| Venv Package Management | Done | Admin UI for managing Python packages in common venv; auto-creates venv; install/uninstall packages |
| Project Manager | Done | Import external Python projects via Git/ZIP/Local Path; auto-detect dependencies & entry points; generate wrapper scripts; clean entry point UI with toggle for custom input |
| One-time Schedule Auto-Cleanup | Done | Completed non-recurring schedules auto-delete after configurable retention period (default 60 min); shows "Completed" badge with auto-delete countdown in UI |
| CLI Verb/Subcommand Support | Done | Scripts can define verbs (like git clone, docker run) with per-verb parameters, required params, and positional placement |
| Unified Create Script Workflow | Done | Single modal combining Project Manager and Add Script functionality; adaptive tabs show/hide based on import vs manual mode; reusable components for each step |

### Test Infrastructure

| Item | Location | Description |
|------|----------|-------------|
| Long Running Script | `samples/scripts/long_running.py` | 30-second test script with progress bar |
| Script Config | `conf/runners/long_running.json` | Config with scheduling enabled (gitignored) |

### Gmail Cleanup Integration

| Item | Location | Description |
|------|----------|-------------|
| Wrapper Script | `samples/scripts/gmail_cleanup.py` | Runs gm project via common venv |
| Script Config | `conf/runners/gmail_cleanup.json` | Script-server config with run/labels/groups/config commands |
| Source Project | `/home/snadboy/projects/gm` | Gmail auto-cleanup source |

**Required packages** (install via Package Manager):
- google-api-python-client
- google-auth-oauthlib
- google-auth
- pydantic
- pydantic-settings
- structlog
- typer
- pyyaml

**Documentation:** See `docs/wrapping-python-projects.md` for detailed guide on wrapping external Python projects.

### Technical Notes

- **Materialize CSS quirk:** The framework sets `select { opacity: 0 }` globally to hide native selects for custom styling. Custom modals using native `<select>` elements must override with `opacity: 1` and `appearance: menulist`.

---

## Pending / Suggested Next Steps

1. **Merge verb branch to master** - Verb feature tested and working, ready for merge
2. **PR to Upstream** - Consider submitting PR to `bugy/script-server` for verb/subcommand feature
3. **Update gmail_cleanup.json** - Convert to use verb config instead of manual Command parameter

---

## Build Commands

```bash
# Frontend build
cd /home/snadboy/projects/script-server/web-src
NODE_OPTIONS=--openssl-legacy-provider npm run build

# Start server (MUST use venv - tornado and other deps are installed there)
cd /home/snadboy/projects/script-server
source .venv/bin/activate && python launcher.py

# Docker build
cd /home/snadboy/projects/script-server
docker build -t script-server:custom .
```

---

## Key Files Changed

- `web-src/src/main-app/components/schedule/ScheduleModal.vue` (new)
- `web-src/src/main-app/components/scripts/EditScriptModal.vue` (new)
- `web-src/src/main-app/components/scripts/ExecuteModal.vue` (new - execute dialog with parameters)
- `web-src/src/main-app/components/scripts/ScriptExecutionsPanel.vue` (new)
- `web-src/src/main-app/components/activity/ActivityPage.vue` (new - unified activity view)
- `web-src/src/main-app/components/activity/ActivityHeader.vue` (new)
- `web-src/src/main-app/components/common/CollapsibleSection.vue` (new - base component)
- `web-src/src/main-app/components/common/ExecutionCard.vue` (new - base component)
- `web-src/src/main-app/components/common/StopButton.vue` (new - reusable stop/kill button)
- `web-src/src/main-app/components/common/RunningSection.vue` (new - unified running executions section)
- `web-src/src/main-app/components/common/ScheduledSection.vue` (new - unified scheduled executions section)
- `web-src/src/main-app/components/common/CompletedSection.vue` (new - unified completed executions section)
- `web-src/src/main-app/components/common/ScheduleCard.vue` (new - reusable schedule card)
- `web-src/src/main-app/utils/executionFormatters.js` (new - shared formatting utilities)
- `web-src/src/main-app/components/scripts/script-view.vue` (modified - uses ScriptExecutionsPanel)
- `web-src/src/main-app/components/SidebarBottomNav.vue` (modified - Activity replaces History/Scheduled)
- `web-src/src/main-app/router/router.js` (modified - Activity route replaces History/Scheduled)
- `web-src/src/main-app/components/history/AppHistoryPanel.vue`
- `web-src/src/main-app/components/scheduled/ScheduledPage.vue`
- `web-src/src/main-app/components/scripts/ScriptInlineActions.vue`
- `web-src/src/common/components/history/executions-log.vue`
- `web-src/src/common/components/history/executions-log-page.vue`
- `web-src/src/main-app/store/index.js` (modified - init history and allSchedules, watcher for live updates)
- `web-src/src/main-app/store/allSchedules.js` (modified - added refresh action)
- `web-src/src/main-app/store/scriptSchedule.js` (modified - cross-store refresh on create/delete)
- `web-src/src/common/store/executions-module.js` (modified - added refresh action)
- `src/scheduling/scheduling_job.py`
- `src/scheduling/schedule_service.py` (modified - passes schedule_id when executing jobs, added update_job method)
- `src/scheduling/schedule_config.py` (modified - added get_last_execution_time method)
- `src/execution/execution_service.py` (modified - added schedule_id tracking to executions)
- `src/execution/logging.py` (modified - added schedule_id to logs and history, added finish_time tracking)
- `src/web/server.py` (modified - added last_execution to schedule API response, added PUT /schedules/{id} endpoint)
- `src/model/external_model.py` (modified - added scheduleId and finishTime to API response)
- `web-src/src/main-app/components/MainAppSidebar.vue` (modified - moved version to bottom)
- `web-src/src/admin/store/script-config-module.js` (modified - improved error handling for save/delete)
- `src/web/server.py` (modified - fixed HTTPError reason parameter, added schedule enable toggle API)
- `web-src/src/main-app/components/SettingsModal.vue` (new - settings dialog)
- `web-src/src/main-app/store/settings.js` (new - settings state with localStorage persistence)
- `samples/themes/dark/theme.css` (modified - added status/stop button/radius/shadow/transition CSS variables)
- `samples/themes/orange/theme.css` (modified - added same CSS variables for light theme)
- `.github/workflows/docker.yml` (new - GitHub Actions workflow for Docker builds)
- `src/venv_manager/__init__.py` (new - venv package module)
- `src/venv_manager/venv_service.py` (new - venv package management service)
- `web-src/src/main-app/components/PackagesModal.vue` (new - admin UI for package management)
- `web-src/src/main-app/components/MainAppSidebar.vue` (modified - replaced Projects button with Create Script button)
- `src/web/server.py` (modified - added venv and project management API endpoints)
- `src/project_manager/__init__.py` (new - project manager module)
- `src/project_manager/project_service.py` (new - project import/management service)
- `web-src/src/admin/components/scripts-config/create-script/CreateScriptModal.vue` (new - unified create script orchestrator)
- `web-src/src/admin/components/scripts-config/create-script/SourceSelector.vue` (new - source selection UI)
- `web-src/src/admin/components/scripts-config/create-script/ImportPanel.vue` (new - Git/ZIP/Local import)
- `web-src/src/admin/components/scripts-config/create-script/ConfigurePanel.vue` (new - dependency/entry point config)
- `web-src/src/admin/components/scripts-config/create-script/DetailsTab.vue` (new - script details form)
- `web-src/src/admin/components/scripts-config/create-script/AdvancedTab.vue` (new - access/scheduling/verbs combined)
- `web-src/src/main-app/components/ProjectsModal.vue` (new - admin UI for project management)
- `src/scheduling/schedule_config.py` (modified - added completion_time field for non-recurring schedule cleanup)
- `src/scheduling/schedule_service.py` (modified - added auto-cleanup logic, expiry helpers, background cleanup task, get/set retention methods)
- `src/model/server_conf.py` (modified - added onetime_schedule_retention_minutes config)
- `src/main.py` (modified - passes retention config to ScheduleService)
- `src/web/server.py` (modified - added expired/auto_delete_at to API, ScheduleSettingsHandler for retention config)
- `web-src/src/main-app/components/common/ScheduleCard.vue` (modified - added expired schedule visual distinction)
- `web-src/src/main-app/components/SettingsModal.vue` (modified - added retention setting for admins)
- `web-src/src/main-app/store/settings.js` (modified - added server-side retention setting with API calls)
