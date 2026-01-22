<template>
  <div v-if="hasVerbs" class="verb-selector">
    <label class="verb-label">Command</label>
    <div class="verb-select-wrapper">
      <select
          v-model="selectedVerb"
          class="verb-select"
          @change="onVerbChange">
        <option v-for="verb in verbOptions" :key="verb.name" :value="verb.name">
          {{ verb.label }}
        </option>
      </select>
    </div>
    <p v-if="selectedVerbDescription" class="verb-description">{{ selectedVerbDescription }}</p>
  </div>
</template>

<script>
import {mapState, mapActions} from 'vuex';

export default {
  name: 'VerbSelector',

  computed: {
    ...mapState('scriptConfig', {
      scriptConfig: 'scriptConfig'
    }),
    ...mapState('scriptSetup', {
      parameterValues: 'parameterValues'
    }),

    verbsConfig() {
      return this.scriptConfig?.verbs || null;
    },

    hasVerbs() {
      return this.verbsConfig && this.verbsConfig.options && this.verbsConfig.options.length > 0;
    },

    verbOptions() {
      if (!this.verbsConfig) return [];
      return this.verbsConfig.options || [];
    },

    verbParameterName() {
      return this.verbsConfig?.parameterName || 'verb';
    },

    selectedVerb: {
      get() {
        const value = this.parameterValues[this.verbParameterName];
        if (value) return value;

        // Return default if no value set
        return this.verbsConfig?.default || (this.verbOptions[0]?.name || '');
      },
      set(value) {
        this.setParameterValue({parameterName: this.verbParameterName, value});
      }
    },

    selectedVerbDescription() {
      if (!this.selectedVerb || !this.verbOptions) return '';
      const verb = this.verbOptions.find(v => v.name === this.selectedVerb);
      return verb?.description || '';
    }
  },

  watch: {
    // Set default verb when config loads
    verbsConfig: {
      immediate: true,
      handler(config) {
        if (config && config.options && config.options.length > 0) {
          const currentValue = this.parameterValues[this.verbParameterName];
          if (!currentValue) {
            const defaultVerb = config.default || config.options[0].name;
            this.setParameterValue({parameterName: this.verbParameterName, value: defaultVerb});
          }
        }
      }
    }
  },

  methods: {
    ...mapActions('scriptSetup', ['setParameterValue']),

    onVerbChange() {
      this.$emit('verb-changed', this.selectedVerb);
    }
  }
};
</script>

<style scoped>
.verb-selector {
  margin-bottom: 16px;
  padding: 12px;
  background-color: var(--background-color-high-emphasis);
  border-radius: var(--radius-sm);
}

.verb-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--font-color-medium);
  display: block;
  margin-bottom: 8px;
}

.verb-select-wrapper {
  position: relative;
}

.verb-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--separator-color);
  border-radius: var(--radius-sm);
  background-color: var(--background-color-level-4dp);
  color: var(--font-color-main);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;

  /* Override Materialize CSS that hides native selects */
  opacity: 1 !important;
  appearance: menulist;
  -webkit-appearance: menulist;
  -moz-appearance: menulist;
  height: auto;
}

.verb-select:hover {
  border-color: var(--primary-color);
}

.verb-select:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(38, 166, 154, 0.2);
  outline: none;
}

.verb-description {
  margin-top: 8px;
  margin-bottom: 0;
  font-size: 12px;
  color: var(--font-color-medium);
  font-style: italic;
}
</style>
