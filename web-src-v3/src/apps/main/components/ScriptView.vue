<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useScriptConfigStore } from '../stores/scriptConfig'
import { useScriptSetupStore } from '../stores/scriptSetup'
import { useExecutionManagerStore } from '../stores/executionManager'
import ScriptParametersView from './ScriptParametersView.vue'
import ExecutionInstanceTabs from './ExecutionInstanceTabs.vue'
import TerminalOutput from './TerminalOutput.vue'
import LogPanel from './LogPanel.vue'

interface Props {
  scriptName: string
}

const props = defineProps<Props>()

const configStore = useScriptConfigStore()
const setupStore = useScriptSetupStore()
const executionStore = useExecutionManagerStore()

const { config, loading, error, connected, outputFormat } = storeToRefs(configStore)
const { isValid } = storeToRefs(setupStore)
const { selectedExecution } = storeToRefs(executionStore)

const executing = ref(false)
const executeError = ref<string | null>(null)

// View mode: 'form' or 'output'
const viewMode = ref<'form' | 'output'>('form')

// Auto-switch to output view when execution starts
watch(
  () => selectedExecution.value,
  (execution) => {
    if (execution && (execution.status === 'executing' || execution.status === 'initializing')) {
      viewMode.value = 'output'
    }
  }
)

// Connect to script config when script name changes
watch(
  () => props.scriptName,
  (name) => {
    if (name) {
      configStore.connect(name)
      setupStore.reset()
      viewMode.value = 'form'
    }
  },
  { immediate: true }
)

onUnmounted(() => {
  configStore.disconnect()
})

async function handleExecute() {
  if (!isValid.value || executing.value) return

  executing.value = true
  executeError.value = null

  try {
    const formData = setupStore.buildFormData()
    await executionStore.startExecution(props.scriptName, formData)
    viewMode.value = 'output'
  } catch (e) {
    executeError.value = e instanceof Error ? e.message : 'Failed to start execution'
  } finally {
    executing.value = false
  }
}

function handleSendInput(input: string) {
  if (selectedExecution.value) {
    executionStore.sendInput(selectedExecution.value.id, input)
  }
}

async function handleStop() {
  if (selectedExecution.value) {
    try {
      await executionStore.stopExecution(selectedExecution.value.id)
    } catch (e) {
      console.error('Failed to stop execution:', e)
    }
  }
}

async function handleKill() {
  if (selectedExecution.value) {
    try {
      await executionStore.killExecution(selectedExecution.value.id)
    } catch (e) {
      console.error('Failed to kill execution:', e)
    }
  }
}

function showForm() {
  viewMode.value = 'form'
}

function showOutput() {
  viewMode.value = 'output'
}

const canExecute = computed(() => {
  return connected.value && isValid.value && !executing.value
})

