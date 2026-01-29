<template>
  <div class="import-panel">
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
      <button
        class="btn btn-primary import-btn"
        :disabled="!gitUrl || importing"
        @click="importFromGit"
      >
        {{ importing ? 'Cloning...' : 'Clone Repository' }}
      </button>
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
      <button
        class="btn btn-primary import-btn"
        :disabled="!selectedFile || importing"
        @click="importFromZip"
      >
        {{ importing ? 'Extracting...' : 'Upload & Extract' }}
      </button>
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
      <button
        class="btn btn-primary import-btn"
        :disabled="!localPath || importing"
        @click="importFromLocal"
      >
        {{ importing ? 'Copying...' : 'Import Project' }}
      </button>
    </div>

    <!-- Directory Browser Modal -->
    <DirectoryBrowserModal
      :visible="showDirBrowser"
      :initial-path="localPath || '/tmp'"
      @select="onDirectorySelected"
      @close="showDirBrowser = false"
    />
  </div>
</template>

<script>
import {axiosInstance} from '@/common/utils/axios_utils';
import DirectoryBrowserModal from '@/main-app/components/common/DirectoryBrowserModal.vue';

export default {
  name: 'ImportPanel',

  components: {
    DirectoryBrowserModal
  },

  emits: ['import-complete', 'error'],

  data() {
    return {
      importType: 'git',
      importing: false,

      // Git import
      gitUrl: '',
      gitBranch: '',

      // ZIP import
      selectedFile: null,

      // Local import
      localPath: '',
      showDirBrowser: false
    };
  },

  methods: {
    onFileSelect(event) {
      const file = event.target.files[0];
      if (file) {
        this.selectedFile = file;
      }
    },

    onDirectorySelected(path) {
      this.localPath = path;
    },

    async importFromGit() {
      if (!this.gitUrl) return;

      this.importing = true;

      try {
        const response = await axiosInstance.post('admin/projects/import', {
          type: 'git',
          url: this.gitUrl.trim(),
          branch: this.gitBranch.trim() || undefined
        });

        this.gitUrl = '';
        this.gitBranch = '';
        this.$emit('import-complete', response.data);
      } catch (e) {
        this.$emit('error', e.response?.data || 'Failed to clone repository');
      } finally {
        this.importing = false;
      }
    },

    async importFromZip() {
      if (!this.selectedFile) return;

      this.importing = true;

      try {
        const fileData = await this.readFileAsBase64(this.selectedFile);

        const response = await axiosInstance.post('admin/projects/import', {
          type: 'zip',
          file: fileData,
          filename: this.selectedFile.name
        });

        this.selectedFile = null;
        if (this.$refs.fileInput) {
          this.$refs.fileInput.value = '';
        }
        this.$emit('import-complete', response.data);
      } catch (e) {
        this.$emit('error', e.response?.data || 'Failed to extract ZIP file');
      } finally {
        this.importing = false;
      }
    },

    async importFromLocal() {
      if (!this.localPath) return;

      this.importing = true;

      try {
        const response = await axiosInstance.post('admin/projects/import', {
          type: 'local',
          path: this.localPath.trim()
        });

        this.localPath = '';
        this.$emit('import-complete', response.data);
      } catch (e) {
        this.$emit('error', e.response?.data || 'Failed to import from local path');
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
    }
  }
}
</script>

<style scoped>
.import-panel {
  padding: 1.5rem;
}

.import-type-selector {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  justify-content: center;
}

.type-btn {
  flex: 1;
  max-width: 200px;
  padding: 1rem;
  border: 2px solid var(--border-color, #ddd);
  border-radius: var(--border-radius, 8px);
  background: var(--background-color, white);
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.type-btn:hover {
  border-color: var(--primary-color, #1976d2);
}

.type-btn.active {
  border-color: var(--primary-color, #1976d2);
  background: var(--primary-color-light, rgba(25, 118, 210, 0.05));
}

.type-btn i {
  font-size: 32px;
  color: var(--primary-color, #1976d2);
}

.import-form {
  max-width: 600px;
  margin: 0 auto;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color, #ddd);
  border-radius: var(--border-radius, 4px);
  font-size: 1rem;
}

.form-input:disabled {
  background: var(--disabled-color, #f5f5f5);
  cursor: not-allowed;
}

.path-input-row {
  display: flex;
  gap: 0.5rem;
}

.btn-browse {
  padding: 0.75rem;
  border: 1px solid var(--border-color, #ddd);
  border-radius: var(--border-radius, 4px);
  background: var(--background-color, white);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-browse:hover:not(:disabled) {
  background: var(--hover-color, #f5f5f5);
}

.btn-browse:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.form-help {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-color-secondary, #666);
}

.file-input-wrapper {
  position: relative;
}

.file-input {
  display: none;
}

.file-input-display {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border: 2px dashed var(--border-color, #ddd);
  border-radius: var(--border-radius, 4px);
  cursor: pointer;
  transition: all 0.2s ease;
}

.file-input-display:hover {
  border-color: var(--primary-color, #1976d2);
  background: var(--hover-color, #f5f5f5);
}

.file-input-display i {
  font-size: 32px;
  color: var(--primary-color, #1976d2);
}

.import-btn {
  width: 100%;
  padding: 1rem;
  border: none;
  border-radius: var(--border-radius, 4px);
  background: var(--primary-color, #1976d2);
  color: white;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.import-btn:hover:not(:disabled) {
  background: var(--primary-color-dark, #1565c0);
}

.import-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
