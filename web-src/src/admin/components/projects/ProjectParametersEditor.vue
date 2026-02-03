<template>
  <div class="parameters-editor">
    <div class="editor-header">
      <div class="header-title">
        <h6>Parameter Definitions</h6>
        <p class="header-subtitle">
          Define parameters once at the project level. Script instances can then select which
          parameters to include and override default values.
        </p>
      </div>
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

    <!-- Parameters List -->
    <div v-else class="parameters-list">
      <div
        v-for="(param, index) in parameters"
        :key="index"
        class="parameter-card"
      >
        <div class="parameter-header">
          <div class="parameter-title">
            <div class="field-with-label">
              <label class="inline-label">Name</label>
              <input
                v-model="param.name"
                class="parameter-name-input"
                placeholder="parameter_name"
                @input="emitUpdate"
              />
              <span class="field-hint">Internal identifier (e.g., days, verbose)</span>
            </div>
            <div class="field-with-label">
              <label class="inline-label">Type</label>
              <select v-model="param.type" class="parameter-type-select" @change="onTypeChange(param, index)">
                <option value="text">Text</option>
                <option value="int">Integer</option>
                <option value="bool">Boolean</option>
                <option value="list">List</option>
              </select>
            </div>
          </div>
          <div class="parameter-actions">
            <button
              v-if="index > 0"
              class="btn-icon"
              title="Move Up"
              @click="moveParameter(index, -1)"
            >
              <i class="material-icons">arrow_upward</i>
            </button>
            <button
              v-if="index < parameters.length - 1"
              class="btn-icon"
              title="Move Down"
              @click="moveParameter(index, 1)"
            >
              <i class="material-icons">arrow_downward</i>
            </button>
            <button
              class="btn-icon btn-delete"
              title="Delete"
              @click="deleteParameter(index)"
            >
              <i class="material-icons">delete</i>
            </button>
          </div>
        </div>

        <div class="parameter-body">
          <!-- Description -->
          <div class="form-group">
            <label>Description</label>
            <input
              v-model="param.description"
              class="form-input"
              placeholder="Parameter description"
              @input="emitUpdate"
            />
          </div>

          <!-- CLI Flag -->
          <div class="form-row">
            <div class="form-group">
              <label>CLI Flag</label>
              <input
                v-model="param.param"
                class="form-input"
                placeholder="--flag-name or -f"
                @input="emitUpdate"
              />
              <p class="help-text">
                Command-line argument (e.g., <code>-d</code> or <code>--days</code>).
                Leave empty for positional arguments.
              </p>
            </div>

            <!-- Required Checkbox -->
            <div class="form-group">
              <label class="checkbox-label">
                <input
                  v-model="param.required"
                  type="checkbox"
                  @change="emitUpdate"
                />
                <span>Required</span>
              </label>
            </div>
          </div>

          <!-- Type-Specific Fields -->
          <div class="type-specific-fields">
            <!-- Text Type -->
            <div v-if="param.type === 'text'" class="form-row">
              <div class="form-group">
                <label>Min Length</label>
                <input
                  v-model.number="param.min_length"
                  type="number"
                  class="form-input"
                  min="0"
                  @input="emitUpdate"
                />
              </div>
              <div class="form-group">
                <label>Max Length</label>
                <input
                  v-model.number="param.max_length"
                  type="number"
                  class="form-input"
                  min="0"
                  @input="emitUpdate"
                />
              </div>
            </div>

            <!-- Integer Type -->
            <div v-if="param.type === 'int'" class="form-row">
              <div class="form-group">
                <label>Min Value</label>
                <input
                  v-model.number="param.min"
                  type="number"
                  class="form-input"
                  @input="emitUpdate"
                />
              </div>
              <div class="form-group">
                <label>Max Value</label>
                <input
                  v-model.number="param.max"
                  type="number"
                  class="form-input"
                  @input="emitUpdate"
                />
              </div>
            </div>

            <!-- Boolean Type -->
            <div v-if="param.type === 'bool'">
              <div class="form-group">
                <label class="checkbox-label">
                  <input
                    v-model="param.no_value"
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
                    v-model="param.default"
                    type="checkbox"
                    @change="emitUpdate"
                  />
                  <span>Enabled by default</span>
                </label>
              </div>
            </div>

            <!-- List Type -->
            <div v-if="param.type === 'list'" class="list-values-section">
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
                  v-for="(option, optIndex) in getListValues(param)"
                  :key="optIndex"
                  class="table-row"
                >
                  <input
                    v-model="option.value"
                    class="form-input"
                    placeholder="value"
                    @input="updateListValues(param, index)"
                  />
                  <input
                    v-model="option.label"
                    class="form-input"
                    placeholder="Display label"
                    @input="updateListValues(param, index)"
                  />
                  <button
                    class="btn-icon btn-delete"
                    title="Remove option"
                    @click="removeListValue(param, optIndex, index)"
                  >
                    <i class="material-icons">close</i>
                  </button>
                </div>
              </div>

              <button class="btn btn-sm" @click="addListValue(param, index)">
                <i class="material-icons">add</i>
                Add Option
              </button>
            </div>
          </div>

          <!-- Default Value (for non-bool, non-list types) -->
          <div v-if="param.type !== 'bool' && param.type !== 'list'" class="form-group">
            <label>Default Value</label>
            <input
              v-if="param.type === 'int'"
              v-model.number="param.default"
              type="number"
              class="form-input"
              @input="emitUpdate"
            />
            <input
              v-else
              v-model="param.default"
              class="form-input"
              :placeholder="getDefaultPlaceholder(param.type)"
              @input="emitUpdate"
            />
          </div>

          <!-- Default Value for List Type -->
          <div v-if="param.type === 'list' && getListValues(param).length > 0" class="form-group">
            <label>Default Selection</label>
            <select v-model="param.default" class="form-input" @change="emitUpdate">
              <option :value="null">-- None --</option>
              <option
                v-for="option in getListValues(param)"
                :key="option.value"
                :value="option.value"
              >
                {{ option.label || option.value }}
              </option>
            </select>
          </div>
        </div>
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
    }
  },

  emits: ['update:modelValue'],

  computed: {
    parameters: {
      get() {
        return this.modelValue;
      },
      set(value) {
        this.$emit('update:modelValue', value);
      }
    }
  },

  methods: {
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
      this.emitUpdate();
    },

    deleteParameter(index) {
      if (confirm('Are you sure you want to delete this parameter?')) {
        this.parameters.splice(index, 1);
        this.emitUpdate();
      }
    },

    moveParameter(index, direction) {
      const newIndex = index + direction;
      if (newIndex >= 0 && newIndex < this.parameters.length) {
        const params = [...this.parameters];
        [params[index], params[newIndex]] = [params[newIndex], params[index]];
        this.parameters = params;
        this.emitUpdate();
      }
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

    onTypeChange(param, index) {
      // Initialize type-specific fields when type changes
      if (param.type === 'list' && !param.values) {
        param.values = [];
        // Add one empty option to start
        this.addListValue(param, index);
      }
      this.emitUpdate();
    },

    getListValues(param) {
      if (!param.values) {
        param.values = [];
      }
      return param.values;
    },

    addListValue(param, paramIndex) {
      if (!param.values) {
        param.values = [];
      }
      param.values.push({ value: '', label: '' });
      this.emitUpdate();
    },

    removeListValue(param, optionIndex, paramIndex) {
      if (param.values && param.values.length > optionIndex) {
        param.values.splice(optionIndex, 1);
        this.emitUpdate();
      }
    },

    updateListValues(param, paramIndex) {
      // Just emit update when list values change
      this.emitUpdate();
    }
  }
};
</script>

