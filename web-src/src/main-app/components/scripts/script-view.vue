<template>
  <div :id="id" class="script-view">
    <ScriptLoadingText v-if="loading && !scriptConfig" :loading="loading" :script="selectedScript"/>
    <p v-show="scriptDescription" class="script-description" v-html="formattedDescription"/>
    <ScriptParametersView ref="parametersView"/>
    <div v-if="hasErrors" v-show="!hideExecutionControls" class="validation-panel">
      <h6 class="header">Validation failed. Errors list:</h6>
      <ul class="validation-errors-list">
        <li v-for="error in shownErrors">{{ error }}</li>
      </ul>
    </div>
    <ScriptExecutionsPanel v-if="!hideExecutionControls && scriptConfig" class="executions-panel"/>
  </div>
</template>

<script>

import {forEachKeyValue, isEmptyObject, isEmptyString, isNull} from '@/common/utils/common';
import ScriptLoadingText from '@/main-app/components/scripts/ScriptLoadingText';
import ScriptExecutionsPanel from '@/main-app/components/scripts/ScriptExecutionsPanel';
import DOMPurify from 'dompurify';
import {marked} from 'marked';
import {mapActions, mapState} from 'vuex'
import {STATUS_DISCONNECTED, STATUS_ERROR, STATUS_EXECUTING, STATUS_FINISHED} from '../../store/scriptExecutor';
import ScriptParametersView from './script-parameters-view'

export default {
  data: function () {
    return {
      id: null,
      shownErrors: [],
      executionInProgress: false
    }
  },

  props: {
    hideExecutionControls: Boolean
  },

  mounted: function () {
    this.id = 'script-panel-' + this._uid;
  },

  components: {
    ScriptLoadingText,
    ScriptExecutionsPanel,
    ScriptParametersView
  },

  computed: {
    ...mapState('scriptConfig', {
      scriptDescription: state => state.scriptConfig ? state.scriptConfig.description : '',
      loading: 'loading',
      scriptConfig: 'scriptConfig'
    }),
    ...mapState('scriptSetup', {
      parameterErrors: 'errors'
    }),
    ...mapState('executions', {
      currentExecutor: 'currentExecutor'
    }),
    ...mapState('scripts', ['selectedScript', 'pendingAutoExecute']),

    hasErrors: function () {
      return !isNull(this.shownErrors) && (this.shownErrors.length > 0);
    },

    formattedDescription: function () {
      if (isEmptyString(this.scriptDescription)) {
        return '';
      }

      const descriptionHtml = DOMPurify.sanitize(marked.parse(this.scriptDescription, {gfm: true, breaks: true}));
      const paragraphRemoval = document.createElement('div');
      paragraphRemoval.innerHTML = descriptionHtml.trim();

      for (var i = 0; i < paragraphRemoval.childNodes.length; i++) {
        var child = paragraphRemoval.childNodes[i];
        if (child.tagName === 'P') {
          i += child.childNodes.length - 1;

          while (child.childNodes.length > 0) {
            paragraphRemoval.insertBefore(child.firstChild, child);
          }

          paragraphRemoval.removeChild(child);
        }
      }

      return paragraphRemoval.innerHTML;
    },

    enableExecuteButton() {
      if (this.hideExecutionControls) {
        return false;
      }

      if (this.loading) {
        return false;
      }

      if (isNull(this.currentExecutor)) {
        return true;
      }

      return this.currentExecutor.state.status === STATUS_FINISHED
          || this.currentExecutor.state.status === STATUS_DISCONNECTED
          || this.currentExecutor.state.status === STATUS_ERROR;
    },

    status() {
      return isNull(this.currentExecutor) ? null : this.currentExecutor.state.status;
    }
  },

  methods: {
    validatePreExecution: function () {
      console.log('[script-view] validatePreExecution called');
      this.shownErrors = [];

      const errors = this.parameterErrors;
      console.log('[script-view] parameterErrors:', errors);
      if (!isEmptyObject(errors)) {
        forEachKeyValue(errors, (paramName, error) => {
          this.shownErrors.push(paramName + ': ' + error);
        });
        console.log('[script-view] Validation failed:', this.shownErrors);
        return false;
      }

      console.log('[script-view] Validation passed');
      return true;
    },

    executeScript: function () {
      console.log('[script-view] executeScript called, executionInProgress:', this.executionInProgress);
      // Prevent double execution
      if (this.executionInProgress) {
        console.log('[script-view] Execution already in progress, skipping');
        return;
      }

      if (!this.validatePreExecution()) {
        return;
      }

      console.log('[script-view] Calling startExecution');
      this.executionInProgress = true;
      this.startExecution();

      // Reset flag after a short delay to allow for subsequent executions
      setTimeout(() => {
        this.executionInProgress = false;
      }, 1000);
    },

    ...mapActions('executions', {
      startExecution: 'startExecution'
    })
  },

  watch: {
    scriptConfig: {
      immediate: true,
      handler(newConfig) {
        this.shownErrors = []
        // Check for pending auto-execute when config loads (handles navigation case)
        if (newConfig && this.pendingAutoExecute && this.enableExecuteButton) {
          console.log('[script-view] scriptConfig loaded while pendingAutoExecute=true, triggering execute');
          this.$store.commit('scripts/SET_PENDING_AUTO_EXECUTE', false);
          this.$nextTick(() => {
            this.executeScript();
          });
        }
      }
    },

    status: {
      handler(newStatus) {
        if (newStatus === STATUS_FINISHED) {
          this.$store.dispatch('executions/' + this.currentExecutor.state.id + '/cleanup');
        }
      }
    },

    // Watch for auto-execute flag (from sidebar inline execute button)
    // This handles the case when script is already loaded
    pendingAutoExecute: {
      handler(newValue) {
        console.log('[script-view] pendingAutoExecute watcher fired:', newValue, 'scriptConfig:', !!this.scriptConfig, 'enableExecuteButton:', this.enableExecuteButton);
        if (newValue && this.scriptConfig && this.enableExecuteButton) {
          console.log('[script-view] All conditions met, calling executeScript');
          this.$store.commit('scripts/SET_PENDING_AUTO_EXECUTE', false);
          this.executeScript();
        }
      }
    }
  }
}
</script>

<style scoped>

.script-view {
  display: flex;
  flex-direction: column;
  flex: 1 1 0;

  /* (firefox)
      we have to specify min-size explicitly, because by default it's content size.
      It means, that when child content is larger than parent, it will grow out of parent
      See https://drafts.csswg.org/css-flexbox/#min-size-auto
      and https://bugzilla.mozilla.org/show_bug.cgi?id=1114904
  */
  min-height: 0;
}

.script-description,
.script-loading-text {
  margin: 0;
}

.validation-panel {
  overflow-y: auto;
  flex-shrink: 0;
  margin: 20px 0 8px;
}

.validation-panel .header {
  padding-left: 0;
}

.validation-errors-list {
  margin-left: 12px;
  margin-top: 8px;
}

.validation-errors-list li {
  color: #F44336;
}

.executions-panel {
  margin-top: 16px;
}

</style>
