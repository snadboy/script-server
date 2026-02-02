<template>
  <div class="details-tab">
    <div class="row">
      <TextField v-model="scriptConfig.name" :config="nameFieldWithValidation" class="col s6" @error="handleNameError"/>
      <TextField v-model="scriptConfig.group" :config="groupField" class="col s5 offset-s1"/>
    </div>
    <!-- Script path and working directory are auto-managed for imported projects -->
    <!-- Only show these fields for manual scripts (backward compatibility) -->
    <div v-if="!pathReadonly" class="row">
      <ScriptPathField
        :config-name="scriptConfig.name"
        :new-config="true"
        :original-path="scriptConfig.script_path"
        :readonly="false"
        class="col s6"
        @change="updateScript"
      />
      <TextField v-model="scriptConfig.working_directory" :config="workDirField" class="col s5 offset-s1"/>
    </div>
    <div class="row">
      <TextArea v-model="scriptConfig.description" :config="descriptionField" class="col s12"/>
    </div>
    <div class="row">
      <Combobox v-model="scriptConfig.output_format" :config="outputFormatField" class="col s4"/>
      <CheckBox v-model="scriptConfig.requires_terminal" :config="requiresTerminalField" class="col s4 checkbox-field"/>
    </div>
  </div>
</template>

<script>
import CheckBox from '@/common/components/checkbox';
import Combobox from '@/common/components/combobox';
import TextArea from '@/common/components/TextArea';
import TextField from '@/common/components/textfield';
import ScriptPathField from '@/admin/components/scripts-config/script-edit/ScriptField';
import {
  descriptionField,
  groupField,
  nameField,
  outputFormatField,
  requiresTerminalField,
  workDirField
} from '../script-fields';

export default {
  name: 'DetailsTab',

  components: {
    CheckBox,
    Combobox,
    ScriptPathField,
    TextArea,
    TextField
  },

  props: {
    pathReadonly: {
      type: Boolean,
      default: false
    }
  },

  data() {
    return {
      nameField,
      groupField,
      workDirField,
      descriptionField,
      outputFormatField,
      requiresTerminalField,
      nameValidationError: null
    };
  },

  computed: {
    existingScriptNames() {
      const adminScripts = this.$store.state.adminScripts?.scripts || [];
      return adminScripts.map(s => s.name.toLowerCase());
    },

    nameFieldWithValidation() {
      const self = this;
      return {
        ...nameField,
        get required() {
          return nameField.required;
        },
        validate(value) {
          if (!value || !value.trim()) {
            return 'Script name is required';
          }
          if (self.existingScriptNames.includes(value.toLowerCase())) {
            return 'A script with this name already exists';
          }
          return '';
        }
      };
    },
    storeModule() {
      return this.$store.state.adminScriptConfig ? 'adminScriptConfig' : 'scriptConfig';
    },
    scriptConfig() {
      return this.$store.state[this.storeModule].scriptConfig;
    }
  },

  methods: {
    updateScript(updatedFields) {
      this.$store.dispatch(`${this.storeModule}/setScript`, updatedFields);
    },

    handleNameError(error) {
      this.nameValidationError = error;
      // Emit to parent to disable save button
      this.$emit('validation-error', { field: 'name', error });
    }
  }
}
</script>

<style scoped>
.details-tab {
  padding: 1.5rem;
}

.row {
  margin-bottom: 1rem;
}

.checkbox-field {
  padding-top: 2rem;
}
</style>
