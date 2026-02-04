# Project-Level Parameters - Phase 1 Implementation Complete

**Date:** 2026-02-02
**Status:** ✅ Phase 1 Backend Foundation Complete

---

## Overview

Phase 1 implements the backend foundation for project-level parameter and verb architecture. This is the first phase of a breaking change migration that moves parameter definitions from script-instance level to project level.

### Architecture Change

**Before (Legacy):**
```
conf/runners/Gmail Trim A.json - Full parameter/verb definitions
conf/runners/Gmail Trim B.json - Duplicated definitions
```

**After (New):**
```
projects/gmail-trim/.project-meta.json - Canonical parameter/verb definitions
conf/runners/Gmail Trim A.json - Instance config (selection + values)
conf/runners/Gmail Trim B.json - Instance config (selection + values)
```

---

## Phase 1: Backend Foundation ✅ COMPLETE

### 1.1 Project Metadata Schema

Added two new fields to `.project-meta.json`:

```json
{
  "parameters": [
    {
      "name": "days",
      "type": "int",
      "description": "Number of days to keep emails",
      "required": false,
      "default": 30,
      "min": 1,
      "max": 365,
      "param": "-d"
    }
  ],
  "verbs": {
    "parameter_name": "command",
    "required": true,
    "default": "run",
    "options": [
      {
        "name": "run",
        "label": "Run Cleanup",
        "parameters": ["days", "dry_run"],
        "required_parameters": []
      }
    ]
  },
  "shared_parameters": ["verbose"]
}
```

### 1.2 Script Instance Config Format

New format for `conf/runners/*.json`:

```json
{
  "name": "Gmail Trim A",
  "project_id": "gmail-trim-3",
  "description": "Daily cleanup with 14-day retention",
  "group": "Gmail Automation",
  "scheduling": {"enabled": true},
  "instance_config": {
    "included_parameters": ["days", "dry_run", "verbose"],
    "parameter_values": {
      "days": 14,
      "dry_run": true
    },
    "selected_verb": "run"
  },
  "script_path": "...",
  "working_directory": "..."
}
```

**What's removed:**
- ❌ `parameters` array (moved to project)
- ❌ `verbs` object (moved to project)

**What's added:**
- ✅ `project_id` - Reference to project
- ✅ `instance_config` - Parameter selection and values

### 1.3 ProjectService Changes

**File:** `src/project_manager/project_service.py`

**New methods:**

```python
def update_project_parameters(self, project_id: str, parameters: list[dict]) -> dict:
    """Update parameter definitions for a project."""

def update_project_verbs(
    self, project_id: str,
    verbs_config: Optional[dict],
    shared_params: Optional[list[str]] = None
) -> dict:
    """Update verb configuration for a project."""

def get_project_parameters(self, project_id: str) -> list[dict]:
    """Get parameter definitions from project."""

def get_project_verbs(self, project_id: str) -> Optional[dict]:
    """Get verb configuration from project."""
```

**Modified method:**

```python
def generate_runner_config(
    self,
    project_id: str,
    script_name: str,
    description: Optional[str] = None,
    group: str = 'Imported Projects',
    parameters: Optional[list[dict]] = None,  # LEGACY
    included_parameters: Optional[list[str]] = None,  # NEW
    parameter_values: Optional[dict] = None,  # NEW
    selected_verb: Optional[str] = None  # NEW
) -> str:
    """
    Generate script-server runner configuration.
    Supports both legacy (direct parameters) and new (instance config) formats.
    """
```

### 1.4 ScriptConfig Changes

**File:** `src/model/script_config.py`

**New class:**

```python
class InstanceConfig:
    """Configuration for a script instance (project-based)."""

    def __init__(self, config_dict: dict):
        self.included_parameters = config_dict.get('included_parameters', [])
        self.parameter_values = config_dict.get('parameter_values', {})
        self.selected_verb = config_dict.get('selected_verb')
```

**Modified ConfigModel:**

```python
def __init__(self, config_object, path, username, ...):
    # ...
    project_id = config_object.get('project_id')
    if project_id:
        self._load_from_project(project_id, config_object, username, audit_name)
    else:
        # Legacy standalone script
        self._init_parameters(username, audit_name)
```

**New method:**

```python
def _load_from_project(self, project_id: str, config_object: dict, ...):
    """
    Load parameters and verbs from project metadata.

    1. Load project metadata
    2. Parse instance config
    3. Filter parameters to included_parameters only
    4. Override defaults with instance values
    5. Load verb config and set selected verb
    """
```

### 1.5 API Endpoints

**File:** `src/web/server.py`

**New handlers:**

