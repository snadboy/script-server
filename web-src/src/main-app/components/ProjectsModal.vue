<template>
  <div v-if="visible" class="projects-modal-overlay" @click.self="close">
    <div class="projects-modal">
      <div class="modal-header">
        <span class="modal-title">Project Manager</span>
      </div>

      <!-- Tabs -->
      <div class="modal-tabs">
        <button
          :class="['tab-btn', { active: activeTab === 'projects' }]"
          @click="activeTab = 'projects'"
        >
          Projects
        </button>
        <button
          :class="['tab-btn', { active: activeTab === 'import' }]"
          @click="activeTab = 'import'"
        >
          Import
        </button>
        <button
          v-if="selectedProject"
          :class="['tab-btn', { active: activeTab === 'configure' }]"
          @click="activeTab = 'configure'"
        >
          Configure
        </button>
      </div>

      <div class="modal-body">
        <!-- Error Display -->
        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <!-- Success Display -->
        <div v-if="success" class="success-message">
          {{ success }}
        </div>

        <!-- Projects Tab -->
        <div v-if="activeTab === 'projects'" class="tab-content">
          <div v-if="loading" class="loading">Loading projects...</div>
          <div v-else-if="projects.length === 0" class="no-projects">
            No projects imported yet. Use the Import tab to add a project.
          </div>
          <div v-else class="projects-list">
            <div
              v-for="project in projects"
              :key="project.id"
              :class="['project-row', { selected: selectedProject?.id === project.id }]"
              @click="selectProject(project)"
            >
              <div class="project-info">
                <div class="project-name">{{ project.name }}</div>
                <div class="project-meta">
                  <span class="project-type">{{ project.import_type }}</span>
                  <span v-if="project.source_url" class="project-url">{{ truncateUrl(project.source_url) }}</span>
                  <span v-if="project.imported_at" class="project-date">{{ formatDate(project.imported_at) }}</span>
                </div>
                <div v-if="project.wrapper_script" class="project-status">
                  <i class="material-icons status-icon">check_circle</i>
                  <span>Configured</span>
                </div>
              </div>
              <div class="project-actions">
                <button
                  class="btn-action"
                  @click.stop="configureProject(project)"
                  title="Configure"
                >
                  <i class="material-icons">settings</i>
                </button>
                <button
                  class="btn-delete"
                  :disabled="deleting === project.id"
                  @click.stop="deleteProject(project.id)"
                  title="Delete"
                >
                  <i class="material-icons">{{ deleting === project.id ? 'hourglass_empty' : 'delete' }}</i>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Import Tab -->
        <div v-if="activeTab === 'import'" class="tab-content">
          <div class="import-section">
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
          </div>
        </div>

        <!-- Configure Tab -->
        <div v-if="activeTab === 'configure' && selectedProject" class="tab-content">
          <div class="configure-section">
            <h6>{{ selectedProject.name }}</h6>

            <!-- Dependencies -->
            <div class="config-group">
              <div class="config-group-header">
                <span class="config-label">Dependencies ({{ selectedProject.dependencies?.length || 0 }})</span>
                <button
                  v-if="selectedProject.dependencies?.length > 0"
                  class="btn btn-sm"
                  :disabled="installingDeps"
                  @click="installAllDependencies"
                >
                  {{ installingDeps ? 'Installing...' : 'Install All' }}
                </button>
              </div>
              <div v-if="selectedProject.dependencies?.length > 0" class="deps-list">
                <span v-for="dep in selectedProject.dependencies" :key="dep" class="dep-tag">
                  {{ dep }}
                </span>
              </div>
              <div v-else class="no-deps">No dependencies detected</div>
            </div>

            <!-- Entry Point Selection -->
            <div class="config-group">
              <label class="config-label">Entry Point</label>
              <select v-model="configEntryPoint" class="form-select">
                <option value="">Select an entry point...</option>
                <option v-for="ep in selectedProject.entry_points" :key="ep" :value="ep">
                  {{ ep }}
                </option>
              </select>
              <div class="form-help">
                Or enter custom entry point:
              </div>
              <input
                v-model="customEntryPoint"
                type="text"
                placeholder="module.main:app"
                class="form-input"
              />
            </div>

            <!-- Script Name -->
            <div class="config-group">
              <label class="config-label">Script Name</label>
              <input
                v-model="configScriptName"
                type="text"
                :placeholder="selectedProject.name"
                class="form-input"
              />
            </div>

            <!-- Description -->
            <div class="config-group">
              <label class="config-label">Description</label>
              <input
                v-model="configDescription"
                type="text"
                placeholder="What this script does"
                class="form-input"
              />
            </div>

            <!-- Config Path (optional) -->
            <div class="config-group">
              <label class="config-label">Config Path (optional)</label>
              <input
                v-model="configPath"
                type="text"
                placeholder="/path/to/config.yaml"
                class="form-input"
              />
            </div>

            <!-- Config Command (optional) -->
            <div class="config-group">
              <label class="config-label">Config Command (optional)</label>
              <input
                v-model="configCmd"
                type="text"
                placeholder="run"
                class="form-input"
              />
              <div class="form-help">
                If specified, --config will be injected when this command is used
              </div>
            </div>

            <!-- Wrapper Preview -->
            <div class="config-group">
              <div class="config-group-header">
                <span class="config-label">Wrapper Script Preview</span>
                <button class="btn btn-sm" @click="previewWrapper" :disabled="!effectiveEntryPoint">
                  <i class="material-icons btn-icon-sm">refresh</i>
                  Preview
                </button>
              </div>
              <div v-if="wrapperPreview" class="wrapper-preview">
                <pre>{{ wrapperPreview }}</pre>
              </div>
            </div>

            <!-- Generate Button -->
            <div class="config-actions">
              <button
                class="btn btn-primary"
                :disabled="!effectiveEntryPoint || !configScriptName || generating"
                @click="generateWrapper"
              >
                {{ generating ? 'Generating...' : 'Generate Wrapper & Config' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn waves-effect" @click="close">Close</button>
        <button class="btn waves-effect" @click="refreshProjects" :disabled="loading">
          <i class="material-icons btn-icon">refresh</i>
          Refresh
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import {axiosInstance} from '@/common/utils/axios_utils';

export default {
  name: 'ProjectsModal',

  props: {
    visible: {
      type: Boolean,
      default: false
    }
  },

  data() {
    return {
      activeTab: 'projects',
      projects: [],
      loading: false,
      importing: false,
      deleting: null,
      generating: false,
      installingDeps: false,
      error: null,
      success: null,

      // Import form
      importType: 'git',
      gitUrl: '',
      gitBranch: '',
      selectedFile: null,

      // Configure form
      selectedProject: null,
      configEntryPoint: '',
      customEntryPoint: '',
      configScriptName: '',
      configDescription: '',
      configPath: '',
      configCmd: '',
      wrapperPreview: ''
    };
  },

  computed: {
    effectiveEntryPoint() {
      return this.customEntryPoint || this.configEntryPoint;
    }
  },

  watch: {
    visible(newVal) {
      if (newVal) {
        this.error = null;
        this.success = null;
        this.loadProjects();
      }
    },

    selectedProject(newVal) {
      if (newVal) {
        this.configEntryPoint = newVal.entry_points?.[0] || '';
        this.customEntryPoint = '';
        this.configScriptName = newVal.name || '';
        this.configDescription = '';
        this.configPath = '';
        this.configCmd = '';
        this.wrapperPreview = '';
      }
    }
  },

  methods: {
    close() {
      this.$emit('close');
    },

    async loadProjects() {
      this.loading = true;
      this.error = null;
      try {
        const response = await axiosInstance.get('admin/projects');
        this.projects = response.data.projects || [];
      } catch (e) {
        this.error = 'Failed to load projects';
        console.error('Failed to load projects:', e);
      } finally {
        this.loading = false;
      }
    },

    async refreshProjects() {
      await this.loadProjects();
    },

    selectProject(project) {
      this.selectedProject = project;
    },

    configureProject(project) {
      this.selectedProject = project;
      this.activeTab = 'configure';
    },

    truncateUrl(url) {
      if (!url) return '';
      if (url.length > 40) {
        return '...' + url.slice(-37);
      }
      return url;
    },

    formatDate(dateStr) {
      if (!dateStr) return '';
      const date = new Date(dateStr);
      return date.toLocaleDateString();
    },

    onFileSelect(event) {
      const file = event.target.files[0];
      if (file) {
        this.selectedFile = file;
      }
    },

    async importFromGit() {
      if (!this.gitUrl) return;

      this.importing = true;
      this.error = null;
      this.success = null;

      try {
        const response = await axiosInstance.post('admin/projects/import', {
          type: 'git',
          url: this.gitUrl.trim(),
          branch: this.gitBranch.trim() || undefined
        });

        this.success = `Successfully imported ${response.data.name}`;
        this.gitUrl = '';
        this.gitBranch = '';
        this.selectedProject = response.data;
        await this.loadProjects();
        this.activeTab = 'configure';
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
      this.success = null;

      try {
        // Read file as base64
        const fileData = await this.readFileAsBase64(this.selectedFile);

        const response = await axiosInstance.post('admin/projects/import', {
          type: 'zip',
          file: fileData,
          filename: this.selectedFile.name
        });

        this.success = `Successfully imported ${response.data.name}`;
        this.selectedFile = null;
        if (this.$refs.fileInput) {
          this.$refs.fileInput.value = '';
        }
        this.selectedProject = response.data;
        await this.loadProjects();
        this.activeTab = 'configure';
      } catch (e) {
        this.error = e.response?.data || 'Failed to extract ZIP file';
      } finally {
        this.importing = false;
      }
    },

    readFileAsBase64(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
          // Remove data URL prefix to get just the base64 data
          const base64 = reader.result.split(',')[1];
          resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });
    },

    async deleteProject(projectId) {
      if (!confirm('Are you sure you want to delete this project? This will also remove any generated wrapper scripts and configs.')) {
        return;
      }

      this.deleting = projectId;
      this.error = null;
      this.success = null;

      try {
        await axiosInstance.delete(`admin/projects/${encodeURIComponent(projectId)}/delete`);
        this.success = 'Project deleted successfully';
        if (this.selectedProject?.id === projectId) {
          this.selectedProject = null;
          this.activeTab = 'projects';
        }
        await this.loadProjects();
      } catch (e) {
        this.error = e.response?.data || 'Failed to delete project';
      } finally {
        this.deleting = null;
      }
    },

    async installAllDependencies() {
      if (!this.selectedProject?.dependencies?.length) return;

      this.installingDeps = true;
      this.error = null;
      this.success = null;

      try {
        for (const dep of this.selectedProject.dependencies) {
          try {
            await axiosInstance.post('admin/venv/packages/install', {
              package: dep
            });
          } catch (e) {
            // Continue with other packages even if one fails
            console.warn(`Failed to install ${dep}:`, e);
          }
        }
        this.success = 'Dependencies installed (check Package Manager for details)';
      } catch (e) {
        this.error = 'Failed to install some dependencies';
      } finally {
        this.installingDeps = false;
      }
    },

    async previewWrapper() {
      if (!this.effectiveEntryPoint || !this.selectedProject) return;

      this.error = null;

      try {
        const response = await axiosInstance.post(
          `admin/projects/${encodeURIComponent(this.selectedProject.id)}/wrapper-preview`,
          {
            entry_point: this.effectiveEntryPoint,
            config_path: this.configPath || undefined,
            config_cmd: this.configCmd || undefined
          }
        );
        this.wrapperPreview = response.data.wrapper_content;
      } catch (e) {
        this.error = e.response?.data || 'Failed to generate preview';
      }
    },

    async generateWrapper() {
      if (!this.effectiveEntryPoint || !this.configScriptName || !this.selectedProject) return;

      this.generating = true;
      this.error = null;
      this.success = null;

      try {
        const response = await axiosInstance.post(
          `admin/projects/${encodeURIComponent(this.selectedProject.id)}/wrapper`,
          {
            entry_point: this.effectiveEntryPoint,
            config_path: this.configPath || undefined,
            config_cmd: this.configCmd || undefined,
            script_name: this.configScriptName,
            description: this.configDescription || undefined
          }
        );

        this.success = `Wrapper and config generated! Script "${this.configScriptName}" should now appear in the script list.`;

        // Reload project to get updated metadata
        await this.loadProjects();
        const updated = this.projects.find(p => p.id === this.selectedProject.id);
        if (updated) {
          this.selectedProject = updated;
        }
      } catch (e) {
        this.error = e.response?.data || 'Failed to generate wrapper';
      } finally {
        this.generating = false;
      }
    }
  }
};
</script>

<style scoped>
.projects-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.projects-modal {
  background: var(--background-color);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  width: 90%;
  max-width: 700px;
  max-height: 90vh;
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
  font-size: 1.4em;
  font-weight: 500;
  color: var(--font-color-main);
}

.modal-tabs {
  display: flex;
  border-bottom: 1px solid var(--separator-color);
  padding: 0 24px;
  flex-shrink: 0;
}

.tab-btn {
  padding: 12px 20px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--font-color-medium);
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: var(--font-color-main);
}

