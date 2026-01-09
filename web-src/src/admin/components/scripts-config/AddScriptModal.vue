<template>
  <div v-if="visible" class="modal-overlay">
    <div class="modal-content add-script-modal card">
      <div class="modal-header">
        <span class="modal-title">Add New Script</span>
      </div>

      <div class="modal-tabs">
        <button
          v-for="(tab, index) in tabs"
          :key="tab.id"
          class="tab-btn"
          :class="{ active: activeTab === index }"
          @click="activeTab = index"
        >
          <span class="tab-number">{{ index + 1 }}</span>
          <span class="tab-label">{{ tab.label }}</span>
        </button>
      </div>

      <div class="modal-body">
        <div v-if="loadingError" class="error">{{ loadingError }}</div>
        <template v-else-if="scriptConfig">
          <!-- Tab 1: Details -->
          <div v-show="activeTab === 0" class="tab-panel">
            <div class="row">
              <TextField v-model="scriptConfig.name" :config="nameField" class="col s6"/>
              <TextField v-model="scriptConfig.group" :config="groupField" class="col s5 offset-s1"/>
            </div>
            <div class="row">
              <ScriptPathField
                :config-name="scriptConfig.name"
                :new-config="true"
                :original-path="scriptConfig.script_path"
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

          <!-- Tab 2: Access -->
          <div v-show="activeTab === 1" class="tab-panel">
            <div class="row">
              <div v-if="allowAllUsers" class="input-field col s9">
                <input id="allowed_users_disabled" disabled type="text" value="All users">
                <label class="active" for="allowed_users_disabled">Allowed users</label>
              </div>
              <ChipsList v-else v-model="allowedUsers" class="col s9" title="Allowed users"/>
              <CheckBox v-model="allowAllUsers" :config="allowAllField" class="col s2 offset-s1 checkbox-field"/>
            </div>
            <div class="row">
              <div v-if="allowAllAdmins" class="input-field col s9">
                <input id="admin_users_disabled" disabled type="text" value="Any admin">
                <label class="active" for="admin_users_disabled">Admin users</label>
              </div>
              <ChipsList v-else v-model="adminUsers" class="col s9" title="Admin users"/>
              <CheckBox v-model="allowAllAdmins" :config="allowAllAdminsField" class="col s2 offset-s1 checkbox-field"/>
            </div>
            <div class="row">
              <CheckBox v-model="globalInstances" :config="globalInstancesField" class="col s6 checkbox-field"/>
            </div>
          </div>

          <!-- Tab 3: Scheduling -->
          <div v-show="activeTab === 2" class="tab-panel">
            <div class="row">
              <div class="col s12 scheduling-description">
                This section allows users to schedule scripts to be executed in the future.
              </div>
            </div>
            <div class="row">
              <CheckBox v-model="schedulingEnabled" :config="schedulingEnabledField" class="col s4 checkbox-field"/>
              <CheckBox
                v-model="schedulingAutoCleanup"
                :config="schedulingAutoCleanupField"
                :disabled="!schedulingEnabled"
                class="col s4 checkbox-field"
              />
            </div>
          </div>

          <!-- Tab 4: Parameters -->
          <div v-show="activeTab === 3" class="tab-panel">
            <ScriptParamList :parameters="scriptConfig.parameters"/>
          </div>
        </template>
      </div>

      <div class="modal-footer">
        <button class="btn-flat waves-effect" @click="handleCancel">Cancel</button>
        <PromisableButton :click="save" :enabled="isFormValid" title="Add"/>
      </div>
    </div>
  </div>
</template>

<script>
import {NEW_SCRIPT} from '@/admin/store/script-config-module';
import PromisableButton from '@/common/components/PromisableButton';
import ScriptParamList from './ScriptParamList';
import ScriptPathField from '@/admin/components/scripts-config/script-edit/ScriptField';
import CheckBox from '@/common/components/checkbox';
import ChipsList from '@/common/components/ChipsList';
import Combobox from '@/common/components/combobox';
import TextArea from '@/common/components/TextArea';
import TextField from '@/common/components/textfield';
import {isEmptyArray, isNull} from '@/common/utils/common';
import get from 'lodash/get';
import {
  allowAllField,
  allowAllAdminsField,
  descriptionField,
  globalInstancesField,
  groupField,
  includeScriptField,
  nameField,
  outputFormatField,
  requiresTerminalField,
  schedulingAutoCleanupField,
  schedulingEnabledField,
  workDirField
} from './script-fields';

