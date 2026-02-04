# Testing the New Playground Modal

## Quick Start

### 1. Find Where the Old Modal is Used

```bash
cd /home/snadboy/projects/script-server/web-src
grep -r "ProjectConfigModal" src/
```

Look for imports like:
```js
import ProjectConfigModal from '@/admin/components/projects/ProjectConfigModal.vue';
```

### 2. Update the Import

**Before:**
```js
import ProjectConfigModal from '@/admin/components/projects/ProjectConfigModal.vue';
```

**After:**
```js
import ProjectConfigPlaygroundModal from '@/admin/components/projects/ProjectConfigPlaygroundModal.vue';
```

**In components section:**
```js
components: {
  ProjectConfigPlaygroundModal  // Changed from ProjectConfigModal
}
```

**In template:**
```vue
<ProjectConfigPlaygroundModal   <!-- Changed from ProjectConfigModal -->
  :visible="showModal"
  :project="selectedProject"
  @close="showModal = false"
  @saved="handleSaved"
/>
```

### 3. Build and Test

```bash
cd /home/snadboy/projects/script-server/web-src
NODE_OPTIONS=--openssl-legacy-provider npm run build

cd /home/snadboy/projects/script-server
source .venv/bin/activate && python launcher.py
```

Visit: http://localhost:5000/admin

## Visual Verification Checklist

Open the modal and verify:

### General Appearance
- [ ] Dark theme applied (`#1e1e1e` background)
- [ ] Dialog appears centered on screen
- [ ] Close button (×) visible in top right
- [ ] Tabs visible (Parameters, Verbs)
- [ ] Footer buttons visible (Cancel, Save)

### Colors Match Playground
- [ ] Dialog background: Dark gray (`#1e1e1e`)
- [ ] Content areas: Slightly lighter (`#2a2a2a`)
- [ ] Selected table rows: Blue tint (`#1a3a52`)
- [ ] Buttons/accents: Bright blue (`#4a90e2`)
- [ ] Text: Light gray/white (`#e0e0e0`, `#ccc`)

### Parameters Tab
- [ ] Table visible with columns: Name, Type, Required, Default, Actions
- [ ] Clicking row selects it (blue highlight)
- [ ] Detail panel appears below table
- [ ] "Add Parameter" button visible
- [ ] Empty state shows when no parameters exist

### Verbs Tab
- [ ] "Enable Verb/Subcommand Support" checkbox visible
- [ ] When unchecked, shows helpful message
- [ ] When checked, table appears
- [ ] Global Settings section is collapsible
- [ ] Detail panel shows when verb selected
- [ ] "Add Verb" button visible

## Functional Testing

### Parameters Tab Tests

1. **Add Parameter**
   - Click "Add Parameter"
   - Verify new empty parameter appears in table
   - Verify detail panel auto-selects new parameter
   - Fill in name, type, description
   - Verify unsaved changes tracked

2. **Edit Parameter**
   - Click existing parameter in table
   - Modify fields in detail panel
   - Verify table updates immediately
   - Change type and verify type-specific fields appear

3. **Delete Parameter**
   - Click delete button (trash icon)
   - Verify confirmation dialog
   - Verify parameter removed from table

4. **Reorder Parameters**
   - Click up/down arrows
   - Verify parameter moves in table
   - Verify selection follows moved parameter

5. **Type-Specific Fields**
   - Set type to "int" → verify Min/Max Value fields appear
   - Set type to "text" → verify Min/Max Length fields appear
   - Set type to "list" → verify List Options editor appears
   - Set type to "bool" → verify default checkbox appears

6. **List Options**
   - Add list parameter
   - Click "Add Option" multiple times
   - Fill in value/label pairs
   - Remove options with × button
   - Verify options persist in parameter

### Verbs Tab Tests

1. **Enable Verbs**
   - Check "Enable Verb/Subcommand Support"
   - Verify table and controls appear
   - Uncheck and verify they disappear

2. **Add Verb**
   - Click "Add Verb"
   - Verify new empty verb in table
   - Verify detail panel shows
   - Fill in name, label, description

3. **Global Settings**
   - Click "Global Verb Settings" header
   - Verify section expands/collapses
   - Modify parameter name
   - Toggle "Verb Required" checkbox

