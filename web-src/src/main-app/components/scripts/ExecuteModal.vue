<template>
  <div v-if="visible" class="modal-overlay" @click.self="close">
    <div class="modal-content execute-modal card">
      <div class="modal-header">
        <span class="modal-title">Execute Script</span>
        <span class="modal-subtitle">{{ scriptName }}</span>
      </div>

      <div class="modal-body">
        <div class="instance-field input-field">
          <input type="text" v-model="instanceName" id="execute-instance"
                 placeholder="Optional identifier for this execution">
          <label for="execute-instance">Instance Name</label>
          <button v-if="instanceName" class="clear-btn" @click="instanceName = ''" title="Clear">
            <i class="material-icons">close</i>
          </button>
        </div>

        <div v-if="hasParameters" class="parameters-section">
          <span class="parameters-label">Parameters</span>
          <div class="params-table-wrapper">
            <table class="params-table">
              <thead>
                <tr>
                  <th class="param-name-col">Parameter</th>
                  <th class="param-value-col">Value</th>
                  <th class="param-clear-col"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="param in parameters" :key="param.name" :class="{ 'required-param': param.required }">
                  <td class="param-name">
                    {{ param.name }}
                    <span v-if="param.required" class="required-marker" title="Required">*</span>
                  </td>
                  <td class="param-value">
                    <input v-if="!param.withoutValue && param.type !== 'list' && param.type !== 'multiselect'"
                           type="text"
                           :value="localValues[param.name]"
                           @input="setLocalValue(param.name, $event.target.value)"
                           :placeholder="getPlaceholder(param)"
                           class="param-input"/>
                    <label v-else-if="param.withoutValue" class="checkbox-label">
                      <input type="checkbox"
                             :checked="localValues[param.name]"
                             @change="setLocalValue(param.name, $event.target.checked)"
                             class="filled-in"/>
                      <span></span>
                    </label>
                    <select v-else-if="param.type === 'list'"
                            :value="localValues[param.name]"
                            @change="setLocalValue(param.name, $event.target.value)"
                            class="param-select">
                      <option value="">-- Select --</option>
                      <option v-for="opt in param.values" :key="opt" :value="opt">{{ opt }}</option>
                    </select>
                    <div v-else-if="param.type === 'multiselect'" class="multiselect-display">
                      {{ formatMultiselectValue(localValues[param.name]) }}
                    </div>
                  </td>
                  <td class="param-clear">
                    <button v-if="canClearParam(param)"
                            class="clear-btn"
                            @click="clearParam(param.name)"
                            title="Clear">
                      <i class="material-icons">close</i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="validationError" class="validation-error">
          <i class="material-icons">error</i>
          <span>{{ validationError }}</span>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-flat waves-effect" @click="close">Cancel</button>
        <button class="btn waves-effect waves-light"
                :disabled="!!validationError"
                @click="runScript">
          <i class="material-icons left">play_arrow</i>
          Run
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import {mapState, mapActions} from 'vuex';
import {isNull, isEmptyString, isEmptyValue} from '@/common/utils/common';
import clone from 'lodash/clone';

