<template>
  <div class="script-executions-panel">
    <!-- Detail View (when execution selected) -->
    <div v-if="selectedExecutionId" class="detail-view">
      <div class="detail-header">
        <button class="back-btn waves-effect" @click="clearSelection">
          <i class="material-icons">arrow_back</i>
          <span>Back to list</span>
        </button>
      </div>
      <div class="detail-content">
        <div class="detail-fields">
          <div class="detail-row">
            <span class="detail-label">Status:</span>
            <span class="detail-value" :class="statusClass">{{ selectedExecutionDetails?.fullStatus || selectedExecutionDetails?.status || 'Loading...' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Started:</span>
            <span class="detail-value">{{ selectedExecutionDetails?.startTimeString || 'Loading...' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">User:</span>
            <span class="detail-value">{{ selectedExecutionDetails?.user || 'Loading...' }}</span>
          </div>
        </div>

        <!-- Parameters section -->
        <div v-if="hasSelectedExecutionParameters" class="parameters-section">
          <h6 class="parameters-title">Parameters</h6>
          <div class="params-table-wrapper">
            <table class="params-table">
              <thead>
                <tr>
                  <th>Parameter</th>
                  <th>Value</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(value, name) in selectedExecutionDetails.parameterValues" :key="name">
                  <td class="param-name">{{ name }}</td>
                  <td class="param-value">{{ formatParamValue(value) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Log panel -->
        <LogPanel ref="logPanel"
                  :autoscrollEnabled="isSelectedExecutionRunning"
                  :output-format="selectedExecutionDetails?.outputFormat"
                  class="log-panel"/>
      </div>
    </div>

    <!-- List View (default) -->
    <div v-else class="list-view">
      <!-- Running Section -->
      <section class="running-section">
        <h6 class="section-title" @click="toggleRunningSection">
          <i class="material-icons expand-icon" :class="{ collapsed: runningCollapsed }">expand_more</i>
          Running
          <span v-if="runningExecutions.length" class="badge">{{ runningExecutions.length }}</span>
        </h6>

        <div v-if="!runningCollapsed && !runningExecutions.length" class="empty-state">
          <p>No scripts currently running</p>
        </div>

        <div v-else-if="!runningCollapsed" class="running-list">
          <div v-for="execution in runningExecutions" :key="'running-' + execution.id"
               class="execution-card"
               @click="selectExecution(execution)">
            <div class="card-header">
              <span class="status-badge status-running">Running</span>
            </div>
            <div class="card-body">
              <div class="card-info">
                <div class="card-row">
                  <span class="label">User:</span>
                  <span class="value">{{ execution.user }}</span>
                </div>
                <div class="card-row">
                  <span class="label">Started:</span>
                  <span class="value">{{ execution.startTimeString }}</span>
                </div>
              </div>
              <div class="card-actions">
                <StopButton :executionId="execution.id" />
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Scheduled Section -->
      <section class="scheduled-section">
        <h6 class="section-title" @click="toggleScheduledSection">
          <i class="material-icons expand-icon" :class="{ collapsed: scheduledCollapsed }">expand_more</i>
          Scheduled
          <span v-if="scriptSchedules.length" class="badge">{{ scriptSchedules.length }}</span>
        </h6>

        <div v-if="!scheduledCollapsed && !scriptSchedules.length" class="empty-state">
          <p>No scheduled executions</p>
        </div>

        <div v-else-if="!scheduledCollapsed" class="scheduled-list">
          <div v-for="schedule in scriptSchedules" :key="'schedule-' + schedule.id"
               class="schedule-card">
            <div class="card-header">
              <span v-if="schedule.schedule.repeatable" class="status-badge status-recurring">
                <i class="material-icons">repeat</i>
                Recurring
              </span>
              <span v-else class="status-badge status-once">One-time</span>
            </div>
            <div class="card-body">
              <div class="card-info">
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
                <button class="action-btn delete-btn waves-effect"
                        :disabled="deletingSchedule === schedule.id"
                        @click.stop="confirmDeleteSchedule(schedule)"
                        title="Delete schedule">
                  <i v-if="deletingSchedule === schedule.id" class="material-icons rotating">refresh</i>
                  <i v-else class="material-icons">delete</i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Completed Section -->
      <section class="completed-section">
        <h6 class="section-title" @click="toggleCompletedSection">
          <i class="material-icons expand-icon" :class="{ collapsed: completedCollapsed }">expand_more</i>
          Completed
          <span v-if="completedExecutions.length" class="badge">{{ completedExecutions.length }}</span>
        </h6>

        <div v-if="!completedCollapsed && !completedExecutions.length" class="empty-state">
          <p>No execution history</p>
        </div>

        <div v-else-if="!completedCollapsed" class="completed-list">
          <div v-for="execution in completedExecutions" :key="'completed-' + execution.id"
               class="execution-card"
               @click="selectExecution(execution)">
            <div class="card-header">
              <span class="status-badge" :class="getStatusClass(execution)">{{ execution.fullStatus || execution.status }}</span>
            </div>
            <div class="card-body">
              <div class="card-info">
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
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import {mapState, mapActions} from 'vuex';
import LogPanel from '@/common/components/log_panel';
import StopButton from '@/main-app/components/common/StopButton';

export default {
  name: 'ScriptExecutionsPanel',

  components: {
    LogPanel,
    StopButton
  },

  data() {
    return {
      selectedExecutionId: null,
      selectedExecutionDetails: null,
      deletingSchedule: null,
      liveLogConnection: null,
      runningCollapsed: false,
      scheduledCollapsed: false,
      completedCollapsed: false
    };
  },

  computed: {
    ...mapState('scripts', ['selectedScript']),
    ...mapState('history', {
      executions: 'executions',
      historyLoading: 'loading'
    }),
    ...mapState('allSchedules', {
      schedules: 'schedules',
      schedulesLoading: 'loading'
    }),

    runningExecutions() {
      if (!this.executions || !this.selectedScript) return [];
      return this.executions.filter(e =>
        e.script === this.selectedScript &&
        e.status && e.status.toLowerCase() === 'running'
      );
    },

    completedExecutions() {
      if (!this.executions || !this.selectedScript) return [];
      return this.executions.filter(e =>
        e.script === this.selectedScript &&
        (!e.status || e.status.toLowerCase() !== 'running')
      ).slice(0, 50); // Limit to 50 most recent
    },

    scriptSchedules() {
      if (!this.schedules || !this.selectedScript) return [];
      return this.schedules.filter(s =>
        s.script_name === this.selectedScript
      ).sort((a, b) => {
        const timeA = a.next_execution ? new Date(a.next_execution).getTime() : Infinity;
        const timeB = b.next_execution ? new Date(b.next_execution).getTime() : Infinity;
        return timeA - timeB;
      });
    },

    runningAndScheduledCount() {
      return this.runningExecutions.length + this.scriptSchedules.length;
    },

    isSelectedExecutionRunning() {
      if (!this.selectedExecutionDetails) return false;
      return this.selectedExecutionDetails.status?.toLowerCase() === 'running';
    },

    hasSelectedExecutionParameters() {
      return this.selectedExecutionDetails?.parameterValues &&
             Object.keys(this.selectedExecutionDetails.parameterValues).length > 0;
    },

    statusClass() {
      if (!this.selectedExecutionDetails) return '';
      const status = this.selectedExecutionDetails.status?.toLowerCase();
      if (status === 'running') return 'status-running-text';
      if (this.selectedExecutionDetails.exitCode === 0) return 'status-success-text';
      return 'status-error-text';
    }
  },

  methods: {
    ...mapActions('allSchedules', ['fetchAllSchedules', 'deleteSchedule']),
    ...mapActions('history', {selectHistoryExecution: 'selectExecution'}),

    toggleRunningSection() {
      this.runningCollapsed = !this.runningCollapsed;
    },

    toggleScheduledSection() {
      this.scheduledCollapsed = !this.scheduledCollapsed;
    },

    toggleCompletedSection() {
      this.completedCollapsed = !this.completedCollapsed;
    },

    selectExecution(execution) {
      this.selectedExecutionId = execution.id;
      this.selectedExecutionDetails = execution;

      // Load full details
      this.selectHistoryExecution(execution.id);

      // If running, connect to live log
      if (execution.status?.toLowerCase() === 'running') {
        this.connectToLiveLog(execution.id);
      }
    },

    clearSelection() {
      this.selectedExecutionId = null;
      this.selectedExecutionDetails = null;
      this.disconnectLiveLog();
    },

    connectToLiveLog(executionId) {
      // Use the existing executor if available, otherwise fetch log
      const executor = this.$store.state.executions?.executors?.[executionId];
      if (executor) {
        // Watch executor log chunks
        this.$watch(
          () => executor.state.logChunks,
          (logChunks) => {
            if (logChunks && this.$refs.logPanel) {
              this.$refs.logPanel.setLog(logChunks.join(''));
            }
          },
          { immediate: true, deep: true }
        );
      }
    },

    disconnectLiveLog() {
      // Cleanup if needed
    },

    // Schedule methods
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

    confirmDeleteSchedule(schedule) {
      if (confirm(`Delete this scheduled execution?\n\nNext run: ${this.formatNextExecution(schedule)}`)) {
        this.deletingSchedule = schedule.id;
        this.deleteSchedule({scheduleId: schedule.id})
          .then(() => {
            M.toast({html: 'Schedule deleted'});
          })
          .catch(e => {
            M.toast({html: e.userMessage || 'Failed to delete schedule'});
          })
          .finally(() => {
            this.deletingSchedule = null;
          });
      }
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

    getStatusClass(execution) {
      const status = execution.status?.toLowerCase();
      if (status === 'running') return 'status-running';
      if (execution.exitCode === 0) return 'status-success';
      return 'status-error';
    }
  },

  watch: {
    selectedScript() {
      // Clear selection when script changes
      this.clearSelection();
    },

    // Watch for history store's selected execution to update details
    '$store.state.history.selectedExecution': {
      handler(execution) {
        if (execution && execution.id === this.selectedExecutionId) {
          this.selectedExecutionDetails = execution;
          if (this.$refs.logPanel && execution.log) {
            this.$refs.logPanel.setLog(execution.log);
          }
        }
      }
    }
  },

  mounted() {
    // Ensure schedules are loaded
    this.fetchAllSchedules();
  },

  beforeDestroy() {
    this.disconnectLiveLog();
  }
};
</script>

<style scoped>
.script-executions-panel {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

/* Detail View */
.detail-view {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}

.detail-header {
  padding: 8px 0;
  border-bottom: 1px solid var(--separator-color);
  margin-bottom: 12px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  color: var(--primary-color);
  cursor: pointer;
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  font-size: 14px;
}

.back-btn:hover {
  background: var(--background-color-high-emphasis);
}

.back-btn i {
  font-size: 20px;
}

.detail-content {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}

.detail-fields {
  margin-bottom: 12px;
}

.detail-row {
  display: flex;
  gap: 8px;
  margin-bottom: 4px;
  font-size: 13px;
}

.detail-label {
  color: var(--font-color-medium);
  min-width: 60px;
}

.detail-value {
  color: var(--font-color-main);
}

.status-running-text {
  color: var(--info-color);
  font-weight: 500;
}

.status-success-text {
  color: var(--success-color);
  font-weight: 500;
}

.status-error-text {
  color: var(--error-color);
  font-weight: 500;
}

.parameters-section {
  margin: 12px 0;
  padding: 12px;
  background-color: var(--background-color-high-emphasis);
  border-radius: 4px;
}

.parameters-title {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 500;
  color: var(--font-color-main);
}

.params-table-wrapper {
  max-height: 150px;
  overflow-y: auto;
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
  position: sticky;
  top: 0;
  background-color: var(--background-color-high-emphasis);
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

.log-panel {
  flex: 1;
  min-height: 200px;
}

/* List View */
.list-view {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

/* Running Section */
.running-section {
  flex-shrink: 0;
  margin-bottom: 16px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 500;
  color: var(--font-color-main);
  cursor: pointer;
  user-select: none;
}

.section-title:hover {
  color: var(--primary-color);
}

.section-title i {
  font-size: 20px;
  color: var(--primary-color);
}

.section-title .expand-icon {
  transition: transform 0.2s ease;
}

.section-title .expand-icon.collapsed {
  transform: rotate(-90deg);
}

.section-title .badge {
  background: var(--primary-color);
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.empty-state {
  padding: 16px;
  text-align: center;
  color: var(--font-color-medium);
  background: var(--background-color-slight-emphasis);
  border-radius: var(--radius-md);
}

.empty-state p {
  margin: 0;
  font-size: 13px;
}

.running-list,
.scheduled-list,
.completed-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* Card styling */
.execution-card,
.schedule-card {
  background: var(--background-color-level-4dp);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: box-shadow var(--transition-fast), transform var(--transition-fast);
  box-shadow: var(--shadow-md);
  flex-shrink: 0;
}

.execution-card:hover {
  box-shadow: var(--shadow-lg);
}

.execution-card:active {
  transform: scale(0.995);
}

.schedule-card {
  cursor: default;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 14px;
  border-bottom: 1px solid var(--separator-color);
}

.status-badge {
  font-size: 10px;
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

.status-success {
  background: rgba(76, 175, 80, 0.2);
  color: #81c784;
}

.status-error {
  background: rgba(244, 67, 54, 0.2);
  color: #e57373;
}

.status-recurring {
  display: flex;
  align-items: center;
  gap: 4px;
  background: var(--primary-color-light-color);
  color: var(--primary-color);
}

.status-recurring i {
  font-size: 14px;
}

.status-once {
  background: var(--background-color-high-emphasis);
  color: var(--font-color-medium);
}

.card-body {
  padding: 10px 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.card-info {
  flex: 1;
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
  color: rgba(255, 255, 255, 0.6);
  min-width: 55px;
}

.card-row .value {
  color: rgba(255, 255, 255, 0.87);
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
  flex-shrink: 0;
  display: flex;
  gap: 4px;
}

.stop-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  background-color: #e57373;
  color: white;
  position: relative;
  transition: background-color 0.2s ease;
}

.stop-btn:hover {
  background-color: #ef5350;
}

.stop-btn.kill-mode {
  background-color: #c62828;
}

.stop-btn.kill-mode:hover {
  background-color: #b71c1c;
}

.stop-btn i {
  font-size: 18px;
}

.timeout-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: #c62828;
  color: white;
  font-size: 10px;
  font-weight: bold;
  min-width: 16px;
  height: 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  background: transparent;
}

.action-btn i {
  font-size: 20px;
  color: var(--font-color-medium);
}

.delete-btn:hover i {
  color: var(--error-color);
}

.rotating {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Scheduled Section */
.scheduled-section {
  flex-shrink: 0;
  margin-bottom: 16px;
}

/* Completed Section */
.completed-section {
  flex-shrink: 0;
}

.completed-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
</style>
