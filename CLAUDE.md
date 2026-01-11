# Script Server Fork - Project Context

> **Important:** Keep this file updated throughout each session. When completing significant work (features, bug fixes, refactors), update the relevant sections immediately so context is preserved for future sessions.

---

## Repository

- **Fork:** https://github.com/snadboy/script-server
- **Upstream:** https://github.com/bugy/script-server
- **Local Path:** `/home/snadboy/projects/script-server`

---

## Current State

**Branch:** `feature/schedule-list-and-delete`
**Latest Commit:** `34d7c08` - Add enable/disable toggle for recurring schedules
**Last Updated:** 2026-01-11
**Status:** ✅ All features tested and verified working

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

### Test Infrastructure

| Item | Location | Description |
|------|----------|-------------|
| Long Running Script | `samples/scripts/long_running.py` | 30-second test script with progress bar |
| Script Config | `conf/runners/long_running.json` | Config with scheduling enabled (gitignored) |

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
- `src/scheduling/schedule_service.py` (modified - passes schedule_id when executing jobs)
- `src/scheduling/schedule_config.py` (modified - added get_last_execution_time method)
- `src/execution/execution_service.py` (modified - added schedule_id tracking to executions)
- `src/execution/logging.py` (modified - added schedule_id to logs and history)
- `src/web/server.py` (modified - added last_execution to schedule API response)
- `src/model/external_model.py` (modified - added scheduleId to API response)
- `web-src/src/main-app/components/MainAppSidebar.vue` (modified - moved version to bottom)
- `web-src/src/admin/store/script-config-module.js` (modified - improved error handling for save/delete)
- `src/web/server.py` (modified - fixed HTTPError reason parameter, added schedule enable toggle API)
- `web-src/src/main-app/components/SettingsModal.vue` (new - settings dialog)
- `web-src/src/main-app/store/settings.js` (new - settings state with localStorage persistence)
