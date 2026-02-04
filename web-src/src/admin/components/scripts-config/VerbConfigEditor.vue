<template>
  <div class="verb-config-editor">
    <div class="row">
      <CheckBox
        v-model="verbsEnabled"
        :config="enabledField"
        class="col s12 checkbox-field"
      />
    </div>

    <template v-if="verbsEnabled">
      <!-- Verb Configuration Section -->
      <div class="verb-config-section">
        <h6>Verb Configuration</h6>
        <div class="row">
          <TextField
            v-model="config.parameter_name"
            :config="parameterNameField"
            class="col s4"
          />
          <div class="col s4">
            <label class="section-label">Default Verb</label>
            <select
              v-model="config.default"
              class="browser-default default-verb-select"
            >
              <option value="">None</option>
              <option
                v-for="option in verbOptions"
                :key="option.name"
                :value="option.name"
              >
                {{ option.label || option.name }}
              </option>
            </select>
            <p class="helper-text select-helper">Which verb to pre-select by default</p>
          </div>
          <CheckBox
            v-model="config.required"
            :config="requiredField"
            class="col s3 offset-s1 checkbox-field"
          />
        </div>

        <div class="row">
          <div class="col s12">
            <label class="section-label">Pass As</label>
            <select
              v-model="verbPassMode"
              class="browser-default default-verb-select"
            >
              <option
                v-for="mode in passAsModes"
                :key="mode.value"
                :value="mode.value"
              >
                {{ mode.label }}
              </option>
            </select>
            <p class="helper-text select-helper">How the verb is passed on command line</p>
          </div>
        </div>
      </div>

      <!-- Verb Options Section -->
      <div class="verbs-section">
        <div class="editor-header">
          <span class="header-title">Verb Options ({{ verbOptions.length }})</span>
          <button class="btn btn-primary btn-sm" @click="addVerb">
            <i class="material-icons">add</i>
            Add Verb
          </button>
        </div>

        <!-- Empty State -->
        <div v-if="verbOptions.length === 0" class="empty-state">
          <i class="material-icons">category</i>
          <p>No verbs defined yet</p>
          <p class="empty-hint">Click "Add Verb" to create your first verb/subcommand</p>
        </div>

        <!-- Master-Detail Layout -->
        <div v-else class="master-detail-container">
          <!-- Scrollable Table (Master) -->
          <div class="verbs-table-container">
            <table class="verbs-table">
              <thead>
                <tr>
                  <th class="col-name">Name</th>
                  <th class="col-label">Label</th>
                  <th class="col-description">Description</th>
                  <th class="col-params">Parameters</th>
                  <th class="col-actions">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(verb, index) in verbOptions"
                  :key="index"
                  :class="{ selected: selectedIndex === index }"
                  @click="selectVerb(index)"
                >
                  <td class="col-name">
                    <code>{{ verb.name || '(unnamed)' }}</code>
                  </td>
                  <td class="col-label">{{ verb.label || '-' }}</td>
                  <td class="col-description">{{ truncate(verb.description) }}</td>
                  <td class="col-params">{{ verb.parameters?.length || 0 }}</td>
                  <td class="col-actions">
                    <button
                      v-if="index > 0"
                      class="btn-icon"
                      title="Move Up"
                      @click.stop="moveVerbUp(index)"
                    >
                      <i class="material-icons">arrow_upward</i>
                    </button>
                    <button
                      v-if="index < verbOptions.length - 1"
                      class="btn-icon"
                      title="Move Down"
                      @click.stop="moveVerbDown(index)"
                    >
                      <i class="material-icons">arrow_downward</i>
                    </button>
                    <button
                      class="btn-icon btn-delete"
                      title="Delete"
                      @click.stop="deleteVerb(index)"
                    >
                      <i class="material-icons">delete</i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Edit Panel (Detail) -->
          <div v-if="selectedIndex !== null" class="verb-edit-panel">
            <h6 class="edit-panel-title">
              Edit Verb: <code>{{ selectedVerb.name || '(unnamed)' }}</code>
            </h6>

            <div class="edit-panel-content">
              <!-- Basic Fields -->
              <div class="form-row">
                <div class="form-group">
                  <label>Verb Name <span class="required">*</span></label>
                  <input
                    v-model="selectedVerb.name"
                    class="form-input"
                    placeholder="run, create, delete..."
                    @input="emitUpdate"
                  />
                  <p class="help-text">CLI value (e.g., "create", "delete")</p>
                </div>

                <div class="form-group">
                  <label>Label</label>
                  <input
                    v-model="selectedVerb.label"
                    class="form-input"
                    placeholder="Create Item"
                    @input="emitUpdate"
                  />
                  <p class="help-text">Display text shown in UI</p>
                </div>
              </div>

              <div class="form-group">
                <label>Description</label>
                <textarea
                  v-model="selectedVerb.description"
                  class="form-textarea"
                  rows="2"
                  placeholder="Help text shown when verb is selected"
                  @input="emitUpdate"
                ></textarea>
              </div>

              <!-- Parameter Selection -->
              <div v-if="availableParameters.length > 0" class="form-group">
                <label class="section-label">Available Parameters</label>
                <p class="help-text">Select which parameters are visible when this verb is selected</p>

                <div class="parameter-selection">
                  <div class="parameter-selection-header">
                    <span class="parameter-selection-label">Select Parameters:</span>
                    <div class="parameter-selection-actions">
                      <button
                        type="button"
                        class="link-button"
                        @click="selectAllParameters"
                      >
                        Select All
                      </button>
                      <span class="separator">|</span>
                      <button
                        type="button"
                        class="link-button"
                        @click="deselectAllParameters"
                      >
                        Deselect All
                      </button>
                    </div>
                  </div>

                  <div class="parameter-checkboxes">
                    <label
                      v-for="param in availableParameters"
                      :key="param.name"
                      class="parameter-checkbox-label"
                      :class="{ shared: isSharedParameter(param.name) }"
                    >
                      <input
                        type="checkbox"
                        :checked="isParameterInVerb(param.name)"
                        :disabled="isSharedParameter(param.name)"
                        @change="toggleParameter(param.name, $event)"
                      />
                      <span>{{ param.name }}</span>
                      <i v-if="isSharedParameter(param.name)" class="material-icons shared-icon" title="Shared parameter">public</i>
                    </label>
                  </div>

                  <p class="info-message">
                    <i class="material-icons">info</i>
                    Shared parameters (marked with <i class="material-icons tiny">public</i>) are automatically available to all verbs
                  </p>
                </div>
              </div>

              <!-- Required Parameters -->
              <div v-if="selectedVerbParameters.length > 0" class="form-group">
                <label class="section-label">Required Parameters</label>
                <p class="help-text">Which parameters must have a value for this verb</p>

                <div class="parameter-checkboxes">
                  <label
                    v-for="param in selectedVerbParameters"
                    :key="param"
                    class="parameter-checkbox-label required-param"
                  >
                    <input
                      type="checkbox"
                      :checked="isRequiredParameter(param)"
                      @change="toggleRequiredParameter(param, $event)"
                    />
                    <span>{{ param }}</span>
                  </label>
                </div>
              </div>
            </div>
          </div>

          <!-- No Selection Message -->
          <div v-else class="no-selection-message">
            <i class="material-icons">arrow_upward</i>
            <p>Select a verb from the table above to edit its details</p>
          </div>
        </div>
      </div>
    </template>

    <div v-else class="disabled-message">
      <p class="grey-text">
        Enable verb/subcommand support to configure CLI-style commands
        (e.g., <code>git clone</code>, <code>docker run</code>)
      </p>
    </div>
  </div>
