import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ScriptConfig, Parameter, ConfigSocketEvent } from '@shared/types/api'

export const useScriptConfigStore = defineStore('scriptConfig', () => {
  const config = ref<ScriptConfig | null>(null)
  const parameters = ref<Parameter[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const connected = ref(false)

  let ws: WebSocket | null = null
  let clientStateVersion = 0
  let messageQueue: unknown[] = []

  const scriptName = computed(() => config.value?.name || null)
  const outputFormat = computed(() => config.value?.outputFormat || 'terminal')
  const schedulingEnabled = computed(() => config.value?.schedulingEnabled || false)

  function getWebSocketUrl(name: string): string {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    return `${protocol}//${host}/scripts/${encodeURIComponent(name)}`
  }

  function connect(name: string) {
    disconnect()
    loading.value = true
    error.value = null

    try {
      ws = new WebSocket(getWebSocketUrl(name))

      ws.onopen = () => {
        connected.value = true
        // Send queued messages
        while (messageQueue.length > 0) {
          const msg = messageQueue.shift()
          if (msg !== undefined) {
            ws?.send(JSON.stringify(msg))
          }
        }
      }

      ws.onclose = (event) => {
        connected.value = false
        loading.value = false

        if (event.code === 401 || event.code === 4001) {
          error.value = 'Unauthorized'
          window.location.href = '/login.html'
        } else if (event.code === 403 || event.code === 4003) {
          error.value = 'Access denied'
        } else if (event.code === 404 || event.code === 4004) {
          error.value = 'Script not found'
        }
      }

      ws.onerror = () => {
        error.value = 'Connection error'
        loading.value = false
      }

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data) as ConfigSocketEvent
          handleMessage(message)
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e)
        }
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to connect'
      loading.value = false
    }
  }

  function handleMessage(message: ConfigSocketEvent) {
    switch (message.event) {
      case 'initialConfig':
        config.value = message.data as ScriptConfig
        parameters.value = (message.data as ScriptConfig).parameters || []
        loading.value = false
        break

      case 'reloadedConfig':
        config.value = message.data as ScriptConfig
        parameters.value = (message.data as ScriptConfig).parameters || []
        break

      case 'parameterChanged': {
        const changedParam = message.data as Parameter
        const index = parameters.value.findIndex((p) => p.name === changedParam.name)
        if (index !== -1) {
          parameters.value[index] = changedParam
        }
        break
      }

      case 'parameterAdded': {
        const newParam = message.data as Parameter
        parameters.value.push(newParam)
        break
      }

      case 'parameterRemoved': {
        const removedName = (message.data as { parameterName: string }).parameterName
        const index = parameters.value.findIndex((p) => p.name === removedName)
        if (index !== -1) {
          parameters.value.splice(index, 1)
        }
        break
      }

      case 'clientStateVersionAccepted':
        // Server acknowledged our state version
        break

      case 'preloadScript':
        // Handle preload script output if needed
        break
    }

    // Update client state version if provided
    if (message.clientStateVersion !== undefined) {
      clientStateVersion = message.clientStateVersion
    }
  }

  function sendParameterValue(paramName: string, value: unknown) {
    clientStateVersion++
    const message = {
      event: 'parameterValue',
      data: {
        parameter: paramName,
        value,
        clientStateVersion,
      },
    }

    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message))
    } else {
      messageQueue.push(message)
    }
  }

  function reloadModel(parameterValues: Record<string, unknown>) {
    clientStateVersion++
    const message = {
      event: 'reloadModelValues',
      data: {
        parameterValues,
        clientModelId: config.value?.id,
        clientStateVersion,
      },
    }

    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message))
    } else {
      messageQueue.push(message)
    }
  }

  function disconnect() {
    if (ws) {
      ws.close()
      ws = null
    }
    config.value = null
    parameters.value = []
    connected.value = false
    loading.value = false
    error.value = null
    clientStateVersion = 0
    messageQueue = []
  }

  return {
    config,
    parameters,
    loading,
    error,
    connected,
    scriptName,
    outputFormat,
    schedulingEnabled,
    connect,
    disconnect,
    sendParameterValue,
    reloadModel,
  }
})
