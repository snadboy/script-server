<template>
  <div class="schedule-list">
    <div v-if="loading" class="schedule-loading">
      <div class="preloader-wrapper small active">
        <div class="spinner-layer spinner-primary-only">
          <div class="circle-clipper left"><div class="circle"></div></div>
          <div class="gap-patch"><div class="circle"></div></div>
          <div class="circle-clipper right"><div class="circle"></div></div>
        </div>
      </div>
    </div>
    <div v-else-if="schedules.length === 0" class="no-schedules">
      No scheduled executions
    </div>
    <div v-else class="schedule-items">
      <div v-for="schedule in schedules" :key="schedule.id" class="schedule-item">
        <div class="schedule-info">
          <div class="schedule-time">
            <i class="material-icons">schedule</i>
            <span>{{ formatNextExecution(schedule) }}</span>
          </div>
          <div class="schedule-details">
            <span v-if="schedule.schedule.repeatable" class="schedule-repeat">
              Every {{ schedule.schedule.repeat_period }} {{ schedule.schedule.repeat_unit }}
            </span>
            <span v-else class="schedule-once">One-time</span>
          </div>
        </div>
        <button class="btn-flat waves-effect delete-btn"
                :disabled="deleting === schedule.id"
                @click="confirmDelete(schedule)">
          <i v-if="deleting === schedule.id" class="material-icons rotating">refresh</i>
          <i v-else class="material-icons">delete</i>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import {mapState, mapActions} from 'vuex';

export default {
  name: 'ScheduleList',

  data() {
    return {
      deleting: null
    };
  },

  computed: {
    ...mapState('scriptSchedule', ['schedules', 'loading', 'error']),
    ...mapState('scriptConfig', ['scriptConfig'])
  },

  watch: {
    scriptConfig: {
      handler(newConfig) {
        if (newConfig && newConfig.name) {
          this.fetchSchedules({scriptName: newConfig.name});
        }
      },
      immediate: true
    }
  },

  methods: {
    ...mapActions('scriptSchedule', ['fetchSchedules', 'deleteSchedule']),

    formatNextExecution(schedule) {
      if (!schedule.next_execution) {
        return 'No upcoming execution';
      }
      const date = new Date(schedule.next_execution);
      return date.toLocaleString();
    },

    confirmDelete(schedule) {
      if (confirm(`Delete this scheduled execution?\n\nNext run: ${this.formatNextExecution(schedule)}`)) {
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
.schedule-list {
  margin-top: 8px;
}

.schedule-loading {
  display: flex;
  justify-content: center;
  padding: 16px;
}

.no-schedules {
  color: var(--font-color-medium);
  font-size: 14px;
  padding: 8px 0;
}

.schedule-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.schedule-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background-color: var(--background-color-level-2dp);
  border-radius: 4px;
}

.schedule-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.schedule-time {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.schedule-time i {
  font-size: 18px;
  color: var(--primary-color);
}

.schedule-details {
  font-size: 12px;
  color: var(--font-color-medium);
  margin-left: 26px;
}

.schedule-repeat {
  color: var(--primary-color);
}

.schedule-once {
  color: var(--font-color-medium);
}

.delete-btn {
  padding: 4px 8px;
  min-width: auto;
}

.delete-btn i {
  color: var(--font-color-medium);
}

.delete-btn:hover i {
  color: #f44336;
}

.rotating {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
