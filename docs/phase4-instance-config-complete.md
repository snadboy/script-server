# Phase 4: Frontend - Instance Configuration UI

**Date:** 2026-02-02
**Status:** ✅ Complete - Ready for Testing

---

## Overview

Phase 4 implements the frontend UI for creating script instances using the new project-based parameter format. Users can now select which parameters to include and override default values when creating script instances from imported projects.

---

## What Was Implemented

### 1. ConfigurePanel Enhancements ✅

**File:** `web-src/src/admin/components/scripts-config/create-script/ConfigurePanel.vue`

**New Features:**

**Instance Configuration Section:**
- Automatically appears when project has parameters or verbs
- Clean, highlighted section with border and background
- Info message explaining the workflow

**Verb Selection:**
- Dropdown to select verb/command (if project has verbs)
- Shows verb description below selection
- Required indicator if verb is mandatory
- Resets parameter selection when verb changes

**Parameter Selection:**
- Checkboxes for each available parameter
- Filtered by selected verb (if applicable)
- "Select All" / "Deselect All" quick actions
- Shows parameter type, description, and required status

**Parameter Value Overrides:**
- Appears when parameter is checked
- Type-specific inputs:
  - Boolean: checkbox
  - Integer: number input with min/max
  - Text: text input
- Shows default value as placeholder/hint
- Only sends overridden values to backend

**Smart Features:**
- Auto-initializes values with project defaults
- Only saves values that differ from defaults
- Handles verb-based parameter filtering
- Responsive parameter list updates

---

## User Workflow

### Creating a Script Instance

1. **Open Script Manager** → Import tab
2. **Import Project** (Git/ZIP/Local)
3. **Configure Panel** opens automatically
4. **Install Dependencies** (if needed)
5. **Select Entry Point**
6. **Enter Script Details** (name, description)
7. **Configure Instance:**
   - **Select Verb** (if project has verbs)
   - **Check Parameters** to include
   - **Override Values** (optional)
8. **Preview Wrapper** (optional)
9. **Create Script**

### Example: Gmail Trim Instance

```
Project: gmail-trim-3
├─ Verb: "Run Cleanup" ✓
├─ Parameters:
│  ├─ ☑ days (14) ← overridden from default 30
│  ├─ ☑ dry_run (true)
│  └─ ☑ verbose (false)
└─ Creates: "Gmail Trim - 14 Days"
```

---

## Data Flow

### Component Props

```javascript
{
  project: {
    id: 'gmail-trim-3',
    parameters: [...],  // Parameter definitions
    verbs: {...},       // Verb configuration
    shared_parameters: [...]
  }
}
```

### Component Data

```javascript
{
  selectedVerb: 'run',
  selectedParameters: ['days', 'dry_run', 'verbose'],
  parameterValues: {
    days: 14,  // Override (default is 30)
    dry_run: true  // Same as default, won't be sent
  }
}
```

### Emitted Config

```javascript
{
  entryPoint: 'gmail_cleanup.main:app',
  scriptName: 'Gmail Trim - 14 Days',
  description: '...',

  // Instance config (NEW)
  includedParameters: ['days', 'dry_run', 'verbose'],
  parameterValues: {days: 14},  // Only overrides
  selectedVerb: 'run'
}
```

### API Call

```javascript
POST /admin/projects/{id}/wrapper
{
  entry_point: '...',
  script_name: '...',
  description: '...',

  // Instance config
  included_parameters: ['days', 'dry_run', 'verbose'],
  parameter_values: {days: 14},
  selected_verb: 'run'
}
```

---

## Implementation Details

### New Data Properties

```javascript
data() {
  return {
    // ... existing properties ...

    // Instance configuration
    selectedVerb: '',
    selectedParameters: [],
    parameterValues: {}
  }
}
```

### New Computed Properties

```javascript
computed: {
  hasProjectParameters() {
    // Check if project has parameter definitions
  },

  hasProjectVerbs() {
    // Check if project has verb configuration
  },

  selectedVerbOption() {
    // Get full verb object for selected verb
  },

  availableParameters() {
    // Filter parameters by selected verb
    // Returns verb-specific + shared parameters
  },

  configData() {
    // Include instance config in emitted data
    // includedParameters, parameterValues, selectedVerb
  }
}
```

### New Methods

```javascript
methods: {
  selectAllParameters() {
    // Check all available parameters
  },

  deselectAllParameters() {
    // Uncheck all parameters
  },

  initializeParameterValues() {
    // Set default values for selected parameters
  },

  formatDefaultValue(param) {
    // Format default for display
  },

  getEffectiveParameterValues() {
    // Return only overridden values
  }
}
```

### Watchers

```javascript
watch: {
  selectedVerb(newVal, oldVal) {
    // Reset parameters when verb changes
  },

  selectedParameters: {
    handler() {
      // Initialize values for new selections
    },
    deep: true
  }
}
```

---

## CSS Styling

**New Classes:**
- `.instance-config-group` - Highlighted section container
- `.instance-config-info` - Info message box
- `.verb-selection` - Verb dropdown section
- `.verb-description` - Verb description display
- `.parameter-selection` - Parameters list container
- `.params-header` - Header with select all/deselect all
- `.parameters-list` - Parameter rows container
- `.parameter-row` - Individual parameter card
- `.parameter-select` - Checkbox and info section
- `.parameter-value` - Value override section
- `.param-info` - Parameter name, type, required badge
- `.param-name` - Monospace parameter name
- `.param-type` - Type indicator
- `.param-required` - Required badge
- `.no-parameters-message` - Empty state

