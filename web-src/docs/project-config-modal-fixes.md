# Project Config Modal UI Fixes

**Date:** 2026-02-02
**Status:** ✅ Complete

## Issues Fixed

### 1. Dialog Dismissal Behavior ✅
**Issue:** Modal closed when clicking outside of dialog  
**Fix:** Removed `@click.self="close"` from `.modal-overlay` element  
**File:** `ProjectConfigModal.vue` line 2

### 2. Save Button Validation ✅
**Issue:** Save button should only be enabled when there's at least one verb option (on Verbs tab)  
**Fix:** Added `canSave` computed property that validates verb options  
**File:** `ProjectConfigModal.vue`

### 3. White Background Issue ✅
**Issue:** White background behind buttons made Save button hard to see  
**Fix:** Removed `background: var(--footer-background, #f9f9f9)` from footer CSS  
**File:** `ProjectConfigModal.vue`

### 4. Verbs Tab Layout Reordering ✅
**New order:**
1. Enable Verb/Subcommand Support checkbox
2. Verb Options list
3. Verb Configuration (Parameter Name, Default Verb, Verb Required)

### 5. Shared Parameters Removed ✅
**Issue:** Shared Parameters should not be displayed on Verbs tab  
**Fix:** Removed entire section - users assign parameters per verb individually

### 6. Default Verb as Dropdown ✅
**Issue:** Default Verb was text field  
**Fix:** Changed to dropdown with verb options

## Files Modified

- `web-src/src/admin/components/projects/ProjectConfigModal.vue`
- `web-src/src/admin/components/scripts-config/VerbConfigEditor.vue`

## Testing

**Build Status:** ✅ Success
