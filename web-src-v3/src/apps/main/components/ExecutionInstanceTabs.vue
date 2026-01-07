<script setup lang="ts">
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useExecutionManagerStore, type ExecutionState } from '../stores/executionManager'

const executionStore = useExecutionManagerStore()
const { executions, selectedExecutionId } = storeToRefs(executionStore)

const executionList = computed(() => Array.from(executions.value.values()))
const hasExecutions = computed(() => executionList.value.length > 0)

function getStatusIcon(execution: ExecutionState): string {
  switch (execution.status) {
    case 'executing':
      return 'sync'
    case 'finished':
      return 'check_circle'
    case 'error':
      return 'error'
    case 'disconnected':
      return 'link_off'
    default:
      return 'pending'
  }
}

function getStatusColor(execution: ExecutionState): string {
  switch (execution.status) {
    case 'executing':
      return 'text-blue-500'
    case 'finished':
      return 'text-green-500'
    case 'error':
      return 'text-red-500'
    case 'disconnected':
      return 'text-gray-500'
    default:
      return 'text-gray-400'
  }
}

function selectExecution(executionId: string) {
  executionStore.selectExecution(executionId)
}

function closeExecution(event: Event, executionId: string) {
  event.stopPropagation()
  executionStore.closeExecution(executionId)
}
</script>

<template>
  <div v-if="hasExecutions" class="flex items-center gap-1 px-2 py-1 bg-gray-100 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 overflow-x-auto">
    <button
      v-for="execution in executionList"
      :key="execution.id"
      class="flex items-center gap-2 px-3 py-1.5 rounded-t text-sm whitespace-nowrap transition-colors"
      :class="[
        selectedExecutionId === execution.id
          ? 'bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 shadow-sm'
          : 'text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
      ]"
      @click="selectExecution(execution.id)"
    >
      <!-- Status icon -->
      <span
        class="material-icons text-base"
        :class="[getStatusColor(execution), { 'animate-spin': execution.status === 'executing' }]"
      >
        {{ getStatusIcon(execution) }}
      </span>

      <!-- Script name -->
      <span class="max-w-[150px] truncate">
        {{ execution.scriptName }}
      </span>

      <!-- Execution ID (shortened) -->
      <span class="text-xs text-gray-400">
        #{{ execution.id.slice(0, 6) }}
      </span>

      <!-- Close button -->
      <button
        class="ml-1 p-0.5 rounded hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
        title="Close"
        @click="closeExecution($event, execution.id)"
      >
        <span class="material-icons text-sm text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
          close
        </span>
      </button>
    </button>

    <!-- New execution indicator (optional slot for controls) -->
    <slot name="controls" />
  </div>
</template>
