/**
 * Shared logic for execution section components (Running, Scheduled, Completed).
 * Provides scriptsMap, collapsed state management, and verb parameter filtering.
 */

import {mapState} from 'vuex';
import {getScriptConfig, filterParametersByVerb} from '@/main-app/utils/executionFormatters';

export function createExecutionSectionMixin(storageKey) {
  return {
    data() {
      return {
        collapsed: this.loadCollapsedState()
      };
    },

    computed: {
      ...mapState('scripts', {
        scripts: 'scripts'
      }),

      /**
       * Create a map for efficient script description lookups.
       * Ensures reactivity when scripts change.
       */
      scriptsMap() {
        const map = {};
        if (this.scripts && this.scripts.length > 0) {
          this.scripts.forEach(s => {
            map[s.name] = s.description || '';
          });
        }
        return map;
      }
    },

    methods: {
      /**
       * Load collapsed state from localStorage.
       */
      loadCollapsedState() {
        try {
          return localStorage.getItem(storageKey) === 'true';
        } catch (e) {
          return false;
        }
      },

      /**
       * Save collapsed state to localStorage.
       */
      saveCollapsedState(collapsed) {
        try {
          localStorage.setItem(storageKey, collapsed ? 'true' : 'false');
        } catch (e) {
          // Ignore localStorage errors
        }
      },

      /**
       * Handle section toggle event.
       */
      handleToggle(collapsed) {
        this.collapsed = collapsed;
        this.saveCollapsedState(collapsed);
      },

      /**
       * Get script description from scriptsMap.
       */
      getScriptDesc(scriptName) {
        return this.scriptsMap[scriptName] || '';
      },

      /**
       * Get verb parameter name for a script (if verbs are configured).
       */
      getVerbParameterName(scriptName) {
        const scriptConfig = getScriptConfig(scriptName, this.scripts);
        return scriptConfig?.verbs?.parameterName || null;
      },

      /**
       * Filter execution parameters by verb configuration.
       */
      getFilteredParameters(execution) {
        const scriptConfig = getScriptConfig(execution.script, this.scripts);
        return filterParametersByVerb(execution.parameterValues, scriptConfig);
      }
    }
  };
}
