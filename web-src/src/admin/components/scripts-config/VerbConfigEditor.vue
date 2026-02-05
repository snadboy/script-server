<template>
  <div class="verb-config-editor">
    <!-- Enable Checkbox -->
    <div class="enable-section">
      <label class="enable-label">
        <input
          v-model="verbsEnabled"
          type="checkbox"
          class="enable-checkbox"
        />
        <span>Enable Verb/Subcommand Support</span>
      </label>
      <p class="enable-help">
        Allow this script to have multiple subcommands like git or docker
      </p>
    </div>

    <template v-if="verbsEnabled">
      <!-- Verbs Table Section -->
      <div class="verbs-section">
        <div class="section-header">
          <span class="section-title">Verb Options ({{ verbOptions.length }})</span>
          <button class="btn-add" @click="addVerb">
            <i class="material-icons">add</i>
            ADD VERB
          </button>
        </div>

        <!-- Empty State -->
        <div v-if="verbOptions.length === 0" class="empty-state">
          <i class="material-icons">category</i>
          <p>No verbs defined yet</p>
          <p class="empty-hint">Click "Add Verb" to create your first verb</p>
        </div>

        <!-- Verbs Table -->
        <div v-else class="table-container">
          <table class="verbs-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Label</th>
                <th>Description</th>
                <th>Parameters</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(verb, index) in verbOptions"
                :key="index"
                :class="{ selected: selectedIndex === index }"
                @click="selectVerb(index)"
              >
                <td><code>{{ verb.name || '(unnamed)' }}</code></td>
                <td>{{ verb.label || '-' }}</td>
                <td>{{ truncate(verb.description, 50) }}</td>
                <td>{{ verb.parameters?.length || 0 }}</td>
                <td class="actions-cell">
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
      </div>

      <!-- Global Verb Settings (Always Visible) -->
      <div class="global-section">
        <div class="section-header clickable" @click="toggleGlobal">
          <div class="header-left">
            <i class="material-icons">settings</i>
            <span class="section-title">Global Verb Settings</span>
          </div>
          <button class="btn-icon" @click.stop="toggleGlobal">
            <i class="material-icons">
              {{ globalExpanded ? 'expand_less' : 'expand_more' }}
            </i>
          </button>
        </div>

        <div v-show="globalExpanded" class="section-content">
          <p class="help-text">
            These settings control how the verb parameter is passed to your script.
          </p>

          <div class="form-grid">
            <div class="form-field">
              <label>Parameter Name <span class="required">*</span></label>
              <input
                v-model="config.parameter_name"
                class="form-input"
                placeholder="verb"
                @input="emitUpdate"
              />
              <span class="field-hint">Internal name for the verb parameter</span>
            </div>

            <div class="form-field">
              <label class="checkbox-label">
                <input
                  v-model="config.required"
                  type="checkbox"
                  @change="emitUpdate"
                />
                <span>Verb Required</span>
              </label>
              <span class="field-hint">User must select a verb</span>
            </div>
          </div>

          <div class="form-grid">
            <div class="form-field">
              <label>Default Verb</label>
              <select
                v-model="config.default"
                class="form-input"
                @change="emitUpdate"
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
              <span class="field-hint">Pre-selected verb</span>
            </div>

            <div class="form-field">
              <label>Pass As</label>
              <select
                v-model="verbPassMode"
                class="form-input"
                @change="emitUpdate"
              >
                <option
                  v-for="mode in passAsModes"
                  :key="mode.value"
                  :value="mode.value"
                >
                  {{ mode.label }}
                </option>
              </select>
              <span class="field-hint">CLI format</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Verb Configuration (Only When Selected) -->
      <div v-if="selectedIndex !== null" class="detail-section">
        <div class="section-header">
          <span class="section-title">Verb Configuration</span>
        </div>

        <div class="section-content">
          <div class="form-field">
            <label>Verb Name <span class="required">*</span></label>
            <input
              v-model="selectedVerb.name"
              class="form-input"
              placeholder="run, create, delete..."
              @input="emitUpdate"
            />
            <span class="field-hint">CLI value (e.g., "create", "delete")</span>
          </div>

          <div class="form-field">
            <label>Display Label</label>
            <input
              v-model="selectedVerb.label"
              class="form-input"
              placeholder="Create Item"
              @input="emitUpdate"
            />
            <span class="field-hint">Display text shown in UI</span>
          </div>

          <div class="form-field">
            <label>Description</label>
            <textarea
              v-model="selectedVerb.description"
              class="form-textarea"
              rows="3"
              placeholder="Help text shown when verb is selected"
              @input="emitUpdate"
            ></textarea>
          </div>

          <!-- Available Parameters -->
          <div v-if="availableParameters.length > 0" class="form-field">
            <label>Available Parameters</label>
            <span class="field-hint">
              Select which parameters are visible when this verb is selected
            </span>

            <div class="param-actions">
              <button class="link-btn" @click="selectAllParams">Select All</button>
              <span class="separator">|</span>
              <button class="link-btn" @click="deselectAllParams">Deselect All</button>
            </div>

            <div class="param-grid">
              <label
                v-for="param in availableParameters"
                :key="param.name"
                class="param-label"
                :class="{ shared: isShared(param.name) }"
              >
                <input
                  type="checkbox"
                  :checked="isSelected(param.name)"
                  :disabled="isShared(param.name)"
                  @change="toggleParam(param.name, $event)"
                />
                <span>{{ param.name }}</span>
                <i
                  v-if="isShared(param.name)"
                  class="material-icons shared-icon"
                  title="Shared parameter"
                >
                  public
                </i>
              </label>
            </div>

            <p class="info-note">
              <i class="material-icons">info</i>
              Shared parameters (marked with
              <i class="material-icons tiny">public</i>) are automatically
              available to all verbs
            </p>
          </div>

          <!-- Required Parameters -->
          <div v-if="selectedVerbParams.length > 0" class="form-field">
            <label>Required Parameters</label>
            <span class="field-hint">
              Which parameters must have a value for this verb
            </span>

            <div class="param-grid">
              <label
                v-for="param in selectedVerbParams"
                :key="param"
                class="param-label required"
              >
                <input
                  type="checkbox"
                  :checked="isRequired(param)"
                  @change="toggleRequired(param, $event)"
                />
                <span>{{ param }}</span>
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- No Selection Message -->
      <div v-else class="no-selection">
        <i class="material-icons">arrow_upward</i>
        <p>Select a verb from the table above to configure its details</p>
      </div>
    </template>

    <!-- Disabled Message -->
    <div v-else class="disabled-message">
      <p>
        Enable verb/subcommand support to configure CLI-style commands
        (e.g., <code>git clone</code>, <code>docker run</code>)
      </p>
    </div>
  </div>
