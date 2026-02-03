# Project-Level Parameters & Verbs - Implementation Complete

**Date:** 2026-02-03
**Status:** ✅ Backend Complete, ✅ Frontend Complete, ⏳ Manual Testing Required

---

## Summary

Successfully implemented the project-level parameters & verbs architecture as specified in the original plan. This is a major architectural change that eliminates parameter/verb duplication across script instances.

### Architecture

**Before:**
```
conf/runners/Gmail Trim A.json - Full parameter/verb definitions (200+ lines)
conf/runners/Gmail Trim B.json - Duplicated definitions (200+ lines)
```

**After:**
```
projects/gmail-trim-3/.project-meta.json - Canonical definitions (once)
conf/runners/Gmail Trim A.json - Instance config (selection + overrides, ~20 lines)
conf/runners/Gmail Trim B.json - Instance config (selection + overrides, ~20 lines)
```

---

## Implementation Status

### Phase 1: Backend Foundation ✅ COMPLETE

**Files Modified:**
- `src/project_manager/project_service.py:713-816`
  - ✅ `update_project_parameters()` - Update parameter definitions
  - ✅ `update_project_verbs()` - Update verb configuration
  - ✅ `get_project_parameters()` - Get parameter definitions
  - ✅ `get_project_verbs()` - Get verb configuration
  - ✅ Modified `generate_runner_config()` - Accept instance config params

**Testing:**
```bash
$ PYTHONPATH=src python3 test_backend_loading.py
✓ ALL TESTS PASSED
- Project metadata loads with 4 parameters and 5 verbs
- Instance configs load with project_id reference
- Parameter filtering works (only included params)
- Value overrides work (days: 30→14, 30→60)
```

### Phase 2: Config Loading ✅ COMPLETE

**Files Modified:**
- `src/model/script_config.py:40-53, 115-220`
  - ✅ `InstanceConfig` class - Parse instance configuration
  - ✅ `_load_from_project()` method - Load from project metadata
  - ✅ Modified `__init__()` - Detect and handle project_id

**Key Features:**
- Loads parameter definitions from project metadata
- Filters to included_parameters only
- Overrides defaults with instance parameter_values
- Loads verb configuration from project
- 100% backward compatible with legacy configs

**Testing:**
```bash
✓ ConfigModel loads 3 parameters for Gmail Trim A
✓ ConfigModel loads 2 parameters for Gmail Trim B
✓ ConfigModel loads 1 parameter for Gmail List Labels
✓ Verb configuration loaded correctly (5 options)
```

### Phase 3: Frontend - Project Config UI ✅ COMPLETE

**Files Created:**
- `web-src/src/admin/components/projects/ProjectConfigModal.vue` (334 lines)
  - Two-tab interface: Parameters and Verbs
  - Loads/saves configuration via API
  - Unsaved changes detection

- `web-src/src/admin/components/projects/ProjectParametersEditor.vue` (452 lines)
  - Add/edit/delete parameters
  - Reorder with up/down arrows
  - Type-specific constraints
  - Default value configuration

**Files Modified:**
- `web-src/src/main-app/components/ProjectsModal.vue`
  - Added "Configure Parameters & Verbs" button
  - Opens ProjectConfigModal

**API Integration:**
- `GET /admin/projects/{id}/config` ✅
- `PUT /admin/projects/{id}/parameters` ✅
- `PUT /admin/projects/{id}/verbs` ✅

### Phase 4: Frontend - Instance Config UI ✅ COMPLETE

**Files Modified:**
- `web-src/src/admin/components/scripts-config/create-script/ConfigurePanel.vue` (+200 lines)
  - Instance Configuration section
  - Verb selection dropdown
  - Parameter selection checkboxes
  - Parameter value override inputs
  - "Select All" / "Deselect All" actions

- `web-src/src/admin/components/scripts-config/create-script/CreateScriptModal.vue` (+15 lines)
  - Updated API call to send instance config

**User Workflow:**
```
1. Import Project → 2. Configure Dependencies
↓
3. Instance Configuration:
   Command: [Run Cleanup ▼]
   ☑ days (14) ← override default 30
   ☑ dry_run (true)
   ☑ verbose (false)
↓
4. Details → 5. Save
```