```python
class GetProjectConfigHandler(BaseRequestHandler):
    """GET /admin/projects/{id}/config - Get parameters and verbs"""

class UpdateProjectParametersHandler(BaseRequestHandler):
    """PUT /admin/projects/{id}/parameters - Update parameter definitions"""

class UpdateProjectVerbsHandler(BaseRequestHandler):
    """PUT /admin/projects/{id}/verbs - Update verb configuration"""
```

**Modified handler:**

```python
class GenerateWrapperHandler(BaseRequestHandler):
    """POST /admin/projects/{id}/wrapper - Supports new instance config params"""
```

**New routes:**

```python
(r'/admin/projects/([^/]+)/config', GetProjectConfigHandler),
(r'/admin/projects/([^/]+)/parameters', UpdateProjectParametersHandler),
(r'/admin/projects/([^/]+)/verbs', UpdateProjectVerbsHandler),
```

---

## Files Modified

1. ✅ `src/project_manager/project_service.py` - Added CRUD methods, modified generate_runner_config
2. ✅ `src/model/script_config.py` - Added InstanceConfig, modified loading logic
3. ✅ `src/web/server.py` - Added API handlers and routes

---

## Backward Compatibility

**Legacy format still supported:**
- Old configs without `project_id` continue to work
- `generate_runner_config()` accepts both `parameters` and `included_parameters`
- ConfigModel detects format and uses appropriate loading path

**New format benefits:**
- DRY principle - define parameters once
- Consistency across instances
- Easier maintenance - update in one place
- Clear separation: Project = capabilities, Instance = configuration

---

## Testing

### Backend Import Test ✅

```bash
$ source .venv/bin/activate && python -c "import sys; sys.path.insert(0, 'src'); from project_manager.project_service import ProjectService; from model.script_config import InstanceConfig; print('Backend imports successful')"
Backend imports successful
```

### Manual Testing Steps

1. **Add parameters to project:**
   ```bash
   # API call to PUT /admin/projects/gmail-trim-3/parameters
   {
     "parameters": [
       {"name": "days", "type": "int", "default": 30, "min": 1, "max": 365},
       {"name": "dry_run", "type": "bool", "default": true},
       {"name": "verbose", "type": "bool", "default": false}
     ]
   }
   ```

2. **Create instance config:**
   ```bash
   # API call to POST /admin/projects/gmail-trim-3/wrapper
   {
     "entry_point": "gmail_cleanup.main:app",
     "script_name": "Gmail Trim Test",
     "included_parameters": ["days", "dry_run"],
     "parameter_values": {"days": 14, "dry_run": true},
     "selected_verb": null
   }
   ```

3. **Verify execution:**
   - Load script in UI
   - Verify only included parameters shown
   - Verify default values from instance config
   - Execute script and check command construction

---

## Next Steps

### Phase 2: Config Loading (In Progress)
- [x] Create `InstanceConfig` class
- [x] Modify `ConfigModel.__init__()` to detect project_id
- [x] Add `_load_from_project()` method
- [ ] Test parameter resolution
- [ ] Test verb resolution
- [ ] Test parameter value overrides

### Phase 3: Frontend - Project Config
- [ ] Create `ProjectConfigModal.vue`
- [ ] Create `ProjectParametersEditor.vue`
- [ ] Integrate `VerbConfigEditor` into project context
- [ ] Add "Configure Project" button to ProjectsModal
- [ ] Wire up API calls

### Phase 4: Frontend - Instance Config
- [ ] Modify `ConfigurePanel.vue` in CreateScriptModal
- [ ] Add parameter selection checkboxes
- [ ] Add parameter value inputs
- [ ] Add verb selection dropdown
- [ ] Update `EditScriptModal` - add instance config tab
- [ ] Update `generateWrapper` API call with new params

### Phase 5: Migration & Testing
- [ ] Create migration helper tool (optional)
- [ ] Write migration documentation
- [ ] Test with gmail-trim project (multiple instances)
- [ ] Integration testing

### Phase 6: Documentation
- [ ] Update user documentation
- [ ] Create migration guide
- [ ] Update API documentation
- [ ] Create example projects

---

## Benefits

✅ **DRY Principle** - Define parameters once, use many times
✅ **Consistency** - All instances share parameter definitions
✅ **Maintainability** - Update in one place → all instances updated
✅ **Clear Separation** - Project = capabilities, Instance = configuration
✅ **Reduced Duplication** - Eliminates ~100-200 lines per instance
✅ **Simpler Configs** - Instance configs are just values, not definitions
✅ **Backward Compatible** - Legacy configs continue to work

---

**Last Updated:** 2026-02-02
**Implementation Status:** Phase 1 Complete, Phase 2 In Progress
