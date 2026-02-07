<template>
  <CollapsibleSection
    title="Completed"
    :count="badgeCount"
    :isEmpty="!loading && filteredExecutions.length === 0"
    :emptyMessage="emptyMessage"
    :collapsed="collapsed"
    @toggle="handleToggle"
    class="completed-section">
    <template #actions>
      <button v-if="filteredExecutions.length > 0 || deleting"
              class="delete-all-btn"
              :class="{ 'is-deleting': deleting }"
              :disabled="deleting"
              @click="confirmDeleteAll"
              :title="deleting ? 'Deleting...' : 'Delete all completed entries'">
        <i v-if="deleting" class="material-icons spinning">sync</i>
        <i v-else class="material-icons">delete_sweep</i>
      </button>
    </template>
    <div v-if="error" class="error-message" @click="error = null">{{ error }}</div>
    <template v-if="loading">
      <div class="loading-state">
        <div class="spinner"></div>
      </div>
    </template>
    <template v-else>
      <ExecutionCard
        v-for="execution in displayedExecutions"
        :key="'completed-' + execution.id"
        :title="execution.script + ' (Execution ID: ' + execution.id + ')'"
        :status="getStatus(execution)"
        :statusText="execution.fullStatus || execution.status"
        :user="execution.user"
        :description="getScriptDesc(execution.script)"
        :instanceName="execution.instanceName"
        :isScheduled="!!execution.scheduleId"
        :scheduleDescription="getScheduleDesc(execution.scheduleId)"
        timeLabel="Started"
        :timeValue="execution.startTimeString"
        timeLabel2="Ended"
        :timeValue2="execution.finishTimeString ? execution.finishTimeString + ' ' + execution.durationString : ''"
        :parameters="showParameters ? getFilteredParameters(execution) : null"
        :verbParameterName="showParameters ? getVerbParameterName(execution.script) : null"
        @click="handleClick(execution)">
        <template #actions>
          <button class="action-btn view-btn" @click="viewLog(execution)" title="View log">
            <i class="material-icons">description</i>
          </button>
          <button class="action-btn delete-btn"
                  :disabled="deleting"
                  @click="confirmDelete(execution)"
                  title="Delete">
            <i class="material-icons">delete</i>
          </button>
        </template>
      </ExecutionCard>
    </template>
  </CollapsibleSection>
</template>

<script>
import {mapState, mapActions} from 'vuex';
import CollapsibleSection from './CollapsibleSection';
import ExecutionCard from './ExecutionCard';
import {getExecutionStatus, getScheduleDescription} from '@/main-app/utils/executionFormatters';
import {axiosInstance} from '@/common/utils/axios_utils';
import {createExecutionSectionMixin} from '@/main-app/mixins/executionSectionMixin';

const STORAGE_KEY = 'executionSections.collapsed.completed';

export default {
  name: 'CompletedSection',

  components: {
    CollapsibleSection,
    ExecutionCard
  },

  mixins: [createExecutionSectionMixin(STORAGE_KEY)],

  props: {
    scriptFilter: {
      type: String,
      default: null
    },
    limit: {
      type: Number,
      default: null
    },
    showParameters: {
      type: Boolean,
      default: true
    }
  },

  data() {
    return {
      deleting: false,
      error: null
    };
  },

  computed: {
    ...mapState('history', {
      executions: 'executions',
      loading: 'loading'
    }),
    ...mapState('allSchedules', {
      schedules: 'schedules'
    }),

    filteredExecutions() {
      if (!this.executions) return [];

      let result = this.executions.filter(e =>
        !e.status || e.status.toLowerCase() !== 'running'
      );

      // Apply script filter if provided
      if (this.scriptFilter) {
        result = result.filter(e => e.script === this.scriptFilter);
      }

      return result;
    },

    displayedExecutions() {
      if (this.limit && this.limit > 0) {
        return this.filteredExecutions.slice(0, this.limit);
      }
      return this.filteredExecutions;
    },

    badgeCount() {
      return this.filteredExecutions.length;
    },

    emptyMessage() {
      return this.scriptFilter
        ? 'No execution history for this script'
        : 'No completed executions';
    }
  },

  methods: {
    ...mapActions('history', ['refresh']),

    handleClick(execution) {
      this.$emit('select', execution);

      // Navigate to activity detail if no handler
      if (!this.$listeners.select) {
        this.$router.push(`/activity/${execution.id}`);
      }
    },

    viewLog(execution) {
      this.$router.push(`/activity/${execution.id}`);
    },

    confirmDelete(execution) {
      if (confirm(`Delete execution log for "${execution.script}" (ID: ${execution.id})?`)) {
        this.deleteExecution(execution.id);
      }
    },

    confirmDeleteAll() {
      const msg = this.scriptFilter
        ? `Delete all ${this.filteredExecutions.length} completed entries for "${this.scriptFilter}"?`
        : `Delete all ${this.filteredExecutions.length} completed entries?`;

      if (confirm(msg)) {
        this.deleteAllExecutions();
      }
    },

    async deleteExecution(executionId) {
      try {
        await axiosInstance.delete(`/history/execution_log/${executionId}`);
        this.refresh();
      } catch (e) {
        console.error('Failed to delete execution:', e.response?.data || e.message);
        this.error = 'Failed to delete execution';
      }
    },

    async deleteAllExecutions() {
      this.deleting = true;
      try {
        let url;
        if (this.scriptFilter) {
          url = `/history/execution_log/script/${encodeURIComponent(this.scriptFilter)}`;
        } else {
          url = '/history/execution_log/all';
        }

        await axiosInstance.delete(url);
        this.refresh();
      } catch (e) {
        console.error('Failed to delete executions:', e.response?.data || e.message);
        this.error = 'Failed to delete executions';
      } finally {
        this.deleting = false;
      }
    },

    getStatus(execution) {
      return getExecutionStatus(execution);
    },

    getScheduleDesc(scheduleId) {
      return getScheduleDescription(scheduleId, this.schedules);
    }
  }
};
</script>

<style scoped src="@/main-app/styles/executionSection.css"></style>

<style scoped>
.completed-section {
  flex: 1;
  min-height: 0;
}

.delete-all-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  border: none;
  border-radius: 50%;
  background: transparent;
  color: var(--font-color-medium);
  cursor: pointer;
  transition: background-color 0.2s, color 0.2s;
}

.delete-all-btn:hover:not(:disabled) {
  background-color: var(--status-error-bg);
  color: var(--status-error-color);
}

.delete-all-btn:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.delete-all-btn.is-deleting {
  color: var(--primary-color);
}

.delete-all-btn i {
  font-size: 20px;
}

.delete-all-btn i.spinning {
  animation: spin 1s linear infinite;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  border: none;
  border-radius: 50%;
  background: transparent;
  color: var(--font-color-medium);
  cursor: pointer;
  transition: background-color 0.2s, color 0.2s;
}

.action-btn i {
  font-size: 18px;
}

.view-btn:hover {
  background-color: var(--hover-color);
  color: var(--primary-color);
}

.delete-btn:hover:not(:disabled) {
  background-color: var(--status-error-bg);
  color: var(--status-error-color);
}

.delete-btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}
</style>