### Phase 5: Additional Improvements ✅ COMPLETE

**VerbConfigEditor Enhancement:**
- `web-src/src/admin/components/scripts-config/VerbConfigEditor.vue:186-201`
- ✅ Pass-as examples now use actual verb names
- Before: `--command list`
- After: `--command run` (uses default or first verb)

**Backend API Endpoints:**
- `src/web/server.py:1624-1677, 1814-1816`
- ✅ `GetProjectConfigHandler` - Get project config
- ✅ `UpdateProjectParametersHandler` - Update parameters
- ✅ `UpdateProjectVerbsHandler` - Update verbs

---

## Test Configuration Created

### Project Metadata
**File:** `projects/gmail-trim-3/.project-meta.json`

**Parameters Defined (4):**
1. `days` (int) - Days to keep (default: 30, min: 1, max: 365)
2. `dry_run` (bool) - Preview mode (default: true)
3. `verbose` (bool) - Verbose logging (default: false)
4. `config_file` (text) - Config file path

**Verbs Defined (5):**
1. `run` - Run Cleanup (days, dry_run, verbose, config_file)
2. `auth` - Authenticate (verbose)
3. `labels` - List Labels (verbose)
4. `groups` - List Contact Groups (verbose)
5. `config` - Show Config (config_file, verbose)

**Shared Parameters:** verbose

### Instance Configs Created

**1. Gmail Trim A** (`conf/runners/Gmail Trim A.json`)
```json
{
  "project_id": "gmail-trim-3",
  "instance_config": {
    "included_parameters": ["days", "dry_run", "verbose"],
    "parameter_values": {"days": 14},
    "selected_verb": "run"
  }
}
```

**2. Gmail Trim B** (`conf/runners/Gmail Trim B.json`)
```json
{
  "project_id": "gmail-trim-3",
  "instance_config": {
    "included_parameters": ["days", "verbose"],
    "parameter_values": {"days": 60},
    "selected_verb": "run"
  }
}
```

**3. Gmail List Labels** (`conf/runners/Gmail List Labels.json`)
```json
{
  "project_id": "gmail-trim-3",
  "instance_config": {
    "included_parameters": ["verbose"],
    "parameter_values": {},
    "selected_verb": "labels"
  }
}
```

---

## Benefits Achieved

✅ **DRY Principle** - Parameters defined once, used many times
✅ **Consistency** - All instances share definitions
✅ **Maintainability** - Update in one place → all instances updated
✅ **Clear Separation** - Project = capabilities, Instance = configuration
✅ **Reduced Duplication** - Eliminates ~100-200 lines per instance
✅ **Simpler Configs** - Instance configs are just values, not definitions

---

## Manual Testing Required

### Prerequisites

1. **Install dependencies:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Start server:**
   ```bash
   python launcher.py
   ```

3. **Access UI:**
   - Main: http://localhost:5000
   - Admin: http://localhost:5000/admin.html

### Test Scenario 1: View Project Configuration

1. Open Script Manager (sidebar)
2. Go to Projects tab
3. Find "Gmail Trim" project
4. Click "Configure" tab
5. Click "Configure Parameters & Verbs"
6. **Verify:**
   - Parameters tab shows 4 parameters
   - Each parameter has type, description, default
   - Verbs tab shows 5 verbs
   - Each verb shows associated parameters

### Test Scenario 2: Edit Project Parameters

1. In ProjectConfigModal, go to Parameters tab
2. Click "Add Parameter"
3. Create new parameter:
   - Name: `exclude_from`
   - Type: text
   - Description: Email address to exclude
4. Click "Save"
5. **Verify:**
   - Parameter appears in list
   - Can reorder with arrows
   - Can edit and delete

### Test Scenario 3: Create Instance from Project

1. Open Script Manager → Projects tab
2. Find "Gmail Trim" project
3. Click gear icon (Create Instance)
4. **Configure panel should show:**
   - Instance Configuration section
   - Verb dropdown (5 options)
   - Parameter checkboxes (filtered by verb)
