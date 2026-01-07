<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { TerminalModel, type TerminalListener, type StyledRange, type TextColor, type TextStyle } from '@shared/lib/terminalModel'
import type { LogChunk } from '../stores/executionManager'

interface Props {
  logChunks: LogChunk[]
  inlineImages?: Record<string, string>
}

const props = withDefaults(defineProps<Props>(), {
  inlineImages: () => ({}),
})

const terminal = new TerminalModel()
const renderedLines = ref<string[]>([])
const lineStyles = ref<Map<number, StyledRange[]>>(new Map())

// Track processed chunks to avoid reprocessing
let processedChunkCount = 0

const listener: TerminalListener = {
  linesChanges(changedLines: number[]) {
    for (const lineIndex of changedLines) {
      renderedLines.value[lineIndex] = terminal.lines[lineIndex] || ''
    }
    lineStyles.value = new Map(terminal.lineStyles)
  },
  cleared() {
    renderedLines.value = []
    lineStyles.value = new Map()
    processedChunkCount = 0
  },
  linesDeleted(startLine: number, _oldEnd: number) {
    renderedLines.value = renderedLines.value.slice(0, startLine)
    lineStyles.value = new Map(terminal.lineStyles)
  },
}

// Color mappings for terminal colors
const colorMap: Record<string, string> = {
  red: '#f44336',
  black: '#000000',
  green: '#4caf50',
  yellow: '#ffeb3b',
  blue: '#2196f3',
  magenta: '#e91e63',
  cyan: '#00bcd4',
  lightgray: '#9e9e9e',
  darkgray: '#616161',
  lightred: '#ef5350',
  lightgreen: '#66bb6a',
  lightyellow: '#ffee58',
  lightblue: '#42a5f5',
  lightmagenta: '#ec407a',
  lightcyan: '#26c6da',
  white: '#ffffff',
}

function getColorStyle(color: TextColor): string {
  if (!color) return ''
  return colorMap[color] || ''
}

function getStyleClasses(styles: TextStyle[]): string {
  const classes: string[] = []
  for (const style of styles) {
    switch (style) {
      case 'bold':
        classes.push('font-bold')
        break
      case 'dim':
        classes.push('opacity-50')
        break
      case 'underlined':
        classes.push('underline')
        break
      case 'hidden':
        classes.push('invisible')
        break
    }
  }
  return classes.join(' ')
}

function renderLine(lineIndex: number): { text: string; style?: string; classes?: string }[] {
  const line = renderedLines.value[lineIndex] || ''
  const styles = lineStyles.value.get(lineIndex)

  if (!styles || styles.length === 0) {
    return [{ text: line || '\n' }]
  }

  const segments: { text: string; style?: string; classes?: string }[] = []
  let lastEnd = 0

  for (const range of styles) {
    // Add unstyled text before this range
    if (range.start > lastEnd) {
      segments.push({ text: line.substring(lastEnd, range.start) })
    }

    // Add styled text
    const styleStr: string[] = []
    const classes: string[] = []

    if (range.style) {
      if (range.style.color) {
        styleStr.push(`color: ${getColorStyle(range.style.color)}`)
      }
      if (range.style.background) {
        styleStr.push(`background-color: ${getColorStyle(range.style.background)}`)
      }
      if (range.style.styles.length > 0) {
        classes.push(getStyleClasses(range.style.styles))
      }
    }

    segments.push({
      text: line.substring(range.start, range.end),
      style: styleStr.join('; '),
      classes: classes.join(' '),
    })

    lastEnd = range.end
  }

  // Add remaining unstyled text
  if (lastEnd < line.length) {
    segments.push({ text: line.substring(lastEnd) })
  }

  // Ensure empty lines still render
  if (segments.length === 0 || (segments.length === 1 && segments[0].text === '')) {
    return [{ text: '\n' }]
  }

  return segments
}

// Process new log chunks
watch(
  () => props.logChunks,
  (chunks) => {
    // Process only new chunks
    for (let i = processedChunkCount; i < chunks.length; i++) {
      terminal.write(chunks[i].text)
    }
    processedChunkCount = chunks.length
  },
  { deep: true }
)

// Handle inline images
watch(
  () => props.inlineImages,
  (images) => {
    // Update terminal inline images
    for (const [path, url] of Object.entries(images)) {
      terminal.setInlineImage(path, url)
    }
  },
  { deep: true, immediate: true }
)

onMounted(() => {
  terminal.addListener(listener)

  // Process existing chunks
  for (const chunk of props.logChunks) {
    terminal.write(chunk.text)
  }
  processedChunkCount = props.logChunks.length
})

onUnmounted(() => {
  terminal.removeListener(listener)
})

const lineCount = computed(() => renderedLines.value.length || 1)
</script>

<template>
  <div class="terminal-output font-mono text-sm leading-relaxed">
    <div v-for="lineIndex in lineCount" :key="lineIndex - 1" class="whitespace-pre-wrap break-words">
      <template v-for="(segment, segIndex) in renderLine(lineIndex - 1)" :key="segIndex">
        <span
          v-if="segment.style || segment.classes"
          :style="segment.style"
          :class="segment.classes"
        >{{ segment.text }}</span>
        <template v-else>{{ segment.text }}</template>
      </template>
    </div>

    <!-- Inline images -->
    <div v-if="Object.keys(inlineImages).length > 0" class="mt-4 space-y-2">
      <img
        v-for="(url, path) in inlineImages"
        :key="path"
        :src="url"
        :alt="String(path)"
        class="max-w-full rounded"
      />
    </div>

    <!-- Empty state -->
    <div
      v-if="renderedLines.length === 0 && logChunks.length === 0"
      class="text-gray-500 italic"
    >
      Waiting for output...
    </div>
  </div>
</template>
