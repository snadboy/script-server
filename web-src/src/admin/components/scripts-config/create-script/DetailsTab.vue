<template>
  <div class="details-tab">
    <div class="row">
      <TextField v-model="scriptConfig.name" :config="nameField" class="col s6"/>
      <TextField v-model="scriptConfig.group" :config="groupField" class="col s5 offset-s1"/>
    </div>
    <div class="row">
      <ScriptPathField
        :config-name="scriptConfig.name"
        :new-config="true"
        :original-path="scriptConfig.script_path"
        :readonly="pathReadonly"
        class="col s6"
        @change="updateScript"
      />
      <TextField v-model="scriptConfig.working_directory" :config="workDirField" class="col s5 offset-s1"/>
    </div>
    <div class="row">
      <TextArea v-model="scriptConfig.description" :config="descriptionField" class="col s12"/>
    </div>
    <div class="row">
      <Combobox v-model="scriptConfig.output_format" :config="outputFormatField" class="col s3"/>
      <CheckBox v-model="scriptConfig.requires_terminal" :config="requiresTerminalField" class="col s3 checkbox-field"/>
      <TextField v-model="scriptConfig.include" :config="includeScriptField" class="col s5 offset-s1"/>
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
  includeScriptField,
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
      includeScriptField
    };
  },

  computed: {
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
