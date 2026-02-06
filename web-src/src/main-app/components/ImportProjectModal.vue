<template>
  <div v-if="visible" class="modal-overlay" @click.self="close">
    <div class="import-modal">
      <div class="modal-header">
        <h3>Import Project</h3>
        <button class="btn-close" @click="close">×</button>
      </div>

      <div class="modal-body">
        <!-- Error Display -->
        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <!-- Type Selector (Git/ZIP/Local) -->
        <div class="import-type-selector">
          <button
            :class="['type-btn', { active: importType === 'git' }]"
            @click="importType = 'git'"
          >
            <i class="material-icons">code</i>
            Git Clone
          </button>
          <button
            :class="['type-btn', { active: importType === 'zip' }]"
            @click="importType = 'zip'"
          >
            <i class="material-icons">folder_zip</i>
            ZIP Upload
          </button>
          <button
            :class="['type-btn', { active: importType === 'local' }]"
            @click="importType = 'local'"
          >
            <i class="material-icons">folder_open</i>
            Local Path
          </button>
        </div>

        <!-- Git Import -->
        <div v-if="importType === 'git'" class="import-form">
          <div class="form-group">
            <label>Repository URL</label>
            <input
              v-model="gitUrl"
              type="text"
              placeholder="https://github.com/user/repo"
              class="form-input"
              :disabled="importing"
            />
          </div>
          <div class="form-group">
            <label>Branch (optional)</label>
            <input
              v-model="gitBranch"
              type="text"
              placeholder="main"
              class="form-input"
              :disabled="importing"
            />
          </div>
        </div>

        <!-- ZIP Import -->
        <div v-if="importType === 'zip'" class="import-form">
          <div class="form-group">
            <label>Select ZIP File</label>
            <div class="file-input-wrapper">
              <input
                ref="fileInput"
                type="file"
                accept=".zip"
                class="file-input"
                :disabled="importing"
                @change="onFileSelect"
              />
              <div class="file-input-display" @click="$refs.fileInput.click()">
                <i class="material-icons">upload_file</i>
                <span>{{ selectedFile ? selectedFile.name : 'Choose a ZIP file...' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Local Path Import -->
        <div v-if="importType === 'local'" class="import-form">
          <div class="form-group">
            <label>Local Directory Path</label>
            <div class="path-input-row">
              <input
                v-model="localPath"
                type="text"
                placeholder="/path/to/project"
                class="form-input"
                :disabled="importing"
              />
              <button
                class="btn-browse"
                :disabled="importing"
                @click="showDirBrowser = true"
                title="Browse directories"
              >
                <i class="material-icons">folder_open</i>
              </button>
            </div>
            <div class="form-help">
              Enter a path or click the folder icon to browse
            </div>
          </div>
        </div>

        <!-- Directory Browser Modal -->
        <DirectoryBrowserModal
          :visible="showDirBrowser"
          :initial-path="localPath || '/tmp'"
          @select="onDirectorySelected"
          @close="showDirBrowser = false"
        />
      </div>

      <div class="modal-footer">
        <button class="btn" @click="close">Cancel</button>
        <button
          class="btn btn-primary"
          :disabled="!canImport || importing"
          @click="handleImport"
        >
          {{ importButtonText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import {axiosInstance} from '@/common/utils/axios_utils';
import DirectoryBrowserModal from './common/DirectoryBrowserModal.vue';

export default {
  name: 'ImportProjectModal',

  components: {
    DirectoryBrowserModal
  },

  props: {
    visible: {
      type: Boolean,
      default: false
    }
  },

  data() {
    return {
      importType: 'git',
      importing: false,
      error: null,

      // Git
      gitUrl: '',
      gitBranch: '',

      // ZIP
      selectedFile: null,

      // Local
      localPath: '',
      showDirBrowser: false
    };
  },

  computed: {
    canImport() {
      if (this.importType === 'git') {
        return !!this.gitUrl;
      } else if (this.importType === 'zip') {
        return !!this.selectedFile;
      } else if (this.importType === 'local') {
        return !!this.localPath;
      }
      return false;
    },

    importButtonText() {
      if (this.importing) {
        if (this.importType === 'git') return 'Cloning...';
        if (this.importType === 'zip') return 'Extracting...';
        if (this.importType === 'local') return 'Copying...';
      }
      if (this.importType === 'git') return 'Clone Repository';
      if (this.importType === 'zip') return 'Upload & Extract';
      if (this.importType === 'local') return 'Import Project';
      return 'Import';
    }
  },

  watch: {
    visible(newVal) {
      if (newVal) {
        this.error = null;
      }
    }
  },

  methods: {
    close() {
      this.$emit('close');
    },

    onFileSelect(event) {
      const file = event.target.files[0];
      if (file) {
        this.selectedFile = file;
      }
    },

    onDirectorySelected(path) {
      this.localPath = path;
    },

    async handleImport() {
      if (this.importType === 'git') {
        await this.importFromGit();
      } else if (this.importType === 'zip') {
        await this.importFromZip();
      } else if (this.importType === 'local') {
        await this.importFromLocal();
      }
    },

    async importFromGit() {
      if (!this.gitUrl) return;

      this.importing = true;
      this.error = null;

      try {
        const response = await axiosInstance.post('admin/projects/import', {
          type: 'git',
          url: this.gitUrl.trim(),
          branch: this.gitBranch.trim() || undefined
        });

        this.$emit('imported', response.data);
        this.resetForm();
      } catch (e) {
        this.error = e.response?.data || 'Failed to clone repository';
      } finally {
        this.importing = false;
      }
    },

    async importFromZip() {
      if (!this.selectedFile) return;

      this.importing = true;
      this.error = null;

      try {
        const fileData = await this.readFileAsBase64(this.selectedFile);

        const response = await axiosInstance.post('admin/projects/import', {
          type: 'zip',
          file: fileData,
          filename: this.selectedFile.name
        });

        this.$emit('imported', response.data);
        this.resetForm();
      } catch (e) {
        this.error = e.response?.data || 'Failed to extract ZIP file';
      } finally {
        this.importing = false;
      }
    },

    async importFromLocal() {
      if (!this.localPath) return;

      this.importing = true;
      this.error = null;

      try {
        const response = await axiosInstance.post('admin/projects/import', {
          type: 'local',
          path: this.localPath.trim()
        });

        this.$emit('imported', response.data);
        this.resetForm();
      } catch (e) {
        this.error = e.response?.data || 'Failed to import from local path';
      } finally {
        this.importing = false;
      }
    },

    readFileAsBase64(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
          const base64 = reader.result.split(',')[1];
          resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });
    },

    resetForm() {
      this.gitUrl = '';
      this.gitBranch = '';
      this.selectedFile = null;
      this.localPath = '';
      if (this.$refs.fileInput) {
        this.$refs.fileInput.value = '';
      }
    }
  }
};
</script>

<style scoped>
/* Modal Overlay */
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
  z-index: 1001;
}

.import-modal {
  background: #1a1a1a;
  border-radius: 6px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

/* Header */
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid #333333;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  color: #e0e0e0;
}

.btn-close {
  background: transparent;
  border: none;
  color: #999999;
  font-size: 28px;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.btn-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #e0e0e0;
}

/* Body */
.modal-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.error-message {
  padding: 12px 16px;
  margin-bottom: 16px;
  background: rgba(244, 67, 54, 0.15);
  color: #f44336;
  border-radius: 6px;
  font-size: 13px;
  border-left: 3px solid #f44336;
}

/* Type Selector */
.import-type-selector {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.type-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 16px;
  background: #222222;
  border: 2px solid transparent;
  border-radius: 6px;
  color: #999999;
  cursor: pointer;
  transition: all 0.2s;
}

.type-btn:hover {
  background: #2a2a2a;
}

.type-btn.active {
  border-color: #5dade2;
  color: #5dade2;
}

.type-btn i {
  font-size: 24px;
}

/* Forms */
.import-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 13px;
  font-weight: 500;
  color: #999999;
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #333333;
  border-radius: 6px;
  background: #222222;
  color: #e0e0e0;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #5dade2;
}

