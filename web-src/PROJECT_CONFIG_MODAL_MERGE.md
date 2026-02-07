# ProjectConfig Modal Merge Plan

## Summary
Merge ProjectConfigModal.vue (556 lines) and ProjectConfigPlaygroundModal.vue (1,594 lines) into a single component with mode switching.

**Total duplication: ~75% (1,600+ duplicate lines)**

## File Analysis

### ProjectConfigModal.vue (556 lines)
- Standard modal styling
- Basic 3-tab layout: Parameters, Verbs, Connections
- Uses ProjectParametersEditor component
- Uses VerbConfigEditor component
- Simple connection type checkboxes
- Material Design styling

### ProjectConfigPlaygroundModal.vue (1,594 lines)
- Enhanced "playground" dark theme
- Same 3-tab layout: Parameters, Verbs, Connections
- **Inline parameter editor** (master-detail, 600+ lines)
- **Inline verb editor** (master-detail, 400+ lines)
- Same connection type checkboxes
- Custom dark theme (#1a1a1a, #222222, etc.)

## Key Differences

| Feature | Standard | Playground |
|---------|----------|-----------|
| **Styling** | Material Design | Custom dark theme |
| **Parameter Editor** | External component | Inline master-detail |
| **Verb Editor** | External component | Inline master-detail |
| **Empty States** | Basic | Enhanced with icons |
| **Move Up/Down** | Not visible | Prominent buttons |
| **Layout** | Simple | Master-detail split |
| **Lines** | 556 | 1,594 |

## Merge Strategy

### Option 1: Mode Prop (Recommended)

Create single component with `mode` prop:

```vue
<script>
export default {
  name: 'ProjectConfigModal',
  props: {
    mode: {
      type: String,
      default: 'standard',
      validator: v => ['standard', 'playground'].includes(v)
    }
  }
}
</script>

<template>
  <div
    v-if="visible"
    :class="mode === 'playground' ? 'dialog-overlay' : 'modal-overlay'"
  >
    <!-- Conditional rendering based on mode -->
    <component
      :is="mode === 'playground' ? 'div' : 'div'"
      :class="getDialogClass"
    >
      <!-- Common header structure -->
      <!-- Common tabs structure -->
      <!-- Conditional content rendering -->
    </component>
  </div>
</template>
```

#### Benefits
- Single source of truth
- Easy to maintain
- Can switch modes dynamically
- Preserves both UX patterns

#### Drawbacks
- More conditional logic
- Slightly larger component (~1,200 lines after merge)

### Option 2: Extract Shared Base (Alternative)

Create `ProjectConfigBase.vue` with:
- Tab structure
- Save/load logic
- State management

Extend with:
- `ProjectConfigStandard.vue` (150 lines)
- `ProjectConfigPlayground.vue` (400 lines)

#### Benefits
- Clean separation
- Easier to test

#### Drawbacks
- More files
- Inheritance complexity

## Recommended Approach: Mode Prop

### Implementation Steps

#### 1. Start with Playground version (more complete)
```bash
cp ProjectConfigPlaygroundModal.vue ProjectConfigModal.vue.new
```

#### 2. Add mode prop and conditionals

```vue
<script>
export default {
  props: {
    mode: {
      type: String,
      default: 'standard',
      validator: v => ['standard', 'playground'].includes(v)
    },
    // ... existing props
  },

  computed: {
    dialogClass() {
      return this.mode === 'playground'
        ? 'dialog-preview'
        : 'modal-dialog project-config-modal';
    },
    overlayClass() {
      return this.mode === 'playground'
        ? 'dialog-overlay'
        : 'modal-overlay';
    },
    useInlineEditors() {
      return this.mode === 'playground';
    }
  }
}
</script>
```

#### 3. Conditional parameter editor

```vue
<!-- Parameters Tab -->
<div v-if="activeTab === 'parameters'" class="tab-content">
  <!-- Playground: Inline editor -->
  <template v-if="useInlineEditors">
    <!-- Inline master-detail parameter editor -->
    <div class="master-detail">
      <!-- ... playground editor code ... -->
    </div>
  </template>

  <!-- Standard: External component -->
  <template v-else>
    <ProjectParametersEditor
      v-model="parameters"
      :verbs="verbsConfig"
      :shared-parameters="sharedParameters"
      @update:modelValue="markUnsaved"
    />
  </template>
</div>
```

#### 4. Conditional verb editor

```vue
<!-- Verbs Tab -->
<div v-if="activeTab === 'verbs'" class="tab-content">
  <!-- Playground: Inline editor -->
  <template v-if="useInlineEditors">
    <!-- Inline master-detail verb editor -->
    <div class="master-detail">
      <!-- ... playground editor code ... -->
    </div>
  </template>

  <!-- Standard: External component -->
  <template v-else>
    <VerbConfigEditor
      v-model:verbs-config="verbsConfig"
      :available-parameters="parameterNames"
      @update:verbsConfig="markUnsaved"
    />
  </template>
</div>
```

#### 5. Conditional styling

```vue
<style scoped>
/* Common styles */
.modal-overlay,
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-overlay {
  background: rgba(0, 0, 0, 0.5);
}

.dialog-overlay {
  background: rgba(0, 0, 0, 0.6);
}

/* Standard mode styles */
.modal-dialog.project-config-modal {
  /* Material Design styles */
}

/* Playground mode styles */
.dialog-preview {
  /* Custom dark theme styles */
}
</style>
```

#### 6. Update imports

```javascript
// ProjectsModal.vue
import ProjectConfigModal from '@/admin/components/projects/ProjectConfigModal.vue';

// ProjectsModalPlayground.vue
import ProjectConfigModal from '@/admin/components/projects/ProjectConfigModal.vue';

// Usage in standard mode
<ProjectConfigModal
  :visible="showConfigModal"
  :project="selectedProject"
  @close="closeConfigModal"
/>

// Usage in playground mode
<ProjectConfigModal
  :visible="showConfigModal"
  :project="selectedProject"
  mode="playground"
  @close="closeConfigModal"
/>
```

#### 7. Delete old files

```bash
rm ProjectConfigPlaygroundModal.vue
```

## Expected Results

### Before Merge
- ProjectConfigModal.vue: 556 lines
- ProjectConfigPlaygroundModal.vue: 1,594 lines
- **Total: 2,150 lines**

### After Merge
- ProjectConfigModal.vue: ~1,200 lines (with mode support)
- **Savings: ~950 lines (44% reduction)**

## Testing Checklist

- [ ] Standard mode renders correctly
- [ ] Playground mode renders correctly
- [ ] Can switch between modes
- [ ] Parameter editor works in both modes
- [ ] Verb editor works in both modes
- [ ] Connection selection works
- [ ] Save/load works in both modes
- [ ] Styling correct in both modes
- [ ] No console errors
- [ ] All parent components still work

## Alternative: Keep Separate (Not Recommended)

If merge is too risky:

1. Extract shared logic to composables
2. Create shared parameter/verb editing logic
3. Keep separate files but reduce duplication to ~30%
4. Savings: ~600 lines instead of 950

## Recommendation

**Proceed with Mode Prop merge** for maximum code reduction and maintainability. The conditional logic is straightforward and the mode switching provides flexibility for future enhancements.

## Estimated Time

- Analysis: ✅ Complete
- Implementation: 3-4 hours
- Testing: 1-2 hours
- **Total: 4-6 hours**

## Status

✅ Analysis complete
✅ Merge strategy documented
⏳ Implementation pending
