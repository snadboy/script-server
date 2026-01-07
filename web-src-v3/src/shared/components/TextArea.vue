<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Parameter } from '@shared/types/api'

interface Props {
  modelValue: string
  config?: Parameter
  label?: string
  placeholder?: string
  rows?: number
  required?: boolean
  disabled?: boolean
  error?: string
}

const props = withDefaults(defineProps<Props>(), {
  rows: 4,
  required: false,
  disabled: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const localError = ref<string | null>(null)

const displayLabel = computed(() => props.label || props.config?.name || '')
const displayError = computed(() => props.error || localError.value)
const isRequired = computed(() => props.required || props.config?.required)

function handleInput(event: Event) {
  const target = event.target as HTMLTextAreaElement
  emit('update:modelValue', target.value)
  validate(target.value)
}

function validate(value: string) {
  localError.value = null

  if (isRequired.value && !value) {
    localError.value = 'This field is required'
    return
  }

  if (props.config?.maxLength && value.length > props.config.maxLength) {
    localError.value = `Maximum length is ${props.config.maxLength}`
    return
  }
}
</script>

<template>
  <div class="mb-4">
    <label
      v-if="displayLabel"
      class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
    >
      {{ displayLabel }}
      <span v-if="isRequired" class="text-red-500">*</span>
    </label>
    <textarea
      :value="modelValue"
      :placeholder="placeholder || config?.description"
      :rows="rows"
      :disabled="disabled"
      :required="isRequired"
      :maxlength="config?.maxLength"
      class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-colors disabled:opacity-50 disabled:cursor-not-allowed resize-y font-mono text-sm"
      :class="{
        'border-gray-300 dark:border-gray-600': !displayError,
        'border-red-500': displayError,
      }"
      @input="handleInput"
    />
    <p v-if="config?.description && !displayError" class="mt-1 text-xs text-gray-500 dark:text-gray-400">
      {{ config.description }}
    </p>
    <p v-if="displayError" class="mt-1 text-xs text-red-500">
      {{ displayError }}
    </p>
  </div>
</template>
