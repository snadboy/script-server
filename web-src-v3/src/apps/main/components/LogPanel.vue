<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import type { LogChunk, DownloadableFile } from '../stores/executionManager'

interface Props {
  logChunks: LogChunk[]
  outputFormat?: 'terminal' | 'html' | 'html_iframe' | 'text'
  inputPrompt?: string | null
  downloadableFiles?: DownloadableFile[]
  inlineImages?: Record<string, string>
}

const props = withDefaults(defineProps<Props>(), {
  outputFormat: 'terminal',
  downloadableFiles: () => [],
  inlineImages: () => ({}),
})

const emit = defineEmits<{
  sendInput: [value: string]
}>()

const containerRef = ref<HTMLDivElement>()
const inputRef = ref<HTMLInputElement>()
const inputValue = ref('')
const autoScroll = ref(true)

const outputText = computed(() => {
  return props.logChunks.map((chunk) => chunk.text).join('')
})

// Auto-scroll to bottom when new content arrives
watch(
  () => props.logChunks.length,
  async () => {
    if (autoScroll.value) {
      await nextTick()
      scrollToBottom()
    }
  }
)

// Focus input when prompt appears
watch(
  () => props.inputPrompt,
  (prompt) => {
    if (prompt) {
      nextTick(() => {
        inputRef.value?.focus()
      })
    }
  }
)

function scrollToBottom() {
  if (containerRef.value) {
    containerRef.value.scrollTop = containerRef.value.scrollHeight
  }
}

function handleScroll() {
  if (!containerRef.value) return

  const { scrollTop, scrollHeight, clientHeight } = containerRef.value
  // Consider "at bottom" if within 50px of the bottom
  autoScroll.value = scrollHeight - scrollTop - clientHeight < 50
}

function handleInputSubmit() {
  if (inputValue.value) {
    emit('sendInput', inputValue.value)
    inputValue.value = ''
  }
}

function handleInputKeydown(event: KeyboardEvent) {
  if (event.key === 'Enter') {
    event.preventDefault()
    handleInputSubmit()
  }
}

onMounted(() => {
  scrollToBottom()
})
</script>

<template>
  <div class="flex flex-col h-full bg-gray-900 rounded-lg overflow-hidden">
    <!-- Output area -->
    <div
      ref="containerRef"
      class="flex-1 overflow-auto p-4 font-mono text-sm text-gray-100 whitespace-pre-wrap break-words"
      @scroll="handleScroll"
    >
      <!-- Terminal output -->
      <div v-if="outputFormat === 'terminal' || outputFormat === 'text'">
        {{ outputText }}
      </div>

      <!-- HTML output (sanitized) -->
      <div
        v-else-if="outputFormat === 'html'"
        class="prose prose-invert max-w-none"
        v-html="outputText"
      />

      <!-- HTML iframe output -->
      <iframe
        v-else-if="outputFormat === 'html_iframe'"
        :srcdoc="outputText"
        class="w-full h-full border-0 bg-white"
      />

      <!-- Inline images -->
      <div v-if="Object.keys(inlineImages).length > 0" class="mt-4 space-y-2">
        <img
          v-for="(url, path) in inlineImages"
          :key="path"
          :src="url"
          :alt="path"
          class="max-w-full rounded"
        />
      </div>

      <!-- Empty state -->
      <div
        v-if="logChunks.length === 0"
        class="text-gray-500 italic"
      >
        Waiting for output...
      </div>
    </div>

    <!-- Downloadable files -->
    <div
      v-if="downloadableFiles.length > 0"
      class="border-t border-gray-700 p-3 bg-gray-800"
    >
      <div class="text-xs text-gray-400 mb-2">Downloadable files:</div>
      <div class="flex flex-wrap gap-2">
        <a
          v-for="file in downloadableFiles"
          :key="file.url"
          :href="file.url"
          download
          class="inline-flex items-center gap-1 px-2 py-1 bg-gray-700 hover:bg-gray-600 rounded text-xs text-gray-200 transition-colors"
        >
          <span class="material-icons text-sm">download</span>
          {{ file.filename }}
        </a>
      </div>
    </div>

    <!-- Input prompt -->
    <div
      v-if="inputPrompt"
      class="border-t border-gray-700 p-3 bg-gray-800"
    >
      <div class="flex items-center gap-2">
        <span class="text-gray-400 text-sm">{{ inputPrompt }}</span>
        <input
          ref="inputRef"
          v-model="inputValue"
          type="text"
          class="flex-1 px-2 py-1 bg-gray-700 border border-gray-600 rounded text-gray-100 text-sm focus:outline-none focus:border-primary"
          @keydown="handleInputKeydown"
        />
        <button
          class="px-3 py-1 bg-primary hover:bg-primary-dark text-white text-sm rounded transition-colors"
          @click="handleInputSubmit"
        >
          Send
        </button>
      </div>
    </div>

    <!-- Auto-scroll indicator -->
    <button
      v-if="!autoScroll"
      class="absolute bottom-20 right-4 p-2 bg-gray-700 hover:bg-gray-600 rounded-full shadow-lg transition-colors"
      title="Scroll to bottom"
      @click="autoScroll = true; scrollToBottom()"
    >
      <span class="material-icons text-gray-300">arrow_downward</span>
    </button>
  </div>
</template>
