# Project-Level Parameters - Manual Testing Guide

**Server:** http://localhost:5000
**Status:** ✅ Server Running
**Test Project:** gmail-trim-3 (already configured with parameters and verbs)

---

## Pre-Test Verification

### 1. Check Server Status
```bash
# Server should be running on port 5000
curl -s http://localhost:5000 | grep -q "script-server" && echo "✅ Server running" || echo "❌ Server not running"
```

### 2. Verify Test Data Exists
```bash
# Check that gmail-trim-3 project has parameters configured
cat projects/gmail-trim-3/.project-meta.json | grep -q '"parameters"' && echo "✅ Parameters configured" || echo "❌ No parameters"
```

---

## Test Suite 1: Project Configuration UI

### Test 1.1: Open Project Configuration Modal

**Steps:**
1. Open browser to http://localhost:5000
2. Click **"Script Manager"** button in sidebar (description icon)
3. Click **"Projects"** tab
4. Click on **"Gmail Trim"** project row
5. Click **"Configure"** tab
6. Click **"Configure Parameters & Verbs"** button

**Expected Result:**
- ✅ ProjectConfigModal opens
- ✅ Shows "Configure Project: Gmail Trim" title
- ✅ Has two tabs: "Parameters" and "Verbs"
- ✅ Parameters tab is active by default

### Test 1.2: View Existing Parameters

**Steps:**
1. In ProjectConfigModal, verify Parameters tab is selected
2. Observe the parameter list

**Expected Result:**
- ✅ Shows 4 parameters:
  - `days` (int) - Number of days to keep emails
  - `dry_run` (bool) - Preview deletions without deleting
  - `verbose` (bool) - Enable verbose debug logging
  - `config` (text) - Path to YAML config file
- ✅ Each parameter shows type, description, default value
- ✅ Can see up/down arrows for reordering
- ✅ Can see delete button (trash icon)

### Test 1.3: Add New Parameter

**Steps:**
1. Click **"Add Parameter"** button
2. Fill in new parameter:
   - Name: `test_param`
   - Type: `int`
   - Description: `Test parameter for verification`
   - Param: `--test`
   - Default: `42`
   - Min: `1`
   - Max: `100`
3. Click **"Save Configuration"** button

**Expected Result:**
- ✅ Success message appears
- ✅ Modal closes after ~1.5 seconds
- ✅ No errors in browser console

### Test 1.4: Verify Parameter Persistence

**Steps:**
1. Click **"Configure Parameters & Verbs"** button again
2. Check if `test_param` still exists

**Expected Result:**
- ✅ `test_param` appears in parameter list
- ✅ All properties are preserved

**Backend Verification:**
```bash
cat projects/gmail-trim-3/.project-meta.json | grep -A5 '"test_param"'
```

### Test 1.5: Edit Parameter

**Steps:**
1. In ProjectConfigModal, find `test_param`
2. Change default value from `42` to `50`
3. Save configuration

**Expected Result:**
- ✅ Changes saved successfully
- ✅ Reloading shows updated value

### Test 1.6: Delete Parameter

**Steps:**
1. Click delete button (trash icon) on `test_param`
2. Confirm deletion in dialog
3. Save configuration

**Expected Result:**
- ✅ Parameter removed from list
- ✅ Changes persist after reload

### Test 1.7: View Verbs Tab

**Steps:**
1. In ProjectConfigModal, click **"Verbs"** tab

**Expected Result:**
- ✅ Shows VerbConfigEditor component
- ✅ Shows existing verbs:
  - run (Run Cleanup)
  - auth (Authenticate)
  - labels (List Labels)
  - groups (List Groups)
  - config (Show Config)
- ✅ Can edit verb configuration
- ✅ Can see parameter associations

---

## Test Suite 2: Instance Configuration UI

### Test 2.1: Create New Script Instance

**Steps:**
1. Close ProjectConfigModal
2. Click **"Script Manager"** in sidebar
3. Click **"Import"** tab
4. Select **"Local Path"**
5. Enter path: `/home/snadboy/projects/gmail-trim` (or use the existing gmail-trim-3)
6. Click **"Import"**
7. After import, click gear icon on gmail-trim-3 project
8. Observe the Configure panel

**Expected Result:**
- ✅ Configure panel shows Dependencies section
- ✅ Shows Entry Point selection
- ✅ Shows **"Instance Configuration"** section with blue border
- ✅ Instance Configuration section shows:
  - Info message about selecting parameters
  - Verb/Command dropdown
  - Parameters section

