<template>
  <div class="script-inline-actions" v-if="visible" @click.stop>
    <button
        class="action-btn execute-btn waves-effect waves-light"
        :class="{ disabled: !canExecute }"
        :disabled="!canExecute"
        :title="canExecute ? 'Execute script' : 'Script is running'"
        @click="navigateAndExecute">
      <i class="material-icons">play_arrow</i>
    </button>

    <button
        class="action-btn stop-btn waves-effect waves-light"
        :class="{
          disabled: !canStop,
          'kill-mode': killEnabled
        }"
        :disabled="!canStop"
        :title="stopButtonTitle"
        @click="stopScript">
      <i class="material-icons">{{ killEnabled ? 'dangerous' : 'stop' }}</i>
      <span v-if="killTimeoutSec" class="timeout-badge">{{ killTimeoutSec }}</span>
    </button>

    <a v-if="isAdmin"
       class="action-btn edit-btn waves-effect waves-light"
       :href="editUrl"
       title="Edit script configuration">
      <i class="material-icons">edit</i>
    </a>
  </div>
</template>

<script>
import {forEachKeyValue, isNull} from '@/common/utils/common';
import {scriptNameToHash} from '../../utils/model_helper';
import {STATUS_EXECUTING, STATUS_INITIALIZING, STATUS_FINISHED, STATUS_DISCONNECTED, STATUS_ERROR} from '../../store/scriptExecutor';
import {mapState} from 'vuex';

export default {
  name: 'ScriptInlineActions',

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

  computed: {
    ...mapState('auth', {
      isAdmin: 'admin'
    }),

    visible() {
      return !this.parsingFailed;
    },

    scriptHash() {
      return scriptNameToHash(this.scriptName);
    },

    editUrl() {
      return 'admin.html#/scripts/' + encodeURIComponent(this.scriptName);
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

    canStop() {
      return this.isExecuting;
    },

    killEnabled() {
      return !isNull(this.executor) && this.executor.state.killEnabled;
    },

    killTimeoutSec() {
      return isNull(this.executor) ? null : this.executor.state.killTimeoutSec;
    },

    stopButtonTitle() {
      if (!this.canStop) return 'Script not running';
      if (this.killEnabled) return 'Kill script';
      if (this.killTimeoutSec) return `Stop (${this.killTimeoutSec}s to kill)`;
      return 'Stop script';
    }
  },

  methods: {
    navigateAndExecute() {
      if (!this.canExecute) return;

      // Set flag in store for auto-execution
      this.$store.commit('scripts/SET_PENDING_AUTO_EXECUTE', true);

      // Navigate to the script
      this.$router.push('/' + this.scriptHash);
    },

    stopScript() {
      if (!this.executor || !this.canStop) return;

      const executionId = this.executor.state.id;
      if (this.killEnabled) {
        this.$store.dispatch('executions/' + executionId + '/killExecution');
      } else {
        this.$store.dispatch('executions/' + executionId + '/stopExecution');
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

.execute-btn {
  background-color: var(--primary-color);
  color: var(--font-on-primary-color-main);
}

.execute-btn:hover:not(.disabled) {
  background-color: var(--primary-color-dark);
}

.stop-btn {
  background-color: #e57373;
  color: white;
}

.stop-btn:hover:not(.disabled) {
  background-color: #ef5350;
}

.stop-btn.kill-mode {
  background-color: #c62828;
}

.stop-btn.kill-mode:hover:not(.disabled) {
  background-color: #b71c1c;
}

.edit-btn {
  background-color: var(--surface-color);
  color: var(--font-color-main);
  border: 1px solid var(--separator-color);
}

.edit-btn:hover {
  background-color: var(--hover-color);
  color: var(--primary-color);
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
