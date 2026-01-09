<template>
  <div v-if="visible" class="modal-overlay" @click.self="handleClose">
    <div class="modal-content add-script-modal card">
      <div class="modal-header">
        <span class="modal-title">Add New Script</span>
        <button class="btn-flat modal-close-btn" @click="handleClose">
          <i class="material-icons">close</i>
        </button>
      </div>

      <div class="modal-body">
        <div v-if="loadingError" class="error">{{ loadingError }}</div>
        <template v-else-if="scriptConfig">
          <ScriptConfigForm v-model="scriptConfig" :original-name="NEW_SCRIPT"/>
          <h5>Parameters</h5>
          <ScriptParamList :parameters="scriptConfig.parameters"/>
        </template>
      </div>

      <div class="modal-footer">
        <button class="btn-flat waves-effect" @click="handleClose">Cancel</button>
        <PromisableButton :click="save" title="Save"/>
      </div>
    </div>
  </div>
</template>

<script>
import {NEW_SCRIPT} from '@/admin/store/script-config-module';
import PromisableButton from '@/common/components/PromisableButton';
import ScriptConfigForm from './ScriptConfigForm';
import ScriptParamList from './ScriptParamList';

export default {
  name: 'AddScriptModal',
  components: {PromisableButton, ScriptParamList, ScriptConfigForm},

  props: {
    visible: {
      type: Boolean,
      default: false
    }
  },

  data() {
    return {
      NEW_SCRIPT
    };
  },

  computed: {
    // Detect which store module to use (admin.html uses 'scriptConfig', index.html uses 'adminScriptConfig')
    storeModule() {
      return this.$store.state.adminScriptConfig ? 'adminScriptConfig' : 'scriptConfig';
    },
    scriptConfig() {
      return this.$store.state[this.storeModule].scriptConfig;
    },
    loadingError() {
      return this.$store.state[this.storeModule].error;
    },
    isDirty() {
      return this.$store.state[this.storeModule].isDirty;
    }
  },

  watch: {
    visible(newVal) {
      if (newVal) {
        document.body.style.overflow = 'hidden';
        this.$store.dispatch(`${this.storeModule}/init`, NEW_SCRIPT);
      } else {
        document.body.style.overflow = '';
      }
    },

    scriptConfig: {
      deep: true,
      handler(newVal, oldVal) {
        if (this.scriptConfig) {
          if (!oldVal && newVal) {
            this.captureOriginal();
          } else {
            this.checkDirty();
          }
        }
      }
    }
  },

  mounted() {
    document.addEventListener('keydown', this.handleKeydown);
  },

  beforeDestroy() {
    document.removeEventListener('keydown', this.handleKeydown);
    document.body.style.overflow = '';
  },

  methods: {
    save() {
      return this.$store.dispatch(`${this.storeModule}/save`)
        .then((result) => {
          const scriptName = this.scriptConfig.name;
          this.$emit('saved', scriptName);
        })
        .catch((e) => {
          if (e.userMessage) {
            M.toast({html: e.userMessage, classes: 'red'});
          } else {
            M.toast({html: 'Failed to save script', classes: 'red'});
          }
          throw e;
        });
    },

    handleClose() {
      if (this.isDirty) {
        const confirmed = window.confirm('You have unsaved changes. Discard changes and close?');
        if (!confirmed) {
          return;
        }
      }
      this.$store.commit(`${this.storeModule}/SET_DIRTY`, false);
      this.$emit('close');
    },

    handleKeydown(e) {
      if (!this.visible) return;

      if (e.key === 'Escape') {
        this.handleClose();
      }
    },

    captureOriginal() {
      setTimeout(() => {
        if (this.scriptConfig) {
          this.$store.commit(`${this.storeModule}/CAPTURE_ORIGINAL`);
        }
      }, 100);
    },

    checkDirty() {
      const original = this.$store.state[this.storeModule].originalConfigJson;
      if (!original) {
        return false;
      }
      const current = JSON.stringify(this.scriptConfig);
      const isDirty = original !== current;
      this.$store.commit(`${this.storeModule}/SET_DIRTY`, isDirty);
      return isDirty;
    }
  }
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.add-script-modal {
  width: 85%;
  height: 85vh;
  display: flex;
  flex-direction: column;
  border-radius: var(--radius-md);
  margin: 0;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid var(--separator-color);
  flex-shrink: 0;
}

.modal-title {
  font-size: 1.4em;
  font-weight: 500;
  color: var(--font-color-main);
}

.modal-close-btn {
  padding: 0 8px;
  min-width: auto;
}

.modal-close-btn i {
  color: var(--font-color-medium);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.modal-body h5 {
  margin-left: 0.75rem;
  margin-top: 0.5rem;
  margin-bottom: 2rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--separator-color);
  flex-shrink: 0;
  background: var(--background-color-level-16dp);
}

.error {
  color: var(--error-color);
  padding: 16px;
  text-align: center;
}

@media screen and (max-width: 768px) {
  .add-script-modal {
    width: 95%;
    height: 95vh;
  }

  .modal-body {
    padding: 16px;
  }
}
</style>
