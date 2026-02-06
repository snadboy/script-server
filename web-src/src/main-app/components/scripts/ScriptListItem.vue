<template>
  <div class="script-list-item-container">
    <router-link :to="'/' + descriptor.hash"
                 class="collection-item waves-effect script-list-item"
                 :class="{
                   active: descriptor.active,
                   'parsing-failed': descriptor.parsingFailed,
                   'validation-warning': descriptor.validationWarning
                 }"
                 :title="getTitle()">
      <div v-if="projectName" class="script-list-item-content">
        <div class="project-name">{{ projectName }}</div>
        <div class="instance-name">{{ descriptor.name }}</div>
      </div>
      <template v-else>{{ descriptor.name }}</template>

      <div :class="descriptor.state" class="menu-item-state">
        <i class="material-icons check-icon">check</i>
        <i class="material-icons failed-icon">priority_high</i>
        <i class="material-icons validation-warning-icon" :title="descriptor.validationError">warning</i>
        <div class="preloader-wrapper active">
          <div class="spinner-layer">
            <div class="circle-clipper left">
              <div class="circle"></div>
            </div>
            <div class="gap-patch">
              <div class="circle"></div>
            </div>
            <div class="circle-clipper right">
              <div class="circle"></div>
            </div>
          </div>
        </div>
      </div>
    </router-link>

    <ScriptInlineActions
        v-if="descriptor.active"
        :script-name="descriptor.name"
        :parsing-failed="descriptor.parsingFailed"/>
  </div>
</template>

<script>
import '@/common/materializecss/imports/spinner'
import {forEachKeyValue} from '@/common/utils/common';
import {mapState} from 'vuex';
import {scriptNameToHash} from '../../utils/model_helper';
import ScriptInlineActions from './ScriptInlineActions';

export default {
  name: 'ScriptListItem',
  components: {
    ScriptInlineActions
  },
  props: {
    script: {
      type: Object,
      default: null
    }
  },
  computed: {
    descriptor() {
      const validation = this.script.validation || {};
      const hasValidationError = validation.valid === false;

      return {
        name: this.script.name,
        state: this.getState(this.script.name),
        active: this.selectedScript === this.script.name,
        hash: this.toHash(this.script.name),
        parsingFailed: this.script.parsing_failed,
        validationWarning: hasValidationError,
        validationError: hasValidationError ? validation.error : null
      }
    },
    projectName() {
      // If script has a project_id, look up the project name
      if (!this.script.project_id) {
        return null;
      }

      // Get projects from adminScripts store
      const projects = this.$store.state.adminScripts?.projects || [];
      const project = projects.find(p => p.id === this.script.project_id);
      return project ? project.name : this.script.project_id;
    },
    ...mapState('scripts', ['selectedScript'])
  },
  methods: {
    getTitle() {
      if (this.descriptor.parsingFailed) {
        return 'Failed to parse config file';
      }
      if (this.descriptor.validationWarning) {
        return this.descriptor.validationError || 'Script validation failed';
      }
      return '';
    },
    getState(scriptName) {
      let state = 'idle';

      if (this.script.parsing_failed) {
        return 'cannot-parse'
      }

      // Show validation warning state if there's a validation error
      const validation = this.script.validation || {};
      if (validation.valid === false) {
        return 'validation-warning'
      }

      forEachKeyValue(this.$store.state.executions.executors, function (id, executor) {
        if (executor.state.scriptName !== scriptName) {
          return;
        }

        state = executor.state.status;
      });

      return state;
    },
    toHash: scriptNameToHash
  }
}
</script>

<style scoped>
.scripts-list .collection-item {
  border: none;
  padding-right: 32px;
}

.scripts-list .collection-item.parsing-failed {
  color: var(--font-color-disabled);
}

.scripts-list .collection-item.validation-warning {
  /* Keep normal color but show warning icon */
}

.scripts-list .collection-item .menu-item-state {
  width: 24px;
  height: 24px;
  position: absolute;
  right: 16px;
  top: calc(50% - 12px);
  display: none;
}

.scripts-list .collection-item .menu-item-state > .check-icon {
  color: var(--primary-color);
  display: none;
  font-size: 24px;
}

.scripts-list .collection-item .menu-item-state > .failed-icon {
  color: #f44336;
  display: none;
  font-size: 24px;
}

.scripts-list .collection-item .menu-item-state > .validation-warning-icon {
  color: #ff9800;
  display: none;
  font-size: 24px;
}

.scripts-list .collection-item .menu-item-state > .preloader-wrapper {
  display: none;
  width: 100%;
  height: 100%;
}

.scripts-list .collection-item .menu-item-state.executing,
.scripts-list .collection-item .menu-item-state.finished,
.scripts-list .collection-item .menu-item-state.cannot-parse,
.scripts-list .collection-item .menu-item-state.validation-warning {
  display: inline;
}

.scripts-list .collection-item .menu-item-state > .check-icon,
.scripts-list .collection-item .menu-item-state > .preloader-wrapper,
.scripts-list .collection-item .menu-item-state > .failed-icon,
.scripts-list .collection-item .menu-item-state > .validation-warning-icon {
  display: none;
}

.scripts-list .collection-item .menu-item-state.executing > .preloader-wrapper {
  display: block;
}

.scripts-list .collection-item .menu-item-state.finished > .check-icon {
  display: block;
}

.scripts-list .collection-item .menu-item-state.cannot-parse > .failed-icon {
  display: block;
}

.scripts-list .collection-item .menu-item-state.validation-warning > .validation-warning-icon {
  display: block;
}

.scripts-list .collection-item .preloader-wrapper .spinner-layer {
  border-color: var(--primary-color);
}

.script-list-item-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
  line-height: 1.2;
}

.project-name {
  font-size: 0.75rem;
  color: var(--font-color-medium);
  font-weight: 500;
}

.instance-name {
  font-size: 0.9rem;
  color: var(--font-color-main);
}

.script-list-item.active .project-name {
  color: rgba(255, 255, 255, 0.8);
}

.script-list-item.active .instance-name {
  color: #ffffff;
}
</style>