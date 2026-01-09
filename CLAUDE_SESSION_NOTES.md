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
| `web-src/src/main-app/components/SidebarBottomNav.vue` | Changed "Add Script" nav item from router-link to button that opens modal |

### Features

- Modal opens instead of navigating to `/_new` page
- Works from both `admin.html` and `index.html` entry points
- **Tabbed wizard interface** with 4 tabs:
  1. Details (name, path, description, output format)
  2. Access (allowed users, admin users, shared instances)
  3. Scheduling (enable/disable, auto cleanup)
  4. Parameters
- Centered modal with max-width 1000px, 85% viewport height
- **Modal can only be closed via Cancel or Add buttons** (no X, no escape, no click-outside)
- Dirty state tracking with confirmation prompt on Cancel

### Technical Notes

- Modal dynamically detects which Vuex store module to use:
  - `admin.html` → `scriptConfig` module
  - `index.html` → `adminScriptConfig` module
- Direct URL access to `#/admin/scripts/_new` still works as full page

### Commits

- `b81825b` - Convert Add Script page to modal dialog
- `24dc162` - Increase modal size to 85% of viewport
- `635fa44` - Fix modal to work from main app navigation
- `ddcd23a` - Convert modal to tabbed wizard with 4 tabs (Details, Access, Scheduling, Parameters)

---

### Add Script Modal Improvements (2026-01-08 continued)

Additional improvements to the Add Script modal:

### Files Changed

| File | Changes |
|------|---------|
| `web-src/src/admin/components/scripts-config/AddScriptModal.vue` | Added form validation, disabled Add button until required fields completed, fixed centering (offset for 300px sidebar) |
| `web-src/src/admin/components/scripts-config/ScriptParamList.vue` | Changed "+ Add" to "+ Add Parameter" |

### Details

1. **Add button disabled until form valid**
   - Added `isFormValid` computed property
   - Checks that Script Name and Script Path are filled
   - Button is grayed out and non-clickable until valid

2. **Fixed centering in content area**
   - Modal overlay now starts at `left: 300px` to account for sidebar
   - Centers in the main content area, not the full viewport
   - Media query resets to `left: 0` on screens < 992px where sidebar collapses

3. **Renamed Add Parameter button**
   - Changed from "+ Add" to "+ Add Parameter" in the Parameters tab

---

### Modal Centering Fix & User Management Modal (2026-01-09)

#### Modal Centering Fix

Fixed the vertical centering issue with the Add Script modal on systems with display scaling:

| File | Changes |
|------|---------|
| `web-src/src/admin/components/scripts-config/AddScriptModal.vue` | Added dynamic overlay sizing via JavaScript to fix display scaling issues with `100vh` |

**Details:**
- Added `boundFixOverlayDimensions` to store bound function reference
- On modal open, sets overlay dimensions to `window.innerWidth` x `window.innerHeight` pixels
- Listens for resize events and updates dimensions accordingly
- Properly unbinds event listener when modal closes

#### User Management Modal

Converted the Users page to a modal dialog, matching the Add Script modal treatment:

| File | Changes |
|------|---------|
| `web-src/src/admin/components/UserManagementModal.vue` | **NEW** - Modal component for user management |
| `web-src/src/main-app/components/SidebarBottomNav.vue` | Changed Users from router-link to button that opens modal |

**Features:**
- Displays user list with admin/code editor checkboxes
- Add User nested modal dialog
- Change Password nested modal dialog
- Delete user with confirmation
- Default password warning banner
- Same centering fix as Add Script modal

---

### Modal Teleport Fix (2026-01-09 continued)

Fixed modal centering issue when window is resized to narrow widths. Both Add Script and User Management modals were breaking because they were rendered inside the sidebar which has a CSS transform when collapsed.

#### Root Cause

The `.app-sidebar` element uses `transform: matrix(1, 0, 0, 1, -315, 0)` when collapsed, which creates a new containing block for `position: fixed` elements. This caused modals inside the sidebar to be positioned relative to the transformed sidebar rather than the viewport.

#### Solution

Teleport modal elements to the document body when opened, and move them back to their original parent when closed.

| File | Changes |
|------|---------|
| `web-src/src/admin/components/scripts-config/AddScriptModal.vue` | Added `originalParent` to data, teleport to body on open, restore on close |
| `web-src/src/admin/components/UserManagementModal.vue` | Same teleport fix |

**Key code changes:**
```javascript
// On modal open
this.$nextTick(() => {
  this.originalParent = this.$el.parentElement;
  document.body.appendChild(this.$el);
  // ... dimension fixes
});

// On modal close
if (this.originalParent && this.$el.parentElement === document.body) {
  this.originalParent.appendChild(this.$el);
}
```

#### Verification

- Modal overlay now has `parentElement: BODY` instead of being nested in sidebar
- Modal stays centered at all viewport widths
- Overlay covers full viewport including sidebar area

