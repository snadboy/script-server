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
          <div v-if="description" class="card-row description-row">
            <span class="description-text">{{ description }}</span>
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
    isScheduled: {
      type: Boolean,
      default: false
    },
    description: {
      type: String,
      default: ''
    },
    scheduleDescription: {
      type: String,
      default: ''
    }
  },

  computed: {
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

.scheduled-badge {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 500;
  background: rgba(156, 39, 176, 0.2);
  color: #ba68c8;
}

.status-badge.status-running {
  background: rgba(33, 150, 243, 0.2);
  color: #64b5f6;
}

.status-badge.status-scheduled {
  background: rgba(156, 39, 176, 0.2);
  color: #ba68c8;
}

.status-badge.status-success {
  background: rgba(76, 175, 80, 0.2);
  color: #81c784;
}

.status-badge.status-error {
  background: rgba(244, 67, 54, 0.2);
  color: #e57373;
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

.description-text {
  font-style: italic;
  color: var(--font-color-medium);
}

.card-row.schedule-description-row {
  margin-bottom: 4px;
}

.schedule-label {
  color: #ba68c8;
  min-width: 55px;
}

.schedule-text {
  color: var(--font-color-medium);
  font-style: italic;
}

.card-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}
</style>
