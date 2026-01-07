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
