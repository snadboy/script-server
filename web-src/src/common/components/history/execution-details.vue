<template>
  <div class="execution-details container">
    <div>
      <readonly-field :value="script" class="readonly-field" title="Script name"/>
      <readonly-field :value="user" class="readonly-field" title="User"/>
      <readonly-field :value="startTime" class="readonly-field" title="Start time"/>
      <readonly-field :value="fullStatus" class="readonly-field" title="Status"/>
      <readonly-field :value="command" class="long readonly-field" title="Command"/>
    </div>
    <div v-if="hasParameters" class="parameters-section">
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
            <tr v-for="(value, name) in parameterValues" :key="name">
              <td class="param-name">{{ name }}</td>
              <td class="param-value">{{ formatParamValue(value) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <log-panel ref="logPanel" :autoscrollEnabled="false" :output-format="outputFormat" class="log-panel"/>
  </div>
</template>

<script>
import {isNull} from '@/common/utils/common';
import {mapActions, mapState} from 'vuex';
import LogPanel from '../log_panel';
import ReadOnlyField from '../readonly-field';

export default {
  name: 'execution-details',

  props: {
    executionId: String
  },

  data: function () {
    return {
      script: '',
      user: '',
      startTime: '',
      fullStatus: '',
      command: '',
      outputFormat: '',
      parameterValues: null,
      mounted: false
    };
  },

  components: {
    'readonly-field': ReadOnlyField,
    'log-panel': LogPanel
  },

  methods: {
    ...mapActions('history', ['selectExecution']),

    setLog(log) {
      if (!this.mounted) {
        return;
      }

      if (!this.$refs.logPanel) {
        this.$nextTick(() => {
          this.$refs.logPanel.setLog(log);
        });
      } else {
        this.$refs.logPanel.setLog(log);
      }
    },

    refreshData(selectedExecution) {
      if (!isNull(selectedExecution)) {
        this.script = selectedExecution.script;
        this.user = selectedExecution.user;
        this.startTime = selectedExecution.startTimeString;
        this.fullStatus = selectedExecution.fullStatus;
        this.command = selectedExecution.command;
        this.outputFormat = selectedExecution.outputFormat;
        this.parameterValues = selectedExecution.parameterValues;
        this.setLog(selectedExecution.log);

      } else {
        this.script = '';
        this.user = '';
        this.startTime = '';
        this.fullStatus = '';
        this.command = '';
        this.outputFormat = null;
        this.parameterValues = null;
        this.setLog('');
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
    }
  },

  computed: {
    ...mapState('history', ['selectedExecution']),

    hasParameters() {
      return this.parameterValues && Object.keys(this.parameterValues).length > 0;
    }
  },

  mounted() {
    this.mounted = true;
    this.refreshData(this.selectedExecution);
  },

  watch: {
    'executionId': {
      immediate: true,
      handler(executionId) {
        this.selectExecution(executionId);
      }
    },
    'selectedExecution': {
      immediate: true,
      handler(selectedExecution) {
        this.refreshData(selectedExecution);
      }
    }
  }
}
</script>

<style scoped>
.execution-details {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.readonly-field {
  margin-top: 6px;
  margin-bottom: 16px;

  display: inline-block;
  width: 200px;
}

.readonly-field.long {
  width: 600px;
  max-width: 100%;
}

.log-panel {
  margin-top: 4px;
}

.parameters-section {
  margin: 16px 0;
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
  max-height: 200px;
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
</style>