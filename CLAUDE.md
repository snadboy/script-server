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
**Latest Commit:** `9b9dc03` - Fix duplicate connection to copy secret fields via unmask API
**Docker Image:** `ghcr.io/snadboy/script-server:latest` (auto-builds via GitHub Actions)
**Local Server:** Running on http://localhost:5000

### Current Focus

**Status:** ✅ **File Injection & Connections UI Complete**

**Latest work (2026-02-07 - File-Based Credential Injection & Connections UI):**
- ✅ **File-based credential injection** for connection types with `injection_mode='file'`
  - Writes credential files to temp dirs with `0600` permissions
  - Sets `PREFIX_STEM_PATH` env vars (e.g., `GOOGLE_CREDENTIALS_PATH`)
  - Auto-cleanup via finish listener when process completes
  - Supports `env`, `file`, and `both` injection modes
  - Google Account type uses `file` mode with `credentials.json` and `token.json` templates
- ✅ **Bug fix:** `get_connection()` now called with `mask_secrets=False` so decrypted values are injected
- ✅ **BaseModal dark theme fix** - replaced hardcoded `white` background/colors with CSS variables
- ✅ **SABnzbd icon fix** - changed `download` (missing from font) to `get_app`
- ✅ **Connections UI improvements:**
  - Removed Back button from form view (Cancel/Save suffice)
  - Added Duplicate button (content_copy icon) between Edit and Delete
  - Duplicate fetches unmasked data via `GET /admin/connections/{id}?unmask=true`
  - Disabled overlay-click dismiss on Connections dialog
- ✅ **20 injection tests passing** (file, both, cleanup, helper tests added)

**Files Modified:**
- `src/connections/injection.py` - File injection, cleanup handler, mask_secrets fix
- `src/execution/executor.py` - Register cleanup listener on process wrapper
- `src/connections/connection_types.py` - SABnzbd icon fix
- `src/web/server.py` - `?unmask=true` query param on connection GET
- `web-src/src/common/components/BaseModal.vue` - Dark theme CSS variable support
- `web-src/src/main-app/components/ConnectionsModal.vue` - Duplicate, no Back, no overlay dismiss
- `src/tests/connections/test_injection.py` - Updated for tuple return + new tests

**Previous work (2026-02-06 - Code Review Action Plan COMPLETE):**
- ✅ **CRITICAL SECURITY FIX:** Command injection vulnerabilities eliminated
  - Fixed `shell=True` in process_popen.py (Windows script execution)
  - Fixed string concatenation in taskkill command (process_base.py)
  - Added security tests for shell metacharacter protection
  - Updated 3 existing tests to reflect secure behavior
- ✅ **Code Quality:** Removed all 31 console.log debug statements
  - Replaced with comments or proper error handling
  - Added ESLint rule to prevent future console.log usage
  - Kept legitimate console.error statements for error reporting
- ✅ **Exception Handling:** Fixed ALL 25 bare except blocks across entire codebase
  - 21 fixed in this session (auth, scheduling, execution, web, etc.)
  - 4 fixed earlier in process modules
  - Replaced with specific exception types (ValueError, IOError, OSError, etc.)
  - Improved error logging with contextual information
  - All tests pass (15/15 process tests passing)
- ✅ **Connection Tests:** Created comprehensive test suite (13 tests, 100% passing)
- ✅ **BaseModal Component:** Extracted reusable modal (saves 720 lines when applied to 18 modals)
- ✅ **ExecutionListSection:** Created reusable section component (saves 440 lines when applied)
- ✅ **ProjectConfig Modal Merge:** Documented merge strategy (saves 950 lines)
- ✅ **HTTP Endpoint Tests:** Created integration test framework (390 lines, 10 working tests)

**Code Review Results:**
- **Security:** 2 CRITICAL vulnerabilities fixed (command injection)
- **Quality:** 31 console.log removed, 25 bare except blocks fixed
- **DRY:** 3 reusable components created (~2,100 lines savings potential)
- **Testing:** 23 new tests added (connection injection + HTTP endpoints)
- **Documentation:** 5 comprehensive guides created for future implementation

