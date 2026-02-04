# UI/UX Improvements

## Overview

Comprehensive UI/UX redesign to unify experience across the application, including unified activity page, modal dialogs, consistent styling, and improved information display.

## Major Features

### 1. Unified Activity Page

**Status:** ✅ Complete

**Replaced separate History and Scheduled pages with single unified Activity view.**

**Sections:**
- **Running** - Currently executing scripts (auto-refreshes)
- **Scheduled** - Upcoming scheduled executions
- **Completed** - Execution history

**Features:**
- Collapsible sections with localStorage persistence
- Live updates when executions start/complete
- Consistent execution cards across all sections
- Purple "Scheduled" badge for schedule-triggered executions

**Components created:**
- `ActivityPage.vue` - Main unified activity view
- `ActivityHeader.vue` - Page header matching script view
- `CollapsibleSection.vue` - Reusable collapsible section base
- `ExecutionCard.vue` - Reusable execution card base
- `RunningSection.vue` - Unified running executions section
- `ScheduledSection.vue` - Unified scheduled executions section
- `CompletedSection.vue` - Unified completed executions section

---

### 2. Modal Dialogs

**Status:** ✅ Complete

**Replaced inline panels with modal dialogs for better UX.**

#### Execute Modal

**ExecuteModal.vue:**
- Modal dialog for script execution
- Instance name input (optional)
- Parameter configuration
- Verb selection (if applicable)
- Parameter filtering by verb

#### Edit Script Modal

**EditScriptModal.vue:**
- Tabbed wizard matching Add Script UX
- Tabs: Details, Parameters, Advanced
- Consistent styling with CreateScriptModal
- Real-time validation

#### Schedule Modal

**ScheduleModal.vue:**
- Modal for creating/editing schedules
- One-time vs Recurring selection
- Date/time picker for one-time
- Cron expression builder for recurring
- Optional description field
- Multi-schedule support (stays open after scheduling)

#### User Management Modal

**Status:** ✅ Complete

Modal dialog for user administration.

#### Settings Modal

**SettingsModal.vue:**
- Configurable completed executions limit
- Configurable completed schedule retention
- Log size limit setting
- Admin-only settings (retention, etc.)

---

### 3. Unified Script Manager

**Status:** ✅ Complete

**Consolidated Create Script and Manage Projects into single "Script Manager" button.**

**ProjectsModal.vue:**
- 3-tab interface: Projects, Import, Configure
- Projects tab - View and delete imported projects
- Import tab - Import Python projects via Git/ZIP/Local
- Configure tab - Dependency & entry point configuration (removed Create tab in import-only architecture)

**MainAppSidebar.vue:**
- Single "Script Manager" button (description icon)
- Removed separate "Create Script" and "Manage Projects" buttons

---

### 4. Consistent Card Layout

**Status:** ✅ Complete

**Standardized execution and schedule card layouts.**

**Features:**
- Badges on left (status, schedule, etc.)
- Script name + execution ID title format
- Script description display
- Instance name display (when present)
- Schedule timing information
- Consistent date/time format (M/D/YYYY @ HH:MM)
- Action buttons on right

**Badge visibility:**
- Increased opacity to 0.35 for better visibility
- Color-coded: green (completed), blue (running), purple (scheduled)

---

### 5. Stop/Kill Buttons

**Status:** ✅ Complete

**Reusable stop button component with state-based behavior.**

**StopButton.vue:**
- Shows "Stop" (SIGTERM) initially
- Shows "Kill" (SIGKILL) after stop clicked
- Visual feedback during operation
- Used in History, Scheduled, and Running sections

**Execute/Stop Button Merge:**
- Single button on script view
- "Execute" when script not running
- "Stop"/"Kill" when script is running
- State-based behavior

---

### 6. Execution Tracking Improvements

**Status:** ✅ Complete

**Enhanced execution information display.**

#### Instance Name Tracking
- Optional instance name for executions
- Stored in logs
- Displayed in Running/Completed sections
- Helps distinguish multiple executions

#### Finish Time Tracking
- Tracks `finish_time` in logs
- Shows "Started" and "Completed" times on cards
- Duration calculation

#### Script/Instance Descriptions
- All cards show script description
- Instance name displayed when present
- Uses computed `scriptsMap` for reactivity
- `/scripts` API includes description field

---

### 7. Live Updates

**Status:** ✅ Complete

**Auto-refresh of execution lists when state changes.**

**Implementation:**
- Watcher in main store for execution state changes
- Refreshes Running, Scheduled, and Completed lists
- Updates schedule last run times
- Cross-store communication (scriptSchedule → allSchedules)

---

### 8. Collapsed State Persistence

**Status:** ✅ Complete

**Remember section collapsed/expanded state across sessions.**

- Uses localStorage to persist state
- Keys: `runningSection.collapsed`, `scheduledSection.collapsed`, `completedSection.collapsed`
- Applies to both Activity page and Script view

---

### 9. Consistent Title Format

**Status:** ✅ Complete

**Unified title format across all execution cards:**

**Format:** `ScriptName (Execution ID: nnn)`

**Applied to:**
- Running section cards
- Completed section cards
- History page entries
- Log viewer titles

---

### 10. Settings Modal Features

**Status:** ✅ Complete

**Configurable limits and retention settings.**

**Settings:**
- **Completed Executions Limit** - How many completed executions to show (5-50, default 20)
- **Log Size Limit** - How many execution history entries to fetch (10-250, default 170)
- **Completed Schedule Retention** - How long to keep one-time schedules after completion (admin only)

