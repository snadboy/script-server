# BaseModal Migration Guide

## Summary
Created `common/components/BaseModal.vue` to eliminate ~700 lines of duplicate modal boilerplate across 19 modal components.

## Completed
✅ Created BaseModal.vue with full functionality
✅ Refactored SettingsModal.vue as proof of concept

## Pattern

### Before (60-70 lines of boilerplate per modal):
```vue
<template>
  <div v-if="visible" class="modal-overlay" @click.self="close">
    <div class="modal-dialog">
      <div class="modal-header">
        <h3>{{ title }}</h3>
        <button class="btn-close" @click="close">×</button>
      </div>
      <div class="modal-body">
        <!-- content -->
      </div>
      <div class="modal-footer">
        <!-- buttons -->
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay { /* 40+ lines of duplicate CSS */ }
.modal-dialog { /* ... */ }
.modal-header { /* ... */ }
.modal-body { /* ... */ }
.modal-footer { /* ... */ }
</style>
```

### After (5-10 lines):
```vue
<template>
  <BaseModal
    :visible="visible"
    title="My Modal"
    modal-class="custom-modal"
    @close="close"
  >
    <!-- content -->

    <template #footer>
      <button @click="close">Cancel</button>
      <button @click="save">Save</button>
    </template>
  </BaseModal>
</template>

<script>
import BaseModal from '@/common/components/BaseModal.vue';

export default {
  components: { BaseModal },
  // ...
}
</script>
```

## Remaining Modals to Migrate (18):

### Main App (13):
- [ ] PythonPackagesModal.vue
- [ ] ConnectionsModal.vue
- [ ] ExecuteModal.vue
- [ ] ParameterHistoryModal.vue
- [ ] ImportProjectModal.vue
- [ ] InstanceSettingsModal.vue
- [ ] ProjectsModal.vue
- [ ] ServerLogsModal.vue
- [ ] DirectoryBrowserModal.vue
- [ ] RequirementsModal.vue
- [ ] ScheduleModal.vue
- [ ] CreateScriptInstanceModal.vue
- [ ] PackagesModal.vue

### Admin (5):
- [ ] UserManagementModal.vue
- [ ] AddScriptModal.vue
- [ ] CreateScriptModal.vue
- [ ] ProjectConfigPlaygroundModal.vue
- [ ] ProjectConfigModal.vue

## BaseModal Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| visible | Boolean | required | Show/hide modal |
| title | String | '' | Modal title (or use #header slot) |
| modalClass | String/Object/Array | '' | Custom class for dialog |
| overlayClass | String/Object/Array | '' | Custom class for overlay |
| headerClass | String/Object/Array | '' | Custom class for header |
| bodyClass | String/Object/Array | '' | Custom class for body |
| footerClass | String/Object/Array | '' | Custom class for footer |
| closeButtonClass | String/Object/Array | '' | Custom class for close button |
| modalStyle | Object | {} | Inline styles for dialog |
| showCloseButton | Boolean | true | Show/hide × button |
| closeText | String | '×' | Close button text |
| closeLabel | String | 'Close modal' | Close button aria-label |
| closeOnOverlayClick | Boolean | true | Close when clicking overlay |

## Slots

- **default**: Modal body content
- **header**: Custom header (replaces title)
- **footer**: Modal footer content

## Events

- **@close**: Emitted when modal should close

## Benefits

1. **DRY**: Eliminates 700+ lines of duplicate code
2. **Consistency**: All modals have identical structure
3. **Maintainability**: Fix bugs in one place
4. **Customization**: Props + slots allow full flexibility
5. **Accessibility**: Built-in ARIA labels
6. **Responsive**: Mobile-friendly by default

## Migration Steps

For each modal:
1. Import BaseModal component
2. Replace outer template with `<BaseModal>`
3. Move title to prop
4. Keep modal body content in default slot
5. Move footer buttons to `#footer` slot
6. Move custom modal sizing to scoped styles
7. Remove duplicate overlay/dialog/header/body/footer CSS
8. Test modal opens/closes correctly

## Estimated Savings

- Average boilerplate per modal: ~40 lines
- Modals to migrate: 18
- Total lines removed: ~720 lines
- Code reduction: ~5% of frontend codebase
