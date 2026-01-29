<template>
  <div v-if="visible" class="modal-overlay">
    <div class="modal-content create-script-modal card">
      <div class="modal-header">
        <span class="modal-title">Create Script</span>
      </div>

      <div class="modal-tabs">
        <button
          v-for="(tab, index) in visibleTabs"
          :key="tab.id"
          class="tab-btn"
          :class="{ active: activeTab === index }"
          @click="activeTab = index"
        >
          <span class="tab-number">{{ index + 1 }}</span>
          <span class="tab-label">{{ tab.label }}</span>
        </button>
      </div>

      <div class="modal-body">
        <div v-if="error" class="error-message">{{ error }}</div>
        <div v-if="success" class="success-message">{{ success }}</div>

        <!-- Source Tab (always visible) -->
        <div v-if="currentTabId === 'source'" class="tab-panel">
          <SourceSelector
            :selected="creationMode"
            @select="handleSourceSelect"
          />
        </div>

        <!-- Import Tab (import mode only) -->
        <div v-if="currentTabId === 'import'" class="tab-panel">
          <ImportPanel
            @import-complete="handleImportComplete"
            @error="handleError"
          />
        </div>

        <!-- Configure Tab (import mode only) -->
        <div v-if="currentTabId === 'configure' && importedProject" class="tab-panel">
          <ConfigurePanel
            :project="importedProject"
            :installed-packages="installedPackages"
            @configure-complete="handleConfigureComplete"
            @packages-updated="loadInstalledPackages"
            @error="handleError"
            @success="handleSuccess"
          />
        </div>

        <!-- Details Tab (always visible after source selection) -->
        <div v-if="currentTabId === 'details'" class="tab-panel">
          <DetailsTab :path-readonly="creationMode === 'import'" />
        </div>

        <!-- Parameters Tab (always visible after source selection) -->
        <div v-if="currentTabId === 'parameters'" class="tab-panel">
          <ScriptParamList :parameters="scriptConfig.parameters"/>
        </div>

        <!-- Advanced Tab (always visible after source selection) -->
        <div v-if="currentTabId === 'advanced'" class="tab-panel">
          <AdvancedTab />
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-flat waves-effect" @click="handleCancel">Cancel</button>
        <button
          v-if="canProceed"
          class="btn waves-effect"
          @click="handleNext"
        >
          {{ nextButtonLabel }}
        </button>
        <button
          v-if="canSave"
          class="btn btn-primary waves-effect"
          :disabled="!isFormValid || saving"
          @click="handleSave"
        >
          {{ saving ? 'Saving...' : 'Save Script' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import {NEW_SCRIPT} from '@/admin/store/script-config-module';
import {axiosInstance} from '@/common/utils/axios_utils';
import ScriptParamList from '../ScriptParamList';
import SourceSelector from './SourceSelector.vue';
import ImportPanel from './ImportPanel.vue';
import ConfigurePanel from './ConfigurePanel.vue';
import DetailsTab from './DetailsTab.vue';
import AdvancedTab from './AdvancedTab.vue';

export default {
  name: 'CreateScriptModal',

  components: {
    ScriptParamList,
    SourceSelector,
    ImportPanel,
    ConfigurePanel,
    DetailsTab,
    AdvancedTab
  },

  props: {
    visible: {
      type: Boolean,
      default: false
    },
    initialMode: {
      type: String,
      default: null,
      validator: (value) => value === null || ['import', 'manual'].includes(value)
    }
  },

  emits: ['close', 'saved'],

  data() {
    return {
      creationMode: null,  // 'import' | 'manual'
      activeTab: 0,
      error: null,
      success: null,
      saving: false,

      // Import state
      importedProject: null,

      // Configure state (from ConfigurePanel)
      configData: {
        entryPoint: '',
        scriptName: '',
        description: '',
        configPath: '',
        configCmd: ''
      },

      // Installed packages
      installedPackages: [],

      // Original parent for modal body append
      originalParent: null,
      boundFixOverlayDimensions: null
    };
  },

  computed: {
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
    },

    visibleTabs() {
      const tabs = [{ id: 'source', label: 'Source' }];

      if (this.creationMode === 'import') {
        tabs.push(
          { id: 'import', label: 'Import' },
          { id: 'configure', label: 'Configure' }
        );
      }

      if (this.creationMode) {
        tabs.push(
          { id: 'details', label: 'Details' },
          { id: 'parameters', label: 'Parameters' },
          { id: 'advanced', label: 'Advanced' }
        );
      }

      return tabs;
    },

    currentTabId() {
      return this.visibleTabs[this.activeTab]?.id;
    },

    canProceed() {
      // Show Next button except on last tab and when form is complete
      if (!this.creationMode) return false;
      if (this.activeTab >= this.visibleTabs.length - 1) return false;

      // For configure tab, require entry point and script name
      if (this.currentTabId === 'configure') {
        return this.configData.entryPoint && this.configData.scriptName;
      }

      return true;
    },

    canSave() {
      // Show Save button on last 3 tabs (Details, Parameters, Advanced)
      if (!this.creationMode) return false;
      const lastThreeTabs = ['details', 'parameters', 'advanced'];
      return lastThreeTabs.includes(this.currentTabId);
    },

    isFormValid() {
      if (!this.scriptConfig) return false;
      const hasName = this.scriptConfig.name && this.scriptConfig.name.trim().length > 0;
      const hasScript = this.scriptConfig.script_path ||
        (this.scriptConfig.script && (this.scriptConfig.script.path || this.scriptConfig.script.command));
      return hasName && hasScript;
    },

    nextButtonLabel() {
      if (this.currentTabId === 'configure') {
        return 'Continue to Details';
      }
      return 'Next';
    }
  },

  watch: {
    visible(newVal) {
      if (newVal) {
        document.body.style.overflow = 'hidden';
        this.resetState();
        this.$store.dispatch(`${this.storeModule}/init`, NEW_SCRIPT);

        // Handle initial mode (skip Source tab if specified)
        if (this.initialMode === 'manual') {
          this.creationMode = 'manual';
          this.activeTab = 1; // Skip Source tab, go directly to Details
        }

        // Move modal to body
        this.$nextTick(() => {
          this.originalParent = this.$el.parentElement;
          document.body.appendChild(this.$el);
          this.boundFixOverlayDimensions = this.fixOverlayDimensions.bind(this);
          this.boundFixOverlayDimensions();
          window.addEventListener('resize', this.boundFixOverlayDimensions);
        });
      } else {
        document.body.style.overflow = '';
        if (this.boundFixOverlayDimensions) {
          window.removeEventListener('resize', this.boundFixOverlayDimensions);
        }
        if (this.originalParent && this.$el.parentElement === document.body) {
          this.originalParent.appendChild(this.$el);
        }
      }
    }
  },

  methods: {
    resetState() {
      this.creationMode = null;
      this.activeTab = 0;
      this.error = null;
      this.success = null;
      this.saving = false;
      this.importedProject = null;
      this.configData = {
        entryPoint: '',
        scriptName: '',
        description: '',
        configPath: '',
        configCmd: ''
      };
    },

    handleSourceSelect(mode) {
      this.creationMode = mode;
      this.error = null;
      this.success = null;

      if (mode === 'import') {
        // Go to import tab
        this.activeTab = 1;
        this.loadInstalledPackages();
      } else if (mode === 'manual') {
        // Go directly to details tab
        this.activeTab = 1;
      }
    },

    handleImportComplete(project) {
      this.importedProject = project;
      this.success = `Successfully imported ${project.name}`;
      this.error = null;
      // Move to configure tab
      this.activeTab = 2;
    },

    handleConfigureComplete(configData) {
      this.configData = configData;
    },

    handleError(errorMsg) {
      this.error = errorMsg;
      this.success = null;
    },

    handleSuccess(successMsg) {
      this.success = successMsg;
      this.error = null;
    },

    handleNext() {
      // For configure tab, pre-fill Details tab fields
      if (this.currentTabId === 'configure') {
        this.prefillDetailsFromImport();
      }

      this.activeTab++;
    },

    prefillDetailsFromImport() {
      // Generate wrapper path
      const wrapperPath = `samples/scripts/${this.importedProject.id}.py`;

      // Update script config
      this.$store.dispatch(`${this.storeModule}/updateConfig`, {
        ...this.scriptConfig,
        name: this.configData.scriptName || this.importedProject.name,
        description: this.configData.description || '',
        script_path: wrapperPath
      });
    },

    handleCancel() {
      if (this.isDirty) {
        if (!confirm('You have unsaved changes. Are you sure you want to cancel?')) {
          return;
        }
      }
      this.close();
    },

    close() {
      this.$emit('close');
    },

    async loadInstalledPackages() {
      try {
        const response = await axiosInstance.get('admin/venv/packages');
        this.installedPackages = (response.data.packages || []).map(p => p.name || p);
      } catch (e) {
        console.warn('Failed to load installed packages:', e);
        this.installedPackages = [];
      }
    },

    async handleSave() {
      if (!this.isFormValid) return;

      this.saving = true;
      this.error = null;
      this.success = null;

      try {
        if (this.creationMode === 'import') {
          await this.saveImportPath();
        } else {
          await this.saveManualPath();
        }
      } catch (e) {
        this.error = e.response?.data || e.message || 'Failed to save script';
      } finally {
        this.saving = false;
      }
    },

    async saveImportPath() {
      // Generate wrapper + config via backend
      const response = await axiosInstance.post(
        `admin/projects/${encodeURIComponent(this.importedProject.id)}/wrapper`,
        {
          entry_point: this.configData.entryPoint,
          config_path: this.configData.configPath || undefined,
          config_cmd: this.configData.configCmd || undefined,
          script_name: this.scriptConfig.name,
          description: this.scriptConfig.description || undefined
        }
      );

      this.success = `Wrapper and config generated! Script "${this.scriptConfig.name}" is now available.`;
      this.$emit('saved', this.scriptConfig.name);

      // Wait a bit to show success message
      setTimeout(() => {
        this.close();
      }, 1500);
    },

    async saveManualPath() {
      // Use existing scriptConfig store
      await this.$store.dispatch(`${this.storeModule}/save`);

      this.success = `Script "${this.scriptConfig.name}" created successfully!`;
      this.$emit('saved', this.scriptConfig.name);

      // Wait a bit to show success message
      setTimeout(() => {
        this.close();
      }, 1500);
    },

    fixOverlayDimensions() {
      // Fix overlay to cover full viewport
      if (this.$el) {
        const overlay = this.$el.querySelector('.modal-overlay');
        if (overlay) {
          overlay.style.width = '100vw';
          overlay.style.height = '100vh';
        }
      }
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  overflow-y: auto;
  padding: 2rem;
}

.modal-content {
  background: white;
  width: 90%;
  max-width: 1200px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  border-radius: var(--border-radius, 8px);
  box-shadow: var(--shadow, 0 8px 32px rgba(0, 0, 0, 0.2));
}

.modal-header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid var(--border-color, #e0e0e0);
}

.modal-title {
  font-size: 1.5rem;
  font-weight: 500;
}

.modal-tabs {
  display: flex;
  border-bottom: 2px solid var(--border-color, #e0e0e0);
  background: var(--tabs-bg, #f5f5f5);
  overflow-x: auto;
}

.tab-btn {
  flex: 1;
  min-width: 120px;
  padding: 1rem;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.2s ease;
  border-bottom: 3px solid transparent;
}

.tab-btn:hover {
  background: var(--hover-color, rgba(0, 0, 0, 0.05));
}

.tab-btn.active {
  background: white;
  border-bottom-color: var(--primary-color, #1976d2);
}

.tab-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--number-bg, #ddd);
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
}

.tab-btn.active .tab-number {
  background: var(--primary-color, #1976d2);
}

.tab-label {
  font-weight: 500;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}

.tab-panel {
  min-height: 400px;
}

.error-message {
  margin: 1rem 2rem;
  padding: 1rem;
  background: var(--error-bg, #ffebee);
  border: 1px solid var(--error-color, #f44336);
  border-radius: var(--border-radius, 4px);
  color: var(--error-color, #f44336);
}

.success-message {
  margin: 1rem 2rem;
  padding: 1rem;
  background: var(--success-bg, #e8f5e9);
  border: 1px solid var(--success-color, #4caf50);
  border-radius: var(--border-radius, 4px);
  color: var(--success-color, #4caf50);
}

.modal-footer {
  padding: 1rem 2rem;
  border-top: 1px solid var(--border-color, #e0e0e0);
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.btn-flat {
  padding: 0.75rem 1.5rem;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: var(--border-radius, 4px);
  transition: all 0.2s ease;
}

.btn-flat:hover {
  background: var(--hover-color, rgba(0, 0, 0, 0.05));
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  background: var(--primary-color, #1976d2);
  color: white;
  cursor: pointer;
  border-radius: var(--border-radius, 4px);
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn:hover:not(:disabled) {
  background: var(--primary-color-dark, #1565c0);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--primary-color, #1976d2);
}
</style>
