<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Parameter } from '@shared/types/api'

interface Props {
  modelValue: File | null
  config?: Parameter
  label?: string
  accept?: string
  required?: boolean
  disabled?: boolean
  error?: string
}

const props = withDefaults(defineProps<Props>(), {
  required: false,
  disabled: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: File | null]
}>()

const inputRef = ref<HTMLInputElement>()
const localError = ref<string | null>(null)
const dragOver = ref(false)

const displayLabel = computed(() => props.label || props.config?.name || '')
const displayError = computed(() => props.error || localError.value)
const isRequired = computed(() => props.required || props.config?.required)
const fileName = computed(() => props.modelValue?.name || null)

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0] || null
  emit('update:modelValue', file)
  validate(file)
}

function handleDrop(event: DragEvent) {
  event.preventDefault()
  dragOver.value = false

  const file = event.dataTransfer?.files?.[0] || null
  if (file) {
    emit('update:modelValue', file)
    validate(file)
  }
}

function handleDragOver(event: DragEvent) {
  event.preventDefault()
  dragOver.value = true
}

function handleDragLeave() {
  dragOver.value = false
}

function clearFile() {
  emit('update:modelValue', null)
  if (inputRef.value) {
    inputRef.value.value = ''
  }
}

function openFilePicker() {
  inputRef.value?.click()
}

function validate(file: File | null) {
  localError.value = null

  if (isRequired.value && !file) {
    localError.value = 'Please select a file'
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

    <!-- Hidden file input -->
    <input
      ref="inputRef"
      type="file"
      :accept="accept"
      :disabled="disabled"
      class="hidden"
      @change="handleFileSelect"
    />

    <!-- Drop zone -->
    <div
      class="relative border-2 border-dashed rounded-lg p-4 text-center transition-colors cursor-pointer"
      :class="{
        'border-gray-300 dark:border-gray-600 hover:border-primary': !dragOver && !displayError,
        'border-primary bg-primary/5': dragOver,
        'border-red-500': displayError,
        'opacity-50 cursor-not-allowed': disabled,
      }"
      @click="!disabled && openFilePicker()"
      @drop="!disabled && handleDrop($event)"
      @dragover="!disabled && handleDragOver($event)"
      @dragleave="handleDragLeave"
    >
      <div v-if="fileName" class="flex items-center justify-center gap-2">
        <span class="material-icons text-primary">description</span>
        <span class="text-sm text-gray-700 dark:text-gray-300 truncate max-w-xs">
          {{ fileName }}
        </span>
        <button
          type="button"
          class="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
          @click.stop="clearFile"
        >
          <span class="material-icons text-gray-500 text-lg">close</span>
        </button>
      </div>
      <div v-else class="text-gray-500 dark:text-gray-400">
        <span class="material-icons text-3xl mb-2">cloud_upload</span>
        <p class="text-sm">Drop a file here or click to browse</p>
      </div>
    </div>

    <p v-if="config?.description && !displayError" class="mt-1 text-xs text-gray-500 dark:text-gray-400">
      {{ config.description }}
    </p>
    <p v-if="displayError" class="mt-1 text-xs text-red-500">
      {{ displayError }}
    </p>
  </div>
</template>
