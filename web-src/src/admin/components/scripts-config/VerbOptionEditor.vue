<template>
  <div class="verb-option-editor">
    <div class="row">
      <TextField
        v-model="option.name"
        :config="nameField"
        class="col s4"
        @error="emitError('name', $event)"
      />
      <TextField
        v-model="option.label"
        :config="labelField"
        class="col s4"
        @error="emitError('label', $event)"
      />
    </div>

    <div class="row">
      <TextArea
        v-model="option.description"
        :config="descriptionField"
        class="col s12"
      />
    </div>

    <div class="row">
      <div class="col s12">
        <label class="section-label">Parameters for this verb</label>
        <p class="helper-text">Select which parameters are visible when this verb is selected</p>
        <div class="parameter-checkboxes">
          <label
            v-for="param in availableParameters"
            :key="param.name"
            class="parameter-checkbox"
          >
            <input
              type="checkbox"
              :checked="isParameterSelected(param.name)"
              @change="toggleParameter(param.name, $event.target.checked)"
            />
            <span>{{ param.name }}</span>
          </label>
        </div>
      </div>
    </div>

    <div class="row">
      <div class="col s12">
        <label class="section-label">Required Parameters</label>
        <p class="helper-text">Select which parameters are required for this verb</p>
        <div class="parameter-checkboxes">
          <label
            v-for="paramName in selectedParameters"
            :key="paramName"
            class="parameter-checkbox"
          >
            <input
              type="checkbox"
              :checked="isParameterRequired(paramName)"
              @change="toggleRequired(paramName, $event.target.checked)"
            />
            <span>{{ paramName }}</span>
          </label>
        </div>
        <p v-if="selectedParameters.length === 0" class="grey-text">
          No parameters selected for this verb
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import TextField from '@/common/components/textfield';
import TextArea from '@/common/components/TextArea';
import {isEmptyString} from '@/common/utils/common';

export default {
  name: 'VerbOptionEditor',

  components: {
    TextField,
    TextArea
  },

  props: {
    option: {
      type: Object,
      required: true
    },
    availableParameters: {
      type: Array,
      default: () => []
    }
  },

  data() {
    return {
      nameField: {
        name: 'Verb Name',
        required: true,
        description: 'CLI value (e.g., "create", "delete")'
      },
      labelField: {
        name: 'Label',
        description: 'Display text shown in UI (e.g., "Create Item")'
      },
      descriptionField: {
        name: 'Description',
        description: 'Help text shown when verb is selected'
      }
    };
  },

  computed: {
    selectedParameters() {
      return this.option.parameters || [];
    },
    requiredParameters() {
      return this.option.required_parameters || [];
    }
  },

  methods: {
    isParameterSelected(paramName) {
      return this.selectedParameters.includes(paramName);
    },

    isParameterRequired(paramName) {
      return this.requiredParameters.includes(paramName);
    },

    toggleParameter(paramName, checked) {
      if (!this.option.parameters) {
        this.$set(this.option, 'parameters', []);
      }

      const index = this.option.parameters.indexOf(paramName);
      if (checked && index === -1) {
        this.option.parameters.push(paramName);
      } else if (!checked && index !== -1) {
        this.option.parameters.splice(index, 1);
        // Also remove from required if unchecked
        this.toggleRequired(paramName, false);
      }
    },

    toggleRequired(paramName, checked) {
      if (!this.option.required_parameters) {
        this.$set(this.option, 'required_parameters', []);
      }

      const index = this.option.required_parameters.indexOf(paramName);
      if (checked && index === -1) {
        this.option.required_parameters.push(paramName);
      } else if (!checked && index !== -1) {
        this.option.required_parameters.splice(index, 1);
      }
    },

    emitError(fieldName, message) {
      this.$emit('error', {fieldName, message});
    }
  },

  watch: {
    'option.name'(newName) {
      // Auto-fill label if empty
      if (isEmptyString(this.option.label) && !isEmptyString(newName)) {
        this.$set(this.option, 'label', newName.charAt(0).toUpperCase() + newName.slice(1));
      }
    }
  }
};
</script>

<style scoped>
.verb-option-editor {
  padding: 12px;
}

.section-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--font-color-main, #fff);
  margin-bottom: 4px;
  display: block;
}

.helper-text {
  font-size: 12px;
  color: var(--font-color-medium, rgba(255, 255, 255, 0.7));
  margin-top: 0;
  margin-bottom: 12px;
}

.parameter-checkboxes {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 8px;
}

.parameter-checkbox {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  min-width: 150px;
}

.parameter-checkbox input[type="checkbox"] {
  position: static;
  opacity: 1;
  pointer-events: auto;
}

.parameter-checkbox span {
  font-size: 14px;
  color: var(--font-color-main, #fff);
}
</style>
