<template>
  <div class="script-inline-actions" v-if="visible" @click.stop>
    <button
        class="action-btn execute-btn waves-effect waves-light"
        title="Execute script"
        @click="openExecuteModal">
      <i class="material-icons">play_arrow</i>
    </button>

    <button
        v-if="isSchedulable"
        class="action-btn schedule-btn waves-effect waves-light"
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

    <button
        v-if="isAdmin"
        class="action-btn delete-btn waves-effect waves-light"
        title="Delete script"
        @click="deleteScript">
      <i class="material-icons">delete</i>
    </button>

    <ExecuteModal
        :visible="showExecuteModal"
        :script-name="scriptName"
        @close="showExecuteModal = false"/>

    <ScheduleModal
        :visible="showScheduleModal"
        :script-name="scriptName"
        @close="showScheduleModal = false"/>

    <EditScriptModal
        :visible="showEditModal"
        :script-name="scriptName"
        @close="showEditModal = false"
        @saved="handleEditSaved"/>
  </div>
</template>

<script>
import {scriptNameToHash} from '../../utils/model_helper';
import {mapState} from 'vuex';
import ExecuteModal from '@/main-app/components/scripts/ExecuteModal';
import ScheduleModal from '@/main-app/components/schedule/ScheduleModal';
import EditScriptModal from '@/main-app/components/scripts/EditScriptModal';

export default {
  name: 'ScriptInlineActions',

  components: {
    ExecuteModal,
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
      showExecuteModal: false,
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

    isSchedulable() {
      // Only show schedule button for the currently selected script
      // and only if that script is schedulable
      if (this.selectedScript !== this.scriptName) {
        return false;
      }
      return this.scriptConfig && this.scriptConfig.schedulable;
    }
  },

  methods: {
    openExecuteModal() {
      // Navigate to the script first to load its config
      if (this.selectedScript !== this.scriptName) {
        this.$router.push('/' + this.scriptHash);
        // Wait for navigation and script load before showing modal
        this.$nextTick(() => {
          setTimeout(() => {
            this.showExecuteModal = true;
          }, 100);
        });
      } else {
        this.showExecuteModal = true;
      }
    },

    openScheduleModal() {
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

    deleteScript() {
      const confirmed = window.confirm(`Are you sure you want to delete "${this.scriptName}"?`);
      if (!confirmed) {
        return;
      }

      // Store the script name before deleting (component may unmount)
      const scriptName = this.scriptName;
      const isCurrentScript = this.selectedScript === scriptName;

      // Call delete API
      this.$store.dispatch('adminScriptConfig/init', scriptName)
        .then(() => {
          return this.$store.dispatch('adminScriptConfig/deleteScript');
        })
        .then(() => {
          M.toast({ html: 'Script deleted successfully', classes: 'green' });

          // Navigate away if viewing the deleted script
          if (isCurrentScript) {
            this.$router.push('/');
          }

          // Refresh scripts list
          this.$nextTick(() => {
            this.$store.dispatch('scripts/init');
          });
        })
        .catch((e) => {
          const message = e.userMessage || 'Failed to delete script';
          M.toast({ html: message, classes: 'red' });
        });
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

.execute-btn:hover,
.edit-btn:hover,
.schedule-btn:hover {
  background-color: var(--hover-color);
  color: var(--primary-color);
}

.delete-btn {
  background-color: var(--surface-color);
  color: var(--error-color);
  border: 1px solid var(--separator-color);
}

.delete-btn:hover {
  background-color: var(--error-color);
  color: white;
}

.action-btn.disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
