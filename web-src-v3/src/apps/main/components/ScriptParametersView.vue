<script setup lang="ts">
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useScriptConfigStore } from '../stores/scriptConfig'
import { useScriptSetupStore } from '../stores/scriptSetup'
import type { Parameter } from '@shared/types/api'

import TextField from '@shared/components/TextField.vue'
import TextArea from '@shared/components/TextArea.vue'
import Checkbox from '@shared/components/Checkbox.vue'
import Combobox from '@shared/components/Combobox.vue'
import FileUpload from '@shared/components/FileUpload.vue'

const configStore = useScriptConfigStore()
const setupStore = useScriptSetupStore()

const { parameters } = storeToRefs(configStore)
const { parameterValues, errors, forcedValueParameters } = storeToRefs(setupStore)

const COMBOBOX_TYPES = ['list', 'multiselect', 'editable_list']

function getComponentForParameter(param: Parameter) {
  // Checkbox for boolean/flag parameters
  if (param.withoutValue) {
    return Checkbox
  }

  // Combobox for list types
  if (COMBOBOX_TYPES.includes(param.type)) {
    return Combobox
  }

  // File upload
  if (param.type === 'file_upload') {
    return FileUpload
  }

  // TextArea for multiline
  if (param.type === 'multiline_text') {
    return TextArea
  }

  // Default to TextField
  return TextField
}

function getPropsForParameter(param: Parameter) {
  const baseProps = {
    config: param,
    modelValue: parameterValues.value[param.name],
    error: errors.value[param.name] || undefined,
    disabled: forcedValueParameters.value.includes(param.name),
  }

  // Add multiple prop for multiselect
  if (param.type === 'multiselect') {
    return { ...baseProps, multiple: true }
  }

  return baseProps
}

function handleValueChange(paramName: string, value: unknown) {
  setupStore.setValue(paramName, value as any)
}

// Check if parameter should be visible based on dependencies
function isParameterVisible(param: Parameter): boolean {
  if (!param.requiredParameters || param.requiredParameters.length === 0) {
    return true
  }

  // Check if all required parameters have values
  return param.requiredParameters.every((reqParam) => {
    const value = parameterValues.value[reqParam]
    return value !== undefined && value !== null && value !== '' && value !== false
  })
}

const visibleParameters = computed(() => {
  return parameters.value.filter(isParameterVisible)
})
</script>

<template>
  <div class="space-y-4">
    <div
      v-for="param in visibleParameters"
      :key="param.name"
      class="transition-all duration-200"
    >
      <!-- Separator if defined -->
      <div
        v-if="param.ui?.separatorBefore"
        class="border-t border-gray-200 dark:border-gray-700 pt-4 mt-4"
      >
        <h3
          v-if="param.ui.separatorBefore.title"
          class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-4"
        >
          {{ param.ui.separatorBefore.title }}
        </h3>
      </div>

      <!-- Parameter input -->
      <component
        :is="getComponentForParameter(param)"
        v-bind="getPropsForParameter(param)"
        @update:model-value="handleValueChange(param.name, $event)"
      />
    </div>

    <!-- Empty state -->
    <div
      v-if="visibleParameters.length === 0"
      class="text-center py-8 text-gray-500 dark:text-gray-400"
    >
      <span class="material-icons text-4xl mb-2">tune</span>
      <p>No parameters required for this script</p>
    </div>
  </div>
</template>