export default {
  name: 'AddScriptModal',
  components: {
    PromisableButton,
    ScriptParamList,
    ScriptPathField,
    CheckBox,
    ChipsList,
    Combobox,
    TextArea,
    TextField
  },

  props: {
    visible: {
      type: Boolean,
      default: false
    }
  },

  data() {
    return {
      NEW_SCRIPT,
      activeTab: 0,
      boundFixOverlayDimensions: null,
      originalParent: null,
      tabs: [
        { id: 'details', label: 'Details' },
        { id: 'access', label: 'Access' },
        { id: 'scheduling', label: 'Scheduling' },
        { id: 'parameters', label: 'Parameters' }
      ],
      // Field configs
      nameField,
      groupField,
      workDirField,
      descriptionField,
      outputFormatField,
      requiresTerminalField,
      includeScriptField,
      allowAllField,
      allowAllAdminsField,
      globalInstancesField,
      schedulingEnabledField,
      schedulingAutoCleanupField,
      // Access state
      allowedUsers: [],
      allowAllUsers: true,
      adminUsers: [],
      allowAllAdmins: true,
      globalInstances: false,
      // Scheduling state
      schedulingEnabled: true,
      schedulingAutoCleanup: false
    };
  },

  computed: {
    storeModule() {
      return this.$store.state.adminScriptConfig ? 'adminScriptConfig' : 'scriptConfig';
    },
    scriptConfig() {
      return this.$store.state[this.storeModule].scriptConfig;
    },
    loadingError() {
      return this.$store.state[this.storeModule].error;
    },
    isDirty() {
      return this.$store.state[this.storeModule].isDirty;
    },
    isFormValid() {
      if (!this.scriptConfig) return false;
      const hasName = this.scriptConfig.name && this.scriptConfig.name.trim().length > 0;
      const hasScript = this.scriptConfig.script_path ||
        (this.scriptConfig.script && (this.scriptConfig.script.path || this.scriptConfig.script.command));
      return hasName && hasScript;
    }
  },

  watch: {
    visible(newVal) {
      if (newVal) {
        document.body.style.overflow = 'hidden';
        this.activeTab = 0;
        this.$store.dispatch(`${this.storeModule}/init`, NEW_SCRIPT);
        // Move modal to body to avoid transform containment issues from parent elements
        this.$nextTick(() => {
          this.originalParent = this.$el.parentElement;
          document.body.appendChild(this.$el);
          this.boundFixOverlayDimensions = this.fixOverlayDimensions.bind(this);
          this.boundFixOverlayDimensions();
          window.addEventListener('resize', this.boundFixOverlayDimensions);
        });
      } else {
        document.body.style.overflow = '';
        if (this.boundFixOverlayDimensions) {
          window.removeEventListener('resize', this.boundFixOverlayDimensions);
        }
        // Move modal back to original parent
        if (this.originalParent && this.$el.parentElement === document.body) {
          this.originalParent.appendChild(this.$el);
        }
      }
    },

    scriptConfig: {
      deep: true,
      immediate: true,
      handler(config) {
        if (config) {
          // Sync access fields from config
          this.syncAccessFromConfig(config);
          // Sync scheduling from config
          this.schedulingEnabled = config.scheduling?.enabled !== false;
          this.schedulingAutoCleanup = config.scheduling?.auto_cleanup || false;
        }
      }
    },

    // Watch local state and sync back to config
    allowAllUsers() {
      this.updateAllowedUsersInConfig();
    },
    allowedUsers() {
      this.updateAllowedUsersInConfig();
    },
    allowAllAdmins() {
      this.updateAdminUsersInConfig();
    },
    adminUsers() {
      this.updateAdminUsersInConfig();
    },
    globalInstances() {
      if (this.scriptConfig) {
        if (this.globalInstances) {
          this.$set(this.scriptConfig, 'access', { shared_access: { type: 'ALL_USERS' } });
        } else {
          this.$delete(this.scriptConfig, 'access');
        }
      }
    },
    schedulingEnabled() {
      this.updateSchedulingInConfig();
    },
    schedulingAutoCleanup() {
      this.updateSchedulingInConfig();
    }
  },

  methods: {
    fixOverlayDimensions() {
      // Fix for display scaling causing 100vh to be larger than viewport
      const overlay = this.$el;
      if (overlay && overlay.classList.contains('modal-overlay')) {
        overlay.style.height = window.innerHeight + 'px';
        overlay.style.width = window.innerWidth + 'px';
      }
    },

    save() {
      return this.$store.dispatch(`${this.storeModule}/save`)
        .then(() => {
          const scriptName = this.scriptConfig.name;
          this.$emit('saved', scriptName);
        })
        .catch((e) => {
          if (e.userMessage) {
            M.toast({ html: e.userMessage, classes: 'red' });
          } else {
            M.toast({ html: 'Failed to save script', classes: 'red' });
          }
          throw e;
        });
    },

    handleCancel() {
      if (this.isDirty) {
        const confirmed = window.confirm('You have unsaved changes. Discard changes and close?');
        if (!confirmed) {
          return;
        }
      }
      this.$store.commit(`${this.storeModule}/SET_DIRTY`, false);
      this.$emit('close');
    },

    updateScript(newScriptObject) {
      if (this.scriptConfig) {
        this.scriptConfig.script = newScriptObject;
      }
    },

    syncAccessFromConfig(config) {
      // Allowed users
      let users = get(config, 'allowed_users');
      if (isNull(users)) {
        users = [];
      }
      this.allowedUsers = users.filter(u => u !== '*');
      this.allowAllUsers = isNull(config.allowed_users) || users.includes('*');

      // Admin users
      let admins = get(config, 'admin_users');
      if (isNull(admins)) {
        admins = [];
      }
      this.adminUsers = admins.filter(u => u !== '*');
      this.allowAllAdmins = isNull(config.admin_users) || admins.includes('*');

      // Global instances
      this.globalInstances = config?.access?.shared_access?.type === 'ALL_USERS';
    },

    updateAllowedUsersInConfig() {
      if (!this.scriptConfig) return;

      if (isEmptyArray(this.allowedUsers) && this.allowAllUsers) {
        this.$delete(this.scriptConfig, 'allowed_users');
      } else if (this.allowAllUsers) {
        if (!this.allowedUsers.includes('*')) {
          this.scriptConfig.allowed_users = [...this.allowedUsers, '*'];
        }
      } else {
        this.scriptConfig.allowed_users = this.allowedUsers;
      }
    },

    updateAdminUsersInConfig() {
      if (!this.scriptConfig) return;

      if (isEmptyArray(this.adminUsers) && this.allowAllAdmins) {
        this.$delete(this.scriptConfig, 'admin_users');
      } else if (this.allowAllAdmins) {
        if (!this.adminUsers.includes('*')) {
          this.scriptConfig.admin_users = [...this.adminUsers, '*'];
        }
      } else {
        this.scriptConfig.admin_users = this.adminUsers;
      }
    },

    updateSchedulingInConfig() {
      if (!this.scriptConfig) return;

      if (this.schedulingEnabled) {
        const schedulingConf = { enabled: true };
        if (this.schedulingAutoCleanup) {
          schedulingConf.auto_cleanup = true;
        }
        this.$set(this.scriptConfig, 'scheduling', schedulingConf);
      } else {
        this.$delete(this.scriptConfig, 'scheduling');
      }
    }
  }
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.add-script-modal {
  width: 85%;
  max-width: 1000px;
  height: 85vh;
  max-height: 700px;
  display: flex;
  flex-direction: column;
  border-radius: var(--radius-md);
  margin: 0 !important;
  position: relative;
}

.modal-header {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid var(--separator-color);
  flex-shrink: 0;
}

.modal-title {
  font-size: 1.4em;
  font-weight: 500;
  color: var(--font-color-main);
}

.modal-tabs {
  display: flex;
  border-bottom: 1px solid var(--separator-color);
  flex-shrink: 0;
  background: var(--background-color-level-4dp);
}

.tab-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  border: none;
  background: transparent;
  color: var(--font-color-medium);
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: inherit;
  font-size: 14px;
  position: relative;
}

