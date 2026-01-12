<template>
  <CollapsibleSection
    title="Running"
    :count="badgeCount"
    :isEmpty="!loading && filteredExecutions.length === 0"
    emptyMessage="No scripts currently running"
    :collapsed="collapsed"
    @toggle="handleToggle">
    <template v-if="loading">
      <div class="loading-state">
        <div class="spinner"></div>
      </div>
    </template>
    <template v-else>
      <ExecutionCard
        v-for="execution in filteredExecutions"
        :key="'running-' + execution.id"
        :title="getExecutionTitle(execution)"
        status="running"
        statusText="Running"
        :user="execution.user"
        :description="getExecutionDescription(execution)"
        timeLabel="Started"
        :timeValue="execution.startTimeString"
        :isScheduled="!!execution.scheduleId"
        :scheduleDescription="getScheduleDesc(execution.scheduleId)"
        @click="handleClick(execution)">
        <template #actions>
          <StopButton :executionId="execution.id" />
        </template>
      </ExecutionCard>
    </template>
  </CollapsibleSection>
</template>

<script>
import {mapState, mapActions} from 'vuex';
import CollapsibleSection from './CollapsibleSection';
import ExecutionCard from './ExecutionCard';
import StopButton from './StopButton';
import {getScheduleDescription} from '@/main-app/utils/executionFormatters';

const STORAGE_KEY = 'executionSections.collapsed.running';

export default {
  name: 'RunningSection',

  components: {
    CollapsibleSection,
    ExecutionCard,
    StopButton
  },

  props: {
    scriptFilter: {
      type: String,
      default: null
    },
    showScriptName: {
      type: Boolean,
      default: true
    }
  },

  data() {
    return {
      collapsed: this.loadCollapsedState()
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
        e.status && e.status.toLowerCase() === 'running'
      );

      // Apply script filter if provided
      if (this.scriptFilter) {
        result = result.filter(e => e.script === this.scriptFilter);
      }

      return result;
    },

    badgeCount() {
      return this.filteredExecutions.length;
    }
  },

  methods: {
    loadCollapsedState() {
      try {
        return localStorage.getItem(STORAGE_KEY) === 'true';
      } catch (e) {
        return false;
      }
    },

    saveCollapsedState(collapsed) {
      try {
        localStorage.setItem(STORAGE_KEY, collapsed ? 'true' : 'false');
      } catch (e) {
        // Ignore localStorage errors
      }
    },

    handleToggle(collapsed) {
      this.collapsed = collapsed;
      this.saveCollapsedState(collapsed);
    },

    handleClick(execution) {
      this.$emit('select', execution);

      // Navigate to activity detail if no handler
      if (!this.$listeners.select) {
        this.$router.push(`/activity/${execution.id}`);
      }
    },

    getScheduleDesc(scheduleId) {
      return getScheduleDescription(scheduleId, this.schedules);
    },

    getExecutionTitle(execution) {
      if (this.showScriptName) {
        return `${execution.script} (Execution ID: ${execution.id})`;
      }
      return `Execution ID: ${execution.id}`;
    },

    getExecutionDescription(execution) {
      const parts = [];

      // Add instance name if present
      if (execution.instanceName) {
        parts.push(`Instance: ${execution.instanceName}`);
      }

      // Get schedule description if this was a scheduled execution
      if (execution.scheduleId) {
        const scheduleDesc = getScheduleDescription(execution.scheduleId, this.schedules);
        if (scheduleDesc) {
          parts.push(scheduleDesc);
        }
      }

      return parts.join(' | ');
    }
  }
};
</script>

<style scoped>
.loading-state {
  display: flex;
  justify-content: center;
  padding: 24px;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--separator-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