</template>

<script>
import '@/common/materializecss/imports/toast';

export default {
  name: 'VerbConfigEditor',

  props: {
    value: { type: Object, default: null },
    availableParameters: { type: Array, default: () => [] },
    sharedParameters: { type: Array, default: () => [] }
  },

  data() {
    return {
      config: this.initConfig(),
      selectedIndex: null,
      globalExpanded: true
    };
  },

  computed: {
    verbsEnabled: {
      get() { return this.config !== null; },
      set(enabled) {
        this.config = enabled ? this.createDefault() : null;
        this.$emit('input', this.config);
      }
    },

    verbOptions() {
      return this.config?.options || [];
    },

    selectedVerb() {
      return this.selectedIndex !== null
        ? this.verbOptions[this.selectedIndex]
        : null;
    },

    selectedVerbParams() {
      return this.selectedVerb?.parameters || [];
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
            this.$set(this.config, 'verb_position', 'after_verb');
            this.$set(this.config, 'param', '');
            this.$set(this.config, 'no_value', false);
            break;
          case 'keyvalue':
            const paramName = this.config.parameter_name || 'verb';
            this.$set(this.config, 'param', `--${paramName}=`);
            this.$set(this.config, 'verb_position', undefined);
            this.$set(this.config, 'no_value', false);
            break;
          case 'flag':
          default:
            const flagName = this.config.parameter_name || 'verb';
            this.$set(this.config, 'param', `--${flagName}`);
            this.$set(this.config, 'verb_position', undefined);
            this.$set(this.config, 'no_value', false);
            break;
        }
      }
    },

    passAsModes() {
      const paramName = this.config?.parameter_name || 'verb';
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
    }
  },

  methods: {
    initConfig() {
      if (this.value) {
        if (!this.value.options) {
          this.$set(this.value, 'options', []);
        }
        return this.value;
      }
      return null;
    },

    createDefault() {
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

    emitUpdate() {
      this.$emit('input', this.config);
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
      this.selectedIndex = this.config.options.length - 1;
      this.emitUpdate();
    },

    deleteVerb(index) {
      if (!confirm('Are you sure you want to delete this verb?')) return;

      const verb = this.config.options[index];
      this.config.options.splice(index, 1);

      if (this.selectedIndex === index) {
        this.selectedIndex = null;
      } else if (this.selectedIndex > index) {
        this.selectedIndex--;
      }

      // Clear default if we deleted the default verb
      if (this.config.default === verb.name) {
        this.config.default = '';
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

      if (this.selectedIndex === index) {
        this.selectedIndex = index + 1;
      } else if (this.selectedIndex === index + 1) {
        this.selectedIndex = index;
      }

      this.emitUpdate();
    },

    toggleGlobal() {
      this.globalExpanded = !this.globalExpanded;
      localStorage.setItem('verbGlobalExpanded', String(this.globalExpanded));
    },

    isShared(name) {
      return this.sharedParameters && this.sharedParameters.includes(name);
    },

    isSelected(name) {
      return this.selectedVerbParams.includes(name);
    },

    isRequired(name) {
      return this.selectedVerb?.required_parameters?.includes(name);
    },

    toggleParam(name, event) {
      if (!this.selectedVerb) return;

      const isChecked = event.target.checked;

      if (!this.selectedVerb.parameters) {
        this.$set(this.selectedVerb, 'parameters', []);
      }

      if (isChecked) {
        if (!this.selectedVerb.parameters.includes(name)) {
          this.selectedVerb.parameters.push(name);
        }
      } else {
        this.selectedVerb.parameters = this.selectedVerb.parameters.filter(p => p !== name);
        if (this.selectedVerb.required_parameters) {
          this.selectedVerb.required_parameters = this.selectedVerb.required_parameters.filter(p => p !== name);
        }
      }

      this.emitUpdate();
    },

    toggleRequired(name, event) {
      if (!this.selectedVerb) return;

      const isChecked = event.target.checked;

      if (!this.selectedVerb.required_parameters) {
        this.$set(this.selectedVerb, 'required_parameters', []);
      }

      if (isChecked) {
        if (!this.selectedVerb.required_parameters.includes(name)) {
          this.selectedVerb.required_parameters.push(name);
        }
      } else {
        this.selectedVerb.required_parameters = this.selectedVerb.required_parameters.filter(p => p !== name);
      }

      this.emitUpdate();
    },

    selectAllParams() {
      if (!this.selectedVerb) return;

      if (!this.selectedVerb.parameters) {
        this.$set(this.selectedVerb, 'parameters', []);
      }

      this.availableParameters.forEach(param => {
        if (!this.isShared(param.name) && !this.selectedVerb.parameters.includes(param.name)) {
          this.selectedVerb.parameters.push(param.name);
        }
      });

      this.emitUpdate();
    },

    deselectAllParams() {
      if (!this.selectedVerb) return;

      this.$set(this.selectedVerb, 'parameters', []);
      this.$set(this.selectedVerb, 'required_parameters', []);

      this.emitUpdate();
    },

    truncate(text, length) {
      return text?.length > length ? text.substring(0, length - 3) + '...' : text || '-';
    }
  },

  mounted() {
    const saved = localStorage.getItem('verbGlobalExpanded');
    if (saved !== null) {
      this.globalExpanded = saved === 'true';
    }
  },

  watch: {
    value: {
      immediate: true,
      handler() {
        this.config = this.initConfig();
      }
    }
  }
};
</script>

<style scoped>
.verb-config-editor {
  padding: 0;
  color: var(--dialog-text);
}

/* Enable Section */
.enable-section {
  margin-bottom: 24px;
  padding: 16px;
  background: var(--dialog-content-bg);
  border: 1px solid var(--dialog-border);
  border-radius: 4px;
}

.enable-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.enable-checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.enable-help {
  margin: 8px 0 0 26px;
  font-size: 12px;
  color: var(--dialog-text-dim);
}

/* Section Headers */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--dialog-header-bg);
  border: 1px solid var(--dialog-border);
  border-radius: 4px 4px 0 0;
  margin-bottom: -1px;
}

