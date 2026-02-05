# Script Server Fork - Project Context

> **Detailed documentation:** See `docs/features/` for comprehensive feature documentation organized by area.

---

## Repository

- **Fork:** https://github.com/snadboy/script-server
- **Upstream:** https://github.com/bugy/script-server
- **Local Path:** `/home/snadboy/projects/script-server`
- **Main Branch:** `master`

---

## Current State

**Branch:** `master`
**Latest Commit:** `bc8307f` - Improve script instance creation error handling
**Docker Image:** `ghcr.io/snadboy/script-server:latest` (auto-builds via GitHub Actions)
**Local Server:** Running on http://localhost:5000

### Current Focus

**Status:** ✅ **CreateScriptInstanceModal Complete** - All error handling and validation working

**Latest work (2026-02-05):**
- ✅ Fixed 500 error by adding `@inject_user` decorator to GenerateWrapperHandler
- ✅ Made duplicate script name check case-insensitive
- ✅ Fixed error message display (Tornado sends plain text, not JSON)
- ✅ Fixed button text centering with flexbox (inline-flex, align-items, justify-content)
- ✅ Ultra-compact modal layout (50vh max-height) to prevent button clipping
- ✅ All validation and error messages working correctly
- ⏳ **Next:** Ready for production use, consider Docker image push

