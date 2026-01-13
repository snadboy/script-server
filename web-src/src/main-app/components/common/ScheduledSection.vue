<template>
  <div>
    <CollapsibleSection
      title="Scheduled"
      :count="badgeCount"
      :isEmpty="!loading && filteredSchedules.length === 0"
      :emptyMessage="emptyMessage"
      :collapsed="collapsed"
      @toggle="handleToggle">
      <template v-if="loading">
        <div class="loading-state">
          <div class="spinner"></div>
        </div>
      </template>
      <template v-else>
        <ScheduleCard
          v-for="schedule in filteredSchedules"
          :key="'schedule-' + schedule.id"
          :schedule="schedule"
          :showScriptName="showScriptName"
          :showParams="showParams"
          :scriptDescription="getScriptDesc(schedule.script_name)"
          :paramsExpanded="expandedParams === schedule.id"
          :deleting="deleting === schedule.id"
          :toggling="toggling === schedule.id"
          @toggle-params="toggleParams(schedule.id)"
          @toggle-enabled="handleToggleEnabled(schedule)"
          @edit="handleEdit(schedule)"
          @delete="confirmDelete(schedule)"
        />
      </template>
    </CollapsibleSection>

    <ScheduleModal
      :visible="showEditModal"
      :scriptName="editingSchedule ? editingSchedule.script_name : ''"
      :editSchedule="editingSchedule"
      @close="closeEditModal"
    />
  </div>
</template>

<script>
import {mapState, mapActions} from 'vuex';
import CollapsibleSection from './CollapsibleSection';
import ScheduleCard from './ScheduleCard';
import ScheduleModal from '@/main-app/components/schedule/ScheduleModal';
import {formatNextExecution, getScriptDescription} from '@/main-app/utils/executionFormatters';

const STORAGE_KEY = 'executionSections.collapsed.scheduled';

export default {
  name: 'ScheduledSection',

  components: {
    CollapsibleSection,
    ScheduleCard,
    ScheduleModal
  },

  props: {
    scriptFilter: {
      type: String,
      default: null
    },
    showScriptName: {
      type: Boolean,
      default: true
    },
    showParams: {
      type: Boolean,
      default: true
    }
  },

  data() {
    return {
      collapsed: this.loadCollapsedState(),
      expandedParams: null,
      deleting: null,
      toggling: null,
      showEditModal: false,
      editingSchedule: null
    };
  },

  computed: {
    ...mapState('allSchedules', {
      schedules: 'schedules',
      loading: 'loading'
    }),
    ...mapState('scripts', {
      scripts: 'scripts'
    }),

    filteredSchedules() {
      let result = this.schedules ? [...this.schedules] : [];

      // Apply script filter if provided
      if (this.scriptFilter) {
        result = result.filter(s => s.script_name === this.scriptFilter);
      }

      // Sort by next execution time (soonest first)
      return result.sort((a, b) => {
        const timeA = a.next_execution ? new Date(a.next_execution).getTime() : Infinity;
        const timeB = b.next_execution ? new Date(b.next_execution).getTime() : Infinity;
        return timeA - timeB;
      });
    },

    badgeCount() {
      return this.filteredSchedules.length;
    },

    emptyMessage() {
      return this.scriptFilter
        ? 'No scheduled executions for this script'
        : 'No scheduled executions';
    },

    // Create a map for efficient script description lookups (and ensure reactivity)
    scriptsMap() {
      const map = {};
      if (this.scripts && this.scripts.length > 0) {
        this.scripts.forEach(s => {
          map[s.name] = s.description || '';
        });
      }
      return map;
    }
  },

  mounted() {
    this.fetchAllSchedules();
  },

  methods: {
    ...mapActions('allSchedules', ['fetchAllSchedules', 'deleteSchedule', 'toggleScheduleEnabled']),

    loadCollapsedState() {
      try {
        return localStorage.getItem(STORAGE_KEY) === 'true';
      } catch (e) {
        return false;
      }
    },

    saveCollapsedState(collapsed) {
      try {
        localStorage.setItem(STORAGE_KEY, collapsed ? 'true' : 'false');
      } catch (e) {
        // Ignore localStorage errors
      }
    },

    handleToggle(collapsed) {
      this.collapsed = collapsed;
      this.saveCollapsedState(collapsed);
    },

    toggleParams(scheduleId) {
      this.expandedParams = this.expandedParams === scheduleId ? null : scheduleId;
    },

    confirmDelete(schedule) {
      const nextRun = formatNextExecution(schedule);
      const message = this.showScriptName
        ? `Delete this scheduled execution?\n\nScript: ${schedule.script_name}\nNext run: ${nextRun}`
        : `Delete this scheduled execution?\n\nNext run: ${nextRun}`;

      if (confirm(message)) {
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
    },

    handleToggleEnabled(schedule) {
      const newEnabled = schedule.enabled === false;
      this.toggling = schedule.id;
      this.toggleScheduleEnabled({scheduleId: schedule.id, enabled: newEnabled})
        .then(() => {
          M.toast({html: newEnabled ? 'Schedule enabled' : 'Schedule disabled'});
        })
        .catch(e => {
          M.toast({html: e.userMessage || 'Failed to update schedule'});
        })
        .finally(() => {
          this.toggling = null;
        });
    },

    handleEdit(schedule) {
      this.editingSchedule = schedule;
      this.showEditModal = true;
    },

    closeEditModal() {
      this.showEditModal = false;
      this.editingSchedule = null;
    },

    getScriptDesc(scriptName) {
      return this.scriptsMap[scriptName] || '';
    }
  }
};
</script>

<style scoped>
.loading-state {
  display: flex;
  justify-content: center;
  padding: 24px;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--separator-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