.section-header.clickable {
  cursor: pointer;
  user-select: none;
}

.section-header.clickable:hover {
  background: color-mix(in srgb, var(--dialog-header-bg) 90%, var(--dialog-primary));
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--dialog-text);
}

.section-content {
  padding: 16px;
  background: var(--dialog-content-bg);
  border: 1px solid var(--dialog-border);
  border-top: none;
  border-radius: 0 0 4px 4px;
}

/* Verbs Section */
.verbs-section {
  margin-bottom: 16px;
}

/* Verbs Table */
.table-container {
  max-height: 250px;
  overflow-y: auto;
  border: 1px solid var(--dialog-border);
  border-radius: 0 0 4px 4px;
  background: var(--dialog-content-bg);
}

.verbs-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.verbs-table thead {
  position: sticky;
  top: 0;
  background: var(--dialog-header-bg);
  z-index: 1;
}

.verbs-table th {
  padding: 10px 12px;
  text-align: left;
  font-weight: 600;
  color: var(--dialog-text);
  border-bottom: 1px solid var(--dialog-border);
}

.verbs-table tbody tr {
  cursor: pointer;
  transition: background-color 0.15s;
  border-bottom: 1px solid var(--dialog-border);
}

.verbs-table tbody tr:hover {
  background: var(--dialog-header-bg);
}

