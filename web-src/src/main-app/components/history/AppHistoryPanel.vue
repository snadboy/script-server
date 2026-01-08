<template>
  <div class="app-history-panel">
    <!-- Running Scripts Section -->
    <section class="running-section">
      <h6 class="section-title">
        <i class="material-icons">play_circle_filled</i>
        Running
        <span v-if="runningExecutions.length" class="badge">{{ runningExecutions.length }}</span>
      </h6>
      <div v-if="runningExecutions.length === 0" class="empty-state">
        <p>No scripts currently running</p>
      </div>
      <div v-else class="running-list">
        <div v-for="execution in runningExecutions" :key="'running-' + execution.id"
             class="execution-card"
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

    <!-- History Section -->
    <section class="history-section">
      <h6 class="section-title">
        <i class="material-icons">history</i>
        Completed
      </h6>
      <ExecutionsLogPage :disableProgressIndicator="true" class="main-app-executions-log"/>
    </section>
  </div>
</template>

<script>
import ExecutionsLogPage from '@/common/components/history/executions-log-page';
import {mapActions, mapState} from 'vuex';

export default {
  name: 'AppHistoryPanel',
  components: {ExecutionsLogPage},
  methods: {
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
    }
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
}

.section-title i {
  font-size: 20px;
  color: var(--primary-color);
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

/* History Section */
.history-section {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
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