const isRunning = computed(() => {
  return selectedExecution.value?.status === 'executing' || selectedExecution.value?.status === 'initializing'
})
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Header -->
    <div class="flex-none border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
      <div class="flex items-center justify-between px-4 py-3">
        <!-- Script title -->
        <div>
          <h1 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
            {{ config?.name || scriptName }}
          </h1>
          <p v-if="config?.description" class="text-sm text-gray-500 dark:text-gray-400 mt-1">
            {{ config.description }}
          </p>
        </div>

        <!-- Action buttons -->
        <div class="flex items-center gap-3">
          <!-- View toggle -->
          <div class="flex rounded-lg bg-gray-100 dark:bg-gray-800 p-1">
            <button
              class="px-3 py-1 text-sm rounded-md transition-colors"
              :class="viewMode === 'form'
                ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100'"
              @click="showForm"
            >
              <span class="material-icons text-base mr-1 align-text-bottom">tune</span>
              Parameters
            </button>
            <button
              class="px-3 py-1 text-sm rounded-md transition-colors"
              :class="viewMode === 'output'
                ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100'"
              @click="showOutput"
            >
              <span class="material-icons text-base mr-1 align-text-bottom">terminal</span>
              Output
            </button>
          </div>

          <!-- Stop/Kill buttons (when running) -->
          <template v-if="isRunning">
            <button
              class="px-4 py-2 bg-yellow-500 hover:bg-yellow-600 text-white rounded-lg transition-colors flex items-center gap-2"
              @click="handleStop"
            >
              <span class="material-icons text-base">stop</span>
              Stop
            </button>
            <button
              class="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors flex items-center gap-2"
              @click="handleKill"
            >
              <span class="material-icons text-base">close</span>
              Kill
            </button>
          </template>

          <!-- Execute button (when not running) -->
          <button
            v-else
            class="px-4 py-2 bg-primary hover:bg-primary-dark text-white rounded-lg transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="!canExecute"
            @click="handleExecute"
          >
            <span v-if="executing" class="material-icons text-base animate-spin">sync</span>
            <span v-else class="material-icons text-base">play_arrow</span>
            {{ executing ? 'Starting...' : 'Execute' }}
          </button>
        </div>
      </div>

      <!-- Execution tabs -->
      <ExecutionInstanceTabs />
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <span class="material-icons text-4xl text-primary animate-spin">sync</span>
        <p class="text-gray-500 dark:text-gray-400 mt-2">Loading script configuration...</p>
      </div>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <span class="material-icons text-4xl text-red-500">error</span>
        <p class="text-red-500 mt-2">{{ error }}</p>
        <button
          class="mt-4 px-4 py-2 bg-primary hover:bg-primary-dark text-white rounded-lg transition-colors"
          @click="configStore.connect(scriptName)"
        >
          Retry
        </button>
      </div>
    </div>

    <!-- Content -->
    <div v-else class="flex-1 overflow-hidden">
      <!-- Parameters form -->
      <div
        v-show="viewMode === 'form'"
        class="h-full overflow-auto p-4"
      >
        <div class="max-w-2xl mx-auto">
          <ScriptParametersView />

          <!-- Execute error -->
          <div v-if="executeError" class="mt-4 p-3 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg text-red-600 dark:text-red-400">
            {{ executeError }}
          </div>
        </div>
      </div>

      <!-- Output view -->
      <div
        v-show="viewMode === 'output'"
        class="h-full"
      >
        <div v-if="selectedExecution" class="h-full">
          <!-- Use TerminalOutput for terminal format, LogPanel for others -->
          <div class="h-full bg-gray-900 p-4 overflow-auto">
            <TerminalOutput
              v-if="outputFormat === 'terminal'"
              :log-chunks="selectedExecution.logChunks"
              :inline-images="selectedExecution.inlineImages"
            />
            <LogPanel
              v-else
              :log-chunks="selectedExecution.logChunks"
              :output-format="outputFormat"
              :input-prompt="selectedExecution.inputPromptText"
              :downloadable-files="selectedExecution.downloadableFiles"
              :inline-images="selectedExecution.inlineImages"
              @send-input="handleSendInput"
            />
          </div>

          <!-- Input prompt overlay -->
          <div
            v-if="selectedExecution.inputPromptText && outputFormat === 'terminal'"
            class="absolute bottom-0 left-0 right-0 border-t border-gray-700 bg-gray-800 p-3"
          >
            <div class="flex items-center gap-2">
              <span class="text-gray-400 text-sm">{{ selectedExecution.inputPromptText }}</span>
              <input
                type="text"
                class="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded text-gray-100 text-sm focus:outline-none focus:border-primary"
                @keydown.enter="handleSendInput(($event.target as HTMLInputElement).value); ($event.target as HTMLInputElement).value = ''"
              />
              <button
                class="px-4 py-2 bg-primary hover:bg-primary-dark text-white text-sm rounded transition-colors"
                @click="handleSendInput(($refs.inputField as HTMLInputElement)?.value || '')"
              >
                Send
              </button>
            </div>
          </div>
        </div>

        <!-- No execution selected -->
        <div v-else class="h-full flex items-center justify-center bg-gray-100 dark:bg-gray-800">
          <div class="text-center text-gray-500 dark:text-gray-400">
            <span class="material-icons text-4xl mb-2">terminal</span>
            <p>No active execution</p>
            <p class="text-sm mt-1">Click "Execute" to run the script</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
