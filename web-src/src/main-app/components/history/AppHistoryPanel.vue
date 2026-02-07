<template>
  <div class="app-history-panel">
    <!-- Running Scripts Section -->
    <section class="running-section">
      <h6 class="section-title" @click="toggleRunningSection">
        <i class="material-icons expand-icon" :class="{ collapsed: runningCollapsed }">expand_more</i>
        Running
        <span v-if="runningExecutions.length" class="badge">{{ runningExecutions.length }}</span>
      </h6>
      <div v-if="!runningCollapsed && runningExecutions.length === 0" class="empty-state">
        <p>No scripts currently running</p>
      </div>
      <div v-else-if="!runningCollapsed" class="running-list">
        <div v-for="execution in runningExecutions" :key="'running-' + execution.id"
             class="execution-card"
             @click="viewExecution(execution)">
          <div class="card-header">
            <span class="script-name">{{ execution.script }}</span>
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
              <button class="stop-btn waves-effect"
                      :class="{ 'kill-mode': isKillMode(execution.id) }"
                      :title="getStopButtonTitle(execution.id)"
                      @click.stop="stopExecution(execution)">
                <i class="material-icons">{{ getStopIcon(execution.id) }}</i>
                <span v-if="getKillTimeout(execution.id)" class="timeout-badge">{{ getKillTimeout(execution.id) }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- History Section -->
    <section class="history-section" :class="{ collapsed: historyCollapsed }">
      <h6 class="section-title" @click="toggleHistorySection">
        <i class="material-icons expand-icon" :class="{ collapsed: historyCollapsed }">expand_more</i>
        Completed
      </h6>
      <ExecutionsLogPage v-if="!historyCollapsed" :disableProgressIndicator="true" :excludeRunning="true" class="main-app-executions-log"/>
    </section>
  </div>
</template>

<script>
import ExecutionsLogPage from '@/common/components/history/executions-log-page';
import {mapActions, mapState} from 'vuex';
import {axiosInstance} from '@/common/utils/axios_utils';
import {API} from '@/common/api-constants';
import Vue from 'vue';

export default {
  name: 'AppHistoryPanel',
  components: {ExecutionsLogPage},

  data() {
    return {
      stoppingExecutions: {},  // { executionId: { killEnabled: false, killTimeout: null, intervalId: null } }
      runningCollapsed: false,
      historyCollapsed: false
    };
  },

  methods: {
    toggleRunningSection() {
      this.runningCollapsed = !this.runningCollapsed;
    },

    toggleHistorySection() {
      this.historyCollapsed = !this.historyCollapsed;
    },

    ...mapActions('page', ['setLoading']),

    updateLoadingIndicator() {
      if (this.$route.params.executionId) {
        this.setLoading(this.detailsLoading);
      } else {
        this.setLoading(this.loading);
      }
    },

    viewExecution(execution) {
      this.$router.push(`/history/${execution.id}`);
    },

    stopExecution(execution) {
      const id = execution.id;
      const stopState = this.stoppingExecutions[id];

      if (stopState && stopState.killEnabled) {
        // Kill mode - send kill request
        axiosInstance.post(`${API.EXECUTIONS.KILL}/${id}`)
          .then(() => {
            M.toast({html: 'Script killed'});
            this.clearStopState(id);
          })
          .catch(e => {
            M.toast({html: e.response?.data || 'Failed to kill script'});
          });
      } else {
        // Stop mode - send stop request and start kill countdown
        axiosInstance.post(`${API.EXECUTIONS.STOP}/${id}`)
          .then(() => {
            M.toast({html: 'Stop signal sent'});
            this.startKillCountdown(id);
          })
          .catch(e => {
            M.toast({html: e.response?.data || 'Failed to stop script'});
          });
      }
    },

    startKillCountdown(id) {
      // Initialize stop state with 5 second countdown
      Vue.set(this.stoppingExecutions, id, {
        killEnabled: false,
        killTimeout: 5,
        intervalId: setInterval(() => {
          this.tickKillCountdown(id);
        }, 1000)
      });
    },

    tickKillCountdown(id) {
      const stopState = this.stoppingExecutions[id];
      if (!stopState) return;

      // Check if execution is still running
      const stillRunning = this.runningExecutions.some(e => e.id === id);
      if (!stillRunning) {
        this.clearStopState(id);
        return;
      }

      if (stopState.killTimeout <= 1) {
        // Enable kill mode
        clearInterval(stopState.intervalId);
        Vue.set(this.stoppingExecutions, id, {
          killEnabled: true,
          killTimeout: null,
          intervalId: null
        });
      } else {
        // Decrement countdown
        Vue.set(this.stoppingExecutions, id, {
          ...stopState,
          killTimeout: stopState.killTimeout - 1
        });
      }
    },

    clearStopState(id) {
      const stopState = this.stoppingExecutions[id];
      if (stopState && stopState.intervalId) {
        clearInterval(stopState.intervalId);
      }
      Vue.delete(this.stoppingExecutions, id);
    },

    isKillMode(id) {
      return this.stoppingExecutions[id]?.killEnabled || false;
    },

    getKillTimeout(id) {
      return this.stoppingExecutions[id]?.killTimeout || null;
    },

    getStopIcon(id) {
      if (this.isKillMode(id)) return 'dangerous';
      return 'stop';
    },

    getStopButtonTitle(id) {
      if (this.isKillMode(id)) return 'Kill script';
      const timeout = this.getKillTimeout(id);
      if (timeout) return `Stop (${timeout}s to kill)`;
      return 'Stop script';
    }
  },

  computed: {
    ...mapState('history', ['loading', 'detailsLoading', 'executions']),
    runningExecutions() {
      if (!this.executions) return [];
      return this.executions.filter(e =>
        e.status && e.status.toLowerCase() === 'running'
      );
    }
  },

  watch: {
    loading: {
      immediate: true,
      handler() {
        this.updateLoadingIndicator()
      }
    },
    detailsLoading: {
      immediate: true,
      handler() {
        this.updateLoadingIndicator()
      }
    },
    runningExecutions: {
      handler(newVal, oldVal) {
        // Clear stop state for executions that are no longer running
        if (oldVal) {
          const currentIds = new Set(newVal.map(e => e.id));
          Object.keys(this.stoppingExecutions).forEach(id => {
            if (!currentIds.has(id)) {
              this.clearStopState(id);
            }
          });
        }
      }
    }
  },

  beforeDestroy() {
    // Clean up all intervals
    Object.keys(this.stoppingExecutions).forEach(id => {
      this.clearStopState(id);
    });
  }
}

</script>

<style scoped>
.app-history-panel {
  height: 100%;
  overflow-y: auto;

  background: var(--background-color);
  padding-bottom: 12px;

  display: flex;
  flex-direction: column;
}

/* Running Section */
.running-section {
  padding: 16px;
  flex-shrink: 0;
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

.running-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.execution-card {
  background: var(--background-color-level-4dp);
  border-radius: var(--radius-md);
  overflow: hidden;
  cursor: pointer;
  transition: box-shadow var(--transition-fast), transform var(--transition-fast);
  box-shadow: var(--shadow-md);
}

.execution-card:hover {
  box-shadow: var(--shadow-lg);
}

.execution-card:active {
  transform: scale(0.995);
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
  color: var(--font-color-medium);
  min-width: 55px;
}

.card-row .value {
  color: var(--font-color-main);
}

.card-actions {
  flex-shrink: 0;
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

/* History Section */
.history-section {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.history-section.collapsed {
  flex: 0;
}

.history-section .section-title {
  padding: 0 16px;
  margin-bottom: 8px;
}

.main-app-executions-log {
  flex: 1;
  min-height: 0;
}
</style>