**Styling Features:**
- Blue border and background for instance config section
- Info box with left border accent
- Parameter cards with hover effects
- Type badges and required indicators
- Responsive grid layout
- Consistent spacing and typography

---

## Files Modified

### 1. ConfigurePanel.vue ✅

**Lines Added:** ~200 lines
**Changes:**
- Added Instance Configuration section to template
- Added data properties for instance config
- Added 5 new computed properties
- Added 5 new methods
- Added 2 watchers
- Added comprehensive CSS styling

### 2. CreateScriptModal.vue ✅

**Lines Changed:** ~15 lines
**Changes:**
- Updated wrapper generation API call
- Added instance config to payload
- Conditional inclusion based on presence of parameters

---

## Testing Checklist

### Manual Testing Required

- [ ] Import project with parameters and verbs
- [ ] Verify Instance Configuration section appears
- [ ] Test verb selection dropdown
- [ ] Verify parameter filtering by verb
- [ ] Test "Select All" / "Deselect All"
- [ ] Check individual parameter selection
- [ ] Test boolean parameter value override
- [ ] Test integer parameter value override
- [ ] Test text parameter value override
- [ ] Verify default values shown correctly
- [ ] Test parameter value initialization
- [ ] Test saving with overridden values
- [ ] Verify only changed values sent to backend
- [ ] Test verb change resets parameters
- [ ] Test with project without parameters
- [ ] Test with project without verbs

---

## Integration Points

### Backend API ✅

**Endpoint:** `POST /admin/projects/{id}/wrapper`

**Request Body (New Fields):**
```json
{
  "included_parameters": ["days", "dry_run", "verbose"],
  "parameter_values": {"days": 14},
  "selected_verb": "run"
}
```

**Backend Handler:**
```python
def post(self, project_id):
    # ...
    included_parameters = body.get('included_parameters')
    parameter_values = body.get('parameter_values')
    selected_verb = body.get('selected_verb')

    config_path = project_service.generate_runner_config(
        project_id,
        script_name,
        description,
        group,
        parameters,  # Legacy
        included_parameters,  # NEW
        parameter_values,  # NEW
        selected_verb  # NEW
    )
```

Already implemented in Phase 1! ✅

---

## UI Components

### Instance Configuration Section

```
┌─────────────────────────────────────────────┐
│ ⚙ Instance Configuration                    │
├─────────────────────────────────────────────┤
│ Select which parameters to include and      │
│ optionally override their default values.   │
├─────────────────────────────────────────────┤
│ Command/Verb *                              │
│ [Run Cleanup ▼]                             │
│ Execute email cleanup process               │
├─────────────────────────────────────────────┤
│ Parameters        [Select All] [Deselect All]│
│ ┌─────────────────────────────────────────┐ │
│ │ ☑ days (int) required                   │ │
│ │   Number of days to keep emails         │ │
│ │   Override Default (default: 30)        │ │
│ │   [14_____________]                     │ │
│ ├─────────────────────────────────────────┤ │
│ │ ☑ dry_run (bool)                        │ │
│ │   Preview deletions without deleting    │ │
│ │   Override Default (default: true)      │ │
│ │   ☑ Enabled                             │ │
│ ├─────────────────────────────────────────┤ │
│ │ ☑ verbose (bool)                        │ │
│ │   Enable verbose logging                │ │
│ │   Override Default (default: false)     │ │
│ │   ☐ Enabled                             │ │
│ └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

---

## Benefits

✅ **Clear Workflow**
- Visual separation of instance config
- Step-by-step parameter selection
- Immediate feedback on selections

✅ **Smart Defaults**
- Auto-populates with project defaults
- Only saves overridden values
- Reduces config file size

✅ **Verb Integration**
- Seamless verb selection
- Automatic parameter filtering
- Consistent with verb architecture

✅ **Flexible Configuration**
- Select any combination of parameters
- Override any value
- No unnecessary data sent to backend

✅ **User-Friendly**
- Clear labels and descriptions
- Type indicators and constraints
- Required parameter highlighting
- Default value hints

---

## Architecture Alignment

**Project = Capabilities**
```json
{
  "parameters": [/* all possible parameters */],
  "verbs": {/* all possible verbs */}
}
```

**Instance = Configuration**
```json
{
  "instance_config": {
    "included_parameters": [/* selected subset */],
    "parameter_values": {/* only overrides */},
    "selected_verb": "run"
  }
}
```

Perfect separation of concerns! ✅

---

## Known Issues

None currently identified. Awaiting manual testing.

---

## Next Steps

### Immediate
1. Manual UI testing with gmail-trim-3 project
2. Test all parameter types (text, int, bool)
3. Test verb selection and filtering
4. Verify instance creation end-to-end

### Phase 5: Migration & Documentation
- Create migration helper tool (optional)
- Write user documentation
- Create example configurations
- Full integration testing

### Phase 6: EditScriptModal
- Add "Instance Config" tab to EditScriptModal
- Allow editing instance configuration post-creation
- Show current parameter selection
- Allow changing overridden values

---

## Completion Status

**Phase 4:** ✅ **COMPLETE**

| Task | Status |
|------|--------|
| Add verb selection UI | ✅ Done |
| Add parameter selection UI | ✅ Done |
| Add parameter value override UI | ✅ Done |
| Update configData computed | ✅ Done |
| Update API call payload | ✅ Done |
| Add CSS styling | ✅ Done |
| Frontend builds successfully | ✅ Done |
| Manual testing | ⏳ Pending |

---

**Build Status:** ✅ Successful
**Ready for Testing:** Yes
**Next Phase:** Migration & Documentation