**Previous work (2026-02-04):**
- ✅ Created `script-manager-playground.html` interactive design tool
- ✅ Built brand new `ProjectsModalPlayground.vue` from scratch
- ✅ Card-based 2-column grid layout (not table-based rows)
- ✅ Exact match to playground dark theme (#1a1a1a, #222222, #5dade2, #333333)
- ✅ Three tabs: Projects, Import, Configure
- ✅ Created separate `CreateScriptInstanceModal.vue` for instance creation
- ✅ Group selection dropdown with existing groups and new group confirmation

**Commits (9 total):**
1. `03951e2` - Complete rebuild with card-based grid layout
2. `29bdfd0` - Fix CSS variables (moved from :root to .projects-modal-overlay)
3. `9e135b0` - Reorganize Configure tab, extract Create Script Instance modal
4. `b758f9d` - Remove 405 error, fix cutoff buttons
5. `c55ccb9` - Use correct endpoint (/admin/projects/{id}/wrapper)
6. `c438c58` - Add group selection, improve modal UX
7. `21af915` - Prevent duplicate script names in backend
8. `aef9a3d` - Proper error handling (preserve 400 status), compact layout
9. `bc8307f` - Improve error handling and case-insensitive duplicate check

**Files Created:**
- `script-manager-playground.html` - Interactive design playground
- `web-src/src/main-app/components/ProjectsModalPlayground.vue` - New Script Manager (795 lines)
- `web-src/src/main-app/components/CreateScriptInstanceModal.vue` - Instance creation modal (411 lines)

**Files Modified:**
- `web-src/src/main-app/components/MainAppSidebar.vue` - Import ProjectsModalPlayground
- `src/web/server.py` - Duplicate validation in GenerateWrapperHandler

**Documentation:**
- `QUICK_START_NEW_MODAL.md` - 3-step integration guide (✅ COMPLETE)
- `PLAYGROUND_MODAL_SUMMARY.md` - Complete implementation summary
- `PLAYGROUND_MODAL_IMPLEMENTATION.md` - Architecture details
- `TESTING_NEW_MODAL.md` - Comprehensive testing checklist
- `MODAL_UX_IMPROVEMENTS.md` - UX refinements changelog (NEW)

---

## Quick Reference

### Build Commands

```bash
# Frontend build
cd web-src
NODE_OPTIONS=--openssl-legacy-provider npm run build

# Start server (use venv - tornado installed there)
cd /home/snadboy/projects/script-server
source .venv/bin/activate && python launcher.py

# Docker build
docker build -t script-server:custom .
```

### Test Project

**Location:** `projects/gmail-trim-3/`
- 4 parameters: `days`, `dry_run`, `verbose`, `labels`
- 5 verbs: `run`, `auth`, `labels`, `groups`, `config`
- 3 instance configs: Gmail Trim A, Gmail Trim B, Gmail List Labels

### Deployment

- **Docker Image:** `ghcr.io/snadboy/script-server:latest`
- **GitHub Actions:** Auto-builds on push to master
- **Deployment:** Update Dockhand stack on utilities host

---

## Feature Documentation

Detailed implementation notes organized by feature area:

| Document | Description |
|----------|-------------|
| [project-parameters.md](docs/features/project-parameters.md) | Project-level parameters & verbs (Phases 1-5) |
| [parameter-configuration.md](docs/features/parameter-configuration.md) | Simplified parameter UI & dual-flag booleans |
| [verbs.md](docs/features/verbs.md) | CLI verb/subcommand support |
| [import-workflow.md](docs/features/import-workflow.md) | Import-only architecture & project manager |
| [scheduling.md](docs/features/scheduling.md) | Schedule features (auto-cleanup, editing, etc.) |
| [ui-ux.md](docs/features/ui-ux.md) | Unified activity page, modals, consistency |
| [code-quality.md](docs/features/code-quality.md) | Code quality improvements & type safety |

---

## Completed Features Summary

### Major Features

- ✅ **Project-Level Parameters** - Define parameters once, create multiple instances
- ✅ **CLI Verb/Subcommand Support** - Scripts with multiple commands (git-style)
- ✅ **Import-Only Architecture** - Auto-managed paths with sandboxed execution
- ✅ **Unified Activity Page** - Running, Scheduled, Completed in one view
- ✅ **Schedule Auto-Cleanup** - One-time schedules auto-delete after completion
- ✅ **Simplified Parameter UI** - Reduced from 11 to 6 parameter types
- ✅ **Dual-Flag Booleans** - Support for opposing flags (--verbose/--quiet)
- ✅ **Master-Detail UX** - Fixed-height tables for parameter/verb editing
- ✅ **Project Manager** - Import projects via Git/ZIP/Local with auto-detection
- ✅ **Venv Package Management** - Admin UI for Python package management

### UI/UX Improvements

- ✅ Unified Script Manager (Projects + Import + Configure)
- ✅ Execute/Edit/Schedule modals (replaced inline panels)
- ✅ Consistent card layouts and date formatting
- ✅ Stop/Kill buttons with state-based behavior
- ✅ Live list updates (auto-refresh on state changes)
- ✅ Collapsed state persistence (localStorage)
- ✅ Settings modal with configurable limits
- ✅ Icon visibility fix (Material Icons compatibility)

---

## Key Files

### Backend

- `src/project_manager/project_service.py` - Project import & management
- `src/model/script_config.py` - Config loading with project support
- `src/model/verb_config.py` - Verb/subcommand configuration
- `src/model/parameter_config.py` - Parameter definitions
- `src/execution/executor.py` - Command building with verb support
- `src/scheduling/schedule_service.py` - Schedule management & auto-cleanup
- `src/venv_manager/venv_service.py` - Package management

### Frontend

- `web-src/src/admin/components/projects/ProjectConfigModal.vue` - Project parameter/verb config
- `web-src/src/admin/components/scripts-config/create-script/CreateScriptModal.vue` - Unified create script
- `web-src/src/main-app/components/activity/ActivityPage.vue` - Unified activity view
- `web-src/src/main-app/components/ProjectsModal.vue` - Script Manager (Projects/Import/Configure)
- `web-src/src/main-app/components/scripts/ExecuteModal.vue` - Execute dialog
- `web-src/src/main-app/components/schedule/ScheduleModal.vue` - Schedule dialog

---

## Next Steps

1. **Phase 6: Manual UI Testing**
   - Test master-detail UX with 20+ parameters/verbs
   - Test instance creation with parameter selection
   - Verify execution with different verbs
   - Test all parameter types and value overrides

2. **Future Considerations**
   - Consider PR to upstream for verb/parameter features
   - Update gmail_trim.json to use new project-level parameters
   - Documentation for end users

---

## Related Projects

### Gmail Cleanup Integration

**Wrapper Script:** `samples/scripts/gmail_cleanup.py`
**Config:** `conf/runners/gmail_cleanup.json`
**Source:** `/home/snadboy/projects/gm`

**Required packages** (install via Package Manager):
- google-api-python-client, google-auth-oauthlib, google-auth
- pydantic, pydantic-settings, structlog, typer, pyyaml

**Documentation:** See `docs/wrapping-python-projects.md`

---

**Last Updated:** 2026-02-04
**Session History:** Detailed session notes organized by feature in `docs/features/`
**Layout Playground:** `verb-parameters-layout-playground.html` - Interactive tool for tweaking dialog UX
