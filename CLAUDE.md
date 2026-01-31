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
**Latest Commit:** 3a1cb71 - Add wrapper scripts for gmail-trim and upcoming-episodes integration
**Last Updated:** 2026-01-29
**Docker Image:** `ghcr.io/snadboy/script-server:latest` (auto-builds on push to master)

### Recent Session (2026-01-31) - Icon Visibility Fix

**Fixed Requirements button appearing invisible due to identical Material Icons.**

**Issue:**
- User reported Requirements button was missing from sidebar
- All 5 buttons existed in DOM but only 4 icons were visually distinguishable
- Material Icons "storage" (Python Packages) and "list_alt" (Requirements) rendered as nearly identical list icons

**Solution:**
- Changed Python Packages icon: `storage` → `inventory_2` (box icon 📦)
- Changed Requirements icon: `list_alt` → `assignment` (clipboard icon 📋)

**Commit:** `a9d99fb` - Fix: Use distinctive Material Icons for Python Packages and Requirements buttons

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
