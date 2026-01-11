<template>
  <div class="schedule-card" :class="{ 'schedule-disabled': schedule.enabled === false }">
    <div class="card-header">
      <span v-if="showScriptName" class="script-name">{{ schedule.script_name }}</span>
      <div class="badge-container">
        <span v-if="schedule.schedule.repeatable" class="status-badge status-recurring">
          <i class="material-icons">repeat</i>
          Recurring
        </span>
        <span v-else class="status-badge status-once">One-time</span>
        <span v-if="schedule.enabled === false" class="status-badge status-disabled">Disabled</span>
      </div>
    </div>
    <div class="card-body">
      <div class="card-info">
        <div v-if="schedule.description" class="card-row description-row">
          <span class="description-text">{{ schedule.description }}</span>
        </div>
        <div v-if="schedule.schedule.repeatable && schedule.last_execution" class="card-row">
          <span class="label">Last run:</span>
          <span class="value">{{ formattedLastExecution }}</span>
        </div>
        <div class="card-row">
          <span class="label">Next run:</span>
          <span class="value next-run" :class="{ 'disabled-text': schedule.enabled === false }">
            {{ schedule.enabled === false ? 'Disabled' : formattedNextExecution }}
          </span>
        </div>
        <div v-if="schedule.schedule.repeatable" class="card-row">
          <span class="label">Repeats:</span>
          <span class="value">Every {{ schedule.schedule.repeat_period }} {{ schedule.schedule.repeat_unit }}</span>
        </div>
        <div class="card-row">
          <span class="label">User:</span>
          <span class="value">{{ userName }}</span>
        </div>
      </div>
      <div class="card-actions">
        <button v-if="showParams && hasParams"
                class="action-btn params-btn waves-effect"
                :class="{ active: paramsExpanded }"
                @click.stop="$emit('toggle-params')"
                title="Show parameters">
          <i class="material-icons">tune</i>
        </button>
        <button v-if="schedule.schedule.repeatable"
                class="action-btn toggle-btn waves-effect"
                :disabled="toggling"
                @click.stop="$emit('toggle-enabled')"
                :title="schedule.enabled === false ? 'Enable schedule' : 'Disable schedule'">
          <i v-if="toggling" class="material-icons rotating">refresh</i>
          <i v-else-if="schedule.enabled === false" class="material-icons">play_arrow</i>
          <i v-else class="material-icons">pause</i>
        </button>
        <button class="action-btn delete-btn waves-effect"
                :disabled="deleting"
                @click.stop="$emit('delete')"
                title="Delete schedule">
          <i v-if="deleting" class="material-icons rotating">refresh</i>
          <i v-else class="material-icons">delete</i>
        </button>
      </div>
    </div>
    <transition name="expand">
      <div v-if="paramsExpanded && hasParams" class="params-panel">
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

<script>
import {
  getUserName,
  formatNextExecution,
  formatLastExecution,
  formatParamValue,
  hasParameters
} from '@/main-app/utils/executionFormatters';

export default {
  name: 'ScheduleCard',

  props: {
    schedule: {
      type: Object,
      required: true
    },
    showScriptName: {
      type: Boolean,
      default: false
    },
    showParams: {
      type: Boolean,
      default: true
    },
    paramsExpanded: {
      type: Boolean,
      default: false
    },
    deleting: {
      type: Boolean,
      default: false
    },
    toggling: {
      type: Boolean,
      default: false
    }
  },

  computed: {
    userName() {
      return getUserName(this.schedule.user);
    },

    formattedNextExecution() {
      return formatNextExecution(this.schedule);
    },

    formattedLastExecution() {
      return formatLastExecution(this.schedule);
    },

    hasParams() {
      return hasParameters(this.schedule);
    }
  },

  methods: {
    formatParamValue
  }
};
</script>

<style scoped>
.schedule-card {
  background: var(--background-color-level-4dp);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  flex-shrink: 0;
}

.schedule-card:hover {
  box-shadow: var(--shadow-lg);
}

.schedule-card.schedule-disabled {
  opacity: 0.6;
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

.badge-container {
  display: flex;
  gap: 6px;
  align-items: center;
}

.status-badge {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 500;
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

.status-disabled {
  background: rgba(158, 158, 158, 0.2);
  color: #9e9e9e;
}

.card-body {
  padding: 10px 14px;
  display: flex;
  align-items: flex-start;
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

.disabled-text {
  color: #9e9e9e !important;
  font-weight: normal !important;
}

.card-actions {
  flex-shrink: 0;
  display: flex;
  gap: 4px;
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
  padding: 0;
  min-width: auto;
}

.action-btn i {
  font-size: 20px;
  color: var(--font-color-medium);
}

.params-btn:hover i,
.params-btn.active i {
  color: var(--primary-color);
}

.toggle-btn:hover i {
  color: var(--primary-color);
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
