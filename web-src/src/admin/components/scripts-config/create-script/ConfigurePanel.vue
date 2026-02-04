<template>
  <div class="configure-panel">
    <h6>{{ project.name }}</h6>

    <!-- Dependencies -->
    <div class="config-group">
      <div class="config-group-header">
        <span class="config-label">
          Dependencies ({{ project.dependencies?.length || 0 }})
          <span v-if="loadingPackages" class="loading-indicator">checking...</span>
          <span v-else-if="allDependenciesInstalled" class="all-installed-badge">All Installed</span>
        </span>
        <button
          v-if="project.dependencies?.length > 0 && missingDependencies.length > 0"
          class="btn btn-sm"
          :disabled="installingDeps || loadingPackages"
          @click="installAllDependencies"
        >
          {{ installingDeps ? 'Installing...' : `Install Missing (${missingDependencies.length})` }}
        </button>
      </div>
      <div v-if="project.dependencies?.length > 0" class="deps-list">
        <span
          v-for="dep in project.dependencies"
          :key="dep"
          :class="['dep-tag', { 'dep-installed': isPackageInstalled(dep) }]"
        >
          <i v-if="isPackageInstalled(dep)" class="material-icons dep-check">check_circle</i>
          {{ dep }}
        </span>
      </div>
      <div v-else class="no-deps">No dependencies detected</div>
    </div>

    <!-- Entry Point Selection -->
    <div class="config-group">
      <label class="config-label">Entry Point</label>
      <select v-model="entryPoint" class="form-select">
        <option value="">Select an entry point...</option>
        <option v-for="ep in project.entry_points" :key="ep" :value="ep">
          {{ ep }}
        </option>
      </select>
      <button
        type="button"
        class="btn-link advanced-toggle"
        @click="showCustomEntryPoint = !showCustomEntryPoint"
      >
        {{ showCustomEntryPoint ? '− Hide custom entry point' : '+ Custom entry point' }}
      </button>
      <div v-if="showCustomEntryPoint" class="custom-entry-point">
        <input
          v-model="customEntryPoint"
          type="text"
          placeholder="module.main:app"
          class="form-input"
        />
        <div class="form-help">
          Use if the detected entry points don't include what you need
        </div>
      </div>
    </div>

    <!-- Script Name -->
    <div class="config-group">
      <label class="config-label">Script Name</label>
      <input
        v-model="scriptName"
        type="text"
        :placeholder="project.name"
        class="form-input"
      />
    </div>

    <!-- Description -->
    <div class="config-group">
      <label class="config-label">Description</label>
      <input
        v-model="description"
        type="text"
        placeholder="What this script does"
        class="form-input"
      />
    </div>

    <!-- Instance Configuration (Project-based) -->
    <div v-if="hasProjectParameters || hasProjectVerbs" class="config-group instance-config-group">
      <div class="config-group-header">
        <span class="config-label">
          <i class="material-icons">tune</i>
          Instance Configuration
        </span>
      </div>

      <div class="instance-config-info">
        <p>Select which parameters to include and optionally override their default values.</p>
      </div>

      <!-- Verb Selection (if project has verbs) -->
      <div v-if="hasProjectVerbs" class="verb-selection">
        <label class="config-label">
          Command/Verb
          <span v-if="project.verbs?.required" class="required-indicator">*</span>
        </label>
        <select v-model="selectedVerb" class="form-select">
          <option value="">{{ project.verbs?.required ? 'Select a command...' : 'None (use all parameters)' }}</option>
          <option
            v-for="verb in project.verbs?.options"
            :key="verb.name"
            :value="verb.name"
          >
            {{ verb.label || verb.name }}
          </option>
        </select>
        <div v-if="selectedVerbOption" class="verb-description">
          {{ selectedVerbOption.description }}
        </div>
      </div>

      <!-- Parameter Selection -->
      <div v-if="availableParameters.length > 0" class="parameter-selection">
        <div class="params-header">
          <label class="config-label">Parameters</label>
          <div class="select-actions">
            <button
              type="button"
              class="btn-link"
              @click="selectAllParameters"
            >
              Select All
            </button>
            <button
              type="button"
              class="btn-link"
              @click="deselectAllParameters"
            >
              Deselect All
            </button>
          </div>
        </div>

        <div class="parameters-list">
          <div
            v-for="param in availableParameters"
            :key="param.name"
            class="parameter-row"
          >
            <div class="parameter-select">
              <label class="checkbox-label">
                <input
                  v-model="selectedParameters"
                  type="checkbox"
                  :value="param.name"
                />
                <div class="param-info">
                  <span class="param-name">{{ param.name }}</span>
                  <span class="param-type">({{ param.type }})</span>
                  <span v-if="param.required" class="param-required">required</span>
                </div>
              </label>
              <div v-if="param.description" class="param-description">
                {{ param.description }}
              </div>
            </div>

            <!-- Value Override (shown if parameter is selected) -->
            <div v-if="selectedParameters.includes(param.name)" class="parameter-value">
              <label class="value-label">
                Override Default
                <span v-if="param.default !== null && param.default !== undefined" class="default-hint">
                  (default: {{ formatDefaultValue(param) }})
                </span>
              </label>

              <!-- Boolean -->
              <label v-if="param.type === 'bool'" class="checkbox-label">
                <input
                  v-model="parameterValues[param.name]"
                  type="checkbox"
                />
                <span>Enabled</span>
              </label>

              <!-- Integer -->
              <input
                v-else-if="param.type === 'int'"
                v-model.number="parameterValues[param.name]"
                type="number"
                :min="param.min"
                :max="param.max"
                class="form-input"
                :placeholder="`Default: ${param.default !== null ? param.default : 'none'}`"
              />

              <!-- Text/Other -->
              <input
                v-else
                v-model="parameterValues[param.name]"
                type="text"
                class="form-input"
                :placeholder="`Default: ${param.default || 'none'}`"
              />
            </div>
          </div>
        </div>
      </div>

      <div v-else class="no-parameters-message">
        <i class="material-icons">info</i>
        <span>No parameters defined for this project. Configure parameters in the Project Configuration.</span>
      </div>
    </div>

    <!-- Config Path (optional) -->
    <div class="config-group">
      <label class="config-label">Config Path (optional)</label>
      <input
        v-model="configPath"
        type="text"
        placeholder="/path/to/config.yaml"
        class="form-input"
      />
    </div>

    <!-- Config Command (optional) -->
    <div class="config-group">
      <label class="config-label">Config Command (optional)</label>
      <input
        v-model="configCmd"
        type="text"
        placeholder="run"
        class="form-input"
      />
      <div class="form-help">
        If specified, --config will be injected when this command is used
      </div>
    </div>

    <!-- Wrapper Preview -->
    <div class="config-group">
      <div class="config-group-header">
        <span class="config-label">Wrapper Script Preview</span>
        <button class="btn btn-sm" @click="previewWrapper" :disabled="!effectiveEntryPoint">
          <i class="material-icons btn-icon-sm">refresh</i>
          Preview
        </button>
      </div>
      <div v-if="wrapperPreview" class="wrapper-preview">
        <pre>{{ wrapperPreview }}</pre>
      </div>
    </div>
  </div>
