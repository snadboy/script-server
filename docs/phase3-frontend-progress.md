# Phase 3: Frontend - Project Configuration UI

**Date:** 2026-02-02
**Status:** 🚧 In Progress - Core Components Complete

---

## Overview

Phase 3 implements the frontend UI for managing project-level parameters and verbs. Users can now configure parameters and verbs at the project level through an intuitive modal interface.

---

## Components Created

### 1. ProjectConfigModal.vue ✅

**Location:** `web-src/src/admin/components/projects/ProjectConfigModal.vue`

**Purpose:** Main modal for configuring project-level parameters and verbs.

**Features:**
- Two-tab interface: Parameters and Verbs
- Loads existing configuration from API
- Saves configuration to backend
- Unsaved changes detection with confirmation
- Success/error message display
- Loading states for async operations

**Props:**
- `visible` (Boolean) - Controls modal visibility
- `project` (Object) - Project to configure

**Emits:**
- `close` - User closes modal
- `saved` - Configuration saved successfully

**API Calls:**
- `GET /admin/projects/{id}/config` - Load configuration
- `PUT /admin/projects/{id}/parameters` - Save parameters
- `PUT /admin/projects/{id}/verbs` - Save verbs

### 2. ProjectParametersEditor.vue ✅

**Location:** `web-src/src/admin/components/projects/ProjectParametersEditor.vue`

**Purpose:** CRUD interface for project parameter definitions.

**Features:**
- Add/edit/delete parameters
- Reorder parameters (move up/down)
- Type selection: text, int, bool, list
- Type-specific fields:
  - Text: min/max length
  - Integer: min/max value
  - Boolean: flag-only checkbox
- Default value configuration
- CLI flag (param) specification
- Required checkbox
- Empty state with helpful messaging

**Props:**
- `modelValue` (Array) - Parameter definitions

**Emits:**
- `update:modelValue` - Parameters changed

**Parameter Fields:**
- `name` - Parameter name (identifier)
- `type` - Parameter type
- `description` - User-friendly description
- `param` - CLI flag (e.g., --days)
- `required` - Is parameter required
- `default` - Default value
- `min/max` - Validation constraints (type-specific)
- `min_length/max_length` - Text constraints
- `no_value` - Boolean flag-only mode

### 3. ProjectsModal Integration ✅

**Location:** `web-src/src/main-app/components/ProjectsModal.vue`

**Changes:**
- Added "Project Configuration" section in Configure tab
- "Configure Parameters & Verbs" button
- Displays parameter/verb counts from project metadata
- Integrates ProjectConfigModal
- Refreshes projects after configuration saved

