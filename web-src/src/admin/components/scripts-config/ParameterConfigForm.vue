<template>
  <div class="parameter-form">
    <!-- Basic Section -->
    <div class="section-basic">
      <div class="row mb-2">
        <Textfield
          v-model="name"
          :config="nameField"
          class="col s4"
          @error="handleError(nameField, $event)"
        />
        <TextArea
          v-model="description"
          :config="descriptionField"
          class="col s8"
          @error="handleError(descriptionField, $event)"
        />
      </div>

      <div class="row mb-2">
        <Combobox
          v-model="type"
          :config="typeField"
          :dropdownContainer="this.$el"
          class="col s4"
          @error="handleError(typeField, $event)"
        />
        <div class="col s8">
          <label>
            <input
              type="checkbox"
              v-model="required"
              class="filled-in"
            />
            <span>Required</span>
          </label>
        </div>
      </div>
    </div>

    <!-- Separator -->
    <div class="section-divider"></div>

    <!-- Parameter Behavior Section -->
    <div class="section-behavior">
      <h6 class="section-title">Parameter Behavior</h6>

      <div class="row mb-2">
        <Textfield
          v-model="param"
          :config="paramField"
          class="col s4"
          @error="handleError(paramField, $event)"
        />
        <Combobox
          v-model="passAs"
          :config="passAsField"
          class="col s4"
          @error="handleError(passAsField, $event)"
        />
      </div>

      <div v-if="type !== 'flag' && (passAs === 'argument' || passAs === 'argument + env_variable')" class="row mb-1">
        <div class="col s12">
          <label>
            <input
              type="checkbox"
              v-model="sameArgParam"
              class="filled-in"
            />
            <span>Combine param with value (-param=value)</span>
          </label>
        </div>
      </div>
    </div>

    <!-- Separator -->
    <div class="section-divider"></div>

    <!-- Constraints Section (Type-Specific) -->
    <div class="section-constraints">
      <h6 class="section-title bold">Constraints</h6>

      <!-- Text Type Constraints -->
      <div v-if="type === 'text'" class="constraints-text">
        <div class="row mb-2">
          <Textfield
            v-model="minLength"
            :config="minLengthField"
            class="col s3"
            @error="handleError(minLengthField, $event)"
          />
          <Textfield
            v-model="maxLength"
            :config="maxLengthField"
            class="col s3"
            @error="handleError(maxLengthField, $event)"
          />
          <Textfield
            v-model="defaultValue"
            :config="{ name: 'Default value' }"
            class="col s6"
            @error="handleError('Default value', $event)"
          />
        </div>

        <div class="row mb-2">
          <Textfield
            v-model="regexPattern"
            :config="regexPatternField"
            class="col s12"
            @error="handleError(regexPatternField, $event)"
          />
        </div>

        <div v-if="regexPattern" class="row mb-2">
          <Textfield
            v-model="regexDescription"
            :config="regexDescriptionField"
            class="col s12"
            @error="handleError(regexDescriptionField, $event)"
          />
        </div>
      </div>

      <!-- Int Type Constraints -->
      <div v-if="type === 'int'" class="constraints-int">
        <div class="row mb-2">
          <Textfield
            v-model="min"
            :config="minField"
            class="col s4"
            @error="handleError(minField, $event)"
          />
          <Textfield
            v-model="max"
            :config="maxFieldComputed"
            class="col s4"
            @error="handleError(maxFieldComputed, $event)"
          />
          <Textfield
            v-model="defaultValue"
            :config="{ name: 'Default value', type: 'int' }"
            class="col s4"
            @error="handleError('Default value', $event)"
          />
        </div>
      </div>

      <!-- Bool Type Constraints -->
      <div v-if="type === 'bool'" class="constraints-bool">
        <div class="row mb-2">
          <div class="col s12">
            <label class="field-label">Default value</label>
            <p>
              <label>
                <input
                  type="radio"
                  v-model="defaultValue"
                  value="true"
                  name="bool-default"
                />
                <span>True</span>
              </label>
            </p>
            <p>
              <label>
                <input
                  type="radio"
                  v-model="defaultValue"
                  value="false"
                  name="bool-default"
                />
                <span>False</span>
              </label>
            </p>
          </div>
        </div>
      </div>

      <!-- List Type Constraints -->
      <div v-if="type === 'list'" class="constraints-list">
        <!-- Selection Mode -->
        <div class="row mb-2">
          <div class="col s12">
            <label class="field-label">Selection mode</label>
            <p>
              <label>
                <input
                  type="radio"
                  v-model="listSelectionMode"
                  value="single"
                  name="selection-mode"
                />
                <span>Single selection</span>
              </label>
              <label class="ml-4">
                <input
                  type="radio"
                  v-model="listSelectionMode"
                  value="multiple"
                  name="selection-mode"
                />
                <span>Multiple selection</span>
              </label>
            </p>
          </div>
        </div>

        <!-- List Values Table -->
        <div class="row mb-2">
          <div class="col s12">
            <label class="field-label">List values</label>
            <table class="list-values-table">
              <thead>
                <tr>
                  <th>Value (sent to script)</th>
                  <th>UI Display (shown to user)</th>
                  <th width="50"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in listValues" :key="item.id || index">
                  <td>
                    <input
                      type="text"
                      v-model="item.value"
                      class="list-value-input"
                      placeholder="e.g., prod"
                      @blur="handleListValueBlur"
                      @keydown.tab="handleValueTab($event, item)"
                      :ref="`value-${item.id}`"
                    />
                  </td>
                  <td>
                    <input
                      type="text"
                      v-model="item.uiValue"
                      class="list-value-input"
                      placeholder="e.g., Production"
                      @blur="handleListValueBlur"
                      :ref="`uiValue-${item.id}`"
                    />
                  </td>
                  <td>
                    <button
                      type="button"
                      class="btn-flat btn-small"
                      @click="removeListValue(index)"
                    >
                      <i class="material-icons">delete</i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
            <button
              type="button"
              class="btn-flat btn-small mt-1"
              @click="addListValue"
            >
              <i class="material-icons left">add</i>
              Add Value
            </button>
          </div>
        </div>

        <!-- Default Value -->
        <div class="row mb-2">
          <Combobox
            v-model="defaultValue"
            :config="{
              name: 'Default value',
              type: 'list',
              values: listValuesForDropdown
            }"
            class="col s6"
            @error="handleError('Default value', $event)"
          />
        </div>

        <!-- Multiple Selection Format -->
        <div v-if="listSelectionMode === 'multiple'" class="row mb-2">
          <div class="col s12">
            <label class="field-label">How to pass multiple values</label>
            <p>
              <label>
                <input
                  type="radio"
                  v-model="multiselectFormat"
                  value="single_argument"
                  name="multiselect-format"
                />
                <span>Single argument: <code>-env prod,staging</code></span>
              </label>
            </p>
            <p>
              <label>
                <input
                  type="radio"
                  v-model="multiselectFormat"
                  value="argument_per_value"
                  name="multiselect-format"
                />
                <span>Separate arguments: <code>-env prod staging</code></span>
              </label>
            </p>
            <p>
              <label>
                <input
                  type="radio"
                  v-model="multiselectFormat"
                  value="repeat_param_value"
                  name="multiselect-format"
                />
                <span>Repeat parameter: <code>-env prod -env staging</code></span>
              </label>
            </p>
          </div>
        </div>

        <!-- Separator (only for single_argument) -->
        <div
          v-if="listSelectionMode === 'multiple' && multiselectFormat === 'single_argument'"
          class="row mb-2"
        >
          <Textfield
            v-model="separator"
            :config="separatorField"
            class="col s2"
            @error="handleError(separatorField, $event)"
          />
        </div>
      </div>

      <!-- Flag Type Info -->
      <div v-if="type === 'flag'" class="constraints-flag">
        <div class="info-box">
          <i class="material-icons">info</i>
          <span>
            This parameter passes only the flag without a value.<br>
            Example: <code>-v</code> or <code>--verbose</code>
          </span>
        </div>
      </div>

      <!-- Constant Type Constraints -->
      <div v-if="type === 'constant'" class="constraints-constant">
        <div class="row mb-2">
          <Textfield
            v-model="defaultValue"
            :config="{
              name: 'Constant value (visible but read-only)',
              required: true
            }"
            class="col s12"
            @error="handleError('Constant value', $event)"
          />
        </div>
        <div class="info-box">
          <i class="material-icons">info</i>
          <span>
            Constant parameters are visible but read-only. Users will see this value but cannot change it.
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Checkbox from '@/common/components/checkbox';
import Combobox from '@/common/components/combobox';
import TextArea from '@/common/components/TextArea';
import Textfield from '@/common/components/textfield';
import {isEmptyString} from '@/common/utils/common';
import get from 'lodash/get';
import Vue from 'vue';
import {
  descriptionField,
  maxField,
  minField,
  nameField,
  paramField,
  passAsField,
  regexDescriptionField,
  regexPatternField,
  separatorField,
  typeField
} from './parameter-fields';