.tab-btn.active {
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
}

.modal-body {
  padding: 16px 24px;
  overflow-y: auto;
  flex: 1;
}

.tab-content {
  min-height: 200px;
}

.error-message {
  padding: 10px 12px;
  margin-bottom: 16px;
  background: rgba(244, 67, 54, 0.15);
  color: #f44336;
  border-radius: var(--radius-sm);
  font-size: 13px;
}

.success-message {
  padding: 10px 12px;
  margin-bottom: 16px;
  background: rgba(76, 175, 80, 0.15);
  color: #4caf50;
  border-radius: var(--radius-sm);
  font-size: 13px;
}

.loading,
.no-projects {
  padding: 40px 20px;
  text-align: center;
  color: var(--font-color-medium);
  font-size: 14px;
}

/* Projects List */
.projects-list {
  border: 1px solid var(--separator-color);
  border-radius: var(--radius-sm);
}

.project-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--separator-color);
  cursor: pointer;
  transition: background 0.2s;
}

.project-row:last-child {
  border-bottom: none;
}

.project-row:hover {
  background: var(--background-color-level-4dp);
}

.project-row.selected {
  background: var(--background-color-level-8dp);
}

.project-info {
  flex: 1;
  min-width: 0;
}

.project-name {
  font-size: 15px;
  font-weight: 500;
  color: var(--font-color-main);
  margin-bottom: 4px;
}