.form-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-help {
  font-size: 12px;
  color: #999999;
  margin-top: 4px;
}

/* Path Input Row */
.path-input-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.path-input-row .form-input {
  flex: 1;
}

.btn-browse {
  background: #222222;
  border: 1px solid #333333;
  border-radius: 6px;
  padding: 10px 12px;
  cursor: pointer;
  color: #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-browse:hover:not(:disabled) {
  background: #2a2a2a;
  border-color: #5dade2;
  color: #5dade2;
}

.btn-browse:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-browse i {
  font-size: 20px;
}

/* File Input */
.file-input-wrapper {
  position: relative;
}

.file-input {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.file-input-display {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border: 2px dashed #333333;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  background: #222222;
}

.file-input-display:hover {
  border-color: #5dade2;
  background: #2a2a2a;
}

.file-input-display i {
  font-size: 32px;
  color: #999999;
}

.file-input-display span {
  color: #999999;
}

/* Footer */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px;
  border-top: 1px solid #333333;
  background: #222222;
}

.btn {
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  line-height: 1.2;
  cursor: pointer;
  border: 1px solid #333333;
  background: transparent;
  color: #e0e0e0;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn:hover:not(:disabled) {
  background: #2a2a2a;
  border-color: #5dade2;
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
  border-color: #4a9fd6;
}

.btn-primary:disabled {
  background: #5dade2;
  opacity: 0.5;
}

@media screen and (max-width: 768px) {
  .import-modal {
    width: 95%;
  }

  .import-type-selector {
    flex-direction: column;
  }
}
</style>
