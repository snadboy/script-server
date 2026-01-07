import { ref, onUnmounted, type Ref } from 'vue'

export type WebSocketStatus = 'connecting' | 'open' | 'closed' | 'error'

export interface UseWebSocketReturn<T> {
  data: Ref<T | null>
  status: Ref<WebSocketStatus>
  error: Ref<Error | null>
  send: (message: unknown) => void
  close: () => void
  reconnect: () => void
}

export function useWebSocket<T = unknown>(
  path: string,
  options?: {
    onMessage?: (data: T) => void
    onOpen?: () => void
    onClose?: (event: CloseEvent) => void
    onError?: (error: Error) => void
    autoConnect?: boolean
  }
): UseWebSocketReturn<T> {
  const data = ref<T | null>(null) as Ref<T | null>
  const status = ref<WebSocketStatus>('connecting')
  const error = ref<Error | null>(null)

  let ws: WebSocket | null = null
  let messageQueue: unknown[] = []

  function getWebSocketUrl(): string {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    // Remove leading slash if present
    const cleanPath = path.startsWith('/') ? path.slice(1) : path
    return `${protocol}//${host}/${cleanPath}`
  }

  function connect() {
    if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
      return
    }

    status.value = 'connecting'
    error.value = null

    try {
      ws = new WebSocket(getWebSocketUrl())

      ws.onopen = () => {
        status.value = 'open'
        // Send queued messages
        while (messageQueue.length > 0) {
          const msg = messageQueue.shift()
          if (msg !== undefined) {
            ws?.send(JSON.stringify(msg))
          }
        }
        options?.onOpen?.()
      }

      ws.onclose = (event) => {
        status.value = 'closed'
        if (event.code === 401 || event.code === 4001) {
          error.value = new Error('Unauthorized')
        } else if (event.code === 403 || event.code === 4003) {
          error.value = new Error('Forbidden')
        } else if (event.code === 404 || event.code === 4004) {
          error.value = new Error('Not found')
        }
        options?.onClose?.(event)
      }

      ws.onerror = () => {
        status.value = 'error'
        error.value = new Error('WebSocket connection error')
        options?.onError?.(error.value)
      }

      ws.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data) as T
          data.value = parsed
          options?.onMessage?.(parsed)
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e)
        }
      }
    } catch (e) {
      status.value = 'error'
      error.value = e instanceof Error ? e : new Error('Failed to connect')
      options?.onError?.(error.value)
    }
  }

  function send(message: unknown) {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message))
    } else {
      // Queue message to send when connection opens
      messageQueue.push(message)
    }
  }

  function close() {
    if (ws) {
      ws.close()
      ws = null
    }
    messageQueue = []
  }

  function reconnect() {
    close()
    connect()
  }

  // Auto-connect by default
  if (options?.autoConnect !== false) {
    connect()
  }

  // Cleanup on unmount
  onUnmounted(() => {
    close()
  })

  return {
    data,
    status,
    error,
    send,
    close,
    reconnect,
  }
}
