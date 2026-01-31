<template>
  <CollapsibleSection
    title="Running"
    :count="badgeCount"
    :isEmpty="!loading && filteredExecutions.length === 0"
    emptyMessage="No scripts currently running"
    :collapsed="collapsed"
    @toggle="handleToggle">
    <template v-if="loading">
      <div class="loading-state">
        <div class="spinner"></div>
      </div>
    </template>
    <template v-else>
      <ExecutionCard
        v-for="execution in filteredExecutions"
        :key="'running-' + execution.id"
        :title="getExecutionTitle(execution)"
        status="running"
        statusText="Running"
        :user="execution.user"
        :description="getScriptDesc(execution.script)"
        :instanceName="execution.instanceName"
        timeLabel="Started"
        :timeValue="execution.startTimeString"
        :isScheduled="!!execution.scheduleId"
        :scheduleDescription="getScheduleDesc(execution.scheduleId)"
        :parameters="showParameters ? getFilteredParameters(execution) : null"
        :verbParameterName="showParameters ? getVerbParameterName(execution.script) : null"
        @click="handleClick(execution)">
        <template #actions>
          <StopButton :executionId="execution.id" />
        </template>
      </ExecutionCard>
    </template>
  </CollapsibleSection>
</template>

<script>
import {mapState} from 'vuex';
import CollapsibleSection from './CollapsibleSection';
import ExecutionCard from './ExecutionCard';
import StopButton from './StopButton';
import {getScheduleDescription} from '@/main-app/utils/executionFormatters';
import {createExecutionSectionMixin} from '@/main-app/mixins/executionSectionMixin';

const STORAGE_KEY = 'executionSections.collapsed.running';

export default {
  name: 'RunningSection',

  components: {
    CollapsibleSection,
    ExecutionCard,
    StopButton
  },

  mixins: [createExecutionSectionMixin(STORAGE_KEY)],

  props: {
    scriptFilter: {
      type: String,
      default: null
    },
    showScriptName: {
      type: Boolean,
      default: true
    },
    showParameters: {
      type: Boolean,
      default: true
    }
  },

  computed: {
    ...mapState('history', {
      executions: 'executions',
      loading: 'loading'
    }),
    ...mapState('allSchedules', {
      schedules: 'schedules'
    }),

    filteredExecutions() {
      if (!this.executions) return [];

      let result = this.executions.filter(e =>
        e.status && e.status.toLowerCase() === 'running'
      );

      // Apply script filter if provided
      if (this.scriptFilter) {
        result = result.filter(e => e.script === this.scriptFilter);
      }

      return result;
    },

    badgeCount() {
      return this.filteredExecutions.length;
    }
  },

  methods: {
    handleClick(execution) {
      this.$emit('select', execution);

      // Navigate to activity detail if no handler
      if (!this.$listeners.select) {
        this.$router.push(`/activity/${execution.id}`);
      }
    },

    getScheduleDesc(scheduleId) {
      return getScheduleDescription(scheduleId, this.schedules);
    },

    getExecutionTitle(execution) {
      if (this.showScriptName) {
        return `${execution.script} (Execution ID: ${execution.id})`;
      }
      return `Execution ID: ${execution.id}`;
    }
  }
};
</script>

<style scoped src="@/main-app/styles/executionSection.css"></style>
