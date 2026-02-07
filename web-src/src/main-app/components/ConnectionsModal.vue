<template>
  <div v-if="visible" class="connections-modal-overlay" @click.self="close">
    <div class="connections-modal">
      <div class="modal-header">
        <span class="modal-title">Connections</span>
        <button class="modal-close" @click="close">×</button>
      </div>

      <!-- Connection List View -->
      <div v-if="view === 'list'" class="modal-body">
        <div class="connections-header">
          <h6>Manage API Credentials</h6>
          <button class="btn waves-effect btn-primary" @click="showCreateSelector">
            <i class="material-icons left">add</i>
            Add Connection
          </button>
        </div>

        <div v-if="loading" class="connections-loading">Loading...</div>

        <div v-else-if="connections.length === 0" class="connections-empty">
          <p>No connections configured</p>
          <p class="hint">Add a connection to securely store API credentials</p>
        </div>

        <div v-else class="connections-table-container">
          <table class="connections-table">
            <thead>
              <tr>
                <th></th>
                <th>Name</th>
                <th>Type</th>
                <th>Updated</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="conn in connections"
                :key="conn.id"
                class="connection-row"
              >
                <td class="connection-icon-cell">
                  <i class="material-icons">{{ getConnectionIcon(conn.type) }}</i>
                </td>
                <td class="connection-name">{{ conn.name }}</td>
                <td class="connection-type">{{ getConnectionTypeName(conn.type) }}</td>
                <td class="connection-updated">
                  <span v-if="conn.updated_at">{{ formatDate(conn.updated_at) }}</span>
                  <span v-else>-</span>
                </td>
                <td class="connection-actions">
                  <button
                    class="btn-icon waves-effect waves-circle"
                    title="Edit"
                    @click="editConnection(conn)"
                  >
                    <i class="material-icons">edit</i>
                  </button>
                  <button
                    class="btn-icon waves-effect waves-circle"
                    title="Delete"
                    @click="deleteConnection(conn)"
                  >
                    <i class="material-icons">delete</i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Connection Type Selector View -->
      <div v-if="view === 'type-selector'" class="modal-body">
        <div class="type-selector-header">
          <button class="btn-text waves-effect" @click="view = 'list'">
            <i class="material-icons left">arrow_back</i>
            Back
          </button>
          <h6>Select Connection Type</h6>
        </div>

        <div class="connection-types-grid">
          <div
            v-for="type in connectionTypes"
            :key="type.type_id"
            class="connection-type-card"
            @click="selectType(type)"
          >
            <i class="material-icons">{{ type.icon }}</i>
            <div class="type-name">{{ type.display_name }}</div>
            <div class="type-description">{{ type.description }}</div>
          </div>
        </div>
      </div>

      <!-- Add/Edit Connection Form View -->
      <div v-if="view === 'form'" class="modal-body">
        <div class="form-header">
          <button class="btn-text waves-effect" @click="cancelForm">
            <i class="material-icons left">arrow_back</i>
            Back
          </button>
          <h6>{{ formMode === 'create' ? 'New Connection' : 'Edit Connection' }}</h6>
        </div>

        <div class="connection-form">
          <!-- Connection Type (display only in edit mode) -->
          <div v-if="formMode === 'edit'" class="form-row">
            <label>Type</label>
            <div class="type-display">
              <i class="material-icons">{{ currentType.icon }}</i>
              {{ currentType.display_name }}
            </div>
          </div>

          <!-- Connection ID (only for create mode) -->
          <div v-if="formMode === 'create'" class="form-row">
            <label for="connection-id">Connection ID *</label>
            <input
              id="connection-id"
              v-model="formData.id"
              type="text"
              placeholder="e.g., home-plex, work-google"
              class="form-input"
              required
            />
            <span class="field-hint">Unique identifier (lowercase, hyphens, no spaces)</span>
          </div>

          <!-- Connection Name -->
          <div class="form-row">
            <label for="connection-name">Display Name *</label>
            <input
              id="connection-name"
              v-model="formData.name"
              type="text"
              placeholder="e.g., Home Plex Server"
              class="form-input"
              required
            />
          </div>

          <!-- Dynamic Fields Based on Connection Type -->
          <div
            v-for="field in currentType.fields"
            :key="field.name"
            class="form-row"
          >
            <label :for="`field-${field.name}`">
              {{ field.label }}
              <span v-if="field.required">*</span>
            </label>

            <!-- Password/Secret Fields -->
            <div v-if="field.field_type === 'password'" class="secret-field">
              <input
                :id="`field-${field.name}`"
                v-model="formData.fields[field.name]"
                :type="secretFieldRevealed[field.name] ? 'text' : 'password'"
                :placeholder="formMode === 'edit' && !editingField[field.name] ? '********' : field.placeholder"
                :readonly="formMode === 'edit' && !editingField[field.name] && secretFieldRevealed[field.name]"
                :disabled="formMode === 'edit' && !editingField[field.name] && !secretFieldRevealed[field.name]"
                class="form-input"
                :class="{'revealed-secret': formMode === 'edit' && !editingField[field.name] && secretFieldRevealed[field.name]}"
                :required="field.required"
              />
              <button
                v-if="formMode === 'create' || editingField[field.name] || (formMode === 'edit' && isAdmin)"
                class="btn-icon"
                type="button"
                :title="secretFieldRevealed[field.name] ? 'Hide' : 'Show'"
                @click="toggleSecretReveal(field.name)"
              >
                <i class="material-icons">{{ secretFieldRevealed[field.name] ? 'visibility_off' : 'visibility' }}</i>
              </button>
              <button
                v-if="formMode === 'edit' && !editingField[field.name] && !secretFieldRevealed[field.name]"
                class="btn-text"
                type="button"
                @click="startEditingField(field.name)"
              >
                Change
              </button>
            </div>

            <!-- Textarea Fields -->
            <textarea
              v-else-if="field.field_type === 'textarea'"
              :id="`field-${field.name}`"
              v-model="formData.fields[field.name]"
              :placeholder="field.placeholder"
              class="form-textarea"
              :required="field.required"
              rows="4"
            ></textarea>

            <!-- URL Fields -->
            <input
              v-else-if="field.field_type === 'url'"
              :id="`field-${field.name}`"
              v-model="formData.fields[field.name]"
              type="url"
              :placeholder="field.placeholder"
              class="form-input"
              :required="field.required"
            />

            <!-- Text Fields -->
            <input
              v-else
              :id="`field-${field.name}`"
              v-model="formData.fields[field.name]"
              type="text"
              :placeholder="field.placeholder"
              class="form-input"
              :required="field.required"
            />

            <span v-if="field.help_text" class="field-hint">{{ field.help_text }}</span>
          </div>
        </div>
      </div>

      <!-- Modal Footer (for form view) -->
      <div v-if="view === 'form'" class="modal-footer">
        <button class="btn waves-effect" @click="cancelForm">Cancel</button>
        <button
          class="btn waves-effect btn-primary"
          :disabled="saving"
          @click="saveConnection"
        >
          {{ saving ? 'Saving...' : 'Save' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import {mapState} from 'vuex';
import {axiosInstance} from '@/common/utils/axios_utils';

export default {
  name: 'ConnectionsModal',

  props: {
    visible: {
      type: Boolean,
      default: false
    }
  },

  data() {
    return {
      view: 'list', // 'list' | 'type-selector' | 'form'
      formMode: 'create', // 'create' | 'edit'
      loading: false,
      saving: false,
      connections: [],
      connectionTypes: [],
      currentType: null,
      formData: {
        id: '',
        name: '',
        type: '',
        fields: {}
      },
      secretFieldRevealed: {}, // Track which secret fields are revealed
      editingField: {} // Track which fields are being edited (for edit mode)
    };
  },

  computed: {
    ...mapState('auth', {
      isAdmin: 'admin'
    })
  },

  watch: {
    visible(newVal) {
      if (newVal) {
        this.loadData();
      } else {
        this.resetView();
      }
    }
  },

  methods: {
    async loadData() {
      this.loading = true;
      try {
        // Load connection types
        const typesResp = await axiosInstance.get('/admin/connections/types');
        this.connectionTypes = typesResp.data.types || [];

        // Load connections list
        const connsResp = await axiosInstance.get('/admin/connections');
        this.connections = connsResp.data.connections || [];
      } catch (error) {
        console.error('Failed to load connections:', error);
        this.showError('Failed to load connections');
      } finally {
        this.loading = false;
      }
    },

    getConnectionIcon(typeId) {
      const type = this.connectionTypes.find(t => t.type_id === typeId);
      return type ? type.icon : 'vpn_key';
    },

    getConnectionTypeName(typeId) {
      const type = this.connectionTypes.find(t => t.type_id === typeId);
      return type ? type.display_name : typeId;
    },

    formatDate(dateStr) {
      const date = new Date(dateStr);
      const dateOptions = { month: 'numeric', day: 'numeric', year: '2-digit' };
      const timeOptions = { hour: 'numeric', minute: '2-digit', hour12: true };

      const datePart = date.toLocaleDateString('en-US', dateOptions);
      const timePart = date.toLocaleTimeString('en-US', timeOptions);

      return `${datePart} @ ${timePart}`;
    },

    showCreateSelector() {
      this.view = 'type-selector';
    },

    selectType(type) {
      this.currentType = type;
      this.formMode = 'create';
      this.formData = {
        id: '',
        name: '',
        type: type.type_id,
        fields: {}
      };
      // Initialize fields
      type.fields.forEach(field => {
        this.formData.fields[field.name] = '';
      });
      this.secretFieldRevealed = {};
      this.view = 'form';
    },

    editConnection(conn) {
      // Find the connection type
      this.currentType = this.connectionTypes.find(t => t.type_id === conn.type);
      if (!this.currentType) {
        this.showError('Unknown connection type');
        return;
      }

      this.formMode = 'edit';
      this.formData = {
        id: conn.id,
        name: conn.name,
        type: conn.type,
        fields: {...conn.fields}
      };
      this.secretFieldRevealed = {};
      this.editingField = {}; // Reset editing state
      this.view = 'form';
    },

    async deleteConnection(conn) {
      if (!confirm(`Delete connection "${conn.name}"?`)) {
        return;
      }

      try {
        await axiosInstance.delete(`/admin/connections/${conn.id}`);
        await this.loadData();
        this.showSuccess('Connection deleted');
      } catch (error) {
        console.error('Failed to delete connection:', error);
        this.showError('Failed to delete connection');
      }
    },

    async toggleSecretReveal(fieldName) {
      const isRevealing = !this.secretFieldRevealed[fieldName];

      // If revealing in edit mode and field is masked, fetch actual value from backend
      if (isRevealing && this.formMode === 'edit' && !this.editingField[fieldName]) {
        const currentValue = this.formData.fields[fieldName];

        // Check if value is masked (multiple asterisks)
        if (currentValue && /^\*{5,}$/.test(currentValue)) {
          try {
            // Fetch actual decrypted value from backend
            const response = await axiosInstance.get(
              `/admin/connections/${this.formData.id}/field/${fieldName}`
            );

            if (response.data && response.data.value) {
              // Store the actual decrypted value
              this.formData.fields[fieldName] = response.data.value;
            }
          } catch (error) {
            console.error('Failed to fetch decrypted field value:', error);
            this.showError('Failed to reveal field value');
            return;
          }
        }
      }

      this.secretFieldRevealed[fieldName] = isRevealing;
      this.$forceUpdate();
    },

    startEditingField(fieldName) {
      this.editingField[fieldName] = true;
      this.formData.fields[fieldName] = ''; // Clear the masked value
      this.$forceUpdate();
    },

    async saveConnection() {
      // Validate required fields
      for (const field of this.currentType.fields) {
        if (field.required && !this.formData.fields[field.name]) {
          this.showError(`${field.label} is required`);
          return;
        }

        // Validate URL fields
        if (field.field_type === 'url' && this.formData.fields[field.name]) {
          const urlValue = this.formData.fields[field.name].trim();
          if (urlValue) {
            try {
              new URL(urlValue);
            } catch (e) {
              this.showError(`${field.label} must be a valid URL (e.g., https://example.com)`);
              return;
            }
          }
        }
      }

      this.saving = true;
      try {
        if (this.formMode === 'create') {
          // Validate ID
          if (!this.formData.id || !/^[a-z0-9-]+$/.test(this.formData.id)) {
            this.showError('Connection ID must contain only lowercase letters, numbers, and hyphens');
            return;
          }

          await axiosInstance.post('/admin/connections', this.formData);
          this.showSuccess('Connection created');
        } else {
          // In edit mode, remove fields that weren't being edited (still have ******** value)
          const updates = {
            name: this.formData.name,
            fields: {}
          };

          for (const [fieldName, fieldValue] of Object.entries(this.formData.fields)) {
            // Only include fields that were edited or are not secret
            const fieldDef = this.currentType.fields.find(f => f.name === fieldName);
            if (!fieldDef || !fieldDef.secret || this.editingField[fieldName] || fieldValue !== '********') {
              updates.fields[fieldName] = fieldValue;
            } else {
              // Keep the masked value to signal "don't update this field"
              updates.fields[fieldName] = '********';
            }
          }

          await axiosInstance.put(`/admin/connections/${this.formData.id}`, updates);
          this.showSuccess('Connection updated');
        }

        await this.loadData();
        this.view = 'list';
      } catch (error) {
        console.error('Failed to save connection:', error);
        const message = error.response?.data?.reason || 'Failed to save connection';
        this.showError(message);
      } finally {
        this.saving = false;
      }
    },

    cancelForm() {
      this.view = 'list';
    },

    resetView() {
      this.view = 'list';
      this.formData = {
        id: '',
        name: '',
        type: '',
        fields: {}
      };
      this.secretFieldRevealed = {};
      this.editingField = {};
    },

    close() {
      this.$emit('close');
    },

    showSuccess(message) {
      // Use existing notification system if available
      if (window.M && window.M.toast) {
        window.M.toast({html: message, classes: 'green'});
      }
      // Silently succeed if toast system not available
    },

    showError(message) {
      if (window.M && window.M.toast) {
        window.M.toast({html: message, classes: 'red'});
      } else {
        console.error('Error:', message);
      }
    }
  }
};
</script>

<style scoped>
/* Modal Overlay */
.connections-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

/* Modal Container */
.connections-modal {
  background: var(--background-color);
  border-radius: 4px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 24px 38px 3px rgba(0,0,0,0.14), 0 9px 46px 8px rgba(0,0,0,0.12);
}

/* Modal Header */
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px;
  border-bottom: 1px solid var(--separator-color);
}

.modal-title {
  font-size: 1.5rem;
  font-weight: 400;
  color: var(--font-color-main);
}

.modal-close {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: var(--font-color-medium);
  padding: 0;
  width: 36px;
  height: 36px;
  line-height: 36px;
  text-align: center;
  border-radius: 50%;
}

.modal-close:hover {
  background: var(--background-color-high-emphasis);
}

/* Modal Body */
.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

/* Connections List View */
.connections-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.connections-header h6 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 400;
  color: var(--font-color-main);
}

