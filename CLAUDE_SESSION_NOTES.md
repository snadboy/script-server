# Script Server Fork - Schedule List Feature

## Session Summary (2026-01-02)

### What Was Done

Forked `bugy/script-server` to `snadboy/script-server` and implemented the ability to **view and delete scheduled executions** - functionality that was completely missing from the original project.

### Repository Info
- **Fork URL**: https://github.com/snadboy/script-server
- **Branch**: `feature/schedule-list-and-delete`
- **Local Path**: `/home/snadboy/projects/script-server`

### Files Changed

#### Backend (Python)
| File | Changes |
|------|---------|
| `src/scheduling/schedule_service.py` | Added `get_jobs()`, `get_job()`, `delete_job()` methods + `AccessDeniedException`, `JobNotFoundException` exceptions |
| `src/scheduling/scheduler.py` | Added `_events` dict to track scheduled jobs, added `cancel()` method |
| `src/web/server.py` | Added `GET /schedules` and `DELETE /schedules/{id}` API endpoints (`GetSchedules`, `DeleteSchedule` classes) |

#### Frontend (Vue.js)
| File | Changes |
|------|---------|
| `web-src/src/main-app/components/schedule/ScheduleList.vue` | **NEW** - Component to display existing schedules with delete buttons |
| `web-src/src/main-app/store/scriptSchedule.js` | Added Vuex state (`schedules`, `loading`, `error`), mutations, `fetchSchedules` and `deleteSchedule` actions |
| `web-src/src/main-app/components/schedule/SchedulePanel.vue` | Integrated ScheduleList component, updated styling |

### API Endpoints Added

```
GET /schedules              - List all schedules for current user
GET /schedules?script=NAME  - List schedules for specific script
DELETE /schedules/{id}      - Delete a schedule by ID
```

### Next Steps

1. **Build Docker image** from the fork
2. **Test** the implementation on your Script Server instance
3. Optionally submit a **PR to upstream** (`bugy/script-server`) if you want to contribute back

### Building & Testing

To build a Docker image from the fork:
```bash
cd /home/snadboy/projects/script-server
docker build -t script-server:custom .
```

Or update your docker-compose to use the fork:
```yaml
services:
  script-server:
    build:
      context: https://github.com/snadboy/script-server.git#feature/schedule-list-and-delete
```

### GitHub Token

GitHub PAT was used for this session:
- Token stored at: `~/.config/gh/token`
- Also needs to be added to `/mnt/shareables/.claude/.env` as `GITHUB_TOKEN=ghp_...`

### Related Work

This session also completed:
- Refactored `portainer_backup.py` to save to shareables instead of Google Drive
- Added backup retention (30 days / max 10 backups)
- Deleted the now-unnecessary `gdrive_auth.py`
- Installed script to Script Server on `utilities` host (endpoint 13)

---

## Session Summary (2026-01-08)

### What Was Done

Fixed UI inconsistency between the History and Scheduled page headers. The banners were visually different and needed to match.

### Files Changed

| File | Changes |
|------|---------|
| `web-src/src/main-app/components/scheduled/ScheduledHeader.vue` | Updated to match `AppHistoryHeader.vue` styling - changed `<h5>` to `<h3>`, replaced `scheduled-header primary-color-dark` class with `main-content-header`, shortened title from "Scheduled Executions" to "Scheduled" |

### Details

**Before:**
- History header: Used `main-content-header` class, `<h3>` tag, title "History"
- Schedule header: Used `scheduled-header primary-color-dark` class, `<h5>` tag, title "Scheduled Executions"

**After:**
- Both headers now use identical structure and styling
- Consistent font size (1.3em), height (56px), and text color

### Build Notes

Frontend build requires OpenSSL legacy provider on newer Node.js versions:
```bash
cd /home/snadboy/projects/script-server/web-src
NODE_OPTIONS=--openssl-legacy-provider npm run build
```

### Commit

- `ac2ce81` - Fix Scheduled header banner to match History header styling

---

### Add Script Modal Feature (2026-01-08 continued)

Converted the "Add Script" page into a modal dialog that opens when clicking "Add Script" button in the admin scripts list.

### Files Changed

| File | Changes |
|------|---------|
| `web-src/src/admin/components/scripts-config/AddScriptModal.vue` | **NEW** - Modal component wrapping ScriptConfigForm and ScriptParamList |
| `web-src/src/admin/components/scripts-config/ScriptsList.vue` | Replaced router-link with button that opens modal, added modal component |

### Features

- Modal opens instead of navigating to `/_new` page
- Full form with all sections: Script details, Access, Scheduling, Parameters
- Scrollable modal body taking up 85% of viewport (width and height)
- Dirty state tracking with confirmation prompt on close
- Multiple close methods: Cancel button, X button, Escape key, click outside
- Uses existing Vuex `scriptConfig` module for state management

### Technical Notes

- Admin app has its own Vuex store in `AdminApp.vue` with module name `scriptConfig` (not `adminScriptConfig`)
- Direct URL access to `#/admin/scripts/_new` still works as full page

### Commits

- `b81825b` - Convert Add Script page to modal dialog
- Modal size updated to 85% of viewport for better usability