.tab-btn:hover {
  background: var(--hover-color);
  color: var(--font-color-main);
}

.tab-btn.active {
  color: var(--primary-color);
  background: var(--background-color);
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--primary-color);
}

.tab-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--font-color-medium);
  color: var(--background-color);
  font-size: 12px;
  font-weight: 600;
}

.tab-btn.active .tab-number {
  background: var(--primary-color);
}

.tab-label {
  font-weight: 500;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.tab-panel {
  min-height: 100%;
}

.tab-panel .row {
  margin-bottom: 0;
  margin-left: 0;
  margin-right: 0;
}

.col.checkbox-field {
  margin-top: 2.1em;
}

.scheduling-description {
  color: var(--font-color-medium);
  margin-bottom: 16px;
  font-size: 14px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--separator-color);
  flex-shrink: 0;
  background: var(--background-color-level-16dp);
}

.modal-footer >>> .promisable-button[disabled] {
  color: var(--font-color-disabled) !important;
  pointer-events: none;
  cursor: default;
}

.error {
  color: var(--error-color);
  padding: 16px;
  text-align: center;
}

@media screen and (max-width: 768px) {
  .add-script-modal {
    width: 95%;
    height: 95vh;
    max-height: none;
  }

  .modal-body {
    padding: 16px;
  }

  .tab-label {
    display: none;
  }

  .tab-btn {
    padding: 12px 8px;
  }
}
</style>
