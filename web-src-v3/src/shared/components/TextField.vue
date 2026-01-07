<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Parameter } from '@shared/types/api'

interface Props {
  modelValue: string | number
  config?: Parameter
  label?: string
  type?: 'text' | 'number' | 'password' | 'email'
  placeholder?: string
  required?: boolean
  disabled?: boolean
  error?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  required: false,
  disabled: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
}>()

const inputRef = ref<HTMLInputElement>()
const localError = ref<string | null>(null)

const displayLabel = computed(() => props.label || props.config?.name || '')
const displayError = computed(() => props.error || localError.value)
const isRequired = computed(() => props.required || props.config?.required)
const inputType = computed(() => {
  if (props.config?.secure) return 'password'
  if (props.config?.type === 'int') return 'number'
  return props.type
})

function handleInput(event: Event) {
  const target = event.target as HTMLInputElement
  let value: string | number = target.value

  if (inputType.value === 'number' && value !== '') {
    value = Number(value)
  }

  emit('update:modelValue', value)
  validate(target.value)
}

function validate(value: string) {
  localError.value = null

  if (isRequired.value && !value) {
    localError.value = 'This field is required'
    return
  }

  if (props.config?.type === 'int' && value) {
    const num = Number(value)
    if (isNaN(num)) {
      localError.value = 'Must be a number'
      return
    }
    if (props.config.min !== undefined && num < props.config.min) {
      localError.value = `Minimum value is ${props.config.min}`
      return
    }
    if (props.config.max !== undefined && num > props.config.max) {
      localError.value = `Maximum value is ${props.config.max}`
      return
    }
  }

  if (props.config?.maxLength && value.length > props.config.maxLength) {
    localError.value = `Maximum length is ${props.config.maxLength}`
    return
  }

  if (props.config?.regex && value) {
    const regex = new RegExp(props.config.regex)
    if (!regex.test(value)) {
      localError.value = 'Invalid format'
      return
    }
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
    <input
      ref="inputRef"
      :type="inputType"
      :value="modelValue"
      :placeholder="placeholder || config?.description"
      :disabled="disabled"
      :required="isRequired"
      :min="config?.min"
      :max="config?.max"
      :maxlength="config?.maxLength"
      class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
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
