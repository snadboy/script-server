<template>
  <div class="parameters-editor">
    <!-- Header with Add Button -->
    <div class="editor-header">
      <span class="header-title">Parameters ({{ parameters.length }})</span>
      <button class="btn btn-primary btn-sm" @click="addParameter">
        <i class="material-icons">add</i>
        Add Parameter
      </button>
    </div>

    <!-- Empty State -->
    <div v-if="parameters.length === 0" class="empty-state">
      <i class="material-icons">list_alt</i>
      <p>No parameters defined yet</p>
      <p class="empty-hint">Click "Add Parameter" to create your first parameter</p>
    </div>

    <!-- Master-Detail Layout -->
    <div v-else class="master-detail-container">
      <!-- Scrollable Table (Master) -->
      <div class="parameters-table-container">
        <table class="parameters-table">
          <thead>
            <tr>
              <th class="col-name">Name</th>
              <th class="col-type">Type</th>
              <th class="col-required">Required</th>
              <th class="col-default">Default</th>
              <th class="col-cli">CLI Flag</th>
              <th class="col-actions">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(param, index) in parameters"
              :key="index"
              :class="{ selected: selectedIndex === index }"
              @click="selectParameter(index)"
            >
              <td class="col-name">
                <code>{{ param.name || '(unnamed)' }}</code>
              </td>
              <td class="col-type">{{ param.type }}</td>
              <td class="col-required">{{ param.required ? 'Yes' : 'No' }}</td>
              <td class="col-default">{{ formatDefault(param) }}</td>
              <td class="col-cli">
                <code v-if="param.param">{{ param.param }}</code>
                <span v-else class="text-muted">(positional)</span>
              </td>
              <td class="col-actions">
                <button
                  v-if="index > 0"
                  class="btn-icon"
                  title="Move Up"
                  @click.stop="moveParameter(index, -1)"
                >
                  <i class="material-icons">arrow_upward</i>
                </button>
                <button
                  v-if="index < parameters.length - 1"
                  class="btn-icon"
                  title="Move Down"
                  @click.stop="moveParameter(index, 1)"
                >
                  <i class="material-icons">arrow_downward</i>
                </button>
                <button
                  class="btn-icon btn-delete"
                  title="Delete"
                  @click.stop="deleteParameter(index)"
                >
                  <i class="material-icons">delete</i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Edit Panel (Detail) -->
      <div v-if="selectedIndex !== null" class="parameter-edit-panel">
        <h6 class="edit-panel-title">
          Edit Parameter: <code>{{ selectedParameter.name || '(unnamed)' }}</code>
        </h6>

        <div class="edit-panel-content">
          <!-- Basic Fields -->
          <div class="form-row">
            <div class="form-group">
              <label>Name <span class="required">*</span></label>
              <input
                v-model="selectedParameter.name"
                class="form-input"
                placeholder="parameter_name"
                @input="emitUpdate"
              />
              <p class="help-text">Internal identifier (e.g., days, verbose)</p>
            </div>

            <div class="form-group">
              <label>Type <span class="required">*</span></label>
              <select
                v-model="selectedParameter.type"
                class="form-input"
                @change="onTypeChange(selectedParameter)"
              >
                <option value="text">Text</option>
                <option value="int">Integer</option>
                <option value="bool">Boolean</option>
                <option value="list">List</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Description</label>
            <input
              v-model="selectedParameter.description"
              class="form-input"
              placeholder="Parameter description"
              @input="emitUpdate"
            />
          </div>

          <!-- Where Used (Verb Association) -->
          <div v-if="verbs && verbs.options" class="form-group">
            <label>Where Used</label>

            <!-- Shared Parameter Toggle -->
            <label class="checkbox-label">
              <input
                type="checkbox"
                :checked="isSharedParameter(selectedParameter.name)"
                @change="toggleSharedParameter(selectedParameter.name, $event)"
              />
              <span>
                <i class="material-icons">public</i>
                Shared - Available to all verbs
              </span>
            </label>

            <!-- Individual Verb Selection (only if not shared) -->
            <div v-if="!isSharedParameter(selectedParameter.name)" class="verb-selection">
              <div class="verb-selection-header">
                <span class="verb-selection-label">Select Verbs:</span>
                <div class="verb-selection-actions">
                  <button
                    type="button"
                    class="link-button"
                    @click="selectAllVerbs(selectedParameter.name)"
                  >
                    Select All
                  </button>
                  <span class="separator">|</span>
                  <button
                    type="button"
                    class="link-button"
                    @click="deselectAllVerbs(selectedParameter.name)"
                  >
                    Deselect All
                  </button>
                </div>
              </div>

              <div class="verb-checkboxes">
                <label
                  v-for="verb in verbs.options"
                  :key="verb.name"
                  class="verb-checkbox-label"
                >
                  <input
                    type="checkbox"
                    :checked="isParameterInVerb(selectedParameter.name, verb)"
                    @change="toggleParameterInVerb(selectedParameter.name, verb, $event)"
                  />
                  <span>{{ verb.label }}</span>
                </label>
              </div>

              <p v-if="getVerbsUsingParameter(selectedParameter.name).length === 0" class="warning-message">
                <i class="material-icons">warning</i>
                This parameter is not used by any verb
              </p>
            </div>
          </div>

          <!-- CLI Flag and Required -->
          <div class="form-row">
            <div class="form-group">
              <label>CLI Flag</label>
              <input
                v-model="selectedParameter.param"
                class="form-input"
                placeholder="--flag-name or -f"
                @input="emitUpdate"
              />
              <p class="help-text">
                Command-line argument (e.g., <code>-d</code> or <code>--days</code>).
                Leave empty for positional arguments.
              </p>
            </div>

            <div class="form-group">
              <label class="checkbox-label">
                <input
                  v-model="selectedParameter.required"
                  type="checkbox"
                  @change="emitUpdate"
                />
                <span>Required</span>
              </label>
            </div>
          </div>

          <!-- Type-Specific Fields -->
          <div v-if="selectedParameter.type" class="type-specific-section">
            <h6 class="section-title">Type-Specific Settings</h6>

            <!-- Text Type -->
            <div v-if="selectedParameter.type === 'text'" class="form-row">
              <div class="form-group">
                <label>Min Length</label>
                <input
                  v-model.number="selectedParameter.min_length"
                  type="number"
                  class="form-input"
                  min="0"
                  @input="emitUpdate"
                />
              </div>
              <div class="form-group">
                <label>Max Length</label>
                <input
                  v-model.number="selectedParameter.max_length"
                  type="number"
                  class="form-input"
                  min="0"
                  @input="emitUpdate"
                />
              </div>
            </div>

            <!-- Integer Type -->
            <div v-if="selectedParameter.type === 'int'" class="form-row">
              <div class="form-group">
                <label>Min Value</label>
                <input
                  v-model.number="selectedParameter.min"
                  type="number"
                  class="form-input"
                  @input="emitUpdate"
                />
              </div>
              <div class="form-group">
                <label>Max Value</label>
                <input
                  v-model.number="selectedParameter.max"
                  type="number"
                  class="form-input"
                  @input="emitUpdate"
                />
              </div>
            </div>

            <!-- Boolean Type -->
            <div v-if="selectedParameter.type === 'bool'">
              <div class="form-group">
                <label class="checkbox-label">
                  <input
                    v-model="selectedParameter.no_value"
                    type="checkbox"
                    @change="emitUpdate"
                  />
                  <span>Flag only (no value)</span>
                </label>
                <p class="help-text">
                  If checked, parameter is passed as a flag without a value (e.g., --verbose)
                </p>
              </div>

              <div class="form-group">
                <label>Default Value</label>
                <label class="checkbox-label">
                  <input
                    v-model="selectedParameter.default"
                    type="checkbox"
                    @change="emitUpdate"
                  />
                  <span>Enabled by default</span>
                </label>
              </div>
            </div>

            <!-- List Type -->
            <div v-if="selectedParameter.type === 'list'" class="list-values-section">
              <label>List Options</label>
              <p class="help-text">
                Define the available options for this list parameter.
              </p>

              <div class="list-values-table">
                <div class="table-header">
                  <div class="col-value">Value</div>
                  <div class="col-display">Display Label</div>
                  <div class="col-actions">Actions</div>
                </div>

                <div
                  v-for="(option, optIndex) in getListValues(selectedParameter)"
                  :key="optIndex"
                  class="table-row"
                >
                  <input
                    v-model="option.value"
                    class="form-input"
                    placeholder="value"
                    @input="updateListValues()"
                  />
                  <input
                    v-model="option.label"
                    class="form-input"
                    placeholder="Display label"
                    @input="updateListValues()"
                  />
                  <button
                    class="btn-icon btn-delete"
                    title="Remove option"
                    @click="removeListValue(selectedParameter, optIndex)"
                  >
                    <i class="material-icons">close</i>
                  </button>
                </div>
              </div>

              <button class="btn btn-sm" @click="addListValue(selectedParameter)">
                <i class="material-icons">add</i>
                Add Option
              </button>
            </div>
          </div>

          <!-- Default Value (for non-bool, non-list types) -->
          <div v-if="selectedParameter.type !== 'bool' && selectedParameter.type !== 'list'" class="form-group">
            <label>Default Value</label>
            <input
              v-if="selectedParameter.type === 'int'"
              v-model.number="selectedParameter.default"
              type="number"
              class="form-input"
              @input="emitUpdate"
            />
            <input
              v-else
              v-model="selectedParameter.default"
              class="form-input"
              :placeholder="getDefaultPlaceholder(selectedParameter.type)"
              @input="emitUpdate"
            />
          </div>

          <!-- Default Value for List Type -->
          <div v-if="selectedParameter.type === 'list' && getListValues(selectedParameter).length > 0" class="form-group">
            <label>Default Selection</label>
            <select v-model="selectedParameter.default" class="form-input" @change="emitUpdate">
              <option :value="null">-- None --</option>
              <option
                v-for="option in getListValues(selectedParameter)"
                :key="option.value"
                :value="option.value"
              >
                {{ option.label || option.value }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <!-- No Selection Message -->
      <div v-else class="no-selection-message">
        <i class="material-icons">arrow_upward</i>
        <p>Select a parameter from the table above to edit its details</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProjectParametersEditor',

  props: {
    modelValue: {
      type: Array,
      default: () => []
    },
    verbs: {
      type: Object,
      default: null
    },
    sharedParameters: {
      type: Array,
      default: () => []
    }
  },

  emits: ['update:modelValue', 'update:verbs', 'update:sharedParameters'],

  data() {
    return {
      selectedIndex: null
    };
  },

  computed: {
    parameters: {
      get() {
        return this.modelValue;
      },
      set(value) {
        this.$emit('update:modelValue', value);
      }
    },

    selectedParameter() {
      return this.selectedIndex !== null ? this.parameters[this.selectedIndex] : null;
    }
  },

  methods: {
    selectParameter(index) {
      this.selectedIndex = index;
    },

    addParameter() {
      const newParam = {
        name: '',
        type: 'text',
        description: '',
        required: false,
        param: '',
        default: null
      };
      this.parameters.push(newParam);
      this.selectedIndex = this.parameters.length - 1; // Auto-select new parameter
      this.emitUpdate();
    },

    deleteParameter(index) {
      if (confirm('Are you sure you want to delete this parameter?')) {
        this.parameters.splice(index, 1);
        // Clear selection if we deleted the selected parameter
        if (this.selectedIndex === index) {
          this.selectedIndex = null;
        } else if (this.selectedIndex > index) {
          // Adjust selection index if necessary
          this.selectedIndex--;
        }
        this.emitUpdate();
      }
    },

    moveParameter(index, direction) {
      const newIndex = index + direction;
      if (newIndex >= 0 && newIndex < this.parameters.length) {
        const params = [...this.parameters];
        [params[index], params[newIndex]] = [params[newIndex], params[index]];
        this.parameters = params;
        // Update selection to follow the moved parameter
        if (this.selectedIndex === index) {
          this.selectedIndex = newIndex;
        } else if (this.selectedIndex === newIndex) {
          this.selectedIndex = index;
        }
        this.emitUpdate();
      }
    },

    formatDefault(param) {
      if (param.default === null || param.default === undefined) {
        return '-';
      }
      if (param.type === 'bool') {
        return param.default ? 'true' : 'false';
      }
      return String(param.default);
    },

    emitUpdate() {
      this.$emit('update:modelValue', this.parameters);
    },

    getDefaultPlaceholder(type) {
      switch (type) {
        case 'text':
          return 'Default text value';
        case 'int':
          return 'Default number';
        case 'list':
          return 'Default selection';
        default:
          return 'Default value';
      }
    },

    onTypeChange(param) {
      // Initialize type-specific fields when type changes
      if (param.type === 'list' && !param.values) {
        param.values = [];
        // Add one empty option to start
        this.addListValue(param);
      }
      this.emitUpdate();
    },

    getListValues(param) {
      if (!param.values) {
        param.values = [];
      }
      return param.values;
    },

    addListValue(param) {
      if (!param.values) {
        param.values = [];
      }
      param.values.push({ value: '', label: '' });
      this.emitUpdate();
    },

    removeListValue(param, optionIndex) {
      if (param.values && param.values.length > optionIndex) {
        param.values.splice(optionIndex, 1);
        this.emitUpdate();
      }
    },

    updateListValues() {
      // Just emit update when list values change
      this.emitUpdate();
    },

    isSharedParameter(paramName) {
      return this.sharedParameters && this.sharedParameters.includes(paramName);
    },

    getVerbsUsingParameter(paramName) {
      if (!this.verbs || !this.verbs.options) {
        return [];
      }

      return this.verbs.options.filter(verb => {
        return verb.parameters && verb.parameters.includes(paramName);
      });
    },

    toggleSharedParameter(paramName, event) {
      const isChecked = event.target.checked;
      const updatedShared = [...(this.sharedParameters || [])];

      if (isChecked) {
        // Add to shared parameters
        if (!updatedShared.includes(paramName)) {
          updatedShared.push(paramName);
        }
        // Remove from all individual verbs
        if (this.verbs && this.verbs.options) {
          this.verbs.options.forEach(verb => {
            if (verb.parameters && verb.parameters.includes(paramName)) {
              verb.parameters = verb.parameters.filter(p => p !== paramName);
            }
          });
          this.$emit('update:verbs', this.verbs);
        }
      } else {
        // Remove from shared parameters
        const index = updatedShared.indexOf(paramName);
        if (index > -1) {
          updatedShared.splice(index, 1);
        }
      }

      this.$emit('update:sharedParameters', updatedShared);
    },

    isParameterInVerb(paramName, verb) {
      return verb.parameters && verb.parameters.includes(paramName);
    },

    toggleParameterInVerb(paramName, verb, event) {
      const isChecked = event.target.checked;

      if (!verb.parameters) {
        verb.parameters = [];
      }

      if (isChecked) {
        // Add parameter to verb
        if (!verb.parameters.includes(paramName)) {
          verb.parameters.push(paramName);
        }
      } else {
        // Remove parameter from verb
        verb.parameters = verb.parameters.filter(p => p !== paramName);
      }

      this.$emit('update:verbs', this.verbs);
    },

    selectAllVerbs(paramName) {
      if (!this.verbs || !this.verbs.options) return;

      this.verbs.options.forEach(verb => {
        if (!verb.parameters) {
          verb.parameters = [];
        }
        if (!verb.parameters.includes(paramName)) {
          verb.parameters.push(paramName);
        }
      });

      this.$emit('update:verbs', this.verbs);
    },

    deselectAllVerbs(paramName) {
      if (!this.verbs || !this.verbs.options) return;

      this.verbs.options.forEach(verb => {
        if (verb.parameters) {
          verb.parameters = verb.parameters.filter(p => p !== paramName);
        }
      });

      this.$emit('update:verbs', this.verbs);
    }
  }
};
</script>