4. **Parameter Selection**
   - Select a verb
   - In "Available Parameters" section, check/uncheck parameters
   - Verify selections saved to verb

5. **Required Parameters**
   - Select parameters for a verb
   - In "Required Parameters" section, mark some as required
   - Verify required selections saved

6. **Delete Verb**
   - Click delete button on a verb
   - Verify confirmation dialog
   - Verify verb removed

7. **Reorder Verbs**
   - Use up/down arrows
   - Verify verb moves in table

### Save/Load Tests

1. **Save Configuration**
   - Make changes to parameters or verbs
   - Click "Save Configuration"
   - Verify success message appears
   - Verify modal closes after 1.5 seconds

2. **Cancel with Changes**
   - Make changes
   - Click "Cancel"
   - Verify "unsaved changes" warning
   - Click OK to confirm or Cancel to stay

3. **Load Existing Config**
   - Open modal for project with existing config
   - Verify parameters load correctly
   - Verify verbs load correctly
   - Verify all fields populated

4. **Empty Project**
   - Open modal for new project
   - Verify empty states show
   - Add some parameters/verbs
   - Save successfully

### Edge Cases

1. **Many Parameters (20+)**
   - Add 20+ parameters
   - Verify table scrolls
   - Verify table height stays fixed (300px)
   - Verify detail panel still visible

2. **Many Verbs (20+)**
   - Enable verbs, add 20+ verbs
   - Verify table scrolls
   - Verify table height stays fixed
   - Verify detail panel still accessible

3. **Long Descriptions**
   - Add parameter with very long description
   - Verify table truncates (or wraps appropriately)
   - Verify full text visible in detail panel

4. **Special Characters**
   - Use parameter names with underscores: `my_param`
   - Use CLI flags: `--my-flag`, `-f`
   - Verify no issues with save/load

5. **Rapid Interactions**
   - Quickly add/delete multiple items
   - Quickly switch between tabs
   - Verify no console errors
   - Verify state stays consistent

## Error Scenarios

1. **API Failure on Load**
   - Disconnect backend or use invalid project ID
   - Verify error message displays
   - Verify error is user-friendly

2. **API Failure on Save**
   - Break API endpoint temporarily
   - Try to save
   - Verify error message displays
   - Verify modal doesn't close

3. **Invalid Data**
   - Leave parameter name empty
   - Try to save
   - Verify validation (if implemented)

## Browser Compatibility

Test in:
- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari (if available)
- [ ] Edge

Verify:
- No layout issues
- Colors render correctly
- Scrolling works
- Buttons clickable

## Performance

- [ ] Modal opens quickly (<100ms)
- [ ] Switching tabs is instant
- [ ] Selecting rows is responsive
- [ ] Scrolling is smooth
- [ ] No lag with 20+ items

## Console Check

Open browser DevTools → Console:
- [ ] No errors on modal open
- [ ] No warnings about missing props
- [ ] No errors on save/load
- [ ] No errors on tab switch

## Comparison Test

If possible, test both modals side-by-side:

1. Keep old modal import available as `ProjectConfigModalOld`
2. Render both (toggle with flag)
3. Compare:
   - Visual appearance
   - Functionality
   - Performance
   - Data consistency

## Rollback Trigger

If you encounter any of these, consider rolling back:
- ❌ Data loss on save
- ❌ Cannot load existing configs
- ❌ Modal completely broken
- ❌ Critical functionality missing
- ❌ Console full of errors

For minor issues (cosmetic, non-critical):
- ✅ File a bug and keep testing
- ✅ These can be fixed incrementally

## Success Criteria

The new modal is ready for production when:

✅ All visual elements match playground
✅ All functional tests pass
✅ No console errors
✅ Save/load works correctly
✅ Performance is acceptable
✅ No regressions from old modal

## Reporting Issues

If you find issues, document:

1. **What you did** (steps to reproduce)
2. **What you expected** (expected behavior)
3. **What happened** (actual behavior)
4. **Screenshots** (if visual issue)
5. **Console errors** (copy/paste)
6. **Browser/OS** (environment info)

## Getting Help

If stuck:
1. Check browser console for errors
2. Verify API responses in Network tab
3. Check Vue DevTools for component state
4. Review `PLAYGROUND_MODAL_IMPLEMENTATION.md` for architecture details
