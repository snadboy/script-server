<template>
  <CollapsibleSection
    title="Completed"
    :count="badgeCount"
    :isEmpty="!loading && filteredExecutions.length === 0"
    :emptyMessage="emptyMessage"
    :collapsed="collapsed"
    @toggle="handleToggle"
    class="completed-section">
    <template v-if="loading">
      <div class="loading-state">
        <div class="spinner"></div>
      </div>
    </template>
    <template v-else>
      <ExecutionCard
        v-for="execution in displayedExecutions"
        :key="'completed-' + execution.id"
        :title="showScriptName ? execution.script : 'Execution #' + execution.id"
        :status="getStatus(execution)"
        :statusText="execution.fullStatus || execution.status"
        :user="execution.user"
        timeLabel="Completed"
        :timeValue="execution.startTimeString"
        @click="handleClick(execution)">
      </ExecutionCard>
    </template>
  </CollapsibleSection>
</template>

<script>
import {mapState} from 'vuex';
import CollapsibleSection from './CollapsibleSection';
import ExecutionCard from './ExecutionCard';
import {getExecutionStatus} from '@/main-app/utils/executionFormatters';

const STORAGE_KEY = 'executionSections.collapsed.completed';

export default {
  name: 'CompletedSection',

  components: {
    CollapsibleSection,
    ExecutionCard
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
    limit: {
      type: Number,
      default: null
    }
  },

  data() {
    return {
      collapsed: this.loadCollapsedState()
    };
  },

  computed: {
    ...mapState('history', {
      executions: 'executions',
      loading: 'loading'
    }),

    filteredExecutions() {
      if (!this.executions) return [];

      let result = this.executions.filter(e =>
        !e.status || e.status.toLowerCase() !== 'running'
      );

      // Apply script filter if provided
      if (this.scriptFilter) {
        result = result.filter(e => e.script === this.scriptFilter);
      }

      return result;
    },

    displayedExecutions() {
      if (this.limit && this.limit > 0) {
        return this.filteredExecutions.slice(0, this.limit);
      }
      return this.filteredExecutions;
    },

    badgeCount() {
      return this.filteredExecutions.length;
    },

    emptyMessage() {
      return this.scriptFilter
        ? 'No execution history for this script'
        : 'No completed executions';
    }
  },

  methods: {
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

    handleClick(execution) {
      this.$emit('select', execution);

      // Navigate to activity detail if no handler
      if (!this.$listeners.select) {
        this.$router.push(`/activity/${execution.id}`);
      }
    },

    getStatus(execution) {
      return getExecutionStatus(execution);
    }
  }
};
</script>

<style scoped>
.completed-section {
  flex: 1;
  min-height: 0;
}

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