</template>

<script>
import {axiosInstance} from '@/common/utils/axios_utils';

export default {
  name: 'ConfigurePanel',

  props: {
    project: {
      type: Object,
      required: true
    },
    installedPackages: {
      type: Array,
      default: () => []
    }
  },

  emits: ['configure-complete', 'error', 'packages-updated'],

  data() {
    return {
      entryPoint: '',
      customEntryPoint: '',
      showCustomEntryPoint: false,
      scriptName: '',
      description: '',
      configPath: '',
      configCmd: '',
      wrapperPreview: '',
      installingDeps: false,
      loadingPackages: false,

      // Instance configuration
      selectedVerb: '',
      selectedParameters: [],
      parameterValues: {}
    };
  },

  computed: {
    effectiveEntryPoint() {
      return this.customEntryPoint || this.entryPoint;
    },

    missingDependencies() {
      if (!this.project?.dependencies) return [];
      const installedLower = this.installedPackages.map(p => p.toLowerCase());
      return this.project.dependencies.filter(
        dep => !installedLower.includes(dep.toLowerCase())
      );
    },

    allDependenciesInstalled() {
      return this.project?.dependencies?.length > 0 &&
             this.missingDependencies.length === 0;
    },

    hasProjectParameters() {
      return this.project?.parameters && this.project.parameters.length > 0;
    },

    hasProjectVerbs() {
      return this.project?.verbs && this.project.verbs.options && this.project.verbs.options.length > 0;
    },

    selectedVerbOption() {
      if (!this.selectedVerb || !this.hasProjectVerbs) return null;
      return this.project.verbs.options.find(v => v.name === this.selectedVerb);
    },

    availableParameters() {
      if (!this.hasProjectParameters) return [];

      const allParams = this.project.parameters;

      // If a verb is selected, filter to verb-specific + shared parameters
      if (this.selectedVerbOption) {
        const verbParams = this.selectedVerbOption.parameters || [];
        const sharedParams = this.project.shared_parameters || [];
        const allowedParams = new Set([...verbParams, ...sharedParams]);

        return allParams.filter(p => allowedParams.has(p.name));
      }

      // No verb selected - show all parameters
      return allParams;
    },

    configData() {
      const data = {
        entryPoint: this.effectiveEntryPoint,
        scriptName: this.scriptName,
        description: this.description,
        configPath: this.configPath,
        configCmd: this.configCmd
      };

      // Add instance config if using project-based parameters
      if (this.hasProjectParameters || this.hasProjectVerbs) {
        data.includedParameters = this.selectedParameters;
        data.parameterValues = this.getEffectiveParameterValues();
        data.selectedVerb = this.selectedVerb || null;
      }

      return data;
    }
  },

  watch: {
    project: {
      immediate: true,
      handler(newVal) {
        if (newVal) {
          this.$nextTick(() => {
            this.entryPoint = newVal.entry_points?.[0] || '';
          });
          this.customEntryPoint = '';
          this.scriptName = newVal.name || '';
          this.description = '';
          this.configPath = '';
          this.configCmd = '';
          this.wrapperPreview = '';
        }
      }
    },

    configData: {
      deep: true,
      handler(newVal) {
        this.$emit('configure-complete', newVal);
      }
    }
  },

  methods: {
    isPackageInstalled(dep) {
      const depLower = dep.toLowerCase();
      return this.installedPackages.some(p => p.toLowerCase() === depLower);
    },

    async installAllDependencies() {
      const toInstall = this.missingDependencies;
      if (!toInstall.length) return;

      this.installingDeps = true;

      let installed = 0;
      let failed = 0;

      try {
        for (const dep of toInstall) {
          try {
            await axiosInstance.post('admin/venv/packages/install', {
              package: dep
            });
            installed++;
          } catch (e) {
            console.warn(`Failed to install ${dep}:`, e);
            failed++;
          }
        }

        this.$emit('packages-updated');

        if (failed === 0) {
          this.$emit('success', `Successfully installed ${installed} package${installed !== 1 ? 's' : ''}`);
        } else {
          this.$emit('success', `Installed ${installed} package${installed !== 1 ? 's' : ''}, ${failed} failed`);
        }
      } catch (e) {
        this.$emit('error', 'Failed to install dependencies');
      } finally {
        this.installingDeps = false;
      }
    },

    async previewWrapper() {
      if (!this.effectiveEntryPoint || !this.project) return;

      try {
        const response = await axiosInstance.post(
          `admin/projects/${encodeURIComponent(this.project.id)}/wrapper-preview`,
          {
            entry_point: this.effectiveEntryPoint,
            config_path: this.configPath || undefined,
            config_cmd: this.configCmd || undefined
          }
        );
        this.wrapperPreview = response.data.wrapper_content;
      } catch (e) {
        this.$emit('error', e.response?.data || 'Failed to generate preview');
      }
    },

    selectAllParameters() {
      this.selectedParameters = this.availableParameters.map(p => p.name);
      this.initializeParameterValues();
    },

    deselectAllParameters() {
      this.selectedParameters = [];
      this.parameterValues = {};
    },

    initializeParameterValues() {
      // Initialize values for newly selected parameters with their defaults
      this.selectedParameters.forEach(paramName => {
        if (this.parameterValues[paramName] === undefined) {
          const param = this.availableParameters.find(p => p.name === paramName);
          if (param && param.default !== null && param.default !== undefined) {
            this.$set(this.parameterValues, paramName, param.default);
          }
        }
      });
    },

    formatDefaultValue(param) {
      if (param.default === null || param.default === undefined) {
        return 'none';
      }
      if (param.type === 'bool') {
        return param.default ? 'true' : 'false';
      }
      return String(param.default);
    },

    getEffectiveParameterValues() {
      // Only return values that differ from the project defaults
      const overrides = {};
      this.selectedParameters.forEach(paramName => {
        const param = this.availableParameters.find(p => p.name === paramName);
        const value = this.parameterValues[paramName];

        // Check if value is different from default
        if (value !== undefined && value !== param?.default) {
          overrides[paramName] = value;
        }
      });
      return overrides;
    }
  },

  watch: {
    selectedVerb(newVal, oldVal) {
      if (newVal !== oldVal) {
        // Verb changed - reset parameter selection
        this.selectedParameters = [];
        this.parameterValues = {};
      }
    },

    selectedParameters: {
      handler() {
        this.initializeParameterValues();
      },
      deep: true
    }
  }
}
</script>