**New UI Section:**
```
┌─────────────────────────────────────────┐
│ Project Configuration                   │
│ ┌─────────────────────────────────────┐ │
│ │ Define parameters and verbs at the  │ │
│ │ project level. Script instances can │ │
│ │ then select which parameters...     │ │
│ │                                     │ │
│ │ [📋 4 Parameters] [💻 5 Verbs]     │ │
│ │                                     │ │
│ │ [Configure Parameters & Verbs]      │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

---

## User Workflow

### Configuring Project Parameters

1. **Open Script Manager** - Click "Script Manager" in sidebar
2. **Select Project** - Click on a project in the Projects tab
3. **Open Configuration** - Click gear icon or "Configure" button
4. **Navigate to Configure Tab** - Click "Configure" tab
5. **Open Project Config** - Click "Configure Parameters & Verbs"
6. **Edit Parameters:**
   - Click "Add Parameter" to create new parameter
   - Fill in name, type, description
   - Set CLI flag (param field)
   - Configure type-specific constraints
   - Set default value
   - Reorder with up/down arrows
   - Delete with trash icon
7. **Edit Verbs:** Switch to Verbs tab (uses existing VerbConfigEditor)
8. **Save** - Click "Save Configuration"

### Creating Script Instance (Not Yet Implemented)

This workflow will be implemented in Phase 4:

1. After configuring project, click "Create Script Instance"
2. Select parameters to include (checkboxes)
3. Override default values for selected parameters
4. Select verb (if project has verbs)
5. Configure wrapper/entry point details
6. Save instance

---

## API Integration

### Endpoints Used

✅ **GET /admin/projects/{id}/config**
- Loads parameters, verbs, and shared_parameters
- Called when ProjectConfigModal opens

✅ **PUT /admin/projects/{id}/parameters**
- Saves parameter definitions array
- Called when user saves in ProjectConfigModal

✅ **PUT /admin/projects/{id}/verbs**
- Saves verb configuration and shared_parameters
- Called when user saves in ProjectConfigModal

### Request/Response Format

**GET Config Response:**
```json
{
  "parameters": [
    {
      "name": "days",
      "type": "int",
      "description": "Number of days to keep",
      "param": "--days",
      "required": false,
      "default": 30,
      "min": 1,
      "max": 365
    }
  ],
  "verbs": {
    "parameter_name": "command",
    "required": true,
    "default": "run",
    "options": [...]
  },
  "sharedParameters": ["verbose"]
}
```

**PUT Parameters Request:**
```json
{
  "parameters": [...]
}
```

**PUT Verbs Request:**
```json
{
  "verbs": {...},
  "sharedParameters": [...]
}
```

---

## CSS Styling

All components use consistent styling with:
- CSS variables for theming support
- Responsive design
- Material Icons integration
- Smooth transitions and hover effects
- Loading/error/success states
- Form input consistency

**Key CSS Classes:**
- `.modal-overlay` - Full-screen overlay
- `.modal-dialog` - Centered modal container
- `.modal-tabs` - Tab navigation
- `.form-group` - Form field wrapper
- `.parameter-card` - Parameter editor card
- `.config-info` - Info section with stats

---

## Frontend Build

✅ **Build Status:** Successful

```bash
cd web-src
NODE_OPTIONS=--openssl-legacy-provider npm run build
```

**Output:**
- Build complete without errors
- All components compiled successfully
- Ready for deployment

---

## Files Created/Modified

### Created Files

1. ✅ `web-src/src/admin/components/projects/ProjectConfigModal.vue` (334 lines)
   - Main configuration modal

2. ✅ `web-src/src/admin/components/projects/ProjectParametersEditor.vue` (452 lines)
   - Parameter CRUD interface

3. ✅ `docs/phase3-frontend-progress.md` (this file)
   - Phase 3 documentation

### Modified Files

1. ✅ `web-src/src/main-app/components/ProjectsModal.vue`
   - Added Project Configuration section
   - Integrated ProjectConfigModal
   - Added openProjectConfig method
   - Added CSS styles for new UI elements

---

## Testing Checklist

### Manual Testing Required

- [ ] Open Script Manager
- [ ] Select gmail-trim-3 project
- [ ] Click "Configure Parameters & Verbs" button
- [ ] Verify ProjectConfigModal opens
- [ ] Verify existing parameters load correctly
- [ ] Test adding new parameter
- [ ] Test editing parameter properties
- [ ] Test deleting parameter
- [ ] Test reordering parameters
- [ ] Switch to Verbs tab
- [ ] Verify VerbConfigEditor loads
- [ ] Test saving configuration
- [ ] Verify success message
- [ ] Verify parameters persist after reload
- [ ] Test unsaved changes warning

---

## Phase 3 Remaining Work

### Completed ✅
- [x] Create ProjectConfigModal component
- [x] Create ProjectParametersEditor component
- [x] Integrate into ProjectsModal
- [x] Wire up API calls
- [x] Frontend build successful

### Todo 📋
- [ ] Manual UI testing
- [ ] VerbConfigEditor integration verification
- [ ] Error handling testing
- [ ] Responsive design testing
- [ ] Cross-browser compatibility check

---

## Next Phase: Instance Configuration

**Phase 4 will implement:**
- Update CreateScriptModal to use instance config format
- Add parameter selection checkboxes
- Add parameter value override inputs
- Add verb selection dropdown
- Update EditScriptModal with instance config tab
- Test end-to-end instance creation

---

## Known Issues

None currently identified. Awaiting manual testing.

---

## Architecture Benefits

✅ **Separation of Concerns**
- Project = Capabilities (what parameters/verbs exist)
- Instance = Configuration (which to use, what values)

✅ **DRY Principle**
- Define parameters once at project level
- Reuse across multiple instances
- Update in one place

✅ **User Experience**
- Clear workflow: Configure → Create instances
- Visual stats (parameter/verb counts)
- Intuitive parameter editor
- Immediate feedback

---

**Implementation Status:** Phase 3 Core Components Complete
**Next Step:** Manual UI testing, then Phase 4 (Instance Configuration)
**Build Status:** ✅ Successful
**Ready for Testing:** Yes
