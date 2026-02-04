# CLI Verb/Subcommand Support

**Status:** ✅ Complete - Merged to master

## Overview

Implemented support for CLI verbs/subcommands where scripts can define multiple verbs (like `git clone`, `docker run`, `npm install`), each with their own set of required/optional parameters.

## Features

| Feature | Description |
|---------|-------------|
| Verb Configuration | New `verbs` section in script config to define subcommands |
| VerbOption Model | Defines name, label, description, parameters, and required_parameters per verb |
| Verb-aware Command Building | Executor places verb first, then positional `after_verb` params, then flagged params, then `end` positional params |
| verb_position Parameter | New parameter field: `after_verb` (positional after verb) or `end` (positional at end) |
| shared_parameters | Parameters visible across all verbs (e.g., `--verbose`) |
| VerbSelector.vue | Frontend dropdown component for selecting verb/subcommand |
| Parameter Filtering | Only parameters for selected verb are shown in UI |
| Verb-specific Required | Parameters can be required only for certain verbs |
| ExecuteModal Support | Verb selector integrated into Execute dialog with parameter filtering |
| API Extension | `verbs` and `sharedParameters` serialized in config API response |

## Configuration Format

```json
{
  "name": "My CLI Tool",
  "script_path": "samples/scripts/my_tool.sh",
  "verbs": {
    "parameter_name": "action",
    "default": "list",
    "required": false,
    "options": [
      {
        "name": "list",
        "label": "List Items",
        "description": "List all items with optional filtering",
        "parameters": ["format", "all"],
        "required_parameters": []
      },
      {
        "name": "create",
        "label": "Create Item",
        "description": "Create a new item with the given name",
        "parameters": ["name", "type"],
        "required_parameters": ["name"]
      },
      {
        "name": "delete",
        "label": "Delete Item",
        "description": "Delete an item by its ID",
        "parameters": ["item_id", "force"],
        "required_parameters": ["item_id"]
      }
    ]
  },
  "shared_parameters": ["verbose"],
  "parameters": [
    {
      "name": "action",
      "type": "constant",
      "constant": true,
      "no_value": true,
      "verb_position": "start"
    },
    {
      "name": "name",
      "type": "text",
      "verb_position": "after_verb",
      "description": "Name of the item"
    },
    {
      "name": "verbose",
      "type": "bool",
      "param": "-v",
      "no_value": true,
      "description": "Enable verbose output"
    }
  ]
}
```

## Command Building Order

When a verb is selected, the executor builds commands in this order:

1. **Verb** (from `verbs.parameter_name`)
2. **Positional after verb** (`verb_position: "after_verb"`)
3. **Flagged parameters** (parameters with `param` field)
4. **Positional at end** (`verb_position: "end"`)

**Example command:** `./my_tool.sh create my-item --type widget --verbose`

## Frontend Components

### Admin Interface

**VerbConfigEditor.vue** - Verb configuration in Add/Edit Script Modal
- Enable/disable verb support with checkbox
- Configure verb parameter name, default verb, and required flag
- Define shared parameters (visible for all verbs)
- Add/edit/delete/reorder verb options
- For each verb: set name, label, description, visible parameters, and required parameters
- Real-time parameter filtering based on verb selection
- Master-detail pattern (fixed-height table + edit panel)

**VerbOptionEditor.vue** - Individual verb option editor
- Edit verb name, label, description
- Select visible parameters with checkboxes
- Mark required parameters
- Shows shared parameters with green styling

### User Interface

**VerbSelector.vue** - Verb selection dropdown
- Renders in Execute dialog and script parameters view
- Shows verb label and description
- Filters parameters when verb changes
- Persists selection in execution state

**Parameter Filtering** - Updated in multiple components:
- `script-parameters-view.vue` - Shows only parameters for selected verb
- `ExecuteModal.vue` - Filters parameters before execution
- `scriptSetup.js` - Manages verb selection state

## Session History

### Session 2026-01-29: Parameter Filtering & Script Description

**Fixed:** Execution cards were showing all parameters instead of just those relevant to the verb.

**Changes:**
- Extended `ShortConfig` dataclass to include `verbs_config` and `shared_parameters`
- Modified `/scripts` API to include verb configuration
- Added `filterParametersByVerb()` utility to filter parameters based on verb
- Fixed camelCase parameter naming issues
- Added script description display in script view header

**Files modified:**
- `src/model/script_config.py` - Extended ShortConfig
- `src/web/server.py` - Modified GetScripts handler
- `web-src/src/main-app/utils/executionFormatters.js` - Added filtering utilities
- `web-src/src/main-app/components/common/RunningSection.vue` - Integrated filtering
- `web-src/src/main-app/components/common/CompletedSection.vue` - Integrated filtering
- `web-src/src/main-app/components/scripts/script-view.vue` - Added description header

### Session 2026-01-28: Verb Configuration UI

**Added:** Verb configuration UI in admin interface

**Changes:**
- Created VerbConfigEditor.vue for managing verb configuration
- Created VerbOptionEditor.vue for editing individual verbs
- Added "Verbs" tab (Tab 5) to Add/Edit Script Modal
- Full integration with save/load system

**Files created:**
- `web-src/src/admin/components/scripts-config/VerbConfigEditor.vue`
- `web-src/src/admin/components/scripts-config/VerbOptionEditor.vue`

**Files modified:**
- `web-src/src/admin/components/scripts-config/AddScriptModal.vue` - Added Verbs tab

### Session 2026-01-22: Frontend Testing

**Verified:** CLI verb feature fully working after frontend rebuild

**Tests performed:**
- Tested all three verbs in `verb_demo.json`
- Verified VerbSelector renders correctly
- Confirmed parameter filtering works
- Verified shared parameters appear for all verbs

### Session 2026-01-21: Backend Implementation

**Implemented:** Core verb/subcommand support

**Changes:**
- Created `verb_config.py` with VerbConfig and VerbOption models
- Extended `script_config.py` to load verbs configuration
- Extended `parameter_config.py` with `verb_position` field
- Modified `executor.py` to build verb-aware commands
- Extended `external_model.py` to serialize verbs in API
- Created `VerbSelector.vue` component
- Modified `script-parameters-view.vue` for parameter filtering
- Modified `ExecuteModal.vue` to integrate verb selector
- Modified `scriptSetup.js` store to manage verb selection

**Files created:**
- `src/model/verb_config.py`
- `web-src/src/main-app/components/scripts/VerbSelector.vue`
- `conf/runners/verb_demo.json` - Test config

## Testing

- ✅ Frontend builds successfully
- ✅ Backend tests passing
- ✅ Manual verification with verb_demo.json
- ✅ Parameter filtering verified
- ✅ Execution with different verbs tested
- ✅ Merged to master branch

## Example Result

**Before verb filtering:**
```
days=14, dry_run=true, verbose=false, command=labels
```

**After verb filtering:**
```
command=labels, verbose=false
```

## Benefits

- Support for complex CLI tools with multiple subcommands
- Cleaner parameter display (only relevant params shown)
- Per-verb required parameter validation
- Positional parameter control with verb_position
- Shared parameters available across all verbs
- Intuitive UI for verb selection and configuration