**Storage:**
- Client-side settings stored in localStorage
- Server-side settings managed via API
- Instant updates without page reload

---

### 11. Sidebar Improvements

**Status:** ✅ Complete

**Icon consistency and version placement.**

#### Version Move
- Moved version/build number to bottom of sidebar
- Keeps main nav area clean
- Shows on hover in corner

#### Icon Alignment
- Fixed nav icon alignment issues
- Override global min-height CSS
- Consistent 24px icon size

#### Icon Visibility Fix (2026-01-31)
- Fixed admin buttons appearing invisible
- Changed Python Packages icon: `storage` → `extension` (puzzle piece 🧩)
- Changed Requirements icon: `list_alt` → `assignment` (clipboard 📋)
- Final icon set:
  - Script Manager: `description` (document 📄)
  - Python Packages: `extension` (puzzle piece 🧩)
  - Requirements: `assignment` (clipboard 📋)
  - Server Logs: `subject` (lines ☰)
  - Settings: `settings` (gear ⚙️)

---

### 12. Header Consistency

**Status:** ✅ Complete

**Unified header format across pages.**

- History page header matches script view
- Scheduled page header matches script view
- Activity page header consistent
- Same styling, spacing, and action buttons

---

### 13. History Section Fix

**Status:** ✅ Complete

**Running tasks excluded from Completed section.**

- Completed section only shows finished executions
- Running executions shown in Running section
- No duplicate entries

---

### 14. Error Message Display

**Status:** ✅ Complete

**Backend errors now show actual message.**

- Admin script config module improved error handling
- Shows specific error from server instead of generic "Failed to save"
- Better debugging for users

---

### 15. UI/UX Consistency

**Status:** ✅ Complete

**Standardized styling across application.**

**CSS Variables:**
- `--status-running-bg` - Blue background for running
- `--status-completed-bg` - Green background for completed
- `--status-scheduled-bg` - Purple background for scheduled
- `--stop-btn-bg` / `--stop-btn-hover-bg` - Stop button colors
- `--kill-btn-bg` / `--kill-btn-hover-bg` - Kill button colors
- `--border-radius` - Consistent border radius
- `--box-shadow` - Consistent shadows
- `--transition-duration` - Consistent transitions

**Applied to:**
- `samples/themes/dark/theme.css`
- `samples/themes/orange/theme.css`

---

## Technical Notes

### Materialize CSS Quirks

**Select opacity issue:**
- Framework sets `select { opacity: 0 }` globally
- Custom modals using native `<select>` must override with `opacity: 1`
- Must also set `appearance: menulist` for native styling

**Input border override:**
- Materialize forces red borders on validation
- Required `!important` to override in custom modals
- Applied to Settings modal inputs

---

## Files Created

**Activity Page:**
- `web-src/src/main-app/components/activity/ActivityPage.vue`
- `web-src/src/main-app/components/activity/ActivityHeader.vue`
- `web-src/src/main-app/components/common/CollapsibleSection.vue`
- `web-src/src/main-app/components/common/ExecutionCard.vue`
- `web-src/src/main-app/components/common/StopButton.vue`
- `web-src/src/main-app/components/common/RunningSection.vue`
- `web-src/src/main-app/components/common/ScheduledSection.vue`
- `web-src/src/main-app/components/common/CompletedSection.vue`
- `web-src/src/main-app/components/common/ScheduleCard.vue`
- `web-src/src/main-app/utils/executionFormatters.js`

**Modals:**
- `web-src/src/main-app/components/scripts/ExecuteModal.vue`
- `web-src/src/main-app/components/scripts/EditScriptModal.vue`
- `web-src/src/main-app/components/schedule/ScheduleModal.vue`
- `web-src/src/main-app/components/SettingsModal.vue`

**Unified Script Manager:**
- `web-src/src/main-app/components/ProjectsModal.vue`

---

## Files Modified

**Sidebar:**
- `web-src/src/main-app/components/MainAppSidebar.vue`
- `web-src/src/main-app/components/SidebarBottomNav.vue`

**Script View:**
- `web-src/src/main-app/components/scripts/script-view.vue`
- `web-src/src/main-app/components/scripts/ScriptInlineActions.vue`
- `web-src/src/main-app/components/scripts/ScriptExecutionsPanel.vue`

**Store:**
- `web-src/src/main-app/store/index.js`
- `web-src/src/main-app/store/allSchedules.js`
- `web-src/src/main-app/store/scriptSchedule.js`
- `web-src/src/main-app/store/settings.js`
- `web-src/src/common/store/executions-module.js`
- `web-src/src/admin/store/script-config-module.js`

**Router:**
- `web-src/src/main-app/router/router.js`

**Themes:**
- `samples/themes/dark/theme.css`
- `samples/themes/orange/theme.css`

---

## Testing

- ✅ All modals render correctly
- ✅ Section collapse state persists
- ✅ Live updates working
- ✅ Consistent card layouts
- ✅ Stop/Kill buttons functional
- ✅ Settings save and load correctly
- ✅ Icons visible and aligned
- ✅ Headers consistent across pages

## Benefits

- **Unified Experience** - Consistent UI patterns throughout
- **Better Information Display** - More context on each execution
- **Improved Navigation** - Single unified activity view
- **Persistent Preferences** - Remember user choices
- **Live Updates** - Real-time status without refresh
- **Better Error Messages** - Actual server errors shown
- **Cleaner UI** - Modal dialogs instead of inline panels
