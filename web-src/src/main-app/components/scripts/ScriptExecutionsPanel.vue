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
      <RunningSection
        :scriptFilter="selectedScript"
        :showScriptName="false"
        @select="selectExecution"
      />
      <ScheduledSection
        :scriptFilter="selectedScript"
        :showScriptName="false"
        :showParams="false"
      />
      <CompletedSection
        :scriptFilter="selectedScript"
        :limit="completedExecutionsLimit"
        @select="selectExecution"
      />
    </div>
  </div>
</template>

<script>
import {mapState, mapActions} from 'vuex';
import LogPanel from '@/common/components/log_panel';
import RunningSection from '@/main-app/components/common/RunningSection';
import ScheduledSection from '@/main-app/components/common/ScheduledSection';
import CompletedSection from '@/main-app/components/common/CompletedSection';
import {formatParamValue} from '@/main-app/utils/executionFormatters';

export default {
  name: 'ScriptExecutionsPanel',

  components: {
    LogPanel,
    RunningSection,
    ScheduledSection,
    CompletedSection
  },

  data() {
    return {
      selectedExecutionId: null,
      selectedExecutionDetails: null,
      liveLogConnection: null
    };
  },

  computed: {
    ...mapState('scripts', ['selectedScript']),
    ...mapState('settings', ['completedExecutionsLimit']),

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
    ...mapActions('history', {selectHistoryExecution: 'selectExecution'}),

    formatParamValue,

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
  gap: 16px;
  padding: 16px 0;
}
</style>
