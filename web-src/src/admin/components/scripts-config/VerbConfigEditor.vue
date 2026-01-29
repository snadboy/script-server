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
      <div class="row">
        <TextField
          v-model="config.parameter_name"
          :config="parameterNameField"
          class="col s4"
        />
        <TextField
          v-model="config.default"
          :config="defaultField"
          class="col s4"
        />
        <CheckBox
          v-model="config.required"
          :config="requiredField"
          class="col s3 offset-s1 checkbox-field"
        />
      </div>

      <div class="row">
        <div class="col s12">
          <label class="section-label">Shared Parameters</label>
          <p class="helper-text">Parameters that are visible for ALL verbs (e.g., --verbose, --debug)</p>
          <div class="parameter-checkboxes">
            <label
              v-for="param in availableParameters"
              :key="param.name"
              class="parameter-checkbox"
            >
              <input
                type="checkbox"
                :checked="isSharedParameter(param.name)"
                @change="toggleSharedParameter(param.name, $event.target.checked)"
              />
              <span>{{ param.name }}</span>
            </label>
          </div>
          <p v-if="availableParameters.length === 0" class="grey-text">
            No parameters defined yet. Add parameters in the Parameters tab first.
          </p>
        </div>
      </div>

      <div class="verbs-section">
        <h6>Verb Options</h6>
        <p class="helper-text">Define the subcommands/verbs for this script (e.g., create, delete, list)</p>

        <ul ref="verbsPanel" class="collapsible popout">
          <li
            v-for="(option, index) in verbOptions"
            :key="verbKeys.get(option)"
            class="verb-list-item"
          >
            <div class="collapsible-header verb-header primary-color-light">
              <i class="material-icons">unfold_more</i>
              <span>{{ option.name || 'New Verb' }}</span>
              <div style="flex: 1 1 0"></div>
              <a class="btn-flat waves-circle" @click.stop="deleteVerb(option)">
                <i class="material-icons">delete</i>
              </a>
              <a class="btn-flat waves-circle" @click.stop="moveVerbUp(index)">
                <i class="material-icons">arrow_upward</i>
              </a>
              <a class="btn-flat waves-circle" @click.stop="moveVerbDown(index)">
                <i class="material-icons">arrow_downward</i>
              </a>
            </div>
            <div class="collapsible-body">
              <VerbOptionEditor
                :option="option"
                :available-parameters="nonSharedParameters"
              />
            </div>
          </li>

          <li class="add-verb-item" @click.stop="addVerb">
            <div class="collapsible-header">
              <i class="material-icons">add</i>Add Verb Option
            </div>
          </li>
        </ul>
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
import '@/common/materializecss/imports/collapsible';
import '@/common/materializecss/imports/toast';
import {guid} from '@/common/utils/common';
import TextField from '@/common/components/textfield';
import CheckBox from '@/common/components/checkbox';
import VerbOptionEditor from './VerbOptionEditor';

export default {
  name: 'VerbConfigEditor',

  components: {
    TextField,
    CheckBox,
    VerbOptionEditor
  },

  props: {
    value: {
      type: Object,
      default: null
    },
    sharedParameters: {
      type: Array,
      default: () => []
    },
    availableParameters: {
      type: Array,
      default: () => []
    }
  },

  data() {
    return {
      config: this.initConfig(),
      verbKeys: new Map(),
      openingNewVerb: false,
      enabledField: {
        name: 'Enable Verb/Subcommand Support',
        description: 'Allow this script to have multiple subcommands like git or docker'
      },
      parameterNameField: {
        name: 'Parameter Name',
        required: true,
        description: 'Internal name for the verb parameter (default: "verb")'
      },
      defaultField: {
        name: 'Default Verb',
        description: 'Which verb to pre-select (must match a verb name below)'
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
          this.$emit('update:sharedParameters', []);
        }
      }
    },

    verbOptions() {
      return this.config?.options || [];
    },

    sharedParametersList: {
      get() {
        return this.sharedParameters || [];
      },
      set(value) {
        this.$emit('update:sharedParameters', value);
      }
    },

    nonSharedParameters() {
      return this.availableParameters.filter(
        param => !this.isSharedParameter(param.name)
      );
    }
  },

  mounted() {
    if (this.$refs.verbsPanel) {
      M.Collapsible.init(this.$refs.verbsPanel, {
        onOpenEnd: () => {
          this.openingNewVerb = false;
        }
      });
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
        default: null,
        options: []
      };
    },

    isSharedParameter(paramName) {
      return this.sharedParametersList.includes(paramName);
    },

    toggleSharedParameter(paramName, checked) {
      const list = [...this.sharedParametersList];
      const index = list.indexOf(paramName);

      if (checked && index === -1) {
        list.push(paramName);
      } else if (!checked && index !== -1) {
        list.splice(index, 1);
      }

      this.sharedParametersList = list;
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

      const lastIndex = this.config.options.length;
      this.config.options.push(newVerb);
      this.setVerbKey(newVerb);

      this.$nextTick(() => {
        this.openingNewVerb = true;
        const collapsible = M.Collapsible.getInstance(this.$refs.verbsPanel);
        if (collapsible) {
          collapsible.open(lastIndex);
        }
      });
    },

    deleteVerb(verb) {
      const index = this.config.options.indexOf(verb);
      if (index < 0) return;

      this.config.options.splice(index, 1);

      const toast = M.toast({
        html: `<span>Deleted ${verb.name || 'verb'}</span>` +
            '<button class="btn-flat toast-action">Undo</button>',
        displayLength: 8000
      });

      const undoButton = toast.el.getElementsByTagName('BUTTON')[0];
      undoButton.onclick = () => {
        toast.dismiss();
        const insertPosition = Math.min(index, this.config.options.length);
        this.config.options.splice(insertPosition, 0, verb);
      };
    },

    moveVerbUp(index) {
      if (index <= 0) return;
      const options = this.config.options;
      const temp = options[index - 1];
      this.$set(options, index - 1, options[index]);
      this.$set(options, index, temp);
    },

    moveVerbDown(index) {
      const options = this.config.options;
      if (index >= options.length - 1) return;
      const temp = options[index + 1];
      this.$set(options, index + 1, options[index]);
      this.$set(options, index, temp);
    },

    setVerbKey(verb) {
      if (this.verbKeys.has(verb)) return;
      this.verbKeys.set(verb, guid(32));
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
    },

    verbOptions: {
      immediate: true,
      handler(options) {
        if (options) {
          options.forEach(verb => this.setVerbKey(verb));
        }
      }
    },

    openingNewVerb(opening) {
      if (!opening) return;

      let interval = null;
      interval = setInterval(() => {
        try {
          const verbElements = this.$refs.verbsPanel?.getElementsByTagName('li');
          if (verbElements && verbElements.length > 1) {
            const newVerbElement = verbElements[verbElements.length - 2];
            newVerbElement.scrollIntoView({behavior: 'smooth'});
          }
        } finally {
          if (!this.openingNewVerb) {
            clearInterval(interval);
          }
        }
      }, 40);
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
  margin-bottom: 16px;
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

.verbs-section {
  margin-top: 24px;
}

.verbs-section h6 {
  margin-top: 0;
  margin-bottom: 8px;
  font-size: 16px;
  font-weight: 500;
  color: var(--font-color-main, #fff);
}

.collapsible-header.verb-header {
  padding-top: 8px;
  padding-bottom: 8px;
  align-items: center;
}

.btn-flat {
  padding: 0;
}

.btn-flat i {
  margin-right: 0;
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
</style>
