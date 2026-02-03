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
              <i class="material-icons expand-icon">chevron_right</i>
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
        }
      }
    },

    verbOptions() {
      return this.config?.options || [];
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

  mounted() {
    this.initCollapsible();
  },

  methods: {
    initCollapsible() {
      this.$nextTick(() => {
        if (this.$refs.verbsPanel) {
          // Destroy existing instance if it exists
          const existing = M.Collapsible.getInstance(this.$refs.verbsPanel);
          if (existing) {
            existing.destroy();
          }

          // Initialize new instance
          M.Collapsible.init(this.$refs.verbsPanel, {
            accordion: false,
            onOpenEnd: () => {
              this.openingNewVerb = false;
            }
          });
        }
      });
    },

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
      this.setVerbKey(newVerb);

      this.$nextTick(() => {
        this.openingNewVerb = true;
        this.initCollapsible();

        // Open the newly added verb after collapsible is initialized
        this.$nextTick(() => {
          const collapsible = M.Collapsible.getInstance(this.$refs.verbsPanel);
          if (collapsible) {
            const lastIndex = this.config.options.length - 1;
            collapsible.open(lastIndex);
          }
        });
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
          // Reinitialize collapsible when verbs change
          this.initCollapsible();
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

.verbs-section {
  margin-top: 0;
  margin-bottom: 24px;
}

.verbs-section h6 {
  margin-top: 0;
  margin-bottom: 8px;
  font-size: 16px;
  font-weight: 500;
  color: var(--font-color-main, #fff);
}

.verb-config-section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
}

.verb-config-section h6 {
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 500;
  color: var(--font-color-main, #fff);
}

.default-verb-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.2));
  border-radius: 4px;
  background: var(--background-color, rgba(255, 255, 255, 0.05));
  color: var(--font-color-main, #fff);
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
  background: var(--background-color, #424242);
  color: var(--font-color-main, #fff);
}

.select-helper {
  margin-top: 4px;
  margin-bottom: 0;
}

.collapsible-header.verb-header {
  padding-top: 8px;
  padding-bottom: 8px;
  align-items: center;
}

.expand-icon {
  transition: transform 0.3s ease;
}

/* Rotate chevron when expanded */
.verb-list-item.active .expand-icon {
  transform: rotate(90deg);
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