<style scoped>
.parameters-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
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
  flex: 1;
  min-height: 0;
}

/* Scrollable Table (fixed height) */
.parameters-table-container {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid var(--border-color, #e0e0e0);
  border-radius: 6px;
  background: #fff;
}

.parameters-table {
  width: 100%;
  border-collapse: collapse;
}

.parameters-table thead {
  position: sticky;
  top: 0;
  background: #f5f5f5;
  z-index: 1;
}

.parameters-table th {
  padding: 12px;
  text-align: left;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary, #666);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid var(--border-color, #e0e0e0);
}

.parameters-table tbody tr {
  cursor: pointer;
  transition: background-color 0.2s;
  border-bottom: 1px solid #f0f0f0;
}

.parameters-table tbody tr:hover {
  background-color: #f9f9f9;
}

.parameters-table tbody tr.selected {
  background-color: #e3f2fd;
  font-weight: 500;
}

.parameters-table td {
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

.col-cli code {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  background: #e0f7fa;
  padding: 2px 6px;
  border-radius: 3px;
}

.text-muted {
  color: var(--text-secondary, #999);
  font-style: italic;
  font-size: 12px;
}

.col-actions {
  text-align: right;
}

.col-actions .btn-icon {
  padding: 4px;
  margin-left: 2px;
}

/* Edit Panel (scrollable if needed) */
.parameter-edit-panel {
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

.form-input {
  padding: 8px 10px;
  border: 1px solid var(--border-color, #ddd);
  border-radius: 4px;
  font-size: 14px;
  background: #fff;
  color: #333;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-color, #2196F3);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 0;
}

.checkbox-label span {
  color: #333 !important;
  font-weight: 500;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.checkbox-label .material-icons {
  font-size: 18px;
  vertical-align: middle;
  margin-right: 4px;
}

.help-text {
  margin: 4px 0 0 0;
  font-size: 12px;
  color: var(--text-secondary, #666);
  font-style: italic;
}

.help-text code {
  background: #e0e0e0;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 11px;
  color: #d32f2f;
}

/* Type-Specific Section */
.type-specific-section {
  padding: 16px;
  background: #f5f5f5;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.section-title {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary, #333);
}

/* List Values Table */
.list-values-section {
  padding: 16px;
  background: #fafafa;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.list-values-section label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary, #333);
  margin-bottom: 4px;
  display: block;
}

.list-values-table {
  margin: 12px 0;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  background: #fff;
}

.table-header {
  display: grid;
  grid-template-columns: 1fr 1fr 80px;
  gap: 8px;
  background: #f5f5f5;
  padding: 10px 12px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary, #666);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid #e0e0e0;
}

.table-row {
  display: grid;
  grid-template-columns: 1fr 1fr 80px;
  gap: 8px;
  padding: 8px 12px;
  align-items: center;
  border-bottom: 1px solid #f0f0f0;
}

.table-row:last-child {
  border-bottom: none;
}

.table-row:hover {
  background: #fafafa;
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

/* Verb Selection */
.verb-selection {
  margin-top: 12px;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.verb-selection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e0e0e0;
}

.verb-selection-label {
  font-size: 12px;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.verb-selection-actions {
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

.verb-checkboxes {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 8px;
}

.verb-checkbox-label {
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

.verb-checkbox-label:hover {
  background: #f5f5f5;
  border-color: #2196f3;
}

.verb-checkbox-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.verb-checkbox-label span {
  font-size: 13px;
  color: #333;
  font-weight: 400;
}

.warning-message {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 10px;
  padding: 8px 10px;
  background: #fff3e0;
  border-left: 3px solid #ff9800;
  border-radius: 4px;
  color: #e65100;
  font-size: 12px;
  font-style: italic;
}

.warning-message .material-icons {
  font-size: 18px;
}
</style>
