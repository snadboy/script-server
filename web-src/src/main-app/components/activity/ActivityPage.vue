<template>
  <div class="activity-page">
    <!-- Running Section -->
    <CollapsibleSection
      title="Running"
      :count="runningExecutions.length"
      :isEmpty="!executionsLoading && runningExecutions.length === 0"
      emptyMessage="No scripts currently running"
      :collapsed="runningCollapsed"
      @toggle="runningCollapsed = $event">
      <template v-if="executionsLoading">
        <div class="loading-state">
          <div class="spinner"></div>
        </div>
      </template>
      <template v-else>
        <ExecutionCard
          v-for="execution in runningExecutions"
          :key="'running-' + execution.id"
          :title="execution.script"
          status="running"
          statusText="Running"
          :user="execution.user"
          timeLabel="Started"
          :timeValue="execution.startTimeString"
          :isScheduled="!!execution.scheduleId"
          :scheduleDescription="getScheduleDescription(execution.scheduleId)"
          @click="viewExecution(execution)">
          <template #actions>
            <StopButton :executionId="execution.id" />
          </template>
        </ExecutionCard>
      </template>
    </CollapsibleSection>

    <!-- Scheduled Section -->
    <CollapsibleSection
      title="Scheduled"
      :count="schedules.length"
      :isEmpty="!schedulesLoading && filteredSchedules.length === 0"
      :emptyMessage="searchText ? 'No schedules match your search' : 'No scheduled executions'"
      :collapsed="scheduledCollapsed"
      @toggle="scheduledCollapsed = $event">
      <template v-if="schedulesLoading">
        <div class="loading-state">
          <div class="spinner"></div>
        </div>
      </template>
      <template v-else>
        <div class="schedule-card" v-for="schedule in filteredSchedules" :key="schedule.id">
          <div class="card-header">
            <span class="script-name">{{ schedule.script_name }}</span>
            <span v-if="schedule.schedule.repeatable" class="repeat-badge">
              <i class="material-icons">repeat</i>
              Recurring
            </span>
            <span v-else class="once-badge">One-time</span>
          </div>
          <div class="card-body">
            <div v-if="schedule.description" class="card-row description-row">
              <span class="description-text">{{ schedule.description }}</span>
            </div>
            <div v-if="schedule.schedule.repeatable && schedule.last_execution" class="card-row">
              <span class="label">Last run:</span>
              <span class="value">{{ formatLastExecution(schedule) }}</span>
            </div>
            <div class="card-row">
              <span class="label">Next run:</span>
              <span class="value next-run">{{ formatNextExecution(schedule) }}</span>
            </div>
            <div v-if="schedule.schedule.repeatable" class="card-row">
              <span class="label">Repeats:</span>
              <span class="value">Every {{ schedule.schedule.repeat_period }} {{ schedule.schedule.repeat_unit }}</span>
            </div>
            <div class="card-row">
              <span class="label">User:</span>
              <span class="value">{{ getUserName(schedule.user) }}</span>
            </div>
          </div>
          <div class="card-actions">
            <button v-if="hasParameters(schedule)"
                    class="btn-flat waves-effect params-btn"
                    :class="{ active: expandedParams === schedule.id }"
                    @click.stop="toggleParams(schedule.id)"
                    title="Show parameters">
              <i class="material-icons">tune</i>
            </button>
            <button class="btn-flat waves-effect delete-btn"
                    :disabled="deleting === schedule.id"
                    @click.stop="confirmDelete(schedule)"
                    title="Delete scheduled execution">
              <i v-if="deleting === schedule.id" class="material-icons rotating">refresh</i>
              <i v-else class="material-icons">delete</i>
            </button>
          </div>
          <transition name="expand">
            <div v-if="expandedParams === schedule.id" class="params-panel">
              <table class="params-table">
                <thead>
                  <tr>
                    <th>Parameter</th>
                    <th>Value</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(value, name) in schedule.parameter_values" :key="name">
                    <td class="param-name">{{ name }}</td>
                    <td class="param-value">{{ formatParamValue(value) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </transition>
        </div>
      </template>
    </CollapsibleSection>

    <!-- Completed Section -->
    <CollapsibleSection
      title="Completed"
      :count="completedExecutions.length"
      :isEmpty="!executionsLoading && completedExecutions.length === 0"
      emptyMessage="No completed executions"
      :collapsed="completedCollapsed"
      @toggle="completedCollapsed = $event"
      class="completed-section">
      <template v-if="executionsLoading">
        <div class="loading-state">
          <div class="spinner"></div>
        </div>
      </template>
      <template v-else>
        <ExecutionCard
          v-for="execution in completedExecutions"
          :key="'completed-' + execution.id"
          :title="execution.script"
          :status="getExecutionStatus(execution)"
          :statusText="execution.fullStatus || execution.status"
          :user="execution.user"
          timeLabel="Completed"
          :timeValue="execution.startTimeString"
          @click="viewExecution(execution)">
        </ExecutionCard>
      </template>
    </CollapsibleSection>
  </div>
</template>

<script>
import {mapState, mapActions} from 'vuex';
import CollapsibleSection from '../common/CollapsibleSection';
import ExecutionCard from '../common/ExecutionCard';
import StopButton from '../common/StopButton';

export default {
  name: 'ActivityPage',

  components: {
    CollapsibleSection,
    ExecutionCard,
    StopButton
  },

  data() {
    return {
      expandedParams: null,
      deleting: null,
      searchText: '',
      runningCollapsed: false,
      scheduledCollapsed: false,
      completedCollapsed: false
    };
  },

  computed: {
    ...mapState('history', {
      executions: 'executions',
      executionsLoading: 'loading'
    }),
    ...mapState('allSchedules', {
      schedules: 'schedules',
      schedulesLoading: 'loading'
    }),

    runningExecutions() {
      if (!this.executions) return [];
      return this.executions.filter(e =>
        e.status && e.status.toLowerCase() === 'running'
      );
    },

    completedExecutions() {
      if (!this.executions) return [];
      return this.executions.filter(e =>
        !e.status || e.status.toLowerCase() !== 'running'
      );
    },

    filteredSchedules() {
      let result = this.schedules ? [...this.schedules] : [];

      // Filter by search text if provided
      const searchText = (this.searchText || '').trim().toLowerCase();
      if (searchText) {
        result = result.filter(s => {
          const scriptMatch = s.script_name.toLowerCase().includes(searchText);
          const userName = this.getUserName(s.user).toLowerCase();
          const userMatch = userName.includes(searchText);
          return scriptMatch || userMatch;
        });
      }

      // Sort by next execution time (soonest first)
      return result.sort((a, b) => {
        const timeA = a.next_execution ? new Date(a.next_execution).getTime() : Infinity;
        const timeB = b.next_execution ? new Date(b.next_execution).getTime() : Infinity;
        return timeA - timeB;
      });
    }
  },

  mounted() {
    this.fetchAllSchedules();
  },

  methods: {
    ...mapActions('allSchedules', ['fetchAllSchedules', 'deleteSchedule']),

    viewExecution(execution) {
      this.$router.push(`/activity/${execution.id}`);
    },

    getExecutionStatus(execution) {
      if (!execution.status) return 'success';
      const status = execution.status.toLowerCase();
      if (status === 'running') return 'running';
      if (status === 'finished') {
        return execution.exitCode === 0 ? 'success' : 'error';
      }
      return 'error';
    },

    getUserName(user) {
      if (!user) return 'Unknown';
      if (typeof user === 'string') return user;
      if (user.user_id) return user.user_id;
      if (user.audit_names && user.audit_names.auth_username) {
        return user.audit_names.auth_username;
      }
      return 'Unknown';
    },

    formatNextExecution(schedule) {
      if (!schedule.next_execution) {
        return 'No upcoming execution';
      }
      const date = new Date(schedule.next_execution);
      const now = new Date();
      const diff = date - now;

      // Show relative time if within 24 hours
      if (diff > 0 && diff < 24 * 60 * 60 * 1000) {
        const hours = Math.floor(diff / (60 * 60 * 1000));
        const minutes = Math.floor((diff % (60 * 60 * 1000)) / (60 * 1000));
        if (hours > 0) {
          return `In ${hours}h ${minutes}m`;
        }
        return `In ${minutes}m`;
      }

      return date.toLocaleString();
    },

    formatLastExecution(schedule) {
      if (!schedule.last_execution) {
        return 'Never';
      }
      const date = new Date(schedule.last_execution);
      const now = new Date();
      const diff = now - date;

      // Show relative time if within 24 hours
      if (diff > 0 && diff < 24 * 60 * 60 * 1000) {
        const hours = Math.floor(diff / (60 * 60 * 1000));
        const minutes = Math.floor((diff % (60 * 60 * 1000)) / (60 * 1000));
        if (hours > 0) {
          return `${hours}h ${minutes}m ago`;
        }
        if (minutes > 0) {
          return `${minutes}m ago`;
        }
        return 'Just now';
      }

      return date.toLocaleString();
    },

    hasParameters(schedule) {
      return schedule.parameter_values && Object.keys(schedule.parameter_values).length > 0;
    },

    toggleParams(scheduleId) {
      this.expandedParams = this.expandedParams === scheduleId ? null : scheduleId;
    },

    formatParamValue(value) {
      if (value === null || value === undefined) {
        return '(empty)';
      }
      if (Array.isArray(value)) {
        return value.join(', ');
      }
      if (typeof value === 'boolean') {
        return value ? 'Yes' : 'No';
      }
      return String(value);
    },

    confirmDelete(schedule) {
      if (confirm(`Delete this scheduled execution?\n\nScript: ${schedule.script_name}\nNext run: ${this.formatNextExecution(schedule)}`)) {
        this.deleting = schedule.id;
        this.deleteSchedule({scheduleId: schedule.id})
          .then(() => {
            M.toast({html: 'Schedule deleted'});
          })
          .catch(e => {
            M.toast({html: e.userMessage || 'Failed to delete schedule'});
          })
          .finally(() => {
            this.deleting = null;
          });
      }
    },

    getScheduleDescription(scheduleId) {
      if (!scheduleId || !this.schedules) return '';
      const schedule = this.schedules.find(s => String(s.id) === String(scheduleId));
      return schedule ? schedule.description || '' : '';
    }
  }
};
</script>

<style scoped>
.activity-page {
  height: 100%;
  overflow-y: auto;
  background: var(--background-color);
  padding: 16px 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.completed-section {
  flex: 1;
  min-height: 0;
}

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

/* Schedule card styling */
.schedule-card {
  background: var(--background-color-level-4dp);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  flex-shrink: 0;
}

.schedule-card:hover {
  box-shadow: var(--shadow-lg);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  border-bottom: 1px solid var(--separator-color);
}

.script-name {
  font-weight: 500;
  font-size: 14px;
  color: var(--font-color-main);
}

.repeat-badge,
.once-badge {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 500;
}

.repeat-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  background: var(--primary-color-light-color);
  color: var(--primary-color);
}

.repeat-badge i {
  font-size: 14px;
}

.once-badge {
  background: var(--background-color-high-emphasis);
  color: var(--font-color-medium);
}

.card-body {
  padding: 10px 14px;
}

.card-row {
  display: flex;
  gap: 8px;
  margin-bottom: 2px;
  font-size: 12px;
}

.card-row:last-child {
  margin-bottom: 0;
}

.card-row .label {
  color: var(--font-color-medium);
  min-width: 55px;
}

.card-row .value {
  color: var(--font-color-main);
}

.card-row .next-run {
  font-weight: 500;
  color: var(--primary-color);
}

.card-row.description-row {
  margin-bottom: 6px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--separator-color);
}

.description-text {
  font-style: italic;
  color: var(--font-color-medium);
}

.card-actions {
  display: flex;
  justify-content: flex-end;
  gap: 4px;
  padding: 8px 12px;
  border-top: 1px solid var(--separator-color);
}

.params-btn,
.delete-btn {
  padding: 6px 10px;
  min-width: auto;
  border-radius: var(--radius-sm);
}

.params-btn i,
.delete-btn i {
  font-size: 20px;
  color: var(--font-color-medium);
}

.params-btn:hover i,
.params-btn.active i {
  color: var(--primary-color);
}

.delete-btn:hover i {
  color: var(--error-color);
}

.rotating {
  animation: spin 1s linear infinite;
}

/* Parameters panel */
.params-panel {
  padding: 12px 16px;
  background: var(--background-color-high-emphasis);
  border-top: 1px solid var(--separator-color);
}

.params-table {
  width: 100%;
  font-size: 13px;
  border-collapse: collapse;
}

.params-table th,
.params-table td {
  text-align: left;
  padding: 6px 8px;
}

.params-table th {
  color: var(--font-color-medium);
  font-weight: 500;
  border-bottom: 1px solid var(--separator-color);
}

.params-table .param-name {
  font-weight: 500;
  color: var(--font-color-main);
  white-space: nowrap;
  width: 30%;
}

.params-table .param-value {
  color: var(--font-color-medium);
  word-break: break-word;
}

/* Expand transition */
.expand-enter-active,
.expand-leave-active {
  transition: all var(--transition-normal);
  overflow: hidden;
}

.expand-enter,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}
</style>