</template>

<script>
import '@/common/materializecss/imports/toast';
import TextField from '@/common/components/textfield';
import CheckBox from '@/common/components/checkbox';

export default {
  name: 'VerbConfigEditor',

  components: {
    TextField,
    CheckBox
  },

  props: {
    value: {
      type: Object,
      default: null
    },
    availableParameters: {
      type: Array,
      default: () => []
    },
    sharedParameters: {
      type: Array,
      default: () => []
    }
  },

  data() {
    return {
      config: this.initConfig(),
      selectedIndex: null,
      enabledField: {
        name: 'Enable Verb/Subcommand Support',
        description: 'Allow this script to have multiple subcommands like git or docker'
      },
      parameterNameField: {
        name: 'Parameter Name',
        required: true,
        description: 'Internal name for the verb parameter (default: "verb")'
      },
      requiredField: {
        name: 'Verb Required',
        description: 'User must select a verb to execute'
      }
    };
  },

  computed: {
    verbsEnabled: {
      get() {
        return this.config !== null;
      },
      set(enabled) {
        if (enabled && !this.config) {
          this.config = this.createDefaultConfig();
          this.$emit('input', this.config);
        } else if (!enabled) {
          this.config = null;
          this.$emit('input', null);
        }
      }
    },

    verbOptions() {
      return this.config?.options || [];
    },

    selectedVerb() {
      return this.selectedIndex !== null ? this.verbOptions[this.selectedIndex] : null;
    },

    selectedVerbParameters() {
      return this.selectedVerb?.parameters || [];
    },

    passAsModes() {
      const paramName = this.config?.parameter_name || 'verb';

      // Use actual verb name for examples: default verb, or first option, or fallback to 'run'
      let exampleVerb = this.config?.default;
      if (!exampleVerb && this.config?.options && this.config.options.length > 0) {
        exampleVerb = this.config.options[0].name || 'run';
      }
      if (!exampleVerb) {
        exampleVerb = 'run';
      }

      return [
        {
          value: 'flag',
          label: `Flag with value (e.g., --${paramName} ${exampleVerb})`
        },
        {
          value: 'positional',
          label: `Positional (e.g., script.py ${exampleVerb})`
        },
        {
          value: 'keyvalue',
          label: `Long option with = (e.g., --${paramName}=${exampleVerb})`
        }
      ];
    },

    verbPassMode: {
      get() {
        if (!this.config) return 'flag';

        // Check if it's positional (no param set or verb_position is after_verb)
        if (!this.config.param || this.config.verb_position === 'after_verb') {
          return 'positional';
        }

        // Check if it's --key=value format (param starts with -- and ends with =)
        if (this.config.param && this.config.param.startsWith('--') && this.config.param.endsWith('=')) {
          return 'keyvalue';
        }

        // Otherwise it's a flag with value
        return 'flag';
      },
      set(mode) {
        if (!this.config) return;

        switch (mode) {
          case 'positional':
            // Set verb_position to after_verb, clear param
            this.$set(this.config, 'verb_position', 'after_verb');
            this.$set(this.config, 'param', '');
            this.$set(this.config, 'no_value', false);
            break;
          case 'keyvalue':
            // Set param to --parameter_name=
            const paramName = this.config.parameter_name || 'verb';
            this.$set(this.config, 'param', `--${paramName}=`);
            this.$set(this.config, 'verb_position', undefined);
            this.$set(this.config, 'no_value', false);
            break;
          case 'flag':
          default:
            // Set param to --parameter_name, clear verb_position
            const flagName = this.config.parameter_name || 'verb';
            this.$set(this.config, 'param', `--${flagName}`);
            this.$set(this.config, 'verb_position', undefined);
            this.$set(this.config, 'no_value', false);
            break;
        }
      }
    }
  },

  methods: {
    initConfig() {
      if (this.value) {
        // Ensure options array exists
        if (!this.value.options) {
          this.$set(this.value, 'options', []);
        }
        return this.value;
      }
      return null;
    },

    createDefaultConfig() {
      return {
        parameter_name: 'verb',
        required: true,
        default: '',
        param: '--verb',
        no_value: false,
        verb_position: undefined,
        options: []
      };
    },

    selectVerb(index) {
      this.selectedIndex = index;
    },

    addVerb() {
      if (!this.config.options) {
        this.$set(this.config, 'options', []);
      }

      const newVerb = {
        name: '',
        label: '',
        description: '',
        parameters: [],
        required_parameters: []
      };

      this.config.options.push(newVerb);
      this.selectedIndex = this.config.options.length - 1; // Auto-select new verb
      this.emitUpdate();
    },

    deleteVerb(index) {
      if (!confirm('Are you sure you want to delete this verb?')) return;

      const verb = this.config.options[index];
      this.config.options.splice(index, 1);

      // Clear selection if we deleted the selected verb
      if (this.selectedIndex === index) {
        this.selectedIndex = null;
      } else if (this.selectedIndex > index) {
        this.selectedIndex--;
      }

      M.toast({
        html: `<span>Deleted ${verb.name || 'verb'}</span>`,
        displayLength: 3000
      });

      this.emitUpdate();
    },

    moveVerbUp(index) {
      if (index <= 0) return;
      const options = this.config.options;
      const temp = options[index - 1];
      this.$set(options, index - 1, options[index]);
      this.$set(options, index, temp);

      // Update selection to follow the moved verb
      if (this.selectedIndex === index) {
        this.selectedIndex = index - 1;
      } else if (this.selectedIndex === index - 1) {
        this.selectedIndex = index;
      }

      this.emitUpdate();
    },

    moveVerbDown(index) {
      const options = this.config.options;
      if (index >= options.length - 1) return;
      const temp = options[index + 1];
      this.$set(options, index + 1, options[index]);
      this.$set(options, index, temp);

      // Update selection to follow the moved verb
      if (this.selectedIndex === index) {
        this.selectedIndex = index + 1;
      } else if (this.selectedIndex === index + 1) {
        this.selectedIndex = index;
      }

      this.emitUpdate();
    },

    truncate(text) {
      if (!text) return '-';
      return text.length > 50 ? text.substring(0, 47) + '...' : text;
    },

    emitUpdate() {
      this.$emit('input', this.config);
    },

    isSharedParameter(paramName) {
      return this.sharedParameters && this.sharedParameters.includes(paramName);
    },

    isParameterInVerb(paramName) {
      if (!this.selectedVerb) return false;
      return this.selectedVerb.parameters && this.selectedVerb.parameters.includes(paramName);
    },

    toggleParameter(paramName, event) {
      if (!this.selectedVerb) return;

      const isChecked = event.target.checked;

      if (!this.selectedVerb.parameters) {
        this.$set(this.selectedVerb, 'parameters', []);
      }

      if (isChecked) {
        // Add parameter to verb
        if (!this.selectedVerb.parameters.includes(paramName)) {
          this.selectedVerb.parameters.push(paramName);
        }
      } else {
        // Remove parameter from verb and required list
        this.selectedVerb.parameters = this.selectedVerb.parameters.filter(p => p !== paramName);
        if (this.selectedVerb.required_parameters) {
          this.selectedVerb.required_parameters = this.selectedVerb.required_parameters.filter(p => p !== paramName);
        }
      }

      this.emitUpdate();
    },

    selectAllParameters() {
      if (!this.selectedVerb) return;

      if (!this.selectedVerb.parameters) {
        this.$set(this.selectedVerb, 'parameters', []);
      }

      this.availableParameters.forEach(param => {
        if (!this.isSharedParameter(param.name) && !this.selectedVerb.parameters.includes(param.name)) {
          this.selectedVerb.parameters.push(param.name);
        }
      });

      this.emitUpdate();
    },

    deselectAllParameters() {
      if (!this.selectedVerb) return;

      this.$set(this.selectedVerb, 'parameters', []);
      this.$set(this.selectedVerb, 'required_parameters', []);

      this.emitUpdate();
    },

    isRequiredParameter(paramName) {
      if (!this.selectedVerb) return false;
      return this.selectedVerb.required_parameters && this.selectedVerb.required_parameters.includes(paramName);
    },

    toggleRequiredParameter(paramName, event) {
      if (!this.selectedVerb) return;

      const isChecked = event.target.checked;

      if (!this.selectedVerb.required_parameters) {
        this.$set(this.selectedVerb, 'required_parameters', []);
      }

      if (isChecked) {
        // Add to required list
        if (!this.selectedVerb.required_parameters.includes(paramName)) {
          this.selectedVerb.required_parameters.push(paramName);
        }
      } else {
        // Remove from required list
        this.selectedVerb.required_parameters = this.selectedVerb.required_parameters.filter(p => p !== paramName);
      }

      this.emitUpdate();
    }
  },

  watch: {
    value: {
      immediate: true,
      handler(newValue) {
        this.config = this.initConfig();
      }
    },

    config: {
      deep: true,
      handler(newValue) {
        this.$emit('input', newValue);
      }
    }
  }
};
</script>

