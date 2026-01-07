<script setup lang="ts">
import { computed } from 'vue'
import type { Parameter } from '@shared/types/api'

interface Props {
  modelValue: boolean
  config?: Parameter
  label?: string
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const displayLabel = computed(() => props.label || props.config?.name || '')

function handleChange(event: Event) {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.checked)
}
</script>

<template>
  <div class="mb-4 flex items-start gap-3">
    <input
      type="checkbox"
      :checked="modelValue"
      :disabled="disabled"
      class="mt-1 h-4 w-4 rounded border-gray-300 dark:border-gray-600 text-primary focus:ring-primary/50 bg-white dark:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
      @change="handleChange"
    />
    <div class="flex-1">
      <label class="text-sm font-medium text-gray-700 dark:text-gray-300 cursor-pointer">
        {{ displayLabel }}
      </label>
      <p v-if="config?.description" class="text-xs text-gray-500 dark:text-gray-400">
        {{ config.description }}
      </p>
    </div>
  </div>
</template>
