# Parameter Configuration UI Improvements

## Overview

Complete redesign of parameter configuration forms to reduce complexity, improve usability, and add support for dual-flag boolean parameters.

## Features

### 1. Simplified Parameter Configuration UI (2026-02-01)

**Status:** ✅ Complete

**Goals achieved:**
- Reduced parameter types from 11 to 6 essential types
- Removed redundant checkboxes (converted to types)
- Organized form into 3 clear sections (Basic, Behavior, Constraints)
- Type-specific constraint visibility
- 100% backward compatible with existing configs

#### Simplified Type System

**Reduced from 11 types to 6:**
- `text` - Text input with optional validation
- `int` - Integer input with min/max
- `bool` - Radio buttons for true/false
- `list` - Dropdown or multiselect with predefined values
- `flag` - Boolean flag (no value passed, just the flag itself)
- `constant` - Fixed value (not shown to user)

**Removed specialized types:**
- `ip`, `ip4`, `ip6` → merged into `text`
- `file_upload`, `server_file` → merged into `text`
- `multiline_text` → merged into `text`
- `editable_list` → merged into `list`
- `multiselect` → merged into `list` (multiple selection mode)

#### Form Redesign

**Section 1 - Basic:**
- Name, Description, Type dropdown, Required checkbox

**Section 2 - Parameter Behavior:**
- Param (CLI flag), Pass as, Combine checkbox

**Section 3 - Constraints (bold header):**
- Type-specific validation fields
- Only shows relevant constraints for selected type

**Removed clutter:**
- "Secret value", "Env var", "Stdin expected text" fields

#### Type-Specific Constraints

| Type | Constraints |
|------|------------|
| **Text** | Min/max length, RegExp pattern + description, Default value |
| **Int** | Min/max value, Default value |
| **Bool** | Radio buttons for true/false default |
| **List** | Selection mode, Two-column value/UI mapping table, Multiselect format options |
| **Flag** | Info box explaining usage (no constraints) |
| **Constant** | Constant value field + info box |

#### Automatic Migration

- `no_value: true` → `flag` type
- `constant: true` → `constant` type
- `type: "multiselect"` → `list` (multiple selection mode)
- `type: "editable_list"` → `list`
- `type: "multiline_text"/"ip"/"ip4"/"ip6"` → `text`
- List with `['true', 'false']` → `bool` type

#### Bug Fix: List Parameter Reactivity Loop

**Issue:** Selecting "list" type froze the dialog due to infinite reactivity loop

**Root cause:** Watchers triggering each other (type → syncToBackend → value → fromBackendConfig → listValues → syncToBackend)

**Solution:**
- Added `isLoading` flag to prevent re-entrant watcher execution
- Guarded all field watchers with `if (!this.isLoading)` check
- Set flag in `value` watcher before `fromBackendConfig()`, clear in `$nextTick`
- Initialize `listValues` with one empty row when switching to list type
- Created `listValuesForDropdown` computed property for safe dropdown rendering

#### Benefits

- 45% fewer parameter types (6 vs 11)
- 5 fewer form fields (cleaner UI)
- Constraints section now prominent (bold header)
- Type-specific fields reduce confusion
- Better list editing with two-column table
- Info boxes explain special types

---

### 2. Dual-Flag Boolean Parameters (2026-02-01)

**Status:** ✅ Complete

**Overview:** Added support for boolean parameters with different flags for true vs false values (e.g., `--verbose` / `--quiet`, `--enable-cache` / `--disable-cache`).

#### Backend Changes

**Parameter Model** (`src/model/parameter_config.py`):
- Added `dual_flags`, `param_true`, `param_false` observable fields
- Parse dual-flag config from JSON
- Validate that both flags are provided when dual_flags=true
- Added fields to sorted config key order

**Executor** (`src/execution/executor.py`):
- Updated `_build_param_args()` to check for dual_flags first
- Use `param_true` when value is true, `param_false` when false
- Skip value passing (just add the flag)

#### Frontend Changes

**ParameterConfigForm** (`web-src/src/admin/components/scripts-config/ParameterConfigForm.vue`):
- Added data properties: `boolFlagMode`, `paramTrue`, `paramFalse`
- Added "Boolean flag mode" radio buttons (single/dual)
- Show dual-flag input fields when mode is "dual"
- Disable "Combine param with value" checkbox in dual-flag mode
- Updated `syncToBackend()` to serialize dual-flag config
- Updated `fromBackendConfig()` to detect and load dual-flag bools
- Added watchers for new fields

#### Example Config

```json
{
  "name": "verbosity",
  "type": "bool",
  "dual_flags": true,
  "param_true": "--verbose",
  "param_false": "--quiet",
  "default": false
}
```

#### Use Cases

- `--verbose` (if true) / `--quiet` (if false)
- `--enable-cache` (if true) / `--disable-cache` (if false)
- `--color` (if true) / `--no-color` (if false)

#### Benefits

- More flexible boolean parameter configuration
- Support for CLI tools with opposing flag patterns
- Cleaner command-line output (flags only, no values)
- Intuitive UI for choosing flag mode

---

## Files Modified

**Simplified Parameter UI:**
- `web-src/src/admin/components/scripts-config/ParameterConfigForm.vue` - Complete redesign (815 lines)
- `web-src/src/admin/components/scripts-config/parameter-fields.js` - Updated typeField
- `conf/runners/param_ui_test.json` - Test config with all 6 parameter types

**Dual-Flag Boolean Parameters:**
- `src/model/parameter_config.py` - Added dual-flag fields and validation
- `src/execution/executor.py` - Updated _build_param_args for dual flags
- `web-src/src/admin/components/scripts-config/ParameterConfigForm.vue` - Added dual-flag UI
- `conf/runners/dual_flag_test.json` - Test config with dual-flag examples
- `samples/scripts/dual_flag_demo.sh` - Test script for manual verification

## Documentation

- `docs/simplified-parameter-ui.md` - Comprehensive UI documentation
- `docs/dual-flag-boolean-parameters.md` - Dual-flag feature documentation

## Testing

- ✅ Frontend builds successfully
- ✅ Backend executor logic tested (all tests pass)
- ✅ Manual script execution verified
- ✅ List type reactivity loop fixed
- ✅ All 6 parameter types working correctly
