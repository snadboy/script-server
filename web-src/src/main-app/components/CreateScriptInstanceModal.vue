<template>
  <div v-if="visible" class="modal-overlay" @click.self="close">
    <div class="modal-dialog">
      <div class="modal-header">
        <h5 class="modal-title">Create Script Instance: {{ project?.name || '' }}</h5>
        <button class="modal-close" @click="close">&times;</button>
      </div>

      <div class="modal-body">
        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <div class="form-group">
          <label>Group</label>
          <input
            v-model="groupName"
            type="text"
            list="group-names"
            placeholder="Select or enter group name"
            class="form-input"
            @change="checkNewGroup"
          />
          <datalist id="group-names">
            <option v-for="group in existingGroups" :key="group" :value="group">
              {{ group }}
            </option>
          </datalist>
          <div class="form-help">
            Select existing group or type new name
          </div>
        </div>

        <div class="form-group">
          <label>Entry Point</label>
          <div class="form-value">{{ entryPoint || 'No entry point selected' }}</div>
        </div>

        <div class="form-group">
          <label class="required">Script Name</label>
          <input
            v-model="scriptName"
            type="text"
            :placeholder="project?.name || 'Enter script name'"
            class="form-input"
            :class="{ 'input-error': scriptNameError }"
            @input="validateScriptName"
          />
          <div v-if="scriptNameError" class="validation-error">
            {{ scriptNameError }}
          </div>
          <div class="form-help">
            Name for this script instance (must be unique)
          </div>
        </div>

        <div class="form-group">
          <label>Description</label>
          <input
            v-model="description"
            type="text"
            placeholder="What this script does"
            class="form-input"
          />
          <div class="form-help">
            Optional description for this script instance
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn waves-effect" @click="close">Cancel</button>
        <button
          class="btn btn-primary waves-effect"
          :disabled="!canCreate"
          @click="createInstance"
        >
          {{ creating ? 'Creating...' : 'Create Instance' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import {axiosInstance} from '@/common/utils/axios_utils';

export default {
  name: 'CreateScriptInstanceModal',

  props: {
    visible: {
      type: Boolean,
      default: false
    },
    project: {
      type: Object,
      default: null
    },
    entryPoint: {
      type: String,
      default: ''
    }
  },

  data() {
    return {
      scriptName: '',
      description: '',
      groupName: 'Imported Projects',
      existingGroups: [],
      scriptNameError: null,
      error: null,
      creating: false,
      confirmingNewGroup: false
    };
  },

  computed: {
    canCreate() {
      return (
        this.scriptName &&
        !this.scriptNameError &&
        this.entryPoint &&
        !this.creating
      );
    }
  },

  watch: {
    visible(newVal) {
      if (newVal) {
        // Reset form when modal opens
        this.scriptName = '';
        this.description = '';
        this.groupName = 'Imported Projects';
        this.scriptNameError = null;
        this.error = null;
        this.confirmingNewGroup = false;
        // Load existing groups
        this.loadExistingGroups();
      }
    }
  },

  methods: {
    async loadExistingGroups() {
      try {
        const response = await axiosInstance.get('/scripts');
        const scripts = response.data.scripts || [];
        // Extract unique group names
        const groups = new Set();
        scripts.forEach(script => {
          if (script.group) {
            groups.add(script.group);
          }
        });
        this.existingGroups = Array.from(groups).sort();
        // Add default if not present
        if (!this.existingGroups.includes('Imported Projects')) {
          this.existingGroups.unshift('Imported Projects');
        }
      } catch (err) {
        console.error('Error loading groups:', err);
        // Fallback to default
        this.existingGroups = ['Imported Projects'];
      }
    },

    checkNewGroup() {
      if (this.groupName && !this.existingGroups.includes(this.groupName)) {
        const confirmed = confirm(`Create new group "${this.groupName}"?`);
        if (!confirmed) {
          this.groupName = 'Imported Projects';
        }
      }
    },

    validateScriptName() {
      this.scriptNameError = null;

      if (!this.scriptName) {
        this.scriptNameError = 'Script name is required';
        return;
      }

      // Check for invalid characters
      if (!/^[a-zA-Z0-9_\- ]+$/.test(this.scriptName)) {
        this.scriptNameError = 'Only letters, numbers, spaces, hyphens, and underscores allowed';
        return;
      }

      // Backend will validate uniqueness when creating
    },

    async createInstance() {
      if (!this.canCreate) return;

      this.creating = true;
      this.error = null;

      try {
        const response = await axiosInstance.post(`/admin/projects/${this.project.id}/wrapper`, {
          entry_point: this.entryPoint,
          script_name: this.scriptName,
          description: this.description,
          group: this.groupName
        });

        if (response.data.wrapper_path && response.data.config_path) {
          this.$emit('created', {
            scriptName: this.scriptName,
            description: this.description,
            wrapperPath: response.data.wrapper_path,
            configPath: response.data.config_path
          });
        } else {
          this.error = 'Failed to create script instance';
        }
      } catch (err) {
        this.error = err.response?.data?.error || err.message || 'Failed to create script instance';
      } finally {
        this.creating = false;
      }
    },

    close() {
      if (this.creating) return; // Prevent closing while creating
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

.modal-dialog {
  background: var(--background-color);
  border-radius: 4px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  width: 90%;
  max-width: 550px;
  max-height: 60vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  margin: auto;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-bottom: 1px solid var(--separator-color);
  flex-shrink: 0;
}

.modal-title {
  font-size: 14px;
  font-weight: 500;
  margin: 0;
  color: var(--font-color-main);
}

.modal-close {
  background: none;
  border: none;
  font-size: 28px;
  line-height: 1;
  color: var(--font-color-medium);
  cursor: pointer;
  padding: 0;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  color: var(--font-color-main);
}

.modal-body {
  padding: 12px;
  overflow-y: auto;
  flex: 1;
  min-height: 0;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 8px 12px;
  border-top: 1px solid var(--separator-color);
  flex-shrink: 0;
  background: var(--background-color);
}

.error-message {
  background: var(--error-background-color);
  color: var(--error-color);
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 16px;
}

.form-group {
  margin-bottom: 10px;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-group label {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: var(--font-color-main);
  margin-bottom: 4px;
}

.form-group label.required::after {
  content: ' *';
  color: var(--error-color);
}

.form-value {
  padding: 6px 10px;
  background: var(--background-color-high-emphasis);
  border-radius: 4px;
  font-size: 13px;
  color: var(--font-color-medium);
}

.form-input {
  width: 100%;
  padding: 6px 10px;
  font-size: 13px;
  background: var(--background-color);
  border: 1px solid var(--separator-color);
  border-radius: 4px;
  color: var(--font-color-main);
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.form-input.input-error {
  border-color: var(--error-color);
}

.validation-error {
  color: var(--error-color);
  font-size: 12px;
  margin-top: 4px;
}

.form-help {
  font-size: 11px;
  color: var(--font-color-medium);
  margin-top: 2px;
}

.btn {
  padding: 6px 14px;
  font-size: 13px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  background: var(--background-color-high-emphasis);
  color: var(--font-color-main);
}

.btn:hover {
  background: var(--background-color-medium-emphasis);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-color-light);
}
</style>
