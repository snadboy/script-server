<template>
  <div v-if="visible" class="modal-overlay" @click.self="close">
    <div class="settings-modal">
      <div class="modal-header">
        <h3>Instance Settings: {{ scriptName }}</h3>
        <button class="btn-close" @click="close">×</button>
      </div>

      <div class="modal-tabs">
        <button
          :class="['tab-btn', { active: activeTab === 'defaults' }]"
          @click="activeTab = 'defaults'"
        >
          Defaults
        </button>
        <button
          :class="['tab-btn', { active: activeTab === 'access' }]"
          @click="activeTab = 'access'"
        >
          Access
        </button>
        <button
          :class="['tab-btn', { active: activeTab === 'scheduling' }]"
          @click="activeTab = 'scheduling'"
        >
          Scheduling
        </button>
      </div>

      <div class="modal-body">
        <div v-if="error" class="error-message">{{ error }}</div>
        <div v-if="loading" class="loading">Loading...</div>

        <template v-else-if="config">
          <!-- Defaults Tab -->
          <div v-if="activeTab === 'defaults'" class="tab-content">
            <p class="tab-description">
              Set default values for this instance. These will be pre-filled when executing or scheduling.
            </p>

            <!-- Verb Selection -->
            <div v-if="availableVerbs.length > 0" class="form-group">
              <label>Default Verb</label>
              <select v-model="defaultVerb" class="form-select">
                <option value="">None (user selects)</option>
                <option v-for="verb in availableVerbs" :key="verb.name" :value="verb.name">
                  {{ verb.name }}
                </option>
              </select>
              <div class="form-help">Which command/verb to run by default</div>
            </div>

            <!-- Connection Selection -->
            <div v-if="availableConnections.length > 0" class="form-group">
              <label>Default Connections</label>
              <div class="connections-list">
                <label v-for="conn in availableConnections" :key="conn.id" class="checkbox-label">
                  <input
                    type="checkbox"
                    :value="conn.id"
                    v-model="defaultConnections"
                  />
                  <i class="material-icons">{{ getConnectionIcon(conn.type) }}</i>
                  <span>{{ conn.name }}</span>
                  <span class="connection-type">({{ getConnectionTypeName(conn.type) }})</span>
                </label>
              </div>
              <div class="form-help">Pre-select these connections for execution</div>
            </div>

            <!-- Parameter Defaults -->
            <div v-if="availableParameters.length > 0" class="form-group">
              <label>Parameter Defaults</label>
              <div class="parameters-list">
                <div v-for="param in availableParameters" :key="param.name" class="parameter-row">
                  <label class="param-label">{{ param.name }}</label>
                  <input
                    v-model="defaultParameters[param.name]"
                    :type="param.type === 'int' ? 'number' : 'text'"
                    :placeholder="param.default || 'No default'"
                    class="param-input"
                  />
                </div>
              </div>
              <div class="form-help">Set default values (leave empty to use project defaults)</div>
            </div>

            <div v-if="availableVerbs.length === 0 && availableConnections.length === 0 && availableParameters.length === 0" class="empty-state">
              No defaults to configure. This script has no verbs, connections, or parameters.
            </div>
          </div>

          <!-- Access Tab -->
          <div v-if="activeTab === 'access'" class="tab-content">
            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="allowAllUsers" />
                <span>Allow all users</span>
              </label>
            </div>

            <div v-if="!allowAllUsers" class="form-group">
              <label>Allowed Users (comma-separated)</label>
              <input
                v-model="allowedUsersInput"
                type="text"
                placeholder="user1, user2, user3"
                class="form-input"
              />
            </div>

            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="allowAllAdmins" />
                <span>Allow any admin</span>
              </label>
            </div>

            <div v-if="!allowAllAdmins" class="form-group">
              <label>Admin Users (comma-separated)</label>
              <input
                v-model="adminUsersInput"
                type="text"
                placeholder="admin1, admin2"
                class="form-input"
              />
            </div>
          </div>

          <!-- Scheduling Tab -->
          <div v-if="activeTab === 'scheduling'" class="tab-content">
            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="schedulingEnabled" />
                <span>Enable scheduling</span>
              </label>
            </div>

            <div v-if="schedulingEnabled" class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="schedulingAutoCleanup" />
                <span>Auto-cleanup one-time schedules</span>
              </label>
            </div>
          </div>
        </template>
      </div>

      <div class="modal-footer">
        <button class="btn" @click="close">Cancel</button>
        <button class="btn btn-primary" @click="save" :disabled="saving">
          {{ saving ? 'Saving...' : 'Save Settings' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import {axiosInstance} from '@/common/utils/axios_utils';

export default {
  name: 'InstanceSettingsModal',

  props: {
    visible: {
      type: Boolean,
      default: false
    },
    scriptName: {
      type: String,
      required: true
    }
  },

  data() {
    return {
      activeTab: 'defaults',
      loading: false,
      saving: false,
      error: null,
      config: null,
      // Defaults
      defaultVerb: '',
      defaultConnections: [],
      defaultParameters: {},
      availableVerbs: [],
      availableParameters: [],
      availableConnections: [],
      connectionTypes: [],
      // Access
      allowAllUsers: true,
      allowedUsersInput: '',
      allowAllAdmins: true,
      adminUsersInput: '',
      // Scheduling
      schedulingEnabled: true,
      schedulingAutoCleanup: false
    };
  },

  watch: {
    visible(newVal) {
      if (newVal) {
        this.loadSettings();
      }
    }
  },

  methods: {
    async loadSettings() {
      this.loading = true;
      this.error = null;

      try {
        // Load script config
        const configResponse = await axiosInstance.get('/admin/scripts/' + this.scriptName);
        this.config = configResponse.data;

        // Load available verbs from project
        // TODO: Get project ID from config and fetch project verbs
        this.availableVerbs = this.config.verbs?.options || [];

        // Load available parameters from project
        this.availableParameters = this.config.parameters || [];

        // Load available connections
        const connectionsResponse = await axiosInstance.get('/admin/connections');
        const allConnections = connectionsResponse.data.connections || [];

        // Filter connections by supported types
        const supportedTypes = this.config.supportedConnections || [];
        this.availableConnections = supportedTypes.length > 0
          ? allConnections.filter(conn => supportedTypes.includes(conn.type))
          : allConnections;

        // Load connection types
        const typesResponse = await axiosInstance.get('/admin/connections/types');
        this.connectionTypes = typesResponse.data.types || [];

        // Load existing settings from config
        this.defaultVerb = this.config.defaultVerb || '';
        this.defaultConnections = this.config.defaultConnections || [];
        this.defaultParameters = { ...(this.config.defaultParameters || {}) };

        // Access settings
        this.allowAllUsers = this.config.allowed_users === '*';
        this.allowedUsersInput = Array.isArray(this.config.allowed_users)
          ? this.config.allowed_users.join(', ')
          : '';
        this.allowAllAdmins = !this.config.admin_users || this.config.admin_users.length === 0;
        this.adminUsersInput = Array.isArray(this.config.admin_users)
          ? this.config.admin_users.join(', ')
          : '';

        // Scheduling settings
        this.schedulingEnabled = this.config.scheduling_enabled !== false;
        this.schedulingAutoCleanup = this.config.scheduling_auto_cleanup === true;

      } catch (err) {
        this.error = 'Failed to load settings: ' + (err.message || 'Unknown error');
      } finally {
        this.loading = false;
      }
    },

    async save() {
      this.saving = true;
      this.error = null;

      try {
        // Parse user lists
        const allowedUsers = this.allowAllUsers ? '*' :
          this.allowedUsersInput.split(',').map(u => u.trim()).filter(u => u);
        const adminUsers = this.allowAllAdmins ? [] :
          this.adminUsersInput.split(',').map(u => u.trim()).filter(u => u);

        // Prepare updated config
        const updates = {
          defaultVerb: this.defaultVerb || null,
          defaultConnections: this.defaultConnections,
          defaultParameters: this.defaultParameters,
          allowed_users: allowedUsers,
          admin_users: adminUsers,
          scheduling_enabled: this.schedulingEnabled,
          scheduling_auto_cleanup: this.schedulingAutoCleanup
        };

        await axiosInstance.put('/admin/scripts/' + this.scriptName, updates);

        this.$emit('saved');
        this.close();
      } catch (err) {
        this.error = 'Failed to save settings: ' + (err.message || 'Unknown error');
      } finally {
        this.saving = false;
      }
    },

    getConnectionIcon(type) {
      const icons = {
        'google': 'mail',
        'plex': 'play_circle',
        'sonarr': 'tv',
        'radarr': 'movie',
        'home-assistant': 'home',
        'generic': 'link'
      };
      return icons[type] || 'link';
    },

    getConnectionTypeName(type) {
      const typeObj = this.connectionTypes.find(t => t.type_id === type);
      return typeObj ? typeObj.display_name : type;
    },

    close() {
      this.$emit('close');
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
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.settings-modal {
  background: #1e1e1e;
  border-radius: 8px;
  width: 90%;
  max-width: 700px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #333;
}

.modal-header h3 {
  margin: 0;
  font-size: 16px;
  color: #e0e0e0;
}

.btn-close {
  background: none;
  border: none;
  font-size: 28px;
  color: #999;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.btn-close:hover {
  color: #e0e0e0;
}

.modal-tabs {
  display: flex;
  border-bottom: 1px solid #333;
  background: #1a1a1a;
}

.tab-btn {
  flex: 1;
  padding: 12px 16px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: #999;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.tab-btn:hover {
  background: #222;
  color: #e0e0e0;
}

.tab-btn.active {
  color: #5dade2;
  border-bottom-color: #5dade2;
  background: #222;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.tab-content {
  animation: fadeIn 0.2s;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.tab-description {
  color: #999;
  font-size: 13px;
  margin: 0 0 20px 0;
}

.error-message {
  background: #3d1f1f;
  color: #ff6b6b;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 16px;
}

.loading {
  text-align: center;
  color: #999;
  padding: 40px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #e0e0e0;
  margin-bottom: 8px;
}

.form-select,
.form-input {
  width: 100%;
  padding: 8px 12px;
  background: #2a2a2a;
  border: 1px solid #333;
  border-radius: 4px;
  color: #e0e0e0;
  font-size: 13px;
}

.form-select:focus,
.form-input:focus {
  outline: none;
  border-color: #5dade2;
}

.form-help {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #e0e0e0;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  cursor: pointer;
}

.connections-list,
.parameters-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.checkbox-label .material-icons {
  font-size: 18px;
  color: #5dade2;
}

.connection-type {
  color: #666;
  font-size: 12px;
}

.parameter-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.param-label {
  flex: 0 0 150px;
  font-size: 13px;
  color: #e0e0e0;
  font-family: monospace;
}

.param-input {
  flex: 1;
  padding: 6px 10px;
  background: #2a2a2a;
  border: 1px solid #333;
  border-radius: 4px;
  color: #e0e0e0;
  font-size: 13px;
}

.param-input:focus {
  outline: none;
  border-color: #5dade2;
}

.empty-state {
  text-align: center;
  color: #666;
  padding: 40px;
  font-size: 13px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 16px 20px;
  border-top: 1px solid #333;
}

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  border: 1px solid #333;
  background: #2a2a2a;
  color: #e0e0e0;
  transition: all 0.2s;
}

.btn:hover {
  background: #333;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #5dade2;
  color: #000;
  border-color: #5dade2;
}

.btn-primary:hover:not(:disabled) {
  background: #4a9fd6;
}
</style>