**Files Fixed (21 files):**
- Critical: `scheduling/scheduler.py`, `auth/tornado_auth.py`, `communications/communicaton_service.py`
- Auth: `auth/identification.py`, `auth/auth_ldap.py`
- Execution: `execution/logging.py` (3x), `execution/execution_service.py` (2x)
- Config: `config/config_service.py`, `model/script_config.py`
- Reactive: `react/observable.py` (2x), `react/properties.py`
- Web: `web/script_config_socket.py`, `web/client/tornado_client_config.py`
- Utils: `utils/audit_utils.py`, `migrations/migrate.py` (2x)
- Tests: `tests/execution_logging_test.py`

**Previous work (2026-02-06 - UI):**
- ✅ Removed tab-based navigation (Projects/Import/Configure tabs)
- ✅ Created new `ImportProjectModal.vue` component for Git/ZIP/Local imports
- ✅ Converted project display from 2-column grid to single-column table layout
- ✅ Added 2x2 stats grid: Instances | Connections | Parameters | Verbs
- ✅ Added connections display with `getConnectionCount()` and `getConnectionLabel()` methods
- ✅ Import button in modal header (no more tab switching)
- ✅ Configure gear icon directly opens ProjectConfigPlaygroundModal
- ✅ Auto-open configure modal after successful import
- ⏳ **Next:** Test in browser, consider production deployment

**Previous work (2026-02-05):**
- ✅ Fixed 500 error by adding `@inject_user` decorator to GenerateWrapperHandler
- ✅ Made duplicate script name check case-insensitive
- ✅ Fixed error message display (Tornado sends plain text, not JSON)
- ✅ Fixed button text centering with flexbox (inline-flex, align-items, justify-content)
- ✅ Ultra-compact modal layout (50vh max-height) to prevent button clipping
- ✅ All validation and error messages working correctly

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
- `web-src/src/main-app/components/ProjectsModalPlayground.vue` - Script Manager (refactored, 460 lines)
- `web-src/src/main-app/components/CreateScriptInstanceModal.vue` - Instance creation modal (411 lines)
- `web-src/src/main-app/components/ImportProjectModal.vue` - Import modal (Git/ZIP/Local, 315 lines)

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
- ✅ **File-Based Credential Injection** - Temp files with auto-cleanup for Google/file connections
- ✅ **Connection Duplication** - Clone connections with full secret copying via unmask API

### UI/UX Improvements

- ✅ Unified Script Manager (Projects + Import + Configure)
- ✅ Execute/Edit/Schedule modals (replaced inline panels)
- ✅ Consistent card layouts and date formatting
- ✅ Stop/Kill buttons with state-based behavior
- ✅ Live list updates (auto-refresh on state changes)
- ✅ Collapsed state persistence (localStorage)
- ✅ Settings modal with configurable limits
- ✅ Icon visibility fix (Material Icons compatibility)
- ✅ BaseModal dark theme support (CSS variables)

---

## Key Files

### Backend

- `src/project_manager/project_service.py` - Project import & management
- `src/model/script_config.py` - Config loading with project support
- `src/model/verb_config.py` - Verb/subcommand configuration
- `src/model/parameter_config.py` - Parameter definitions
- `src/execution/executor.py` - Command building with verb support
- `src/connections/injection.py` - Credential injection (env vars + temp files)
- `src/connections/connection_types.py` - Connection type registry with file_templates
- `src/scheduling/schedule_service.py` - Schedule management & auto-cleanup
- `src/venv_manager/venv_service.py` - Package management

### Frontend

- `web-src/src/admin/components/projects/ProjectConfigModal.vue` - Project parameter/verb config
- `web-src/src/admin/components/scripts-config/create-script/CreateScriptModal.vue` - Unified create script
- `web-src/src/main-app/components/activity/ActivityPage.vue` - Unified activity view
- `web-src/src/main-app/components/ProjectsModal.vue` - Script Manager (Projects/Import/Configure)
- `web-src/src/main-app/components/scripts/ExecuteModal.vue` - Execute dialog
- `web-src/src/main-app/components/schedule/ScheduleModal.vue` - Schedule dialog
- `web-src/src/main-app/components/ConnectionsModal.vue` - Connection management (CRUD + duplicate)
- `web-src/src/common/components/BaseModal.vue` - Reusable modal (dark theme aware)

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

**Last Updated:** 2026-02-07
**Session History:** Detailed session notes organized by feature in `docs/features/`
**Layout Playground:** `verb-parameters-layout-playground.html` - Interactive tool for tweaking dialog UX