<style scoped>
.parameters-editor {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.header-title h6 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary, #333);
}

.header-subtitle {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary, #666);
  line-height: 1.4;
  max-width: 600px;
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

.parameters-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.parameter-card {
  border: 1px solid var(--border-color, #e0e0e0);
  border-radius: 6px;
  overflow: hidden;
  background: #fff;
  transition: box-shadow 0.2s;
}

.parameter-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.parameter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f9f9f9;
  border-bottom: 1px solid var(--border-color, #e0e0e0);
}

.parameter-title {
  display: flex;
  gap: 12px;
  align-items: center;
  flex: 1;
}

.parameter-name-input {
  font-family: 'Courier New', monospace;
  font-size: 16px;
  font-weight: 500;
  padding: 6px 10px;
  border: 1px solid var(--border-color, #ddd);
  border-radius: 4px;
  min-width: 200px;
  background: #fff;
  color: #333;
}

.parameter-name-input:focus {
  outline: none;
  border-color: var(--primary-color, #2196F3);
}

.parameter-type-select {
  padding: 6px 10px;
  border: 1px solid var(--border-color, #ddd);
  border-radius: 4px;
  background: #fff;
  color: #333;
  font-size: 14px;
  cursor: pointer;
  opacity: 1 !important;
  appearance: menulist;
}

.parameter-actions {
  display: flex;
  gap: 4px;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon:hover {
  background-color: var(--hover-color, #f0f0f0);
}

.btn-icon .material-icons {
  font-size: 20px;
  color: var(--text-secondary, #666);
}

.btn-icon.btn-delete:hover {
  background-color: #ffebee;
}

.btn-icon.btn-delete:hover .material-icons {
  color: #c62828;
}

.parameter-body {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

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

.form-input,
.form-select {
  padding: 8px 10px;
  border: 1px solid var(--border-color, #ddd);
  border-radius: 4px;
  font-size: 14px;
  background: #fff;
  color: #333;
}

.form-input:focus,
.form-select:focus {
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

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.form-checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.help-text {
  margin: 4px 0 0 0;
  font-size: 12px;
  color: var(--text-secondary, #666);
  font-style: italic;
}

.type-specific-fields {
  padding: 12px;
  background: #f5f5f5;
  border-radius: 4px;
  margin-top: 4px;
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

.btn-primary {
  background: var(--primary-color, #2196F3);
  color: white;
}

.btn-primary:hover {
  background: var(--primary-color-dark, #1976D2);
}

.btn .material-icons {
  font-size: 18px;
}

/* New styles for improved labels and list values */
.field-with-label {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.inline-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary, #666);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0;
}

.field-hint {
  font-size: 11px;
  color: var(--text-secondary, #999);
  font-style: italic;
  margin-top: -2px;
}

.help-text code {
  background: #e0e0e0;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 11px;
  color: #d32f2f;
}

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

.col-value,
.col-display {
  font-size: 13px;
}

.col-actions {
  text-align: center;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 13px;
}

.btn-sm .material-icons {
  font-size: 16px;
}
</style>