---

### Schedule Modal Refactor (2026-01-09 continued)

Moved the SCHEDULE button from the right-hand script view to the left sidebar (next to the edit button), and converted the Schedule Dialog into a proper modal like AddScriptModal and UserManagementModal.

#### Files Created

| File | Description |
|------|-------------|
| `web-src/src/main-app/components/schedule/ScheduleModal.vue` | New modal wrapper for scheduling with teleport-to-body pattern |

#### Files Modified

| File | Changes |
|------|---------|
| `web-src/src/main-app/components/scripts/ScriptInlineActions.vue` | Added schedule button with `date_range` icon, integrated ScheduleModal |
| `web-src/src/main-app/components/scripts/script-view.vue` | Removed SCHEDULE button, actions-panel, and ScriptViewScheduleHolder |

#### Files Deleted

| File | Reason |
|------|--------|
| `web-src/src/main-app/components/scripts/ScriptViewScheduleHolder.vue` | No longer needed - replaced by ScheduleModal |
| `web-src/src/main-app/components/scripts/ScheduleButton.vue` | No longer needed - button now inline in ScriptInlineActions |
| `web-src/src/main-app/components/schedule/SchedulePanel.vue` | Content merged into ScheduleModal |

#### Button Layout

The sidebar inline actions now show: `[Play] [Stop] [Schedule] [Edit]`

- Schedule button only appears for schedulable scripts
- Uses same styling as edit button (surface background, border)
- Opens centered modal with schedule creation form

#### Modal Features

- Teleports to document.body to avoid sidebar transform issues
- Flexbox centering with display scaling fix
- Shows existing schedules + create new schedule form
- Parameters table, one-time vs repeat options
- Cancel/Schedule footer buttons

---

### Execute/Stop Button Merge (2026-01-09 continued)

Merged the execute and stop buttons into a single button that changes behavior based on execution state, and updated styling to match the schedule/edit buttons.

#### Changes

| File | Changes |
|------|---------|
| `web-src/src/main-app/components/scripts/ScriptInlineActions.vue` | Merged execute/stop into single button, updated styling |

#### Button Behavior

- **Not executing**: Shows `play_arrow` icon, executes script on click
- **Executing**: Shows `stop` icon, stops script on click
- **Kill mode**: Shows `dangerous` icon with red background, kills script on click
- **Kill countdown**: Shows timeout badge with seconds remaining

#### Button Layout

The sidebar inline actions now show: `[Execute/Stop] [Schedule] [Edit]`

All buttons now have consistent styling:
- Surface background color
- 1px border with separator color
- Hover effect changes to primary color

---

### Schedule Enhancements & Stop Buttons (2026-01-09 continued)

Three enhancements to scheduling and running script management:

#### 1. Schedule Modal Stays Open After Scheduling

After creating a schedule, the modal now resets the form instead of closing, allowing users to create multiple schedules without reopening the modal.

| File | Changes |
|------|---------|
| `web-src/src/main-app/components/schedule/ScheduleModal.vue` | Added `resetScheduleFields()` method, `refreshScheduleList()` method, changed `runScheduleAction()` to reset instead of close |

#### 2. Description Field for Schedules

Added an optional description field to scheduled executions for better identification.

**Frontend Changes:**

| File | Changes |
|------|---------|
| `web-src/src/main-app/components/schedule/ScheduleModal.vue` | Added description input field, included in `buildScheduleSetup()` and form reset |
| `web-src/src/main-app/components/schedule/ScheduleList.vue` | Display description in schedule cards |
| `web-src/src/main-app/components/scheduled/ScheduledPage.vue` | Display description in schedule cards |

**Backend Changes:**

| File | Changes |
|------|---------|
| `src/scheduling/scheduling_job.py` | Added `description` parameter to `SchedulingJob.__init__()`, included in `as_serializable_dict()`, loaded in `from_dict()` |
| `src/model/external_model.py` | Added `description` to `parse_external_schedule()` |
| `src/scheduling/schedule_service.py` | Extract description from config and pass to `SchedulingJob` |

#### 3. Stop Buttons for Running Scripts

Added stop/kill buttons to running execution cards on History and Scheduled pages.

| File | Changes |
|------|---------|
| `web-src/src/main-app/components/history/AppHistoryPanel.vue` | Added stop button to running cards with kill countdown timer |
| `web-src/src/main-app/components/scheduled/ScheduledPage.vue` | Added stop button to running cards with kill countdown timer |

**Stop Button Behavior:**
- First click: Sends stop signal, starts 5-second countdown
- During countdown: Shows timeout badge with seconds remaining
- After countdown: Button changes to "kill mode" (red background, dangerous icon)
- Kill mode click: Sends kill signal to forcefully terminate script
- Auto-clears when script stops running