<style scoped>
.verb-config-editor {
  padding: 16px 0;
}

.section-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary, #333);
  margin-bottom: 4px;
  display: block;
}

.helper-text {
  font-size: 12px;
  color: var(--text-secondary, #666);
  margin-top: 0;
  margin-bottom: 12px;
}

.verb-config-section {
  margin-top: 0;
  margin-bottom: 24px;
  padding: 16px;
  background: #f9f9f9;
  border-radius: 6px;
  border: 1px solid var(--border-color, #e0e0e0);
}

.verb-config-section h6 {
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary, #333);
}

.default-verb-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--border-color, #ddd);
  border-radius: 4px;
  background: #fff;
  color: #333;
  font-size: 14px;
  opacity: 1 !important;
  appearance: menulist;
  margin-top: 8px;
}

.default-verb-select:focus {
  border-color: var(--primary-color, #2196F3);
  outline: none;
}

.default-verb-select option {
  background: #fff;
  color: #333;
}

.select-helper {
  margin-top: 4px;
  margin-bottom: 0;
}

.verbs-section {
  margin-top: 24px;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #333);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary, #999);
  border: 2px dashed #e0e0e0;
  border-radius: 6px;
}

.empty-state .material-icons {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state p {
  margin: 8px 0;
  font-size: 16px;
}

.empty-hint {
  font-size: 14px !important;
  opacity: 0.7;
}

/* Master-Detail Container */
.master-detail-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Scrollable Table (fixed height) */
.verbs-table-container {
  max-height: 250px;
  overflow-y: auto;
  border: 1px solid var(--border-color, #e0e0e0);
  border-radius: 6px;
  background: #fff;
}

.verbs-table {
  width: 100%;
  border-collapse: collapse;
}

.verbs-table thead {
  position: sticky;
  top: 0;
  background: #f5f5f5;
  z-index: 1;
}

.verbs-table th {
  padding: 12px;
  text-align: left;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary, #666);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid var(--border-color, #e0e0e0);
}

.verbs-table tbody tr {
  cursor: pointer;
  transition: background-color 0.2s;
  border-bottom: 1px solid #f0f0f0;
}

.verbs-table tbody tr:hover {
  background-color: #f9f9f9;
}

.verbs-table tbody tr.selected {
  background-color: #e3f2fd;
  font-weight: 500;
}

.verbs-table td {
  padding: 10px 12px;
  font-size: 14px;
  color: var(--text-primary, #333);
}

.col-name code {
  font-family: 'Courier New', monospace;
  font-size: 13px;
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: 500;
}

.col-description {
  max-width: 300px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.col-actions {
  text-align: right;
}

.col-actions .btn-icon {
  padding: 4px;
  margin-left: 2px;
}

/* Edit Panel */
.verb-edit-panel {
  border-top: 2px solid var(--border-color, #e0e0e0);
  padding-top: 16px;
  max-height: 400px;
  overflow-y: auto;
}

.edit-panel-title {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary, #333);
}

.edit-panel-title code {
  font-family: 'Courier New', monospace;
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: 600;
  color: var(--primary-color, #2196F3);
}

.edit-panel-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.no-selection-message {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary, #999);
  border: 2px dashed #e0e0e0;
  border-radius: 6px;
}

.no-selection-message .material-icons {
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.no-selection-message p {
  margin: 0;
  font-size: 14px;
}

/* Form Controls */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.form-group label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary, #333);
}

.required {
  color: #d32f2f;
  margin-left: 2px;
}

.form-input,
.form-textarea {
  padding: 8px 10px;
  border: 1px solid var(--border-color, #ddd);
  border-radius: 4px;
  font-size: 14px;
  background: #fff;
  color: #333;
  font-family: inherit;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--primary-color, #2196F3);
}

.form-textarea {
  resize: vertical;
  min-height: 60px;
}

.help-text {
  margin: 4px 0 0 0;
  font-size: 12px;
  color: var(--text-secondary, #666);
  font-style: italic;
}

/* Parameter Selection */
.parameter-selection {
  padding: 12px;
  background: #f9f9f9;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.parameter-selection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e0e0e0;
}

.parameter-selection-label {
  font-size: 12px;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.parameter-selection-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.link-button {
  background: none;
  border: none;
  color: #2196f3;
  font-size: 12px;
  cursor: pointer;
  padding: 0;
  text-decoration: underline;
}

.link-button:hover {
  color: #1976d2;
}

.separator {
  color: #ccc;
  font-size: 12px;
}

.parameter-checkboxes {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 8px;
}

.parameter-checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.parameter-checkbox-label:hover:not(.shared) {
  background: #f5f5f5;
  border-color: #2196f3;
}

.parameter-checkbox-label.shared {
  background: #e8f5e9;
  border-color: #4caf50;
  cursor: not-allowed;
}

.parameter-checkbox-label.required-param {
  background: #fff3e0;
  border-color: #ff9800;
}

.parameter-checkbox-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.parameter-checkbox-label input[type="checkbox"]:disabled {
  cursor: not-allowed;
}

.parameter-checkbox-label span {
  font-size: 13px;
  color: #333;
  font-weight: 400;
}

.shared-icon {
  font-size: 16px !important;
  color: #4caf50;
  margin-left: auto;
}

.info-message {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 10px;
  padding: 8px 10px;
  background: #e3f2fd;
  border-left: 3px solid #2196f3;
  border-radius: 4px;
  color: #1565c0;
  font-size: 12px;
}

.info-message .material-icons {
  font-size: 18px;
}

.info-message .tiny {
  font-size: 14px !important;
  vertical-align: middle;
}

/* Buttons */
.btn {
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--primary-color, #2196F3);
  color: white;
}

.btn-primary:hover {
  background: var(--primary-color-dark, #1976D2);
}

.btn-sm {
  padding: 6px 12px;
  font-size: 13px;
}

.btn .material-icons {
  font-size: 18px;
}

.btn-sm .material-icons {
  font-size: 16px;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-icon:hover {
  background-color: var(--hover-color, #f0f0f0);
}

.btn-icon .material-icons {
  font-size: 18px;
  color: var(--text-secondary, #666);
}

.btn-icon.btn-delete:hover {
  background-color: #ffebee;
}

.btn-icon.btn-delete:hover .material-icons {
  color: #c62828;
}

.disabled-message {
  padding: 24px 16px;
  text-align: center;
}

.disabled-message code {
  background: rgba(0, 0, 0, 0.05);
  padding: 2px 6px;
  border-radius: 3px;
  font-family: monospace;
}

.checkbox-field {
  display: flex;
  align-items: center;
}

/* Fix input field visibility */
.verb-config-editor >>> input[type="text"] {
  background: #fff !important;
  color: #333 !important;
  border: 1px solid #ddd !important;
}

.verb-config-editor >>> input[type="text"]:focus {
  border-color: #2196F3 !important;
  outline: none;
}

.verb-config-editor >>> .input-field label {
  color: #666 !important;
}

.verb-config-editor >>> .input-field label.active {
  color: #2196F3 !important;
}
</style>
