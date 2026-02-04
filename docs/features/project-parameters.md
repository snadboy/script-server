# Project-Level Parameters & Verbs

**Status:** ✅ Complete (Phases 1-5) - Ready for Phase 6 Manual Testing

## Overview

Major architectural change moving parameter and verb definitions from script-instance level to project level. This enables the DRY principle: define parameters once in `.project-meta.json`, then create multiple instances with different configurations.

## Implementation Phases

### Phase 1: Backend Foundation ✅
- Extended project metadata schema with `parameters`, `verbs`, `shared_parameters`
- New instance config format with `project_id` and `instance_config`
- ProjectService CRUD methods for project-level parameters and verbs
- ConfigModel supports project-based parameter loading
- API endpoints for managing project configuration
- 100% backward compatible with legacy configs

### Phase 2: Config Loading ✅
- `InstanceConfig` class for instance configuration
- `ConfigModel._load_from_project()` method to load from project metadata
- Parameter filtering by `included_parameters`
- Value overrides (instance values override defaults)

### Phase 3: Frontend Project Config UI ✅
- `ProjectConfigModal.vue` - Main configuration modal with Parameters and Verbs tabs
- `ProjectParametersEditor.vue` - CRUD interface for parameter definitions
- Integrated into ProjectsModal with "Configure Parameters & Verbs" button
- API integration complete (GET/PUT endpoints)

### Phase 4: Frontend Instance Config UI ✅
- Added instance configuration section to ConfigurePanel
- Verb selection dropdown with description display
- Parameter selection with checkboxes (verb-filtered)
- Parameter value override inputs (type-specific)
- "Select All" / "Deselect All" quick actions
- Smart default value handling

### Phase 5: Master-Detail UX Redesign ✅
- **Problem:** Modal footer buttons disappeared off-screen when adding many parameters/verbs
- **Solution:** Implemented master-detail pattern with fixed-height scrollable tables
- **ProjectParametersEditor.vue** - Complete rewrite (1076→1142 lines):
  - Fixed-height table (300px) showing parameter summary
  - Edit panel below (400px max) with full form for selected parameter
  - Auto-selects newly added parameters
- **VerbConfigEditor.vue** - Complete rewrite (565→1163 lines):
  - Fixed-height table (250px) showing verb summary
  - Edit panel below (400px max) with parameter selection checkboxes
  - Shared parameters shown with green styling
- **Result:** Modal never grows, footer always visible, can display 50+ items

## Benefits

- ✅ **DRY Principle** - Define parameters once, use many times
- ✅ **Consistency** - All instances share parameter definitions
- ✅ **Maintainability** - Update in one place → all instances updated
- ✅ **Clear Separation** - Project = capabilities, Instance = configuration
- ✅ **Reduced Duplication** - Eliminates ~100-200 lines per instance config

## Test Project

**Location:** `projects/gmail-trim-3/`

**Project Metadata:** `.project-meta.json`
- 4 parameters: `days`, `dry_run`, `verbose`, `labels`
- 5 verbs: `run`, `auth`, `labels`, `groups`, `config`

**Instance Configurations:**
- `Gmail Trim A.json` - 14-day retention (run verb)
- `Gmail Trim B.json` - 60-day retention (run verb)
- `Gmail List Labels.json` - labels verb with verbose only

## New Instance Config Format

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

## API Endpoints

- `GET /admin/projects/{id}/config` - Get project parameters and verbs
- `PUT /admin/projects/{id}/parameters` - Update project parameters
- `PUT /admin/projects/{id}/verbs` - Update project verb configuration

## Testing Results

- ✅ Frontend builds successfully
- ✅ Backend tests: 4/4 passing (100%)
  - ✅ ProjectService loads project metadata with parameters/verbs
  - ✅ ConfigModel loads instance configs with project_id
  - ✅ Parameter filtering works (only included params loaded)
  - ✅ Value overrides work (instance values override defaults)
- ✅ Local server running with latest build: http://localhost:5000

## User Workflow

1. Import Project → Configure Dependencies & Entry Point
2. Click "Configure Parameters & Verbs" in Configure tab
3. Define parameters in Parameters tab (with master-detail UX)
4. Define verbs in Verbs tab (with master-detail UX)
5. Save configuration
6. Create instance: Select Verb → Check Parameters → Override Values → Create

## Files Modified

**Backend:**
- `src/project_manager/project_service.py` - Added CRUD methods, modified generate_runner_config
- `src/model/script_config.py` - Added InstanceConfig class, project-based loading
- `src/web/server.py` - Added 3 new API handlers and routes

**Frontend:**
- `web-src/src/admin/components/projects/ProjectConfigModal.vue` (new)
- `web-src/src/admin/components/projects/ProjectParametersEditor.vue` (complete rewrite)
- `web-src/src/admin/components/scripts-config/VerbConfigEditor.vue` (complete rewrite)
- `web-src/src/admin/components/scripts-config/create-script/ConfigurePanel.vue` (enhanced)
- `web-src/src/admin/components/scripts-config/create-script/CreateScriptModal.vue` (updated API)
- `web-src/src/main-app/components/ProjectsModal.vue` (added integration)

## Documentation

- `docs/PHASE_5_COMPLETE.md` - Comprehensive phase 5 documentation
- `test_project_level_params.py` - Backend test suite

## Commits

1. `419c899` - feat: Implement Phases 1-4 - Project-Level Parameters & Verbs
2. `5c31122` - docs: Add comprehensive documentation for Phases 1-4
3. `acb4bf2` - feat: Complete Phase 5 - Project-Level Parameters with Master-Detail UX
4. `4cf99d0` - docs: Update CLAUDE.md with latest commit info

## Next Steps

- Phase 6: Manual UI testing (server ready at http://localhost:5000)
  1. Test master-detail UX in both Parameters and Verbs tabs
  2. Test adding/editing parameters and verbs with 20+ items
  3. Test instance creation with parameter selection
  4. Verify execution with different verbs
