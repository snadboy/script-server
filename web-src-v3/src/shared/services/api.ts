import axios, { type AxiosInstance } from 'axios'
import type {
  AuthInfo,
  ServerConfig,
  ScriptsResponse,
  HistoryEntryShort,
  HistoryEntryLong,
  Schedule,
  ExecutionConfig,
} from '@shared/types/api'

class ApiService {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
      },
      withCredentials: true,
    })

    // Handle 401 responses
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Don't redirect if we're already on the login page
          if (!window.location.pathname.includes('login')) {
            window.location.href = '/login.html'
          }
        }
        throw error
      }
    )
  }

  // Server Configuration
  async getServerConfig(): Promise<ServerConfig> {
    const { data } = await this.client.get<ServerConfig>('/conf')
    return data
  }

  // Authentication
  async getAuthInfo(): Promise<AuthInfo> {
    const { data } = await this.client.get<AuthInfo>('/auth/info')
    return data
  }

  async logout(): Promise<void> {
    await this.client.post('/logout')
  }

  // Scripts
  async getScripts(mode?: string): Promise<ScriptsResponse> {
    const params = mode ? { mode } : undefined
    const { data } = await this.client.get<ScriptsResponse>('/scripts', { params })
    return data
  }

  // Executions
  async startExecution(scriptName: string, params: FormData): Promise<string> {
    params.append('__script_name', scriptName)
    const { data } = await this.client.post<string>('/executions/start', params, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return data
  }

  async getActiveExecutions(): Promise<string[]> {
    const { data } = await this.client.get<string[]>('/executions/active')
    return data
  }

  async getExecutionConfig(id: string): Promise<ExecutionConfig> {
    const { data } = await this.client.get<ExecutionConfig>(`/executions/config/${id}`)
    return data
  }

  async getExecutionStatus(id: string): Promise<'running' | 'finished'> {
    const { data } = await this.client.get<'running' | 'finished'>(`/executions/status/${id}`)
    return data
  }

  async stopExecution(id: string): Promise<void> {
    await this.client.post(`/executions/stop/${id}`)
  }

  async killExecution(id: string): Promise<void> {
    await this.client.post(`/executions/kill/${id}`)
  }

  async cleanupExecution(id: string): Promise<void> {
    await this.client.post(`/executions/cleanup/${id}`)
  }

  // History
  async getHistoryShort(): Promise<HistoryEntryShort[]> {
    const { data } = await this.client.get<HistoryEntryShort[]>('/history/execution_log/short')
    return data
  }

  async getHistoryLong(id: string): Promise<HistoryEntryLong> {
    const { data } = await this.client.get<HistoryEntryLong>(`/history/execution_log/long/${id}`)
    return data
  }

  // Schedules
  async getSchedules(scriptName?: string): Promise<{ schedules: Schedule[] }> {
    const params = scriptName ? { script: scriptName } : undefined
    const { data } = await this.client.get<{ schedules: Schedule[] }>('/schedules', { params })
    return data
  }

  async createSchedule(formData: FormData): Promise<{ id: string }> {
    const { data } = await this.client.post<{ id: string }>('/schedule', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return data
  }

  async deleteSchedule(id: string): Promise<void> {
    await this.client.delete(`/schedules/${id}`)
  }

  // WebSocket URL helper
  getWebSocketUrl(path: string): string {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    return `${protocol}//${window.location.host}/${path}`
  }
}

export const api = new ApiService()
