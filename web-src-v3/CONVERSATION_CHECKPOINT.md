# Script-Server Frontend Rebuild - Conversation Checkpoint

**Date:** 2026-01-06
**Status:** MVP Complete - Ready for Testing

## Project Overview

Rebuilding the script-server frontend from Vue 2.7 + Materialize CSS to **Vue 3 + TypeScript + Tailwind CSS** with server-side authentication enforcement.

## What Was Completed

### Phase 1: Backend Auth Modification ✅
- Modified `/home/snadboy/projects/script-server/src/web/web_auth_utils.py`
- Server now returns 401 for HTML files (except login.html) when unauthenticated
- Updated `is_allowed_during_login()` to support Vite asset hashes

### Phase 2: Project Setup ✅
- Created new project at `/home/snadboy/projects/script-server/web-src-v3/`
- Vite 5 + Vue 3.4 + TypeScript + Tailwind CSS + Pinia
- Multi-page app (main, admin, login)
- Build output goes to `../web-v3/`

### Phase 3: Core Infrastructure ✅

**TypeScript Types** (`src/shared/types/api.ts`):
- ScriptConfig, Parameter, ParameterType
- Execution, ExecutionStatus
- Schedule, AuthInfo, ServerConfig

**API Service** (`src/shared/services/api.ts`):
- Axios instance with XSRF token handling
- 401 interceptor redirects to login

**WebSocket Composable** (`src/shared/composables/useWebSocket.ts`):
- Reactive WebSocket wrapper
- Auto-reconnect logic

**Pinia Stores**:
- `auth` - shared/stores/auth.ts
- `scripts` - main/stores/scripts.ts
- `scriptConfig` - main/stores/scriptConfig.ts (WebSocket-based)
- `scriptSetup` - main/stores/scriptSetup.ts
- `executionManager` - main/stores/executionManager.ts

### Phase 4: Components Built ✅

**Base Form Components** (src/shared/components/):
- TextField.vue
- TextArea.vue
- Checkbox.vue
- Combobox.vue
- FileUpload.vue

**Layout Components** (src/apps/main/components/):
- AppLayout.vue
- MainAppSidebar.vue

**Script List** (src/apps/main/components/):
- ScriptsList.vue
- SearchPanel.vue

**Script Execution**:
- ScriptParametersView.vue - Dynamic parameter form
- ScriptView.vue - Main integration component
- ExecutionInstanceTabs.vue - Tab bar for concurrent executions
- TerminalOutput.vue - ANSI-styled terminal output
- LogPanel.vue - Generic output panel (text, html, html_iframe)

**Terminal Model** (src/shared/lib/terminalModel.ts):
- Full TypeScript port of ANSI escape sequence parser
- Supports colors, styles, cursor movement, screen clearing

**Login App** (src/apps/login/):
- App.vue - Login form with username/password

### Phase 5: Views ✅
- HomeView.vue - Welcome screen
- ScriptView.vue (view) - Wrapper using ScriptViewComponent
- HistoryView.vue - Placeholder
- HistoryDetailView.vue - Placeholder

## Build Status

```bash
cd /home/snadboy/projects/script-server/web-src-v3
npm run build  # Successful!
```

Output builds to `/home/snadboy/projects/script-server/web-v3/`

## Running the Servers

**Backend (Python):**
```bash
cd /home/snadboy/projects/script-server
python3 launcher.py
# Runs on port 5000
```

**Frontend (Vite dev server):**
```bash
cd /home/snadboy/projects/script-server/web-src-v3
npm run dev
# Runs on port 5173
```

Access the new frontend at: http://localhost:5173/

## Important Notes

1. **Testing on 'devs' host** - All work/testing done here, NOT on 'utilities'
2. **Run outside Docker** - For testing, run server from source, not Docker container
3. **Vite proxy** - Configured to proxy API calls to backend on port 5000
4. **Login proxy fix** - Changed from `/login` to `^/login$` to prevent proxying login.html

## Next Steps (Post-MVP)

1. **Test the MVP** - Verify login, script list, parameter forms, execution work end-to-end
2. **History Panel** - Build history browsing functionality
3. **Schedule System** - Add scheduling UI
4. **Admin Panel** - Script config editor, user management
5. **Polish** - Error handling, loading states, dark mode toggle

## Key Files Reference

| File | Purpose |
|------|---------|
| `web-src-v3/vite.config.ts` | Build config with proxy settings |
| `web-src-v3/src/apps/main/router/index.ts` | Vue Router config |
| `web-src-v3/src/apps/main/components/ScriptView.vue` | Main execution UI |
| `web-src-v3/src/shared/lib/terminalModel.ts` | ANSI parser |
| `src/web/web_auth_utils.py` | Backend auth (modified) |

## Plan File

Full implementation plan at: `/home/snadboy/.claude/plans/stateless-hopping-ocean.md`