<style scoped>
.configure-panel {
  padding: 1.5rem;
  max-width: 800px;
  margin: 0 auto;
}

.configure-panel h6 {
  margin: 0 0 1.5rem 0;
  font-size: 1.25rem;
  font-weight: 500;
}

.config-group {
  margin-bottom: 1.5rem;
}

.config-group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.config-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.loading-indicator {
  font-size: 0.85rem;
  color: var(--text-color-secondary, #666);
  margin-left: 0.5rem;
}

.all-installed-badge {
  font-size: 0.85rem;
  color: var(--success-color, #4caf50);
  margin-left: 0.5rem;
}

.deps-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.dep-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.75rem;
  border-radius: var(--border-radius, 4px);
  background: var(--tag-bg, #f5f5f5);
  border: 1px solid var(--border-color, #ddd);
  font-size: 0.875rem;
}

.dep-tag.dep-installed {
  background: var(--success-bg, #e8f5e9);
  border-color: var(--success-color, #4caf50);
  color: var(--success-color, #4caf50);
}

.dep-check {
  font-size: 16px !important;
}

.no-deps {
  color: var(--text-color-secondary, #666);
  font-style: italic;
}

.form-select,
.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color, #ddd);
  border-radius: var(--border-radius, 4px);
  font-size: 1rem;
  /* Override Materialize CSS opacity quirk */
  opacity: 1 !important;
  appearance: menulist;
}

.btn-link {
  background: none;
  border: none;
  color: var(--primary-color, #1976d2);
  cursor: pointer;
  font-size: 0.875rem;
  padding: 0.5rem 0;
  text-decoration: underline;
}

.btn-link:hover {
  color: var(--primary-color-dark, #1565c0);
}

.advanced-toggle {
  margin-top: 0.5rem;
}

.custom-entry-point {
  margin-top: 0.75rem;
}

.form-help {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-color-secondary, #666);
}

.wrapper-preview {
  margin-top: 0.75rem;
  padding: 1rem;
  background: var(--code-bg, #f5f5f5);
  border: 1px solid var(--border-color, #ddd);
  border-radius: var(--border-radius, 4px);
  max-height: 300px;
  overflow-y: auto;
}

.wrapper-preview pre {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
  white-space: pre-wrap;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: var(--border-radius, 4px);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-icon-sm {
  font-size: 18px !important;
  vertical-align: middle;
  margin-right: 0.25rem;
}

/* Instance Configuration Styles */
.instance-config-group {
  background: var(--instance-config-bg, #f8f9fa);
  border: 2px solid var(--primary-color, #2196F3);
  border-radius: 6px;
  padding: 16px;
  margin: 20px 0;
}

.instance-config-group .config-group-header .material-icons {
  vertical-align: middle;
  margin-right: 6px;
  color: var(--primary-color, #2196F3);
}

.instance-config-info {
  margin: 12px 0;
  padding: 12px;
  background: var(--info-bg, #e3f2fd);
  border-left: 3px solid var(--primary-color, #2196F3);
  border-radius: 4px;
}

.instance-config-info p {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary, #666);
}

.verb-selection {
  margin: 16px 0;
}

.verb-description {
  margin-top: 8px;
  padding: 8px 12px;
  background: var(--desc-bg, #f5f5f5);
  border-radius: 4px;
  font-size: 13px;
  color: var(--text-secondary, #666);
  font-style: italic;
}

.required-indicator {
  color: #d32f2f;
  font-weight: bold;
  margin-left: 4px;
}

.parameter-selection {
  margin-top: 16px;
}

.params-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.select-actions {
  display: flex;
  gap: 12px;
}

.btn-link {
  background: none;
  border: none;
  color: var(--primary-color, #2196F3);
  cursor: pointer;
  font-size: 13px;
  text-decoration: underline;
  padding: 4px 8px;
}

.btn-link:hover {
  color: var(--primary-color-dark, #1976D2);
}

.parameters-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.parameter-row {
  border: 1px solid var(--border-color, #ddd);
  border-radius: 4px;
  padding: 12px;
  background: var(--card-bg, #fff);
}

.parameter-select {
  margin-bottom: 8px;
}

.checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  margin-top: 3px;
  width: 18px;
  height: 18px;
  cursor: pointer;
  flex-shrink: 0;
}

.param-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.param-name {
  font-family: 'Courier New', monospace;
  font-weight: 500;
  font-size: 14px;
}

.param-type {
  font-size: 12px;
  color: var(--text-secondary, #666);
  font-style: italic;
}

.param-required {
  background: #d32f2f;
  color: white;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
}

.param-description {
  margin-left: 28px;
  font-size: 13px;
  color: var(--text-secondary, #666);
  margin-top: 4px;
}

.parameter-value {
  margin-left: 28px;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed var(--border-color, #ddd);
}

.value-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary, #333);
  margin-bottom: 6px;
  display: block;
}

.default-hint {
  font-size: 12px;
  color: var(--text-secondary, #999);
  font-weight: normal;
  font-style: italic;
}

.no-parameters-message {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--warning-bg, #fff3cd);
  border: 1px solid var(--warning-border, #ffc107);
  border-radius: 4px;
  color: var(--warning-text, #856404);
  margin-top: 12px;
}

.no-parameters-message .material-icons {
  font-size: 24px;
}
</style>