.project-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: var(--font-color-medium);
}

.project-type {
  background: var(--background-color-level-8dp);
  padding: 2px 8px;
  border-radius: 4px;
  text-transform: uppercase;
  font-size: 11px;
}

.project-url {
  font-family: monospace;
}

.project-status {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
  font-size: 12px;
  color: var(--status-success-color);
}

.status-icon {
  font-size: 14px;
}

.project-actions {
  display: flex;
  gap: 8px;
}

.btn-action,
.btn-delete {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 6px;
  border-radius: var(--radius-sm);
  color: var(--font-color-medium);
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-action:hover {
  background: var(--background-color-level-8dp);
  color: var(--primary-color);
}

.btn-delete:hover {
  background: rgba(244, 67, 54, 0.15);
  color: #f44336;
}

.btn-delete:disabled,
.btn-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-action i,
.btn-delete i {
  font-size: 20px;
}

/* Import Section */
.import-section {
  padding: 8px 0;
}

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
  gap: 8px;
  padding: 16px;
  background: var(--background-color-level-4dp);
  border: 2px solid transparent;
  border-radius: var(--radius-sm);
  color: var(--font-color-medium);
  cursor: pointer;
  transition: all 0.2s;
}

.type-btn:hover {
  background: var(--background-color-level-8dp);
}

