<template>
  <div v-if="visible" class="dir-browser-overlay" @click.self="cancel">
    <div class="dir-browser-modal">
      <div class="modal-header">
        <span class="modal-title">Select Directory</span>
      </div>

      <div class="modal-body">
        <!-- Current Path Display -->
        <div class="current-path">
          <button
            class="btn-nav"
            :disabled="!parentPath || loading"
            @click="navigateUp"
            title="Go to parent directory"
          >
            <i class="material-icons">arrow_upward</i>
          </button>
          <input
            v-model="pathInput"
            type="text"
            class="path-input"
            placeholder="/path/to/directory"
            @keyup.enter="navigateToPath"
          />
          <button
            class="btn-nav"
            :disabled="loading"
            @click="navigateToPath"
            title="Go to path"
          >
            <i class="material-icons">arrow_forward</i>
          </button>
        </div>

        <!-- Error Display -->
        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <!-- Directory Listing -->
        <div class="dir-listing">
          <div v-if="loading" class="loading">Loading...</div>
          <div v-else-if="entries.length === 0" class="empty">
            No accessible directories found
          </div>
          <div v-else class="entries-list">
            <div
              v-for="entry in entries"
              :key="entry.path"
              :class="['entry-row', {
                'is-dir': entry.is_dir,
                'is-file': !entry.is_dir,
                'is-python-project': entry.is_python_project,
                'selected': selectedPath === entry.path
              }]"
              @click="selectEntry(entry)"
              @dblclick="handleDoubleClick(entry)"
            >
              <i class="material-icons entry-icon">
                {{ entry.is_python_project ? 'folder_special' : (entry.is_dir ? 'folder' : 'insert_drive_file') }}
              </i>
              <span class="entry-name">{{ entry.name }}</span>
              <span v-if="entry.is_python_project" class="python-badge">Python</span>
            </div>
          </div>
        </div>

        <!-- Selected Path (always visible) -->
        <div class="selected-info">
          <template v-if="selectedPath">
            Selected: <code>{{ selectedPath }}</code>
          </template>
          <template v-else>
            Current: <code>{{ currentPath }}</code>
          </template>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn" @click="cancel">Cancel</button>
        <button
          class="btn btn-primary"
          :disabled="!selectedPath"
          @click="confirmSelection"
        >
          Select
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import {axiosInstance} from '@/common/utils/axios_utils';

export default {
  name: 'DirectoryBrowserModal',

  props: {
    visible: {
      type: Boolean,
      default: false
    },
    initialPath: {
      type: String,
      default: '/tmp'
    }
  },

  data() {
    return {
      currentPath: '',
      parentPath: null,
      pathInput: '',
      entries: [],
      selectedPath: null,
      loading: false,
      error: null
    };
  },

  watch: {
    visible(newVal) {
      if (newVal) {
        this.selectedPath = null;
        this.error = null;
        this.browse(this.initialPath || '/tmp');
      }
    }
  },

  methods: {
    async browse(path) {
      this.loading = true;
      this.error = null;

      try {
        const response = await axiosInstance.get('admin/filesystem/browse', {
          params: { path }
        });

        this.currentPath = response.data.current_path;
        this.parentPath = response.data.parent_path;
        this.pathInput = this.currentPath;
        this.entries = response.data.entries;
      } catch (e) {
        this.error = e.response?.data || 'Failed to browse directory';
        // Keep current entries on error
      } finally {
        this.loading = false;
      }
    },

    navigateUp() {
      if (this.parentPath) {
        this.selectedPath = null;
        this.browse(this.parentPath);
      }
    },

    navigateToPath() {
      if (this.pathInput && this.pathInput !== this.currentPath) {
        this.selectedPath = null;
        this.browse(this.pathInput);
      }
    },

    selectEntry(entry) {
      if (entry.is_dir) {
        this.selectedPath = entry.path;
      }
    },

    handleDoubleClick(entry) {
      if (entry.is_dir) {
        this.selectedPath = null;
        this.browse(entry.path);
      }
    },

    confirmSelection() {
      if (this.selectedPath) {
        this.$emit('select', this.selectedPath);
        this.$emit('close');
      }
    },

    cancel() {
      this.$emit('close');
    }
  }
};
</script>

<style scoped>
.dir-browser-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1100;
}

.dir-browser-modal {
  background: var(--background-color);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px 24px;
  border-bottom: 1px solid var(--separator-color);
  flex-shrink: 0;
}

.modal-title {
  font-size: 1.3em;
  font-weight: 500;
  color: var(--font-color-main);
}

.modal-body {
  padding: 16px 24px;
  overflow-y: auto;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.current-path {
  display: flex;
  gap: 8px;
  align-items: center;
}

.btn-nav {
  background: var(--background-color-level-4dp);
  border: 1px solid var(--separator-color);
  border-radius: var(--radius-sm);
  padding: 8px;
  cursor: pointer;
  color: var(--font-color-main);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-nav:hover:not(:disabled) {
  background: var(--background-color-level-8dp);
}

.btn-nav:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-nav i {
  font-size: 20px;
}

.path-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid var(--separator-color);
  border-radius: var(--radius-sm);
  background: var(--background-color-level-4dp);
  color: var(--font-color-main);
  font-family: monospace;
  font-size: 13px;
}

.path-input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.error-message {
  padding: 10px 12px;
  background: rgba(244, 67, 54, 0.15);
  color: #f44336;
  border-radius: var(--radius-sm);
  font-size: 13px;
}

.dir-listing {
  border: 1px solid var(--separator-color);
  border-radius: var(--radius-sm);
  flex: 1;
  min-height: 250px;
  max-height: 350px;
  overflow-y: auto;
}

.loading,
.empty {
  padding: 40px 20px;
  text-align: center;
  color: var(--font-color-medium);
  font-size: 14px;
}

.entries-list {
  padding: 4px;
}

.entry-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background 0.15s;
}

.entry-row:hover {
  background: var(--background-color-level-4dp);
}

.entry-row.selected {
  background: var(--primary-color);
  color: white;
}

.entry-row.selected .entry-icon {
  color: white;
}

.entry-row.is-file {
  opacity: 0.5;
  cursor: default;
}

.entry-icon {
  font-size: 20px;
  color: var(--font-color-medium);
}

.entry-row.is-python-project .entry-icon {
  color: #4caf50;
}

.entry-row.selected.is-python-project .entry-icon {
  color: white;
}

.entry-name {
  flex: 1;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.python-badge {
  font-size: 10px;
  padding: 2px 6px;
  background: rgba(76, 175, 80, 0.2);
  color: #4caf50;
  border-radius: 4px;
  text-transform: uppercase;
  font-weight: 500;
}

.entry-row.selected .python-badge {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.selected-info {
  padding: 8px 12px;
  background: var(--background-color-level-4dp);
  border-radius: var(--radius-sm);
  font-size: 13px;
  color: var(--font-color-medium);
}

.selected-info code {
  font-family: monospace;
  color: var(--font-color-main);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--separator-color);
  flex-shrink: 0;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 20px;
  border-radius: var(--radius-sm);
  font-size: 14px;
  line-height: 1;
  cursor: pointer;
  border: none;
  background: var(--background-color-high-emphasis);
  color: var(--font-color-main);
}

.btn:hover {
  background: var(--background-color-slight-emphasis);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-primary:hover {
  background: var(--primary-color-dark-color);
}

.btn-primary:disabled {
  background: var(--primary-color);
}
</style>
