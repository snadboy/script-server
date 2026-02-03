<template>
  <div v-if="visible" class="modal-overlay">
    <div class="modal-dialog project-config-modal">
      <div class="modal-header">
        <h5 class="modal-title">
          <i class="material-icons">tune</i>
          Configure Project: {{ project?.name }}
        </h5>
        <button class="modal-close" @click="close">
          <i class="material-icons">close</i>
        </button>
      </div>

      <!-- Tabs -->
      <div class="modal-tabs">
        <button
          :class="['tab-btn', { active: activeTab === 'parameters' }]"
          @click="activeTab = 'parameters'"
        >
          <i class="material-icons">list</i>
          Parameters
        </button>
        <button
          :class="['tab-btn', { active: activeTab === 'verbs' }]"
          @click="activeTab = 'verbs'"
        >
          <i class="material-icons">code</i>
          Verbs
        </button>
      </div>

      <div class="modal-body">
        <!-- Error/Success Messages -->
        <div v-if="error" class="error-message">{{ error }}</div>
        <div v-if="success" class="success-message">{{ success }}</div>

        <!-- Loading State -->
        <div v-if="loading" class="loading-state">
          <i class="material-icons spinning">hourglass_empty</i>
          Loading configuration...
        </div>

        <!-- Parameters Tab -->
        <div v-else-if="activeTab === 'parameters'" class="tab-content">
          <ProjectParametersEditor
            v-model="parameters"
            :verbs="verbs"
            :shared-parameters="sharedParameters"
            @update:modelValue="markUnsaved"
            @update:verbs="updateVerbs"
            @update:sharedParameters="updateSharedParameters"
          />
        </div>

        <!-- Verbs Tab -->
        <div v-else-if="activeTab === 'verbs'" class="tab-content">
          <VerbConfigEditor
            v-model:verbs-config="verbsConfig"
            :available-parameters="parameterNames"
            @update:verbsConfig="markUnsaved"
          />
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn btn-secondary" @click="close">Cancel</button>
        <button
          class="btn btn-primary"
          :disabled="saving || !canSave"
          @click="save"
        >
          <i v-if="saving" class="material-icons spinning">hourglass_empty</i>
          <i v-else class="material-icons">save</i>
          {{ saving ? 'Saving...' : 'Save Configuration' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import {axiosInstance} from '@/common/utils/axios_utils';
import ProjectParametersEditor from './ProjectParametersEditor.vue';
import VerbConfigEditor from '@/admin/components/scripts-config/VerbConfigEditor.vue';

export default {
  name: 'ProjectConfigModal',

  components: {
    ProjectParametersEditor,
    VerbConfigEditor
  },

  props: {
    visible: {
      type: Boolean,
      default: false
    },
    project: {
      type: Object,
      default: null
    }
  },

  emits: ['close', 'saved'],

  data() {
    return {
      activeTab: 'parameters',
      loading: false,
      saving: false,
      error: null,
      success: null,
      hasUnsavedChanges: false,

      // Configuration data
      parameters: [],
      verbsConfig: null,
      sharedParameters: []
    };
  },

  computed: {
    parameterNames() {
      return this.parameters.map(p => p.name);
    },

    canSave() {
      // On Parameters tab, always allow saving
      if (this.activeTab === 'parameters') {
        return this.hasUnsavedChanges;
      }

      // On Verbs tab, require at least one verb option if verbs are enabled
      if (this.activeTab === 'verbs') {
        if (this.verbsConfig && (!this.verbsConfig.options || this.verbsConfig.options.length === 0)) {
          return false;
        }
        return this.hasUnsavedChanges;
      }

      return this.hasUnsavedChanges;
    }
  },

  watch: {
    visible(newVal) {
      if (newVal && this.project) {
        this.loadConfiguration();
      } else {
        this.reset();
      }
    }
  },

  methods: {
    async loadConfiguration() {
      if (!this.project) return;

      this.loading = true;
      this.error = null;

      try {
        const response = await axiosInstance.get(`/admin/projects/${this.project.id}/config`);
        const config = response.data;

        this.parameters = config.parameters || [];
        this.verbsConfig = config.verbs || null;
        this.sharedParameters = config.sharedParameters || [];
        this.hasUnsavedChanges = false;
      } catch (err) {
        console.error('Failed to load project configuration:', err);
        this.error = err.response?.data?.message || 'Failed to load configuration';
      } finally {
        this.loading = false;
      }
    },

    async save() {
      this.saving = true;
      this.error = null;
      this.success = null;

      try {
        // Save parameters
        await axiosInstance.put(
          `/admin/projects/${this.project.id}/parameters`,
          {parameters: this.parameters}
        );

        // Save verbs
        await axiosInstance.put(
          `/admin/projects/${this.project.id}/verbs`,
          {
            verbs: this.verbsConfig,
            sharedParameters: []
          }
        );

        this.success = 'Configuration saved successfully!';
        this.hasUnsavedChanges = false;

        setTimeout(() => {
          this.$emit('saved', this.project);
          this.close();
        }, 1500);
      } catch (err) {
        console.error('Failed to save configuration:', err);
        this.error = err.response?.data?.message || 'Failed to save configuration';
      } finally {
        this.saving = false;
      }
    },

    markUnsaved() {
      this.hasUnsavedChanges = true;
    },

    updateVerbs(updatedVerbs) {
      this.verbs = updatedVerbs;
      this.markUnsaved();
    },

    updateSharedParameters(updatedShared) {
      this.sharedParameters = updatedShared;
      this.markUnsaved();
    },

    close() {
      if (this.hasUnsavedChanges) {
        if (!confirm('You have unsaved changes. Are you sure you want to close?')) {
          return;
        }
      }
      this.$emit('close');
    },

    reset() {
      this.activeTab = 'parameters';
      this.parameters = [];
      this.verbsConfig = null;
      this.sharedParameters = [];
      this.hasUnsavedChanges = false;
      this.error = null;
      this.success = null;
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
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.modal-dialog {
  background: var(--background-color, #fff);
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 900px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color, #e0e0e0);
}

.modal-title {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}

.modal-title .material-icons {
  font-size: 24px;
  color: var(--primary-color, #2196F3);
}

.modal-close {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.modal-close:hover {
  background-color: var(--hover-color, #f5f5f5);
}

.modal-close .material-icons {
  font-size: 24px;
  color: var(--text-secondary, #666);
}

.modal-tabs {
  display: flex;
  border-bottom: 1px solid var(--border-color, #e0e0e0);
  background: var(--tabs-background, #f9f9f9);
}

.tab-btn {
  flex: 1;
  padding: 12px 16px;
  border: none;
  background: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary, #666);
  transition: all 0.2s;
  border-bottom: 2px solid transparent;
}

.tab-btn:hover {
  background-color: var(--hover-color, #f0f0f0);
  color: var(--text-primary, #333);
}

.tab-btn.active {
  color: var(--primary-color, #2196F3);
  border-bottom-color: var(--primary-color, #2196F3);
  background-color: var(--background-color, #fff);
}

.tab-btn .material-icons {
  font-size: 20px;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  min-height: 0;
  max-height: calc(90vh - 200px);
}

.tab-content {
  min-height: 400px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--text-secondary, #666);
}

.loading-state .material-icons {
  font-size: 48px;
  margin-bottom: 16px;
  color: var(--primary-color, #2196F3);
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.error-message {
  padding: 12px 16px;
  background-color: #ffebee;
  color: #c62828;
  border-radius: 4px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.error-message::before {
  content: 'error';
  font-family: 'Material Icons';
  font-size: 20px;
}

.success-message {
  padding: 12px 16px;
  background-color: #e8f5e9;
  color: #2e7d32;
  border-radius: 4px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.success-message::before {
  content: 'check_circle';
  font-family: 'Material Icons';
  font-size: 20px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-color, #e0e0e0);
}

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--background-color, #fff);
  color: var(--text-primary, #333);
  border: 1px solid var(--border-color, #ddd);
}

.btn-secondary:hover:not(:disabled) {
  background-color: var(--hover-color, #f5f5f5);
}

.btn-primary {
  background: var(--primary-color, #2196F3);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-color-dark, #1976D2);
}

.btn .material-icons {
  font-size: 18px;
}
</style>