// Helper function to update value reactively
function updateValue(value, configField, newValue) {
  if (!value.hasOwnProperty(configField)) {
    Object.assign(value, {[configField]: newValue});
  }
  Vue.set(value, configField, newValue);
}

export default {
  name: 'ParameterConfigForm',
  components: {Checkbox, Combobox, TextArea, Textfield},
  props: {
    value: {
      type: Object,
      default: null
    }
  },

  data() {
    return {
      name: null,
      description: null,
      param: null,
      passAs: 'argument + env_variable',
      sameArgParam: false,
      type: 'text',
      required: false,

      // Type-specific fields
      min: null,
      max: null,
      minLength: 0,
      maxLength: 100,
      regexPattern: '',
      regexDescription: '',
      defaultValue: '',
      separator: ',',

      // List-specific fields
      listSelectionMode: 'single',
      multiselectFormat: 'single_argument',
      listValues: [],
      nextListItemId: 1,  // Counter for unique IDs

      // Internal flags
      isLoading: false,  // Prevent reactivity loops
      isTabbing: false,  // Track if user is tabbing between fields

      // Field definitions
      nameField,
      descriptionField,
      paramField,
      passAsField,
      typeField,
      minField,
      maxField,
      regexPatternField,
      regexDescriptionField,
      separatorField,
      minLengthField: {
        name: 'Min length',
        type: 'int',
        min: 0,
        required: true
      },
      maxLengthField: {
        name: 'Max length',
        type: 'int',
        min: 1,
        required: true
      }
    };
  },

  computed: {
    maxFieldComputed() {
      return {
        ...this.maxField,
        min: this.min
      };
    },
    listValuesForDropdown() {
      // Filter out empty values for the default value dropdown
      return this.listValues
        .map(v => v.value)
        .filter(v => !isEmptyString(v));
    }
  },

  watch: {
    value: {
      immediate: true,
      handler(config) {
        if (config && !this.isLoading) {
          // Only reload from backend if not already loading
          // This prevents resetting the array during add/remove operations
          this.isLoading = true;
          this.fromBackendConfig(config);
          this.$nextTick(() => {
            this.isLoading = false;
          });
        }
      }
    },

    // Watch all fields and sync to backend
    name() { if (!this.isLoading) this.syncToBackend(); },
    description() { if (!this.isLoading) this.syncToBackend(); },
    param() { if (!this.isLoading) this.syncToBackend(); },
    passAs() { if (!this.isLoading) this.syncToBackend(); },
    sameArgParam() { if (!this.isLoading) this.syncToBackend(); },
    type(newType, oldType) {
      // Initialize listValues when switching to list type
      if (newType === 'list' && oldType !== 'list' && this.listValues.length === 0) {
        this.listValues = [{
          id: this.nextListItemId++,
          value: '',
          uiValue: ''
        }];
      }
      if (!this.isLoading) this.syncToBackend();
    },
    required() { if (!this.isLoading) this.syncToBackend(); },
    min() { if (!this.isLoading) this.syncToBackend(); },
    max() { if (!this.isLoading) this.syncToBackend(); },
    minLength() { if (!this.isLoading) this.syncToBackend(); },
    maxLength() { if (!this.isLoading) this.syncToBackend(); },
    regexPattern() { if (!this.isLoading) this.syncToBackend(); },
    regexDescription() { if (!this.isLoading) this.syncToBackend(); },
    defaultValue() { if (!this.isLoading) this.syncToBackend(); },
    separator() { if (!this.isLoading) this.syncToBackend(); },
    listSelectionMode() { if (!this.isLoading) this.syncToBackend(); },
    multiselectFormat() { if (!this.isLoading) this.syncToBackend(); }
    // Note: listValues watcher removed - now syncs only on blur or add/remove
    // Deep watching caused re-renders on every keystroke, losing focus
  },

  methods: {
    addListValue() {
      // Set loading flag to prevent value watcher from resetting the array
      const wasLoading = this.isLoading;
      this.isLoading = true;

      // Add new empty row with unique ID
      this.listValues.push({
        id: this.nextListItemId++,
        value: '',
        uiValue: ''
      });

      // Sync after Vue updates, WHILE isLoading is still true
      this.$nextTick(() => {
        if (!wasLoading) {
          this.syncToBackend();
        }
        // Restore loading flag AFTER sync completes
        this.$nextTick(() => {
          this.isLoading = wasLoading;
        });
      });
    },

    removeListValue(index) {
      // Set loading flag to prevent value watcher from resetting the array
      const wasLoading = this.isLoading;
      this.isLoading = true;

      // Remove row
      this.listValues.splice(index, 1);

      // Sync after Vue updates, WHILE isLoading is still true
      this.$nextTick(() => {
        if (!wasLoading) {
          this.syncToBackend();
        }
        // Restore loading flag AFTER sync completes
        this.$nextTick(() => {
          this.isLoading = wasLoading;
        });
      });
    },

    handleListValueBlur() {
      // Don't sync if user is just tabbing between fields
      if (this.isTabbing) return;

      // Sync when user finishes editing a list value
      if (!this.isLoading) this.syncToBackend();
    },

    handleValueTab(event, item) {
      event.preventDefault();

      // Set tabbing flag to prevent blur sync
      this.isTabbing = true;

      // Auto-fill the UI Display if empty
      if (!item.uiValue && item.value) {
        item.uiValue = item.value;
      }

      // Focus and select the UI Display input
      this.$nextTick(() => {
        const uiInput = this.$refs[`uiValue-${item.id}`];

        if (uiInput) {
          // $refs in v-for returns an array
          const input = Array.isArray(uiInput) ? uiInput[0] : uiInput;

          if (input) {
            input.focus();
            input.select();

            // Clear tabbing flag after a delay
            setTimeout(() => {
              this.isTabbing = false;
            }, 100);
          }
        }
      });
    },

    // Convert from backend config format to UI state
    fromBackendConfig(config) {
      this.name = config.name || '';
      this.description = config.description || '';
      this.param = config.param || '';
      this.passAs = config.pass_as || 'argument + env_variable';
      this.sameArgParam = !!get(config, 'same_arg_param', false);
      this.required = !!get(config, 'required', false);

      // Determine simplified type
      if (config.no_value) {
        this.type = 'flag';
      } else if (config.constant) {
        this.type = 'constant';
        this.defaultValue = config.default || '';
      } else if (config.type === 'multiselect') {
        this.type = 'list';
        this.listSelectionMode = 'multiple';
        this.multiselectFormat = config.multiselect_argument_type || 'single_argument';
        this.separator = config.separator || ',';
        this.loadListValues(config);
      } else if (config.type === 'list') {
        // Check if it's a bool type (list with only 'true' and 'false')
        const values = config.values || [];
        if (values.length === 2 && values.includes('true') && values.includes('false')) {
          this.type = 'bool';
          this.defaultValue = config.default || 'false';
        } else {
          this.type = 'list';
          this.listSelectionMode = 'single';
          this.loadListValues(config);
        }
      } else if (config.type === 'editable_list') {
        this.type = 'list';
        this.listSelectionMode = 'single';
        this.loadListValues(config);
      } else if (config.type === 'multiline_text' || config.type === 'ip' ||
                 config.type === 'ip4' || config.type === 'ip6') {
        // Migrate old types to text
        this.type = 'text';
        this.maxLength = config.max_length || 100;
        this.minLength = 0;
        if (config.regex) {
          this.regexPattern = config.regex.pattern || '';
          this.regexDescription = config.regex.description || '';
        }
        this.defaultValue = config.default || '';
      } else {
        this.type = config.type || 'text';
      }

      // Type-specific properties
      if (this.type === 'text') {
        this.maxLength = config.max_length || 100;
        this.minLength = 0;
        if (config.regex) {
          this.regexPattern = config.regex.pattern || '';
          this.regexDescription = config.regex.description || '';
        }
        this.defaultValue = config.default || '';
      } else if (this.type === 'int') {
        this.min = config.min;
        this.max = config.max;
        this.defaultValue = config.default || '';
      } else if (this.type === 'bool') {
        this.defaultValue = config.default || 'false';
      } else if (this.type === 'list') {
        this.defaultValue = config.default || '';
      }
    },

    loadListValues(config) {
      const values = config.values || [];
      const uiMapping = config.values_ui_mapping || {};

      this.listValues = values.map(val => ({
        id: this.nextListItemId++,
        value: val,
        uiValue: uiMapping[val] || val
      }));

      // If no values exist, add one empty row to get started
      if (this.listValues.length === 0) {
        this.listValues.push({
          id: this.nextListItemId++,
          value: '',
          uiValue: ''
        });
      }

      this.defaultValue = config.default || '';
    },

    // Convert from UI state to backend config format
    syncToBackend() {
      if (!this.value) return;

      const config = {
        name: this.name,
        description: this.description,
        required: this.required,
        param: this.param,
        same_arg_param: this.sameArgParam
      };

      // Pass as (only set if not default)
      if (this.passAs !== 'argument + env_variable') {
        config.pass_as = this.passAs;
      }

      // Type-specific serialization
      if (this.type === 'text') {
        config.type = 'text';
        config.max_length = this.maxLength;
        if (this.regexPattern) {
          config.regex = {
            pattern: this.regexPattern,
            description: this.regexDescription
          };
        }
        if (this.defaultValue) {
          config.default = this.defaultValue;
        }
      } else if (this.type === 'int') {
        config.type = 'int';
        if (this.min !== null && this.min !== '') config.min = parseInt(this.min);
        if (this.max !== null && this.max !== '') config.max = parseInt(this.max);
        if (this.defaultValue) {
          config.default = this.defaultValue;
        }
      } else if (this.type === 'bool') {
        // Backend uses list type
        config.type = 'list';
        config.values = ['true', 'false'];
        if (this.defaultValue) {
          config.default = this.defaultValue;
        }
      } else if (this.type === 'list') {
        const values = this.listValues.map(v => v.value).filter(v => !isEmptyString(v));

        if (this.listSelectionMode === 'multiple') {
          config.type = 'multiselect';
          config.multiselect_argument_type = this.multiselectFormat;
          if (this.multiselectFormat === 'single_argument') {
            config.separator = this.separator || ',';
          }
        } else {
          config.type = 'list';
        }

        config.values = values;

        // Add UI mapping if different from values
        const hasMapping = this.listValues.some(v => v.uiValue && v.uiValue !== v.value);
        if (hasMapping) {
          config.values_ui_mapping = {};
          this.listValues.forEach(v => {
            if (v.uiValue && !isEmptyString(v.value)) {
              config.values_ui_mapping[v.value] = v.uiValue;
            }
          });
        }

        if (this.defaultValue) {
          config.default = this.defaultValue;
        }
      } else if (this.type === 'flag') {
        // Backend uses no_value
        config.no_value = true;
      } else if (this.type === 'constant') {
        // Backend uses constant flag
        config.constant = true;
        config.default = this.defaultValue;
      }

      // Update the value object
      Object.keys(this.value).forEach(key => {
        this.$delete(this.value, key);
      });
      Object.keys(config).forEach(key => {
        updateValue(this.value, key, config[key]);
      });
    },

    handleError(fieldConfig, error) {
      let fieldName;
      if (typeof fieldConfig === 'string') {
        fieldName = fieldConfig;
      } else {
        fieldName = fieldConfig.name;
      }
      this.$emit('error', {fieldName, message: error});
    }
  }
};
</script>

