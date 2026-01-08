<template>
  <div class="script-config">
    <div ref="scriptConfigContent" class="script-config-content">
      <div class="container">
        <div v-if="loadingError" class="error">{{ loadingError }}</div>
        <ScriptConfigForm v-else-if="scriptConfig" v-model="scriptConfig" :original-name="scriptName"/>
        <div v-if="!loadingError && scriptConfig">
          <h5>Parameters</h5>
          <ScriptParamList :parameters="scriptConfig.parameters"/>
        </div>
      </div>
    </div>
    <footer class="page-footer primary-color-dark">
      <div class="footer-left">
        <PromisableButton v-if="scriptName !== NEW_SCRIPT"
                          :click="deleteScript"
                          class="delete-button"
                          icon-text="delete"
                          title="Delete"/>
      </div>

      <PromisableButton :click="save" title="Save"/>

      <div class="footer-right"/>
    </footer>
  </div>
</template>

<script>
import {NEW_SCRIPT} from '@/admin/store/script-config-module';
import PromisableButton from '@/common/components/PromisableButton';
import {mapActions, mapState} from 'vuex';
import ParameterConfigForm from './ParameterConfigForm';
import ScriptConfigForm from './ScriptConfigForm';
import ScriptParamList from './ScriptParamList';

export default {
  name: 'ScriptConfig',
  components: {PromisableButton, ScriptParamList, ParameterConfigForm, ScriptConfigForm},
  props: {
    scriptName: {
      type: String
    }
  },

  data() {
    return {
      allowNavigation: false
    }
  },

  methods: {
    ...mapActions('adminScriptConfig', {
      initConfig: 'init',
      saveConfig: 'save',
      deleteConfig: 'deleteScript'
    }),

    init(scriptName) {
      return this.initConfig(scriptName);
    },

    save() {
      return this.saveConfig().then((result) => {
        this.allowNavigation = true;
        if (result && result.navigate) {
          this.$router.push(result.path);
        }
      });
    },

    deleteScript() {
      const confirmed = window.confirm('Are you sure you want to delete this script?');
      if (!confirmed) {
        return Promise.reject({ userMessage: 'Cancelled' });
      }
      return this.deleteConfig().then((result) => {
        this.allowNavigation = true;
        if (result && result.navigate) {
          this.$router.push(result.path);
        }
      });
    },

    checkDirty() {
      const original = this.$store.state.adminScriptConfig.originalConfigJson;
      // If original not yet captured, not dirty
      if (!original) {
        return false;
      }
      const current = JSON.stringify(this.scriptConfig);
      const isDirty = original !== current;
      this.$store.commit('adminScriptConfig/SET_DIRTY', isDirty);
      return isDirty;
    },

    captureOriginal() {
      // Delay capture to allow form to fully initialize
      setTimeout(() => {
        if (this.scriptConfig) {
          this.$store.commit('adminScriptConfig/CAPTURE_ORIGINAL');
        }
      }, 100);
    },

    handleBeforeUnload(e) {
      if (this.checkDirty()) {
        e.preventDefault();
        e.returnValue = '';
        return '';
      }
    }
  },

  computed: {
    ...mapState('adminScriptConfig', {
      scriptConfig: 'scriptConfig',
      loadingError: 'error',
      isDirty: 'isDirty'
    }),
    NEW_SCRIPT() {
      return NEW_SCRIPT;
    }
  },

  watch: {
    scriptName: {
      immediate: true,
      handler(scriptName) {
        this.allowNavigation = false;
        this.init(scriptName);
      }
    },
    scriptConfig: {
      deep: true,
      handler(newVal, oldVal) {
        if (this.scriptConfig) {
          // If config just loaded (oldVal was null), capture original after form initializes
          if (!oldVal && newVal) {
            this.captureOriginal();
          } else {
            this.checkDirty();
          }
        }
      }
    }
  },

  mounted() {
    window.addEventListener('beforeunload', this.handleBeforeUnload);
  },

  beforeDestroy() {
    window.removeEventListener('beforeunload', this.handleBeforeUnload);
  },

  beforeRouteLeave(to, from, next) {
    if (this.allowNavigation) {
      next();
      return;
    }

    if (this.checkDirty()) {
      const confirmed = window.confirm('You have unsaved changes. Discard changes and leave?');
      if (confirmed) {
        this.$store.commit('adminScriptConfig/SET_DIRTY', false);
        next();
      } else {
        next(false);
      }
    } else {
      next();
    }
  }
}
</script>

<style scoped>
.script-config {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.script-config >>> h5 {
  margin-left: 0.75rem;
  margin-top: 0.5rem;
  margin-bottom: 2rem;
}

.script-config .script-config-content {
  padding-top: 1.5em;
  flex: 1 1 0;
  min-height: 0;
  overflow-y: auto;
}

.script-config .script-config-content .container {
  height: 100%;
}

footer.page-footer {
  padding-top: 0;

  flex: 0 0 0;

  display: flex;
}

.script-config >>> footer.page-footer a.btn-flat {
  height: 48px;
  line-height: 48px;
  width: 136px;
  text-align: center;
  font-size: 16px;
}

.script-config .footer-left,
.script-config .footer-right {
  flex: 1 1 0;
}

.script-config >>> footer.page-footer .preloader-wrapper {
  width: 30px;
  height: 30px;
}

.script-config >>> footer.page-footer .spinner-layer {
  border: var(--font-on-primary-color-dark-main);
}

.script-config >>> footer.page-footer .btn-flat i {
  font-size: 24px;
}

</style>