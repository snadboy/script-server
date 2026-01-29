<template>
  <div class="execution-card" :class="cardClasses" @click="$emit('click', $event)">
    <div class="card-header">
      <span class="script-name">{{ title }}</span>
      <div class="badge-container">
        <span class="status-badge" :class="statusClass">{{ statusText }}</span>
        <span v-if="isScheduled" class="scheduled-badge">Scheduled</span>
      </div>
    </div>
    <div class="card-body">
      <div class="card-info">
        <slot name="info">
          <div v-if="description || instanceName" class="card-row description-row">
            <div class="description-block">
              <span v-if="description" class="description-text">{{ description }}</span>
              <span v-if="instanceName" class="instance-text">Instance: {{ instanceName }}</span>
            </div>
          </div>
          <div v-if="scheduleDescription" class="card-row schedule-description-row">
            <span class="schedule-label">Schedule:</span>
            <span class="schedule-text">{{ scheduleDescription }}</span>
          </div>
          <div v-if="user" class="card-row">
            <span class="label">User:</span>
            <span class="value">{{ user }}</span>
          </div>
          <div v-if="timeLabel && timeValue" class="card-row">
            <span class="label">{{ timeLabel }}:</span>
            <span class="value">{{ timeValue }}</span>
          </div>
          <div v-if="timeLabel2 && timeValue2" class="card-row">
            <span class="label">{{ timeLabel2 }}:</span>
            <span class="value">{{ timeValue2 }}</span>
          </div>
          <div v-if="formattedParameters" class="card-row parameters-row">
            <span class="label">Parameters:</span>
            <span class="parameters-value">{{ formattedParameters }}</span>
          </div>
        </slot>
      </div>
      <div class="card-actions" @click.stop>
        <slot name="actions"></slot>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ExecutionCard',

  props: {
    title: {
      type: String,
      required: true
    },
    status: {
      type: String,
      default: ''
    },
    statusText: {
      type: String,
      default: ''
    },
    user: {
      type: String,
      default: ''
    },
    timeLabel: {
      type: String,
      default: ''
    },
    timeValue: {
      type: String,
      default: ''
    },
    timeLabel2: {
      type: String,
      default: ''
    },
    timeValue2: {
      type: String,
      default: ''
    },
    isScheduled: {
      type: Boolean,
      default: false
    },
    description: {
      type: String,
      default: ''
    },
    instanceName: {
      type: String,
      default: ''
    },
    scheduleDescription: {
      type: String,
      default: ''
    },
    parameters: {
      type: Object,
      default: null
    },
    verbParameterName: {
      type: String,
      default: null
    }
  },

  computed: {
    formattedParameters() {
      if (!this.parameters || Object.keys(this.parameters).length === 0) {
        return null;
      }

      const params = [];

      // Show verb first if present
      if (this.verbParameterName && this.parameters[this.verbParameterName]) {
        params.push(`${this.verbParameterName}=${this.parameters[this.verbParameterName]}`);
      }

      // Show other parameters
      for (const [key, value] of Object.entries(this.parameters)) {
        if (key === this.verbParameterName) continue; // Skip verb, already shown

        if (value === true) {
          params.push(key);
        } else if (value === false || value === null || value === undefined) {
          // Skip false/null/undefined values
          continue;
        } else if (Array.isArray(value)) {
          params.push(`${key}=[${value.join(', ')}]`);
        } else {
          params.push(`${key}=${value}`);
        }
      }

      return params.length > 0 ? params.join(', ') : null;
    },
    cardClasses() {
      return {
        'status-running': this.status === 'running',
        'status-scheduled': this.status === 'scheduled',
        'status-success': this.status === 'success',
        'status-error': this.status === 'error'
      };
    },
    statusClass() {
      return `status-${this.status}`;
    }
  }
};
</script>

<style scoped>
.execution-card {
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

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
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

.scheduled-badge {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: var(--radius-lg);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 500;
  background: var(--status-scheduled-bg);
  color: var(--status-scheduled-color);
}

.status-badge.status-running {
  background: var(--status-running-bg);
  color: var(--status-running-color);
}

.status-badge.status-scheduled {
  background: var(--status-scheduled-bg);
  color: var(--status-scheduled-color);
}

.status-badge.status-success {
  background: var(--status-success-bg);
  color: var(--status-success-color);
}

.status-badge.status-error {
  background: var(--status-error-bg);
  color: var(--status-error-color);
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

.card-row.description-row {
  margin-bottom: 6px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--separator-color);
}

.description-block {
  display: flex;
  flex-direction: column;
}

.description-text {
  font-style: italic;
  color: var(--font-color-medium);
}

.instance-text {
  font-style: italic;
  color: var(--font-color-medium);
  padding-left: 1.5em;
  margin-top: 2px;
}

.card-row.schedule-description-row {
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

.card-row.parameters-row {
  margin-top: 4px;
  padding-top: 4px;
  border-top: 1px solid var(--separator-color);
}

.parameters-value {
  color: var(--font-color-main);
  font-family: monospace;
  font-size: 11px;
  word-break: break-word;
}

.card-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}
</style>
