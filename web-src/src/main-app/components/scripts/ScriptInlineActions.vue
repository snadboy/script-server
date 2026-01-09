<template>
  <div class="script-inline-actions" v-if="visible" @click.stop>
    <button
        class="action-btn execute-btn waves-effect waves-light"
        :class="{ 'stop-mode': isExecuting, 'kill-mode': killEnabled }"
        :title="executeButtonTitle"
        @click="handleExecuteClick">
      <i class="material-icons">{{ executeButtonIcon }}</i>
      <span v-if="killTimeoutSec && isExecuting" class="timeout-badge">{{ killTimeoutSec }}</span>
    </button>

    <button
        v-if="isSchedulable"
        class="action-btn schedule-btn waves-effect waves-light"
        :class="{ disabled: !canSchedule }"
        :disabled="!canSchedule"
        title="Schedule execution"
        @click="openScheduleModal">
      <i class="material-icons">date_range</i>
    </button>

    <button
        v-if="isAdmin"
        class="action-btn edit-btn waves-effect waves-light"
        title="Edit script configuration"
        @click="openEditModal">
      <i class="material-icons">edit</i>
    </button>

    <ScheduleModal
        :visible="showScheduleModal"
        :script-name="scriptName"
        @close="showScheduleModal = false"/>

    <EditScriptModal
        :visible="showEditModal"
        :script-name="scriptName"
        @close="showEditModal = false"
        @saved="handleEditSaved"
        @deleted="handleEditDeleted"/>
  </div>
</template>

<script>
import {forEachKeyValue, isNull} from '@/common/utils/common';
import {scriptNameToHash} from '../../utils/model_helper';
import {STATUS_EXECUTING, STATUS_INITIALIZING, STATUS_FINISHED, STATUS_DISCONNECTED, STATUS_ERROR} from '../../store/scriptExecutor';
import {mapState} from 'vuex';
import ScheduleModal from '@/main-app/components/schedule/ScheduleModal';
import EditScriptModal from '@/main-app/components/scripts/EditScriptModal';

export default {
  name: 'ScriptInlineActions',

  components: {
    ScheduleModal,
    EditScriptModal
  },

  props: {
    scriptName: {
      type: String,
      required: true
    },
    parsingFailed: {
      type: Boolean,
      default: false
    }
  },

  data() {
    return {
      showScheduleModal: false,
      showEditModal: false
    };
  },

  computed: {
    ...mapState('auth', {
      isAdmin: 'admin'
    }),
    ...mapState('scriptConfig', {
      scriptConfig: 'scriptConfig'
    }),
    ...mapState('scripts', ['selectedScript']),

    visible() {
      return !this.parsingFailed;
    },

    scriptHash() {
      return scriptNameToHash(this.scriptName);
    },

    executor() {
      // Find any executor for this script
      let foundExecutor = null;
      forEachKeyValue(this.$store.state.executions.executors, (id, executor) => {
        if (executor.state.scriptName === this.scriptName) {
          foundExecutor = executor;
        }
      });
      return foundExecutor;
    },

    isExecuting() {
      if (!this.executor) return false;
      const status = this.executor.state.status;
      return status === STATUS_EXECUTING || status === STATUS_INITIALIZING;
    },

    canExecute() {
      if (!this.executor) return true;
      const status = this.executor.state.status;
      return status === STATUS_FINISHED ||
             status === STATUS_DISCONNECTED ||
             status === STATUS_ERROR;
    },

    killEnabled() {
      return !isNull(this.executor) && this.executor.state.killEnabled;
    },

    killTimeoutSec() {
      return isNull(this.executor) ? null : this.executor.state.killTimeoutSec;
    },

    executeButtonIcon() {
      if (!this.isExecuting) return 'play_arrow';
      if (this.killEnabled) return 'dangerous';
      return 'stop';
    },

    executeButtonTitle() {
      if (!this.isExecuting) return 'Execute script';
      if (this.killEnabled) return 'Kill script';
      if (this.killTimeoutSec) return `Stop (${this.killTimeoutSec}s to kill)`;
      return 'Stop script';
    },

    isSchedulable() {
      // Only show schedule button for the currently selected script
      // and only if that script is schedulable
      if (this.selectedScript !== this.scriptName) {
        return false;
      }
      return this.scriptConfig && this.scriptConfig.schedulable;
    },

    canSchedule() {
      // Can schedule when not currently executing
      return this.canExecute;
    }
  },

  methods: {
    handleExecuteClick() {
      if (this.isExecuting) {
        // Stop/Kill the script
        if (!this.executor) return;

        const executionId = this.executor.state.id;
        if (this.killEnabled) {
          this.$store.dispatch('executions/' + executionId + '/killExecution');
        } else {
          this.$store.dispatch('executions/' + executionId + '/stopExecution');
        }
      } else {
        // Execute the script
        if (!this.canExecute) return;

        // Set flag in store for auto-execution
        this.$store.commit('scripts/SET_PENDING_AUTO_EXECUTE', true);

        // Navigate to the script
        this.$router.push('/' + this.scriptHash);
      }
    },

    openScheduleModal() {
      if (!this.canSchedule) return;
      this.showScheduleModal = true;
    },

    openEditModal() {
      this.showEditModal = true;
    },

    handleEditSaved(scriptName) {
      this.showEditModal = false;
      M.toast({ html: 'Script saved successfully' });
      // Reload script config if we're viewing this script
      if (this.selectedScript === this.scriptName || this.selectedScript === scriptName) {
        this.$store.dispatch('scriptConfig/reloadScript', { selectedScript: scriptName });
      }
    },

    handleEditDeleted() {
      this.showEditModal = false;
      // Navigate to home if we were viewing this script
      if (this.selectedScript === this.scriptName) {
        this.$router.push('/');
      }
    }
  }
}
</script>

<style scoped>
.script-inline-actions {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  padding: 4px 16px 8px;
  gap: 8px;
  background: var(--surface-color);
  border-bottom: 1px solid var(--separator-color);
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
  transition: background-color 0.2s ease, opacity 0.2s ease;
  text-decoration: none;
  position: relative;
}

.action-btn i {
  font-size: 18px;
}

.execute-btn,
.edit-btn,
.schedule-btn {
  background-color: var(--surface-color);
  color: var(--font-color-main);
  border: 1px solid var(--separator-color);
}

.execute-btn:hover:not(.disabled):not(.stop-mode),
.edit-btn:hover:not(.disabled),
.schedule-btn:hover:not(.disabled) {
  background-color: var(--hover-color);
  color: var(--primary-color);
}

.execute-btn.stop-mode {
  background-color: #e57373;
  color: white;
  border-color: #e57373;
}

.execute-btn.stop-mode:hover {
  background-color: #ef5350;
  border-color: #ef5350;
}

.execute-btn.kill-mode {
  background-color: #c62828;
  border-color: #c62828;
}

.execute-btn.kill-mode:hover {
  background-color: #b71c1c;
  border-color: #b71c1c;
}

.action-btn.disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.timeout-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: #c62828;
  color: white;
  font-size: 10px;
  font-weight: bold;
  min-width: 16px;
  height: 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
}
</style>
