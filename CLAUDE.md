# Script Server Fork - Project Context

> **Important:** Keep this file updated throughout each session. When completing significant work (features, bug fixes, refactors), update the relevant sections immediately so context is preserved for future sessions.

---

## Repository

- **Fork:** https://github.com/snadboy/script-server
- **Upstream:** https://github.com/bugy/script-server
- **Local Path:** `/home/snadboy/projects/script-server`

---

## Current State

**Branch:** `feature/venv-management`
**Latest Commit:** (uncommitted) - Add Project Manager feature
**Last Updated:** 2026-01-13
**Docker Image:** `ghcr.io/snadboy/script-server:latest`

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
| Project Manager | Done | Import external Python projects via Git/ZIP; auto-detect dependencies & entry points; generate wrapper scripts |

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

---

## Pending / Suggested Next Steps

1. **Docker Build** - Build a Docker image from the fork for deployment
2. **PR to Upstream** - Consider submitting PR to `bugy/script-server`

---

## Build Commands

```bash
# Frontend build
cd /home/snadboy/projects/script-server/web-src
NODE_OPTIONS=--openssl-legacy-provider npm run build

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
- `web-src/src/main-app/components/MainAppSidebar.vue` (modified - added packages/projects buttons for admins)
- `src/web/server.py` (modified - added venv and project management API endpoints)
- `src/project_manager/__init__.py` (new - project manager module)
- `src/project_manager/project_service.py` (new - project import/management service)
- `web-src/src/main-app/components/ProjectsModal.vue` (new - admin UI for project management)
