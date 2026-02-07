<template>
  <div v-if="visible" class="modal-overlay" @click.self="close">
    <div class="settings-modal">
      <div class="modal-header">
        <h3>Instance Settings: {{ scriptName }}</h3>
        <button class="btn-close" @click="close">×</button>
      </div>

      <div class="modal-tabs">
        <button
          :class="['tab-btn', { active: activeTab === 'connections' }]"
          @click="activeTab = 'connections'"
        >
          Connections
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
          <!-- Connections Tab -->
          <div v-if="activeTab === 'connections'" class="tab-content">
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

            <!-- Connection Selection (Grouped by Type) -->
            <div v-if="connectionsByType && Object.keys(connectionsByType).length > 0" class="form-group">
              <label>Connections</label>
              <div class="connections-grouped">
                <div v-for="(connections, type) in connectionsByType" :key="type" class="connection-type-group">
                  <div class="connection-type-header">
                    <i class="material-icons">{{ getConnectionIcon(type) }}</i>
                    <span>{{ getConnectionTypeName(type) }}</span>
                  </div>
                  <div class="connection-options">
                    <label class="radio-label">
                      <input
                        type="radio"
                        :name="'connection-' + type"
                        :value="null"
                        v-model="defaultConnectionsByType[type]"
                      />
                      <span class="radio-custom"></span>
                      <span class="connection-option-text">None</span>
                    </label>
                    <label v-for="conn in connections" :key="conn.id" class="radio-label">
                      <input
                        type="radio"
                        :name="'connection-' + type"
                        :value="conn.id"
                        v-model="defaultConnectionsByType[type]"
                      />
                      <span class="radio-custom"></span>
                      <span class="connection-option-text">{{ conn.name }}</span>
                    </label>
                  </div>
                </div>
              </div>
              <div class="form-help">Select one connection per type (or none)</div>
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
                <span class="checkbox-custom"></span>
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
                <span class="checkbox-custom"></span>
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
                <span class="checkbox-custom"></span>
                <span>Enable scheduling</span>
              </label>
            </div>

            <div v-if="schedulingEnabled" class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="schedulingAutoCleanup" />
                <span class="checkbox-custom"></span>
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
      activeTab: 'connections',
      loading: false,
      saving: false,
      error: null,
      config: null,
      // Defaults
      defaultVerb: '',
      defaultConnections: [],
      defaultConnectionsByType: {}, // Maps type -> connection_id
      defaultParameters: {},
      availableVerbs: [],
      availableParameters: [],
      availableConnections: [],
      connectionsByType: {}, // Groups connections by type
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

        // Group connections by type
        this.connectionsByType = {};
        this.availableConnections.forEach(conn => {
          if (!this.connectionsByType[conn.type]) {
            this.connectionsByType[conn.type] = [];
          }
          this.connectionsByType[conn.type].push(conn);
        });

        // Load connection types
        const typesResponse = await axiosInstance.get('/admin/connections/types');
        this.connectionTypes = typesResponse.data.types || [];

        // Load existing settings from config
        this.defaultVerb = this.config.defaultVerb || '';
        this.defaultConnections = this.config.defaultConnections || [];
        this.defaultParameters = { ...(this.config.defaultParameters || {}) };

        // Convert defaultConnections array to defaultConnectionsByType object
        // defaultConnections is an array of connection IDs
        // We need to map each to its type
        this.defaultConnectionsByType = {};
        Object.keys(this.connectionsByType).forEach(type => {
          this.defaultConnectionsByType[type] = null; // Default to none
        });
        this.defaultConnections.forEach(connId => {
          const conn = this.availableConnections.find(c => c.id === connId);
          if (conn) {
            this.defaultConnectionsByType[conn.type] = conn.id;
          }
        });

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

        // Convert defaultConnectionsByType object to array
        // Only include non-null selections
        const defaultConnections = Object.values(this.defaultConnectionsByType)
          .filter(connId => connId !== null && connId !== undefined);

        // Prepare updated config
        const updates = {
          defaultVerb: this.defaultVerb || null,
          defaultConnections: defaultConnections,
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
/*
 * IMPORTANT: NEVER use browser default checkboxes!
 * Default checkboxes render as tilted rectangles on some systems.
 * Always use custom checkbox styling like .checkbox-custom below.
 */

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
  position: relative;
}

/* Hide native checkbox (never use default tilted rectangles!) */
.checkbox-label input[type="checkbox"] {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

/* Custom checkbox */
.checkbox-custom {
  position: relative;
  width: 18px;
  height: 18px;
  background: #2a2a2a;
  border: 2px solid #555;
  border-radius: 3px;
  transition: all 0.2s;
  flex-shrink: 0;
}

.checkbox-label:hover .checkbox-custom {
  border-color: #5dade2;
}

/* Checked state */
.checkbox-label input[type="checkbox"]:checked + .checkbox-custom {
  background: #5dade2;
  border-color: #5dade2;
}

/* Checkmark */
.checkbox-label input[type="checkbox"]:checked + .checkbox-custom::after {
  content: '';
  position: absolute;
  left: 5px;
  top: 2px;
  width: 4px;
  height: 8px;
  border: solid #000;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

/* Radio button styling (for connection selection) */
.radio-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #e0e0e0;
  cursor: pointer;
  position: relative;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s;
}

.radio-label:hover {
  background: rgba(93, 173, 226, 0.1);
}

/* Hide native radio button */
.radio-label input[type="radio"] {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

/* Custom radio button */
.radio-custom {
  position: relative;
  width: 18px;
  height: 18px;
  background: #2a2a2a;
  border: 2px solid #555;
  border-radius: 50%;
  transition: all 0.2s;
  flex-shrink: 0;
}

.radio-label:hover .radio-custom {
  border-color: #5dade2;
}

/* Checked state */
.radio-label input[type="radio"]:checked + .radio-custom {
  border-color: #5dade2;
}

/* Radio dot */
.radio-label input[type="radio"]:checked + .radio-custom::after {
  content: '';
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 8px;
  height: 8px;
  background: #5dade2;
  border-radius: 50%;
}

.connection-option-text {
  flex: 1;
}

.parameters-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.connections-grouped {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.connection-type-group {
  background: #2a2a2a;
  border: 1px solid #333;
  border-radius: 6px;
  padding: 12px;
}

.connection-type-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #333;
  font-weight: 600;
  color: #e0e0e0;
}

.connection-type-header .material-icons {
  font-size: 20px;
  color: #5dade2;
}

.connection-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-left: 8px;
}

.checkbox-label .material-icons {
  font-size: 18px;
  color: #5dade2;
  flex-shrink: 0;
}

.connection-name {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.connection-type {
  color: #666;
  font-size: 12px;
  flex-shrink: 0;
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
  display: inline-flex;
  align-items: center;
  justify-content: center;
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
