# Scheduling Features

## Overview

Enhanced scheduling capabilities including schedule management UI, auto-cleanup of one-time schedules, enable/disable toggles, and schedule editing.

## Features

### 1. One-time Schedule Auto-Cleanup (2026-01-20)

**Status:** ✅ Complete - Merged to master

**Features:**
- Completion time tracking for non-recurring schedules
- Configurable retention period (default: 60 minutes)
- Background cleanup runs every 5 minutes + on startup
- Visual distinction for expired schedules
- Admin-configurable retention via Settings modal

#### Backend Changes

**ScheduleService** (`src/scheduling/schedule_service.py`):
- `completion_time` field added to non-recurring schedules
- `_cleanup_expired_schedules()` - Deletes expired schedules
- `_schedule_is_expired()` - Checks if schedule should be deleted
- `_calculate_auto_delete_time()` - Calculates deletion time
- Background cleanup task runs every 5 minutes
- `get_retention_minutes()` / `set_retention_minutes()` - Configuration methods

**ScheduleConfig** (`src/scheduling/schedule_config.py`):
- Added `completion_time` field for tracking when schedule finished

**ServerConf** (`src/model/server_conf.py`):
- Added `onetime_schedule_retention_minutes` config (default: 60)

**API** (`src/web/server.py`):
- `GET /schedules` includes `expired` and `auto_delete_at` fields
- `GET /schedules/settings` - Get retention config
- `PUT /schedules/settings` - Update retention config

#### Frontend Changes

**ScheduleCard.vue:**
- Green "Completed" badge for finished schedules
- Reduced opacity (0.5) for expired schedules
- Auto-delete countdown shown in description

**SettingsModal.vue:**
- "Completed Schedule Retention" setting (admin only)
- Options: 0 (immediate), 15, 30, 60, 120, 240 minutes, -1 (never)
- Real-time updates via API

#### Retention Options

| Setting | Behavior |
|---------|----------|
| 0 | Delete immediately after completion |
| 15-240 | Delete N minutes after completion |
| -1 | Never auto-delete (manual cleanup only) |

#### Commits

- `b476b53` - Add auto-cleanup of non-recurring scheduled tasks
- `bcf1371` - Add retention setting to Settings Modal (admin only)
- `7ee892e` - Fix: Use auth store for admin check in SettingsModal
- `5dffc67` - Fix: Override Materialize red validation border
- `b018d7b` - Fix: Force override Materialize input border styles
- `72ee089` - Fix: Clean up legacy one-time schedules without completion_time

---

### 2. Schedule Enable/Disable Toggle

**Status:** ✅ Complete

**Features:**
- Toggle button on schedule rows in Running/Scheduled sections
- Checkbox in Schedule modal for recurring schedules
- API endpoint for enable/disable
- Visual distinction for disabled schedules

**API:**
- `PUT /schedules/{id}/enabled` - Enable/disable schedule

**UI:**
- Toggle button (green = enabled, gray = disabled)
- Checkbox in ScheduleModal "Enable this schedule"

---

### 3. Schedule Editing (2026-01-18)

**Status:** ✅ Complete

**Features:**
- Edit button on schedule cards
- Opens ScheduleModal in edit mode
- Preserves existing schedule data
- Combined DELETE + PUT into single handler

**Backend:**
- `PUT /schedules/{id}` endpoint
- `update_job()` method in ScheduleService
- Parses camelCase to snake_case for compatibility

**Frontend:**
- Edit button on ScheduleCard components
- ScheduleModal accepts `editMode` and `existingSchedule` props
- Pre-fills form with existing schedule data

**Bug fixes:**
- `cd86463` - Fix schedule edit: parse camelCase to snake_case
- `f6bdf74` - Fix schedule edit: combine DELETE and PUT into single handler

---

### 4. Schedule Modal (Original)

**Status:** ✅ Complete

**Features:**
- Replaced inline scheduling panel with modal dialog
- Optional description field
- Multi-schedule support (modal stays open after scheduling)
- Simplified UX (removed schedule list from dialog)

**ScheduleModal.vue:**
- One-time vs Recurring selection
- Date/time picker for one-time schedules
- Cron expression builder for recurring schedules
- Description field (optional)
- "Schedule & Close" vs "Schedule & Add Another" buttons

---

### 5. Schedule List API

**Status:** ✅ Complete

**Features:**
- `GET /schedules` - List all schedules with metadata
- `DELETE /schedules/{id}` - Delete schedule by ID
- Includes last execution time for recurring schedules
- Schedule ID tracking in executions

**Response fields:**
- `id` - Schedule ID
- `scriptName` - Script name
- `nextRun` - Next execution time
- `recurring` - Boolean
- `cronExpression` - Cron expression (recurring only)
- `description` - Optional description
- `enabled` - Enable/disable state
- `lastRun` - Last execution time
- `expired` - Whether schedule should be deleted
- `autoDeleteAt` - When schedule will be auto-deleted

---

### 6. Schedule Tracking in Executions

**Status:** ✅ Complete

**Features:**
- `schedule_id` tracked in execution logs
- Purple "Scheduled" badge on running/completed executions
- Distinguishes scheduled vs manual executions

**Backend:**
- ExecutionService tracks `schedule_id`
- Logging module writes `schedule_id` to logs
- API includes `scheduleId` in responses

**Frontend:**
- Purple badge for scheduled executions
- Badge shows in Running and Completed sections

---

## Files Modified

**Backend:**
- `src/scheduling/schedule_config.py`
- `src/scheduling/schedule_service.py`
- `src/scheduling/scheduling_job.py`
- `src/execution/execution_service.py`
- `src/execution/logging.py`
- `src/model/server_conf.py`
- `src/model/external_model.py`
- `src/web/server.py`

**Frontend:**
- `web-src/src/main-app/components/schedule/ScheduleModal.vue` (new)
- `web-src/src/main-app/components/common/ScheduleCard.vue` (new)
- `web-src/src/main-app/components/SettingsModal.vue`
- `web-src/src/main-app/store/allSchedules.js`
- `web-src/src/main-app/store/scriptSchedule.js`
- `web-src/src/main-app/store/settings.js`

---

## Testing

- ✅ One-time schedules auto-delete after retention period
- ✅ Recurring schedules never auto-delete
- ✅ Admin can configure retention in Settings
- ✅ Schedule enable/disable toggle works
- ✅ Schedule editing preserves data correctly
- ✅ Scheduled executions show purple badge
- ✅ Last run time displays correctly

## Benefits

- **Automatic Cleanup:** No manual cleanup of completed schedules
- **Flexible Retention:** Configure per deployment needs
- **Visual Feedback:** Clear indication of expired/disabled schedules
- **Edit Support:** Modify schedules without recreating
- **Better Tracking:** Distinguish scheduled vs manual executions
