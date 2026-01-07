<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Parameter } from '@shared/types/api'

interface Props {
  modelValue: string | string[]
  config?: Parameter
  label?: string
  options?: string[]
  multiple?: boolean
  required?: boolean
  disabled?: boolean
  error?: string
}

const props = withDefaults(defineProps<Props>(), {
  multiple: false,
  required: false,
  disabled: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: string | string[]]
}>()

const localError = ref<string | null>(null)

const displayLabel = computed(() => props.label || props.config?.name || '')
const displayError = computed(() => props.error || localError.value)
const isRequired = computed(() => props.required || props.config?.required)
const isMultiple = computed(() => props.multiple || props.config?.type === 'multiselect')
const availableOptions = computed(() => props.options || props.config?.values || [])

function handleChange(event: Event) {
  const target = event.target as HTMLSelectElement

  if (isMultiple.value) {
    const selectedOptions = Array.from(target.selectedOptions).map((opt) => opt.value)
    emit('update:modelValue', selectedOptions)
  } else {
    emit('update:modelValue', target.value)
  }

  validate(target.value)
}

function validate(value: string) {
  localError.value = null

  if (isRequired.value && !value) {
    localError.value = 'Please select an option'
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
    <select
      :value="isMultiple ? undefined : (modelValue as string)"
      :multiple="isMultiple"
      :disabled="disabled"
      :required="isRequired"
      class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      :class="{
        'border-gray-300 dark:border-gray-600': !displayError,
        'border-red-500': displayError,
        'h-32': isMultiple,
      }"
      @change="handleChange"
    >
      <option v-if="!isMultiple && !isRequired" value="">
        -- Select --
      </option>
      <option
        v-for="option in availableOptions"
        :key="option"
        :value="option"
        :selected="isMultiple ? (modelValue as string[])?.includes(option) : modelValue === option"
      >
        {{ option }}
      </option>
    </select>
    <p v-if="config?.description && !displayError" class="mt-1 text-xs text-gray-500 dark:text-gray-400">
      {{ config.description }}
    </p>
    <p v-if="displayError" class="mt-1 text-xs text-red-500">
      {{ displayError }}
    </p>
  </div>
</template>