.verbs-table tbody tr.selected {
  background: var(--dialog-selected);
}

.verbs-table td {
  padding: 10px 12px;
  color: var(--dialog-text);
}

.verbs-table code {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  background: var(--dialog-input-bg);
  padding: 2px 6px;
  border-radius: 3px;
  color: var(--dialog-primary);
}

.actions-cell {
  text-align: right;
  white-space: nowrap;
}

/* Global Section - Always Visible */
.global-section {
  margin-bottom: 16px;
}

/* Detail Section - Only When Verb Selected */
.detail-section {
  margin-bottom: 16px;
  max-height: 400px;
  overflow-y: auto;
}

/* Form Elements */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 16px;
}

.form-field label {
  font-size: 13px;
  font-weight: 500;
  color: var(--dialog-text);
}

.required {
  color: #ff8a80;
}

.form-input,
.form-textarea {
  padding: 8px 12px;
  border: 1px solid var(--dialog-input-border);
  border-radius: 4px;
  background: var(--dialog-input-bg);
  color: var(--dialog-text);
  font-size: 13px;
  font-family: inherit;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--dialog-primary);
}

.form-textarea {
  resize: vertical;
  min-height: 60px;
}

.field-hint {
  font-size: 12px;
  color: var(--dialog-text-dim);
  font-style: italic;
}