<style scoped>
.parameter-form {
  padding: 1rem;
}

.section-divider {
  border-bottom: 1px solid #e0e0e0;
  margin: 1.5rem 0;
}

.section-title {
  font-size: 1rem;
  font-weight: 500;
  margin-bottom: 1rem;
  color: #424242;
}

.section-title.bold {
  font-weight: 700;
  color: #212121;
}

.mb-1 {
  margin-bottom: 0.5rem;
}

.mb-2 {
  margin-bottom: 1rem;
}

.ml-4 {
  margin-left: 2rem;
}

.mt-1 {
  margin-top: 0.5rem;
}

.field-label {
  display: block;
  font-size: 0.9rem;
  font-weight: 500;
  color: #424242;
  margin-bottom: 0.5rem;
}

.list-values-table {
  width: 100%;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  margin-top: 0.5rem;
}

.list-values-table thead th {
  background: #f5f5f5;
  padding: 0.5rem;
  font-size: 0.85rem;
  font-weight: 600;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
  color: #424242;
}

.list-values-table tbody td {
  padding: 0.5rem;
  border-bottom: 1px solid #f0f0f0;
}

.list-values-table tbody tr:last-child td {
  border-bottom: none;
}

.list-value-input {
  width: 100%;
  padding: 0.25rem 0.5rem;
  border: 1px solid #ddd;
  border-radius: 3px;
  font-size: 0.9rem;
}

.list-value-input:focus {
  outline: none;
  border-color: #26a69a;
}

.info-box {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  background: #e3f2fd;
  border-left: 4px solid #2196f3;
  border-radius: 4px;
  font-size: 0.9rem;
  color: #1565c0;
}

.info-box i {
  font-size: 1.25rem;
  color: #2196f3;
}

.info-box code {
  background: #bbdefb;
  padding: 0.125rem 0.375rem;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
}

/* Override Materialize radio button spacing */
[type="radio"]:not(:checked) + span,
[type="radio"]:checked + span {
  padding-left: 2rem;
}

/* Fix Materialize row margin */
.parameter-form .row {
  margin-bottom: 0;
}
</style>