export default {
  name: 'ExecuteModal',

  props: {
    visible: {
      type: Boolean,
      default: false
    },
    scriptName: {
      type: String,
      default: ''
    }
  },

  data() {
    return {
      instanceName: '',
      localValues: {}
    };
  },

  computed: {
    ...mapState('scriptConfig', {
      parameters: 'parameters',
      scriptConfig: 'scriptConfig'
    }),
    ...mapState('scriptSetup', {
      parameterValues: 'parameterValues'
    }),

    hasParameters() {
      return this.parameters && this.parameters.length > 0;
    },

    validationError() {
      if (!this.parameters) return null;

      for (const param of this.parameters) {
        if (param.required) {
          const value = this.localValues[param.name];
          if (isEmptyValue(value) || (typeof value === 'string' && isEmptyString(value.trim()))) {
            return `Required parameter "${param.name}" is missing`;
          }
        }
      }
      return null;
    }
  },

  watch: {
    visible(newVal) {
      if (newVal) {
        this.initLocalValues();
        document.body.style.overflow = 'hidden';
        this.$nextTick(() => {
          M.updateTextFields();
        });
      } else {
        document.body.style.overflow = '';
      }
    }
  },

  methods: {
    ...mapActions('scriptSetup', ['setParameterValue']),

    initLocalValues() {
      // Clone current parameter values to local state
      this.localValues = clone(this.parameterValues) || {};
      this.instanceName = '';
    },

    setLocalValue(paramName, value) {
      this.$set(this.localValues, paramName, value);
    },

    clearParam(paramName) {
      const param = this.parameters.find(p => p.name === paramName);
      if (param) {
        // Set to default or empty
        const defaultValue = !isNull(param.default) ? param.default : (param.withoutValue ? false : '');
        this.$set(this.localValues, paramName, defaultValue);
      }
    },

    canClearParam(param) {
      if (param.withoutValue) return false;
      const value = this.localValues[param.name];
      return !isEmptyValue(value) && value !== '';
    },

    getPlaceholder(param) {
      if (!isNull(param.default)) {
        return `Default: ${param.default}`;
      }
      return param.required ? 'Required' : 'Optional';
    },

    formatMultiselectValue(value) {
      if (!value) return '(none)';
      if (Array.isArray(value)) return value.join(', ');
      return String(value);
    },

    close() {
      this.$emit('close');
    },

    runScript() {
      if (this.validationError) return;

      // Apply local values to the store
      for (const [paramName, value] of Object.entries(this.localValues)) {
        this.setParameterValue({ parameterName: paramName, value: value });
      }

      // Small delay to let values propagate, then start execution
      this.$nextTick(() => {
        this.$store.dispatch('scriptExecutionManager/startExecution');
        this.close();
      });
    }
  }
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.execute-modal {
  width: 85%;
  max-width: 500px;
  height: auto;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  border-radius: var(--radius-md);
  margin: 0 !important;
  position: relative;
}

.modal-header {
  display: flex;
  flex-direction: column;
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

.modal-subtitle {
  font-size: 0.9em;
  color: var(--font-color-medium);
  margin-top: 4px;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px 24px;
}

.instance-field {
  position: relative;
  margin-bottom: 16px;
}

.instance-field input {
  padding-right: 36px;
  border-bottom: 1px solid var(--separator-color) !important;
}

.instance-field input:focus {
  border-bottom: 1px solid var(--primary-color) !important;
  box-shadow: 0 1px 0 0 var(--primary-color) !important;
}

.instance-field .clear-btn {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
}

.clear-btn {
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  color: var(--font-color-medium);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s, color 0.2s;
}

.clear-btn:hover {
  background-color: var(--hover-color);
  color: var(--error-color);
}

.clear-btn i {
  font-size: 18px;
}

.parameters-section {
  background-color: var(--background-color-high-emphasis);
  border-radius: 4px;
  padding: 12px;
}

.parameters-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--font-color-medium);
  display: block;
  margin-bottom: 8px;
}

.params-table-wrapper {
  max-height: 300px;
  overflow-y: auto;
}

.params-table {
  width: 100%;
  font-size: 13px;
  border-collapse: collapse;
}

.params-table th,
.params-table td {
  text-align: left;
  padding: 8px;
  vertical-align: middle;
}

.params-table th {
  color: var(--font-color-medium);
  font-weight: 500;
  border-bottom: 1px solid var(--separator-color);
  position: sticky;
  top: 0;
  background-color: var(--background-color-high-emphasis);
}

.param-name-col {
  width: 35%;
}

.param-value-col {
  width: 55%;
}

.param-clear-col {
  width: 10%;
}

.params-table .param-name {
  font-weight: 500;
  color: var(--font-color-main);
  white-space: nowrap;
}

.required-marker {
  color: var(--error-color);
  font-weight: bold;
  margin-left: 2px;
}

.required-param {
  background-color: rgba(244, 67, 54, 0.05);
}

.param-input,
.param-select {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  background-color: var(--background-color-level-4dp);
  color: var(--font-color-main);
  font-size: 13px;
  box-sizing: border-box;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.param-input:hover,
.param-select:hover {
  border-color: rgba(255, 255, 255, 0.5);
}

.param-input:focus,
.param-select:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(38, 166, 154, 0.2);
  outline: none;
}

.param-input::placeholder {
  color: var(--font-color-medium);
  opacity: 0.7;
}

.checkbox-label {
  display: flex;
  align-items: center;
  height: 24px;
}

.multiselect-display {
  color: var(--font-color-medium);
  font-style: italic;
}

.param-clear {
  text-align: center;
}

.validation-error {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background-color: rgba(244, 67, 54, 0.1);
  border-left: 3px solid var(--error-color);
  border-radius: 0 4px 4px 0;
  margin-top: 16px;
}

.validation-error i {
  color: var(--error-color);
  font-size: 20px;
}

.validation-error span {
  color: var(--error-color);
  font-size: 13px;
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

.modal-footer .btn {
  display: flex;
  align-items: center;
  gap: 4px;
}

.modal-footer .btn i.left {
  margin-right: 4px;
}

@media screen and (max-width: 768px) {
  .execute-modal {
    width: 95%;
    max-height: 95vh;
  }

  .modal-body {
    padding: 16px;
  }
}
</style>
