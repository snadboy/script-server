// Server configuration
export interface ServerConfig {
  title: string
  version: string
  enableScriptTitles: boolean
}

// Authentication
export interface AuthInfo {
  enabled: boolean
  username?: string
  admin: boolean
  canEditCode: boolean
}

// Scripts
export interface Script {
  name: string
  group?: string
  parsing_failed?: boolean
}

export interface ScriptsResponse {
  scripts: Script[]
}

// Script Configuration
export interface ScriptConfig {
  id: string
  clientModelId?: string
  name: string
  description?: string
  schedulingEnabled?: boolean
  outputFormat: OutputFormat
  parameters: Parameter[]
}

export type OutputFormat = 'terminal' | 'html' | 'html_iframe' | 'text'

export interface Parameter {
  name: string
  type: ParameterType
  description?: string
  required?: boolean
  default?: string | number | boolean | string[]
  values?: string[]
  min?: number
  max?: number
  maxLength?: number
  regex?: string
  secure?: boolean
  withoutValue?: boolean
  fileRecursive?: boolean
  fileType?: 'file' | 'folder'
  requiredParameters?: string[]
  ui?: ParameterUI
}

export type ParameterType =
  | 'text'
  | 'int'
  | 'list'
  | 'multiselect'
  | 'editable_list'
  | 'file_upload'
  | 'server_file'
  | 'multiline_text'
  | 'ip'
  | 'ip4'
  | 'ip6'

export interface ParameterUI {
  widthWeight?: number
  separatorBefore?: ParameterSeparator
}

export interface ParameterSeparator {
  title?: string
}

// Execution
export interface Execution {
  id: string
  scriptName: string
  status: ExecutionStatus
  startTime: string
  endTime?: string
  user: string
  exitCode?: number
}

export type ExecutionStatus = 'initializing' | 'executing' | 'finished' | 'disconnected' | 'error'

export interface ExecutionConfig {
  scriptName: string
  parameterValues: Record<string, unknown>
}

export interface HistoryEntryShort {
  id: string
  startTime: string
  user: string
  script: string
  status: string
  exitCode?: number
}

export interface HistoryEntryLong extends HistoryEntryShort {
  command: string
  log: string
  outputFormat: OutputFormat
}

// Schedule
export interface Schedule {
  id: string
  scriptName: string
  userName: string
  nextExecution?: string
  repeatable: boolean
  startDatetime: string
  repeatUnit?: 'minute' | 'hour' | 'day' | 'week' | 'month' | 'year'
  repeatPeriod?: number
  weekDays?: number[]
}

export interface ScheduleCreate {
  scriptName: string
  parameterValues: Record<string, unknown>
  scheduleConfig: {
    repeatable: boolean
    startDatetime: string
    endOption?: 'never' | 'count' | 'date'
    endArg?: string | number
    repeatUnit?: string
    repeatPeriod?: number
    weekDays?: number[]
  }
}

// WebSocket Events
export interface ConfigSocketEvent {
  event: string
  data: unknown
  clientStateVersion?: number
}

export interface StreamSocketEvent {
  event: 'output' | 'input' | 'file' | 'inline-image'
  data: unknown
}

// User Management (Admin)
export interface User {
  username: string
  isAdmin: boolean
  canEditCode: boolean
}