.connections-loading,
.connections-empty {
  text-align: center;
  padding: 48px 24px;
  color: var(--font-color-medium);
}

.connections-empty .hint {
  margin-top: 8px;
  font-size: 0.9rem;
}

.connections-table-container {
  border: 1px solid var(--separator-color);
  border-radius: 4px;
  overflow: hidden;
}

.connections-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
  display: block;
}

.connections-table thead {
  display: block;
  background: var(--background-color-high-emphasis);
}

.connections-table thead tr {
  display: table;
  width: 100%;
  table-layout: fixed;
}

.connections-table tbody {
  display: block;
  max-height: 200px;
  overflow-y: auto;
}

.connections-table tbody tr {
  display: table;
  width: 100%;
  table-layout: fixed;
  border-bottom: 1px solid var(--separator-color);
  transition: background-color 0.2s;
}

.connections-table tbody tr:hover {
  background: var(--background-color-high-emphasis);
}

.connections-table tbody tr:last-child {
  border-bottom: none;
}

.connections-table th {
  text-align: left;
  padding: 12px 16px;
  font-weight: 600;
  color: var(--font-color-main);
  background: var(--background-color-high-emphasis);
  border-bottom: 2px solid var(--separator-color);
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.connections-table td {
  padding: 12px 16px;
  color: var(--font-color-main);
}

.connection-icon-cell {
  width: 40px;
  text-align: center;
}

.connection-icon-cell i {
  color: var(--primary-color);
  font-size: 20px;
  vertical-align: middle;
}

.connection-name {
  font-weight: 500;
  color: var(--font-color-main);
}

.connection-type {
  color: var(--font-color-medium);
  font-size: 0.9rem;
}

.connection-updated {
  color: var(--font-color-medium);
  font-size: 0.85rem;
  white-space: nowrap;
}

.connection-actions {
  display: flex;
  gap: 4px;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  color: var(--font-color-medium);
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon:hover {
  background: var(--background-color-high-emphasis);
  color: var(--font-color-main);
}

.btn-icon i {
  font-size: 20px;
}

/* Type Selector View */
.type-selector-header {
  margin-bottom: 24px;
}

.type-selector-header h6 {
  margin: 12px 0 0 0;
  font-size: 1.2rem;
  font-weight: 400;
  color: var(--font-color-main);
}

.connection-types-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.connection-type-card {
  padding: 24px;
  border: 1px solid var(--separator-color);
  border-radius: 4px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.connection-type-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.connection-type-card i {
  font-size: 48px;
  color: var(--primary-color);
  display: block;
  margin-bottom: 12px;
}

.type-name {
  font-size: 1.1rem;
  font-weight: 500;
  color: var(--font-color-main);
  margin-bottom: 8px;
}

.type-description {
  font-size: 0.85rem;
  color: var(--font-color-medium);
  line-height: 1.4;
}

/* Form View */
.form-header {
  margin-bottom: 24px;
}

.form-header h6 {
  margin: 12px 0 0 0;
  font-size: 1.2rem;
  font-weight: 400;
  color: var(--font-color-main);
}

.connection-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-row label {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--font-color-main);
}

.form-input,
.form-textarea {
  padding: 8px 12px;
  border: 1px solid var(--separator-color);
  border-radius: 4px;
  font-size: 1rem;
  background: var(--background-color);
  color: var(--font-color-main);
  font-family: inherit;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--primary-color);
}

.form-input:disabled {
  background: var(--background-color-high-emphasis);
  color: var(--font-color-medium);
}

.field-hint {
  font-size: 0.8rem;
  color: var(--font-color-medium);
  font-style: italic;
}

.secret-field {
  display: flex;
  gap: 8px;
  align-items: center;
}

.secret-field input {
  flex: 1;
}

.secret-field .btn-icon {
  flex-shrink: 0;
}

.secret-field .btn-text {
  flex-shrink: 0;
  background: none;
  border: 1px solid var(--primary-color);
  color: var(--primary-color);
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.secret-field .btn-text:hover {
  background: var(--primary-color);
  color: white;
}

/* Revealed secret field (admin view only) */
.form-input.revealed-secret {
  background: var(--background-color-high-emphasis);
  border-color: var(--primary-color);
  color: var(--font-color-main);
  cursor: text;
  user-select: text;
  -webkit-user-select: text;
  -moz-user-select: text;
  font-family: 'Courier New', Courier, monospace;
}

.type-display {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--background-color-high-emphasis);
  border-radius: 4px;
  color: var(--font-color-main);
}

.type-display i {
  color: var(--primary-color);
}

/* Modal Footer */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--separator-color);
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  text-transform: uppercase;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn .material-icons {
  font-size: 18px;
  margin: 0;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-color-dark, #3a7bc8);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-text {
  background: none;
  border: none;
  color: var(--primary-color);
  padding: 8px 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.9rem;
  text-transform: uppercase;
  font-weight: 500;
  border-radius: 4px;
}

.btn-text:hover {
  background: var(--background-color-high-emphasis);
}

.btn-text i {
  font-size: 18px;
}
</style>