.help-text {
  padding: 10px 12px;
  background: color-mix(in srgb, var(--dialog-primary) 10%, transparent);
  border-left: 3px solid var(--dialog-primary);
  border-radius: 4px;
  font-size: 13px;
  color: var(--dialog-text);
  margin-bottom: 16px;
}

/* Checkbox Labels */
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

/* Parameter Grid */
.param-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.link-btn {
  background: none;
  border: none;
  color: var(--dialog-primary);
  font-size: 12px;
  cursor: pointer;
  text-decoration: underline;
  padding: 0;
}

.link-btn:hover {
  color: color-mix(in srgb, var(--dialog-primary) 80%, white);
}

.separator {
  color: var(--dialog-text-dim);
}

.param-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin-bottom: 12px;
}

.param-label {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  background: var(--dialog-input-bg);
  border: 1px solid var(--dialog-input-border);
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.param-label:hover:not(.shared) {
  border-color: var(--dialog-primary);
  background: color-mix(in srgb, var(--dialog-primary) 5%, var(--dialog-input-bg));
}

.param-label.shared {
  background: color-mix(in srgb, green 10%, var(--dialog-input-bg));
  border-color: color-mix(in srgb, green 30%, var(--dialog-input-border));
  cursor: not-allowed;
}

.param-label.required {
  background: color-mix(in srgb, orange 10%, var(--dialog-input-bg));
  border-color: color-mix(in srgb, orange 30%, var(--dialog-input-border));
}

.shared-icon {
  font-size: 16px !important;
  color: #4caf50;
  margin-left: auto;
}

.info-note {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  background: color-mix(in srgb, var(--dialog-primary) 10%, transparent);
  border-left: 3px solid var(--dialog-primary);
  border-radius: 4px;
  font-size: 12px;
  color: var(--dialog-text);
}

.info-note .material-icons {
  font-size: 18px;
}

.info-note .tiny {
  font-size: 14px !important;
  vertical-align: middle;
}

/* Buttons */
.btn-add {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: var(--dialog-primary);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-add:hover {
  background: color-mix(in srgb, var(--dialog-primary) 80%, white);
}

.btn-add .material-icons {
  font-size: 18px;
}

.btn-icon {
  background: none;
  border: none;
  padding: 4px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-icon:hover {
  background: var(--dialog-header-bg);
}

.btn-icon .material-icons {
  font-size: 18px;
  color: var(--dialog-text-dim);
}

.btn-icon.btn-delete:hover {
  background: color-mix(in srgb, red 20%, transparent);
}

.btn-icon.btn-delete:hover .material-icons {
  color: #ff5252;
}

/* Empty State */
.empty-state {
  padding: 60px 20px;
  text-align: center;
  color: var(--dialog-text-dim);
  background: var(--dialog-content-bg);
  border: 2px dashed var(--dialog-border);
  border-radius: 4px;
}

.empty-state .material-icons {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state p {
  margin: 8px 0;
  font-size: 14px;
}

.empty-hint {
  font-size: 12px !important;
  opacity: 0.7;
}

/* No Selection Message */
.no-selection {
  padding: 40px 20px;
  text-align: center;
  color: var(--dialog-text-dim);
  background: var(--dialog-content-bg);
  border: 2px dashed var(--dialog-border);
  border-radius: 4px;
}

.no-selection .material-icons {
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.no-selection p {
  margin: 0;
  font-size: 14px;
}

/* Disabled Message */
.disabled-message {
  padding: 24px;
  text-align: center;
  color: var(--dialog-text-dim);
  background: var(--dialog-content-bg);
  border: 1px solid var(--dialog-border);
  border-radius: 4px;
}

.disabled-message code {
  background: var(--dialog-input-bg);
  padding: 2px 6px;
  border-radius: 3px;
  font-family: monospace;
}
</style>
