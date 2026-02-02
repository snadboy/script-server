# Parameter UI Bug Fixes

**Fixed:** 2026-02-01
**Issue:** List parameter type caused dialog to become unresponsive

---

## Problem Description

When users selected "List" as the parameter type in the simplified parameter configuration UI, the dialog became completely unresponsive and frozen.

### Root Cause

**Infinite Reactivity Loop:**

1. User selects "list" type
2. `type` watcher → calls `syncToBackend()`
3. `syncToBackend()` → modifies `this.value` object
4. `value` watcher → triggers, calls `fromBackendConfig()`
5. `fromBackendConfig()` → updates `listValues` array
6. `listValues` deep watcher → calls `syncToBackend()`
7. **Loop repeats infinitely** → UI freezes

This is a classic Vue.js reactivity pitfall where watchers trigger each other in a circular dependency.

---

## Solution Implemented

### 1. Added Loading Flag

Introduced an `isLoading` flag to prevent re-entrant watcher execution:

```javascript
data() {
  return {
    // ... existing fields ...
    isLoading: false,  // Prevent reactivity loops
  };
}
```

### 2. Protected Value Watcher

Set flag when loading from backend config:

```javascript
watch: {
  value: {
    immediate: true,
    handler(config) {
      if (config) {
        this.isLoading = true;  // Block other watchers
        this.fromBackendConfig(config);
        this.$nextTick(() => {
          this.isLoading = false;  // Re-enable after Vue updates
        });
      }
    }
  }
}
```

### 3. Guarded All Field Watchers

Every field watcher now checks the flag before syncing:

```javascript
watch: {
  name() { if (!this.isLoading) this.syncToBackend(); },
  description() { if (!this.isLoading) this.syncToBackend(); },
  param() { if (!this.isLoading) this.syncToBackend(); },
  type() { if (!this.isLoading) this.syncToBackend(); },
  // ... all other fields ...
  listValues: {
    deep: true,
    handler() { if (!this.isLoading) this.syncToBackend(); }
  }
}
```

### 4. Initialize List Values on Type Change

When user switches to list type, automatically provide one empty row:

```javascript
type(newType, oldType) {
  // Initialize listValues when switching to list type
  if (newType === 'list' && oldType !== 'list' && this.listValues.length === 0) {
    this.listValues = [{ value: '', uiValue: '' }];
  }
  if (!this.isLoading) this.syncToBackend();
}
```

### 5. Safe Default Value Dropdown

Use computed property to filter empty values:

```javascript
computed: {
  listValuesForDropdown() {
    // Filter out empty values for the default value dropdown
    return this.listValues
      .map(v => v.value)
      .filter(v => !isEmptyString(v));
  }
}
```

Template usage:
```vue
<Combobox
  v-model="defaultValue"
  :config="{
    name: 'Default value',
    type: 'list',
    values: listValuesForDropdown  // Uses computed property
  }"
/>
```

### 6. Ensure Initial Row When Loading

Modified `loadListValues()` to always have at least one row:

```javascript
loadListValues(config) {
  const values = config.values || [];
  const uiMapping = config.values_ui_mapping || {};

  this.listValues = values.map(val => ({
    value: val,
    uiValue: uiMapping[val] || val
  }));

  // If no values exist, add one empty row to get started
  if (this.listValues.length === 0) {
    this.listValues.push({ value: '', uiValue: '' });
  }

  this.defaultValue = config.default || '';
}
```

---

## Files Modified

- `web-src/src/admin/components/scripts-config/ParameterConfigForm.vue`
  - Added `isLoading` flag to data
  - Protected `value` watcher with flag
  - Guarded all field watchers with flag check
  - Enhanced `type` watcher to initialize `listValues`
  - Added `listValuesForDropdown` computed property
  - Updated template to use computed property
  - Modified `loadListValues()` to ensure at least one row

---

## Testing Performed

### Before Fix
- ✅ Reproduced issue: Selecting "list" type froze dialog
- ✅ Confirmed infinite loop in browser console

### After Fix
- ✅ Selecting "list" type works smoothly
- ✅ One empty row appears in list values table
- ✅ Can add/remove values without issues
- ✅ Can switch between single/multiple selection modes
- ✅ Default value dropdown shows only non-empty values
- ✅ Saving and reloading preserves all values
- ✅ No performance issues or freezing

### Edge Cases Tested
- ✅ Creating new list parameter from scratch
- ✅ Loading existing list parameters
- ✅ Switching from other types to list
- ✅ Switching from list to other types
- ✅ List with empty values (filtered out of dropdown)
- ✅ List with UI mappings
- ✅ Multiselect with different format options

---

## Technical Notes

### Why `$nextTick` is Important

```javascript
this.$nextTick(() => {
  this.isLoading = false;
});
```

We use `$nextTick()` to ensure Vue has finished processing all reactive updates before clearing the flag. This prevents any watchers from firing during the same update cycle.

### Why Deep Watch on `listValues`

```javascript
listValues: {
  deep: true,
  handler() { if (!this.isLoading) this.syncToBackend(); }
}
```

Array mutations (push, splice, etc.) don't trigger regular watchers. Deep watch is needed to detect when user adds/removes/modifies list values.

### Why Computed Property for Dropdown

```javascript
listValuesForDropdown() {
  return this.listValues
    .map(v => v.value)
    .filter(v => !isEmptyString(v));
}
```

Computing this once per render cycle is more efficient than inline `listValues.map()` in the template, which would create a new array on every render.

---

## Prevention Strategy

**For future components with complex reactivity:**

1. ✅ **Use loading flags** for components with bidirectional data flow
2. ✅ **Guard watchers** when they modify data that triggers other watchers
3. ✅ **Use `$nextTick`** when toggling flags to ensure Vue finishes updates
4. ✅ **Prefer computed properties** over inline transformations in templates
5. ✅ **Initialize arrays** with default values to prevent empty state issues
6. ✅ **Test type switching** when multiple types share the same form

---

## Status

- ✅ Bug fixed
- ✅ Frontend rebuilt
- ✅ Server restarted
- ✅ Ready for production use

---

**Server:** http://localhost:5000
**Build:** 2026-02-01 11:27
**Status:** 🟢 Running and healthy
