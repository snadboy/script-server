# Quick Start: New Playground Modal

## TL;DR

✅ New modal component built: `ProjectConfigPlaygroundModal.vue`
✅ 100% playground dark theme match
✅ Frontend builds successfully
⏳ Needs: Wire up in Projects view

---

## 3-Step Integration

### 1. Find the Import (30 seconds)

```bash
cd /home/snadboy/projects/script-server/web-src
grep -r "ProjectConfigModal" src/
```

You'll find something like:
```
src/admin/views/Projects.vue:import ProjectConfigModal from '@/admin/components/projects/ProjectConfigModal.vue';
```

### 2. Update the File (2 minutes)

Open the file (e.g., `src/admin/views/Projects.vue`):

**Change import:**
```js
// OLD
import ProjectConfigModal from '@/admin/components/projects/ProjectConfigModal.vue';

// NEW
import ProjectConfigPlaygroundModal from '@/admin/components/projects/ProjectConfigPlaygroundModal.vue';
```

**Change component registration:**
```js
components: {
  // OLD
  ProjectConfigModal

  // NEW
  ProjectConfigPlaygroundModal
}
```

**Change template:**
```vue
<!-- OLD -->
<ProjectConfigModal
  :visible="showModal"
  :project="selectedProject"
  @close="showModal = false"
  @saved="handleSaved"
/>

<!-- NEW -->
<ProjectConfigPlaygroundModal
  :visible="showModal"
  :project="selectedProject"
  @close="showModal = false"
  @saved="handleSaved"
/>
```

### 3. Rebuild and Test (5 minutes)

```bash
cd /home/snadboy/projects/script-server/web-src
NODE_OPTIONS=--openssl-legacy-provider npm run build

cd /home/snadboy/projects/script-server
source .venv/bin/activate && python launcher.py
```

Open http://localhost:5000/admin and test the modal.

---

## Quick Visual Check

When you open the modal, you should see:

✅ **Dark theme** - Black/dark gray background (#1e1e1e)
✅ **Blue accents** - Buttons and selected rows are blue (#4a90e2)
✅ **Clean layout** - Table above, edit panel below
✅ **Two tabs** - "Parameters" and "Verbs"
✅ **Smooth scrolling** - Tables scroll independently

❌ If you see white background → something went wrong

---

## Quick Functional Check

1. Click "Add Parameter" → parameter appears
2. Click on a parameter row → detail panel updates
3. Switch to "Verbs" tab → verbs section appears
4. Enable verbs → table and controls appear
5. Click "Save" → confirmation message

---

## If Something Goes Wrong

### Rollback (30 seconds)

```js
// Change import back to:
import ProjectConfigModal from '@/admin/components/projects/ProjectConfigModal.vue';

// Change component back to:
ProjectConfigModal

// Change template back to:
<ProjectConfigModal ... />
```

Rebuild and you're back to the old modal.

---

## Full Documentation

- **Architecture:** `PLAYGROUND_MODAL_IMPLEMENTATION.md`
- **Testing Guide:** `TESTING_NEW_MODAL.md`
- **Summary:** `PLAYGROUND_MODAL_SUMMARY.md`
- **This File:** `QUICK_START_NEW_MODAL.md`

---

## Status

✅ Component built
✅ Builds successfully
✅ Documentation complete
⏳ Needs integration

**Time to integrate:** ~10 minutes
**Time to test:** ~30 minutes
**Total:** ~40 minutes

---

## Key Files

```
web-src/src/admin/components/projects/
├── ProjectConfigModal.vue                    ← OLD (keep for rollback)
├── ProjectConfigPlaygroundModal.vue          ← NEW (use this)
├── ProjectParametersEditor.vue               ← OLD (can delete after testing)
└── VerbConfigEditor.vue                      ← OLD (can delete after testing)
```

---

## Success = Dark Theme ✅

If your modal looks like this, you're done:
- Black/dark gray background
- Blue selected rows
- White/gray text
- No white parent modal wrapper

---

**Ready to integrate? Follow the 3 steps above!** 🚀