### Test 2.2: Select Verb

**Steps:**
1. In Instance Configuration section
2. Find "Command/Verb" dropdown
3. Select **"Run Cleanup"**

**Expected Result:**
- ✅ Dropdown shows all 5 verbs
- ✅ Shows description below dropdown: "Execute email cleanup process"
- ✅ Parameters list updates to show verb-specific parameters:
  - days
  - dry_run
  - config
  - verbose (shared parameter)

### Test 2.3: Select Parameters

**Steps:**
1. Click **"Select All"** button
2. Observe parameter selection
3. Click **"Deselect All"** button
4. Manually check:
   - ☑ days
   - ☑ dry_run
   - ☑ verbose

**Expected Result:**
- ✅ Select All checks all 4 parameters
- ✅ Deselect All unchecks all parameters
- ✅ Manual selection works for individual parameters
- ✅ When parameter is checked, value override section appears below it

### Test 2.4: Override Parameter Values

**Steps:**
1. For `days` parameter (checked):
   - Observe default hint: "(default: 30)"
   - Enter value: `14`
2. For `dry_run` parameter (checked):
   - Observe checkbox with label "Enabled"
   - Check the checkbox (set to true)
3. For `verbose` parameter (checked):
   - Leave checkbox unchecked (false)

**Expected Result:**
- ✅ Integer input shows for `days` with min/max constraints
- ✅ Checkbox shows for boolean parameters
- ✅ Default values shown as hints
- ✅ Can override values

### Test 2.5: Create Script Instance

**Steps:**
1. Fill in Script Name: `Gmail Trim - Test 14 Days`
2. Fill in Description: `Test instance with 14-day retention`
3. Click **"Create Script"** or equivalent button
4. Wait for success message

**Expected Result:**
- ✅ Script created successfully
- ✅ Success message appears
- ✅ Modal closes
- ✅ New script appears in sidebar under "Gmail Automation" group

**Backend Verification:**
```bash
# Check that instance config was created correctly
cat "conf/runners/Gmail Trim - Test 14 Days.json"
```

**Expected Config Structure:**
```json
{
  "name": "Gmail Trim - Test 14 Days",
  "project_id": "gmail-trim-3",
  "instance_config": {
    "included_parameters": ["days", "dry_run", "verbose"],
    "parameter_values": {
      "days": 14
    },
    "selected_verb": "run"
  },
  "script_path": "...",
  "working_directory": "projects/gmail-trim-3",
  "description": "Test instance with 14-day retention",
  "group": "Gmail Automation"
}
```

### Test 2.6: Verb Filtering

**Steps:**
1. Start creating another instance
2. Select verb: **"List Labels"**
3. Observe available parameters

**Expected Result:**
- ✅ Only shows parameters for "labels" verb:
  - verbose (from verb parameters)
- ✅ Does NOT show:
  - days (not in labels verb)
  - dry_run (not in labels verb)
  - config (not in labels verb)

### Test 2.7: Create Instance with Different Verb

**Steps:**
1. Verb: "List Labels"
2. Check: ☑ verbose
3. Script Name: `Gmail Labels Lister`
4. Create script

**Expected Result:**
- ✅ Script created with only verbose parameter
- ✅ selected_verb is "labels" in config file

---

## Test Suite 3: Script Execution (Integration Test)

### Test 3.1: Execute Test Instance

**Steps:**
1. In sidebar, find **"Gmail Trim - Test 14 Days"** script
2. Click to open script view
3. Click **"Execute"** button
4. Observe parameters shown

**Expected Result:**
- ✅ Only shows 3 parameters:
  - command (set to "run")
  - days (default 14)
  - dry_run (default true)
  - verbose (default false)
- ✅ Does NOT show `config` parameter (not included in instance)

### Test 3.2: Verify Command Construction

**Steps:**
1. Execute the script
2. View the execution output/command

**Expected Result:**
- ✅ Command includes:
  - `run` (verb)
  - `--days 14` (overridden value)
  - `--dry-run` (flag)
  - Does NOT include --verbose (false/not set)

---

## Test Suite 4: Configuration Stats

### Test 4.1: Verify Parameter/Verb Counts

**Steps:**
1. Go to Script Manager → Projects tab
2. Click on gmail-trim-3
3. Click Configure tab
4. Observe "Project Configuration" section

**Expected Result:**
- ✅ Shows stat badges:
  - "4 Parameters" (or 5 if test_param still exists)
  - "5 Verbs"
