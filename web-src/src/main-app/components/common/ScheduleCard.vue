<template>
  <div class="schedule-card" :class="{ 'schedule-disabled': schedule.enabled === false, 'schedule-expired': schedule.expired }">
    <div class="card-header">
      <span v-if="showScriptName" class="script-name">{{ schedule.script_name }}</span>
      <div class="badge-container">
        <span v-if="schedule.expired" class="status-badge status-completed">Completed</span>
        <span v-else-if="schedule.schedule.repeatable" class="status-badge status-recurring">Recurring</span>
        <span v-else class="status-badge status-once">One-time</span>
        <span v-if="schedule.enabled === false && !schedule.expired" class="status-badge status-disabled">Disabled</span>
      </div>
    </div>
    <div class="card-body">
      <div class="card-info">
        <div v-if="scriptDescription" class="card-row description-row">
          <span class="description-text">{{ scriptDescription }}</span>
        </div>
        <div v-if="schedule.description" class="card-row schedule-desc-row">
          <span class="schedule-label">Schedule:</span>
          <span class="schedule-text">{{ schedule.description }}</span>
        </div>
        <div v-if="schedule.schedule.repeatable" class="card-row">
          <span class="label">Last run:</span>
          <span class="value">{{ schedule.last_execution ? formattedLastExecution : 'No prior runs' }}</span>
        </div>
        <div class="card-row">
          <span class="label">{{ schedule.expired ? 'Status:' : 'Next run:' }}</span>
          <span v-if="schedule.expired" class="value expired-text">
            {{ autoDeleteText }}
          </span>
          <span v-else class="value next-run" :class="{ 'disabled-text': schedule.enabled === false }">
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
        <button class="action-btn edit-btn waves-effect"
                @click.stop="$emit('edit')"
                title="Edit schedule">
          <i class="material-icons">edit</i>
        </button>
        <button v-if="schedule.schedule.repeatable && !schedule.expired"
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
    scriptDescription: {
      type: String,
      default: ''
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
    },

    autoDeleteText() {
      if (!this.schedule.auto_delete_at) {
        return 'Completed - will be kept indefinitely';
      }

      const deleteTime = new Date(this.schedule.auto_delete_at);
      const now = new Date();
      const diffMs = deleteTime - now;

      if (diffMs <= 0) {
        return 'Completed - deleting soon';
      }

      const diffMinutes = Math.ceil(diffMs / 60000);
      if (diffMinutes < 60) {
        return `Completed - auto-deletes in ${diffMinutes} min`;
      }

      const diffHours = Math.floor(diffMinutes / 60);
      const remainingMinutes = diffMinutes % 60;
      if (remainingMinutes === 0) {
        return `Completed - auto-deletes in ${diffHours}h`;
      }
      return `Completed - auto-deletes in ${diffHours}h ${remainingMinutes}m`;
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

.schedule-card.schedule-expired {
  opacity: 0.7;
  border-left: 3px solid var(--status-success-color);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 10px 14px;
  border-bottom: 1px solid var(--separator-color);
}

.card-header:not(:has(.script-name)) {
  justify-content: flex-end;
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
  flex-shrink: 0;
}

.status-badge {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: var(--radius-lg);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 500;
}

.status-recurring {
  background: var(--status-scheduled-bg);
  color: var(--status-scheduled-color);
}

.status-once {
  background: var(--status-disabled-bg);
  color: var(--status-disabled-color);
}

.status-disabled {
  background: var(--status-error-bg);
  color: var(--status-error-color);
}

.status-completed {
  background: var(--status-success-bg);
  color: var(--status-success-color);
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

.card-row.schedule-desc-row {
  margin-bottom: 4px;
}

.schedule-label {
  color: var(--status-scheduled-color);
  min-width: 55px;
}

.schedule-text {
  color: var(--font-color-medium);
  font-style: italic;
}

.disabled-text {
  color: var(--status-disabled-color) !important;
  font-weight: normal !important;
}

.expired-text {
  color: var(--status-success-color) !important;
  font-weight: 500;
  font-style: italic;
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
  border-radius: var(--radius-sm);
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

.edit-btn:hover i {
  color: var(--primary-color);
}

.toggle-btn:hover i {
  color: var(--primary-color);
}

.delete-btn:hover i {
  color: var(--status-error-color);
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
