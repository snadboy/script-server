<template>
  <div class="scheduled-page">
    <div class="container">
      <!-- Running Scripts Section -->
      <section class="section running-section">
        <h5 class="section-title">
          <i class="material-icons">play_circle_filled</i>
          Running
          <span v-if="runningExecutions.length" class="badge">{{ runningExecutions.length }}</span>
        </h5>
        <div v-if="executionsLoading" class="loading-state">
          <div class="spinner"></div>
        </div>
        <div v-else-if="runningExecutions.length === 0" class="empty-state">
          <p>No scripts currently running</p>
        </div>
        <div v-else class="running-list">
          <div v-for="execution in runningExecutions" :key="execution.id"
               class="execution-card card-elevated"
               @click="viewExecution(execution)">
            <div class="card-header">
              <span class="script-name">{{ execution.script }}</span>
              <span class="status-badge status-running">Running</span>
            </div>
            <div class="card-body">
              <div class="card-row">
                <span class="label">User:</span>
                <span class="value">{{ execution.user }}</span>
              </div>
              <div class="card-row">
                <span class="label">Started:</span>
                <span class="value">{{ execution.startTimeString }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Scheduled Scripts Section -->
      <section class="section scheduled-section">
        <h5 class="section-title">
          <i class="material-icons">schedule</i>
          Scheduled
          <span v-if="schedules.length" class="badge">{{ schedules.length }}</span>
        </h5>
        <div v-if="schedulesLoading" class="loading-state">
          <div class="spinner"></div>
        </div>
        <div v-else-if="schedules.length === 0" class="empty-state">
          <p>No scheduled executions</p>
        </div>
        <div v-else class="schedule-list">
          <div v-for="schedule in sortedSchedules" :key="schedule.id" class="schedule-card card-elevated">
            <div class="card-header">
              <span class="script-name">{{ schedule.script_name }}</span>
              <span v-if="schedule.schedule.repeatable" class="repeat-badge">
                <i class="material-icons">repeat</i>
                Recurring
              </span>
              <span v-else class="once-badge">One-time</span>
            </div>
            <div class="card-body">
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
                <span class="value">{{ schedule.user }}</span>
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
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import {mapState, mapActions} from 'vuex';

export default {
  name: 'ScheduledPage',

  data() {
    return {
      expandedParams: null,
      deleting: null
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

    sortedSchedules() {
      if (!this.schedules) return [];
      return [...this.schedules].sort((a, b) => {
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

    viewExecution(execution) {
      this.$router.push(`/history/${execution.id}`);
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
    }
  }
};
</script>

<style scoped>
.scheduled-page {
  padding: 16px 0;
}

.section {
  margin-bottom: 32px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 500;
  color: var(--font-color-main);
}

.section-title i {
  font-size: 24px;
  color: var(--primary-color);
}

.section-title .badge {
  background: var(--primary-color);
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
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

.empty-state {
  padding: 24px;
  text-align: center;
  color: var(--font-color-medium);
  background: var(--background-color-slight-emphasis);
  border-radius: var(--radius-md);
}

.empty-state p {
  margin: 0;
}

/* Card styling */
.running-list,
.schedule-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.execution-card,
.schedule-card {
  background: var(--background-color-level-4dp);
  border-radius: var(--radius-md);
  overflow: hidden;
  cursor: pointer;
  transition: box-shadow var(--transition-fast), transform var(--transition-fast);
}

.execution-card:hover,
.schedule-card:hover {
  box-shadow: var(--shadow-lg);
}

.execution-card:active,
.schedule-card:active {
  transform: scale(0.995);
}

.schedule-card {
  cursor: default;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--separator-color);
}

.script-name {
  font-weight: 500;
  font-size: 15px;
  color: var(--font-color-main);
}

.status-badge,
.repeat-badge,
.once-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 500;
}

.status-running {
  background: var(--info-color-light);
  color: var(--info-color);
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
  padding: 12px 16px;
}

.card-row {
  display: flex;
  gap: 8px;
  margin-bottom: 4px;
  font-size: 13px;
}

.card-row:last-child {
  margin-bottom: 0;
}

.card-row .label {
  color: var(--font-color-medium);
  min-width: 70px;
}

.card-row .value {
  color: var(--font-color-main);
}

.card-row .next-run {
  font-weight: 500;
  color: var(--primary-color);
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

/* Responsive */
@media screen and (max-width: 600px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