- ✅ Clicking "Configure Parameters & Verbs" opens modal

---

## Test Suite 5: Error Handling

### Test 5.1: Required Verb

**Steps:**
1. Create new instance
2. Leave verb unselected (if verb is required)
3. Try to create script

**Expected Result:**
- ✅ Shows validation error if verb is required
- ✅ Cannot create script without required verb

### Test 5.2: Unsaved Changes

**Steps:**
1. Open ProjectConfigModal
2. Add a parameter
3. Click "Cancel" or X button
4. Observe confirmation dialog

**Expected Result:**
- ✅ Shows confirmation: "You have unsaved changes. Are you sure you want to close?"
- ✅ Can cancel the close action
- ✅ Can confirm and lose changes

---

## Test Suite 6: Legacy Compatibility

### Test 6.1: Legacy Script Still Works

**Steps:**
1. Find a script without project_id (legacy format)
2. Click to view script
3. Execute script

**Expected Result:**
- ✅ Script loads normally
- ✅ Shows parameters as before
- ✅ Executes successfully
- ✅ No errors related to missing project_id

---

## Checklist Summary

### Project Configuration UI
- [ ] ProjectConfigModal opens correctly
- [ ] Can view existing parameters
- [ ] Can add new parameter
- [ ] Changes persist after save
- [ ] Can edit parameter properties
- [ ] Can delete parameter
- [ ] Verbs tab shows correctly
- [ ] Can modify verb configuration

### Instance Configuration UI
- [ ] Instance Configuration section appears
- [ ] Verb dropdown works
- [ ] Verb selection filters parameters
- [ ] Select All/Deselect All works
- [ ] Individual parameter selection works
- [ ] Value override inputs appear
- [ ] Boolean parameter shows checkbox
- [ ] Integer parameter shows number input
- [ ] Default values shown as hints
- [ ] Can create instance successfully

### Integration
- [ ] Created instance appears in sidebar
- [ ] Instance config file has correct structure
- [ ] Script execution shows correct parameters
- [ ] Command construction includes overrides
- [ ] Verb filtering works during execution
- [ ] Parameter/verb counts display correctly

### Error Handling & Edge Cases
- [ ] Required verb validation works
- [ ] Unsaved changes warning works
- [ ] Legacy scripts still work
- [ ] No console errors during any operation

---

## Browser Console Check

After each test, check browser console (F12) for errors:

**No errors should appear related to:**
- ProjectConfigModal
- ProjectParametersEditor
- ConfigurePanel
- Instance configuration
- API calls

**Common errors to watch for:**
- ❌ `Cannot read property of undefined`
- ❌ `axios is not defined`
- ❌ `Failed to fetch`
- ❌ Vue component errors

---

## Backend Log Check

Monitor server logs for errors:

```bash
tail -f server.log | grep -i error
```

**Expected:** No errors during testing

---

## Post-Test Verification

### Check Generated Files

```bash
# List all Gmail Trim instances
ls -la "conf/runners/" | grep -i gmail

# View instance config
cat "conf/runners/Gmail Trim - Test 14 Days.json" | jq .

# Check project metadata
cat projects/gmail-trim-3/.project-meta.json | jq .
```

### Verify Database/State

```bash
# Check if any validation errors occurred
grep -i "validation.*fail" server.log

# Check for any Python exceptions
grep -i "traceback" server.log
```

---

## Success Criteria

✅ **All tests pass** - No errors during workflow
✅ **UI responsive** - All modals/components render correctly
✅ **Data persists** - Configuration survives server restart
✅ **Integration works** - Created instances execute correctly
✅ **No regressions** - Legacy scripts still work
✅ **Clean console** - No JavaScript errors
✅ **Clean logs** - No Python exceptions

---

## Troubleshooting

### Modal doesn't open
- Check browser console for JavaScript errors
- Verify frontend build completed successfully
- Check that server is serving latest web files

### Parameters don't appear
- Verify project has parameters in `.project-meta.json`
- Check API response: `curl http://localhost:5000/admin/projects/gmail-trim-3/config`
- Check browser Network tab for failed requests

### Instance creation fails
- Check server logs for Python exceptions
- Verify API endpoint exists
- Check request payload in browser Network tab
- Verify project_id matches existing project

### Verb filtering doesn't work
- Check that verb has parameters list
- Verify shared_parameters array exists
- Check component computed properties in Vue DevTools

---

**Happy Testing!** 🧪✨

**Server:** http://localhost:5000
**Status:** Running and ready for testing
