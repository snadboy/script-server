<template>
  <div class="advanced-tab">
    <!-- Access Control Section -->
    <div class="section">
      <h6 class="section-title">Access Control</h6>
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

    <!-- Scheduling Section -->
    <div class="section">
      <h6 class="section-title">Scheduling</h6>
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

    <!-- Verbs Section -->
    <div class="section">
      <h6 class="section-title">Verbs / Subcommands</h6>
      <VerbConfigEditor
        v-model="verbsConfig"
        :available-parameters="scriptConfig.parameters || []"
        :shared-parameters.sync="sharedParameters"
      />
    </div>
  </div>
</template>

<script>
import CheckBox from '@/common/components/checkbox';
import ChipsList from '@/common/components/ChipsList';
import VerbConfigEditor from '../VerbConfigEditor';
import {isEmptyArray, isNull} from '@/common/utils/common';
import get from 'lodash/get';
import {
  allowAllField,
  allowAllAdminsField,
  globalInstancesField,
  schedulingAutoCleanupField,
  schedulingEnabledField
} from '../script-fields';

export default {
  name: 'AdvancedTab',

  components: {
    CheckBox,
    ChipsList,
    VerbConfigEditor
  },

  data() {
    return {
      // Field configs
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
      schedulingAutoCleanup: false,
      // Verbs state
      verbsConfig: null,
      sharedParameters: []
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

  watch: {
    scriptConfig: {
      deep: true,
      immediate: true,
      handler(config) {
        if (config) {
          this.syncAccessFromConfig(config);
          this.syncSchedulingFromConfig(config);
          this.syncVerbsFromConfig(config);
        }
      }
    },

    allowAllUsers(newVal) {
      this.syncAccessToConfig();
    },
    allowedUsers: {
      deep: true,
      handler() {
        this.syncAccessToConfig();
      }
    },
    allowAllAdmins(newVal) {
      this.syncAccessToConfig();
    },
    adminUsers: {
      deep: true,
      handler() {
        this.syncAccessToConfig();
      }
    },
    globalInstances(newVal) {
      this.$store.dispatch(`${this.storeModule}/updateConfig`, {
        ...this.scriptConfig,
        include: {
          ...this.scriptConfig.include,
          global_instances: newVal || undefined
        }
      });
    },

    schedulingEnabled(newVal) {
      this.syncSchedulingToConfig();
    },
    schedulingAutoCleanup(newVal) {
      this.syncSchedulingToConfig();
    },

    verbsConfig: {
      deep: true,
      handler(newVal) {
        this.$store.dispatch(`${this.storeModule}/updateConfig`, {
          ...this.scriptConfig,
          verbs: newVal || undefined
        });
      }
    },
    sharedParameters: {
      deep: true,
      handler(newVal) {
        this.$store.dispatch(`${this.storeModule}/updateConfig`, {
          ...this.scriptConfig,
          shared_parameters: newVal && newVal.length > 0 ? newVal : undefined
        });
      }
    }
  },

  methods: {
    syncAccessFromConfig(config) {
      const allowed_users = get(config, 'allowed_users');
      if (isNull(allowed_users) || (Array.isArray(allowed_users) && allowed_users.length === 0)) {
        this.allowAllUsers = true;
        this.allowedUsers = [];
      } else {
        this.allowAllUsers = false;
        this.allowedUsers = Array.isArray(allowed_users) ? [...allowed_users] : [];
      }

      const admin_users = get(config, 'admin_users');
      if (isNull(admin_users) || (Array.isArray(admin_users) && admin_users.length === 0)) {
        this.allowAllAdmins = true;
        this.adminUsers = [];
      } else {
        this.allowAllAdmins = false;
        this.adminUsers = Array.isArray(admin_users) ? [...admin_users] : [];
      }

      this.globalInstances = get(config, 'include.global_instances', false);
    },

    syncSchedulingFromConfig(config) {
      this.schedulingEnabled = !get(config, 'scheduling.disabled', false);
      this.schedulingAutoCleanup = get(config, 'scheduling.auto_cleanup_on_stop', false);
    },

    syncVerbsFromConfig(config) {
      this.verbsConfig = get(config, 'verbs', null);
      this.sharedParameters = get(config, 'shared_parameters', []);
    },

    syncAccessToConfig() {
      const allowed_users = this.allowAllUsers ? undefined :
        (this.allowedUsers.length > 0 ? this.allowedUsers : undefined);

      const admin_users = this.allowAllAdmins ? undefined :
        (this.adminUsers.length > 0 ? this.adminUsers : undefined);

      this.$store.dispatch(`${this.storeModule}/updateConfig`, {
        ...this.scriptConfig,
        allowed_users,
        admin_users
      });
    },

    syncSchedulingToConfig() {
      this.$store.dispatch(`${this.storeModule}/updateConfig`, {
        ...this.scriptConfig,
        scheduling: {
          disabled: !this.schedulingEnabled,
          auto_cleanup_on_stop: this.schedulingAutoCleanup
        }
      });
    }
  }
}
</script>

<style scoped>
.advanced-tab {
  padding: 1.5rem;
}

.section {
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid var(--border-color, #e0e0e0);
}

.section:last-child {
  border-bottom: none;
}

.section-title {
  margin: 0 0 1rem 0;
  font-size: 1.1rem;
  font-weight: 500;
  color: var(--primary-color, #1976d2);
}

.row {
  margin-bottom: 1rem;
}

.checkbox-field {
  padding-top: 2rem;
}

.scheduling-description {
  color: var(--text-color-secondary, #666);
  font-size: 0.95rem;
  margin-bottom: 0.5rem;
}
</style>
