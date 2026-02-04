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
**Latest Commit:** `909c8eb` - Reorganize CLAUDE.md by feature area and add layout playground
**Docker Image:** `ghcr.io/snadboy/script-server:latest` (auto-builds via GitHub Actions)
**Local Server:** Running on http://localhost:5000

### Current Focus

**Status:** ✅ **Playground Modal DEPLOYED** - Ready for testing

**Latest work (2026-02-04):**
- ✅ Created brand new `ProjectConfigPlaygroundModal.vue` from playground prototype
- ✅ 100% pixel-perfect match to playground dark theme (#1e1e1e, #2a2a2a, #4a90e2)
- ✅ Inline master-detail layout (no child components)
- ✅ All functionality ported: parameters, verbs, save/load, validation
- ✅ Clean architecture: single ~850 LOC file, easy to maintain
- ✅ Frontend builds successfully with no errors
- ✅ Wired up in `ProjectsModal.vue` (replaced old modal)
- ✅ Server running at http://localhost:5000
- ⏳ **Next:** Manual UI testing (see `TESTING_NEW_MODAL.md`)
- 📝 Old components kept for easy rollback if needed

**Files Modified:**
- `web-src/src/main-app/components/ProjectsModal.vue` - Updated import and usage
- Import changed: `ProjectConfigModal` → `ProjectConfigPlaygroundModal`

**Documentation:**
- `QUICK_START_NEW_MODAL.md` - 3-step integration guide (✅ COMPLETE)
- `PLAYGROUND_MODAL_SUMMARY.md` - Complete implementation summary
- `PLAYGROUND_MODAL_IMPLEMENTATION.md` - Architecture details
- `TESTING_NEW_MODAL.md` - Comprehensive testing checklist

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