5. **Select:**
   - Verb: "Run Cleanup"
   - Check: days, dry_run
   - Override days to 14
6. Click "Next" → Enter name → Save
7. **Verify:**
   - New script appears in sidebar
   - Config file created in conf/runners/

### Test Scenario 4: Verify Instance Config Format

1. Open `conf/runners/[new instance].json`
2. **Verify format:**
   ```json
   {
     "project_id": "gmail-trim-3",
     "instance_config": {
       "included_parameters": ["days", "dry_run"],
       "parameter_values": {"days": 14},
       "selected_verb": "run"
     }
   }
   ```

### Test Scenario 5: Execute Script

1. Click on instance in sidebar
2. Click "Execute"
3. **Verify ExecuteModal shows:**
   - Only included parameters (days, dry_run)
   - Default values (days: 14, dry_run: true)
4. Run script
5. **Check execution logs:**
   - Verify command includes verb: `script.py run`
   - Verify parameters passed correctly: `-d 14 --dry-run`

### Test Scenario 6: Multiple Instances

1. Create second instance from same project
2. Select different verb: "List Labels"
3. **Verify:**
   - Only "verbose" parameter shown (labels verb params)
   - First instance unchanged
   - Both scripts work independently

### Test Scenario 7: Parameter Inheritance

1. Edit project parameters
2. Change default: days → 45
3. **Verify:**
   - Existing instances keep overridden values
   - New instances get new default (45)

---

## Files Modified Summary

### Backend (6 files)
- `src/project_manager/project_service.py` - CRUD methods, generate_runner_config
- `src/model/script_config.py` - InstanceConfig class, _load_from_project
- `src/web/server.py` - API handlers for project config

### Frontend (6 files)
- `web-src/src/admin/components/projects/ProjectConfigModal.vue` (NEW)
- `web-src/src/admin/components/projects/ProjectParametersEditor.vue` (NEW)
- `web-src/src/admin/components/scripts-config/VerbConfigEditor.vue` (MODIFIED)
- `web-src/src/admin/components/scripts-config/create-script/ConfigurePanel.vue` (MODIFIED)
- `web-src/src/admin/components/scripts-config/create-script/CreateScriptModal.vue` (MODIFIED)
- `web-src/src/main-app/components/ProjectsModal.vue` (MODIFIED)

### Test Files (2 files)
- `test_backend_loading.py` (NEW) - Backend verification tests
- `projects/gmail-trim-3/.project-meta.json` (NEW) - Test project config

### Documentation (1 file)
- `docs/PROJECT_LEVEL_PARAMETERS_IMPLEMENTATION_COMPLETE.md` (NEW)

---

## Known Issues

None identified during implementation. Awaiting manual testing.

---

## Next Steps

### Immediate (Phase 6)
- [ ] Manual UI testing with gmail-trim-3 project
- [ ] Test all parameter types (text, int, bool, list)
- [ ] Test verb selection and filtering
- [ ] Verify instance creation end-to-end
- [ ] Test parameter value overrides
- [ ] Verify command construction with verbs

### Future Enhancements (Phase 7)
- [ ] Add "Instance Config" tab to EditScriptModal
- [ ] Allow editing instance configuration post-creation
- [ ] Show current parameter selection in edit dialog
- [ ] Create migration helper tool (optional)
- [ ] Write comprehensive user documentation
- [ ] Consider PR to upstream repository

---

## Completion Checklist

- [x] Phase 1: Backend Foundation
- [x] Phase 2: Config Loading
- [x] Phase 3: Frontend - Project Config UI
- [x] Phase 4: Frontend - Instance Config UI
- [x] Phase 5: Additional Improvements
- [ ] Phase 6: Manual Testing & Verification
- [ ] Phase 7: Documentation & Migration

---

**Implementation:** ✅ **COMPLETE** (5/5 phases)
**Testing:** ⏳ **PENDING** (Manual verification required)
**Documentation:** ✅ **COMPLETE**

**Build Status:** ✅ Frontend builds successfully
**Backend Tests:** ✅ All automated tests passing
