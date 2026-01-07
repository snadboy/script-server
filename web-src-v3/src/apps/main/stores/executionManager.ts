import { defineStore } from 'pinia'
import { ref, computed, reactive } from 'vue'
import { api } from '@shared/services/api'
import type { ExecutionStatus, StreamSocketEvent } from '@shared/types/api'

export interface LogChunk {
  text: string
  timestamp: number
}

export interface DownloadableFile {
  url: string
  filename: string
}

export interface ExecutionState {
  id: string
  scriptName: string
  status: ExecutionStatus
  logChunks: LogChunk[]
  inputPromptText: string | null
  downloadableFiles: DownloadableFile[]
  inlineImages: Record<string, string>
  killEnabled: boolean
  exitCode: number | null
  error: string | null
}

export const useExecutionManagerStore = defineStore('executionManager', () => {
  const executions = ref<Map<string, ExecutionState>>(new Map())
  const selectedExecutionId = ref<string | null>(null)
  const websockets = ref<Map<string, WebSocket>>(new Map())

  const selectedExecution = computed(() => {
    if (!selectedExecutionId.value) return null
    return executions.value.get(selectedExecutionId.value) || null
  })

  const activeExecutions = computed(() => {
    return Array.from(executions.value.values()).filter(
      (e) => e.status === 'initializing' || e.status === 'executing'
    )
  })

  const hasActiveExecutions = computed(() => activeExecutions.value.length > 0)

  function getWebSocketUrl(executionId: string): string {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    return `${protocol}//${host}/executions/io/${executionId}`
  }

  async function startExecution(scriptName: string, formData: FormData): Promise<string> {
    // Start execution via API
    const executionId = await api.startExecution(scriptName, formData)

    // Create execution state
    const execution = reactive<ExecutionState>({
      id: executionId,
      scriptName,
      status: 'initializing',
      logChunks: [],
      inputPromptText: null,
      downloadableFiles: [],
      inlineImages: {},
      killEnabled: false,
      exitCode: null,
      error: null,
    })

    executions.value.set(executionId, execution)
    selectedExecutionId.value = executionId

    // Connect to WebSocket for output streaming
    connectToStream(executionId, execution)

    return executionId
  }

  function connectToStream(executionId: string, execution: ExecutionState) {
    const ws = new WebSocket(getWebSocketUrl(executionId))

    ws.onopen = () => {
      execution.status = 'executing'
    }

    ws.onclose = (event) => {
      websockets.value.delete(executionId)

      if (execution.status === 'executing' || execution.status === 'initializing') {
        if (event.code === 401 || event.code === 4001) {
          execution.status = 'error'
          execution.error = 'Unauthorized'
        } else if (event.code === 403 || event.code === 4003) {
          execution.status = 'error'
          execution.error = 'Access denied'
        } else if (event.code === 404 || event.code === 4004) {
          execution.status = 'error'
          execution.error = 'Execution not found'
        } else if (event.code === 1000) {
          // Normal close - execution finished
          execution.status = 'finished'
        } else {
          execution.status = 'disconnected'
        }
      }
    }

    ws.onerror = () => {
      execution.status = 'error'
      execution.error = 'Connection error'
    }

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data) as StreamSocketEvent
        handleStreamMessage(execution, message)
      } catch (e) {
        // Plain text message (rare)
        execution.logChunks.push({
          text: event.data,
          timestamp: Date.now(),
        })
      }
    }

    websockets.value.set(executionId, ws)
  }

  function handleStreamMessage(execution: ExecutionState, message: StreamSocketEvent) {
    switch (message.event) {
      case 'output':
        execution.logChunks.push({
          text: message.data as string,
          timestamp: Date.now(),
        })
        break

      case 'input':
        execution.inputPromptText = message.data as string
        break

      case 'file': {
        const fileData = message.data as { url: string; filename: string }
        execution.downloadableFiles.push(fileData)
        break
      }

      case 'inline-image': {
        const imageData = message.data as { output_path: string; download_url: string }
        execution.inlineImages[imageData.output_path] = imageData.download_url
        break
      }
    }
  }

  function sendInput(executionId: string, input: string) {
    const ws = websockets.value.get(executionId)
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(input)
    }

    // Clear input prompt
    const execution = executions.value.get(executionId)
    if (execution) {
      execution.inputPromptText = null
    }
  }

  async function stopExecution(executionId: string) {
    await api.stopExecution(executionId)
  }

  async function killExecution(executionId: string) {
    await api.killExecution(executionId)
  }

  function selectExecution(executionId: string) {
    if (executions.value.has(executionId)) {
      selectedExecutionId.value = executionId
    }
  }

  function closeExecution(executionId: string) {
    // Close WebSocket if open
    const ws = websockets.value.get(executionId)
    if (ws) {
      ws.close()
      websockets.value.delete(executionId)
    }

    // Remove execution
    executions.value.delete(executionId)

    // Select another execution if this was selected
    if (selectedExecutionId.value === executionId) {
      const remaining = Array.from(executions.value.keys())
      selectedExecutionId.value = remaining.length > 0 ? remaining[0] : null
    }
  }

  async function reconnectActiveExecutions() {
    try {
      const activeIds = await api.getActiveExecutions()

      for (const id of activeIds) {
        if (!executions.value.has(id)) {
          // Get execution config
          const config = await api.getExecutionConfig(id)

          const execution = reactive<ExecutionState>({
            id,
            scriptName: config.scriptName,
            status: 'executing',
            logChunks: [],
            inputPromptText: null,
            downloadableFiles: [],
            inlineImages: {},
            killEnabled: false,
            exitCode: null,
            error: null,
          })

          executions.value.set(id, execution)
          connectToStream(id, execution)
        }
      }

      // Select first if none selected
      if (!selectedExecutionId.value && executions.value.size > 0) {
        selectedExecutionId.value = Array.from(executions.value.keys())[0]
      }
    } catch (e) {
      console.error('Failed to reconnect active executions:', e)
    }
  }

  function clearAll() {
    // Close all WebSockets
    for (const ws of websockets.value.values()) {
      ws.close()
    }
    websockets.value.clear()
    executions.value.clear()
    selectedExecutionId.value = null
  }

  return {
    executions,
    selectedExecutionId,
    selectedExecution,
    activeExecutions,
    hasActiveExecutions,
    startExecution,
    sendInput,
    stopExecution,
    killExecution,
    selectExecution,
    closeExecution,
    reconnectActiveExecutions,
    clearAll,
  }
})