.type-btn.active {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.type-btn i {
  font-size: 24px;
}

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
  color: var(--font-color-medium);
}

.form-input,
.form-select {
  padding: 10px 12px;
  border: 1px solid var(--separator-color);
  border-radius: var(--radius-sm);
  background: var(--background-color-level-4dp);
  color: var(--font-color-main);
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: var(--primary-color);
}

.form-input:disabled,
.form-select:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-help {
  font-size: 12px;
  color: var(--font-color-disabled);
  margin-top: 4px;
}

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
  border: 2px dashed var(--separator-color);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s;
}

.file-input-display:hover {
  border-color: var(--primary-color);
  background: var(--background-color-level-4dp);
}

.file-input-display i {
  font-size: 32px;
  color: var(--font-color-medium);
}

.file-input-display span {
  color: var(--font-color-medium);
}

.import-btn {
  align-self: flex-start;
}

/* Configure Section */
.configure-section h6 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 500;
  color: var(--font-color-main);
}

.config-group {
  margin-bottom: 20px;
}

.config-group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.config-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--font-color-medium);
  display: block;
  margin-bottom: 6px;
}

.config-group-header .config-label {
  margin-bottom: 0;
}

.deps-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.dep-tag {
  background: var(--background-color-level-8dp);
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  color: var(--font-color-main);
  font-family: monospace;
}

.no-deps {
  font-size: 13px;
  color: var(--font-color-disabled);
  font-style: italic;
}

.wrapper-preview {
  background: var(--background-color-level-4dp);
  border: 1px solid var(--separator-color);
  border-radius: var(--radius-sm);
  max-height: 200px;
  overflow: auto;
}

.wrapper-preview pre {
  margin: 0;
  padding: 12px;
  font-size: 11px;
  font-family: monospace;
  white-space: pre-wrap;
  word-break: break-all;
}

.config-actions {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--separator-color);
}

/* Footer */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--separator-color);
  flex-shrink: 0;
  background: var(--background-color-level-16dp);
}

.btn {
  padding: 10px 20px;
  border-radius: var(--radius-sm);
  font-size: 14px;
  line-height: 1.2;
  cursor: pointer;
  border: none;
  background: var(--background-color-high-emphasis);
  color: var(--font-color-main);
  display: flex;
  align-items: center;
  gap: 6px;
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

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.btn-icon {
  font-size: 18px;
}

.btn-icon-sm {
  font-size: 14px;
}

@media screen and (max-width: 768px) {
  .projects-modal {
    width: 95%;
    max-height: 95vh;
  }

  .import-type-selector {
    flex-direction: column;
  }

  .project-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
}
</style>
