# Script-Server UI/UX Refresh - Session Notes

## Branch
`feature/schedule-list-and-delete`

## Latest Commit
`051cc87` - Fix Scheduled page to match History appearance

## Overview
Working on a UI/UX refresh for script-server web interface. The main focus has been on:
1. Adding a new **Scheduled** page/tab to the navigation
2. Making History and Scheduled pages visually consistent

## Completed Work

### Navigation Changes
- Moved sidebar nav (History, Scheduled, Add Script, Users) above the scripts list
- Added new "Scheduled" tab between History and Add Script

### New Scheduled Page (`/scheduled`)
- Shows **Running** section (scripts currently executing)
- Shows **Scheduled** section (all scheduled scripts across all scripts)
- Search functionality filters scheduled items by script name or user
- Cards display: script name, next run time, repeat info, user
- Delete button to remove scheduled executions
- Parameters expandable panel

### Files Created
- `src/main-app/components/scheduled/ScheduledPage.vue` - Main scheduled page component
- `src/main-app/components/scheduled/ScheduledHeader.vue` - Header component
- `src/main-app/store/allSchedules.js` - Vuex store module for fetching all schedules

### Files Modified
- `src/main-app/router/router.js` - Added `/scheduled` route
- `src/main-app/store/index.js` - Registered allSchedules module
- `src/main-app/components/SidebarBottomNav.vue` - Added Scheduled nav item
- `src/main-app/components/MainAppSidebar.vue` - Moved nav above scripts
- `src/main-app/components/history/AppHistoryPanel.vue` - Added Running section
- `src/common/components/history/executions-log-table.vue` - Converted to card layout

### Visual Consistency Work
Made Scheduled page match History page:
- Same section title styling (h6, 14px font, 20px icons)
- Same card styling (padding, gaps, font sizes, shadows)
- Same layout structure (Running section, then main section with search inside)
- Same empty state styling
- Removed sort dropdown (History doesn't have one)
- Fixed User field to show username instead of raw JSON object

## Current State
Both History and Scheduled pages should now look visually identical in structure:
- Running section at top
- Main section (Completed/Scheduled) with search bar inside
- Card-based layout for items

## Testing
Test on `http://localhost:5000` (script-server must be running)

## Known Issues / Pending
- User was checking if banners match between History and Scheduled
- Last test showed User field was displaying JSON - this was fixed in latest commit

## Key Design Decisions
1. Search only filters the main section (Completed/Scheduled), not the Running section
2. No sort dropdown on Scheduled (matches History's simpler layout)
3. Schedules sorted by next execution time (soonest first)
4. User field extracts username from audit object structure

## Related Plan File
Full UI/UX plan available at: `~/.claude/plans/hashed-sprouting-rainbow.md`
