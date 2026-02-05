<template>
  <div v-if="visible" class="projects-modal-overlay">
    <div class="projects-modal">
      <div class="modal-header">
        <span class="modal-title">Script Manager</span>
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
          <div class="projects-header">
            <button
              class="btn btn-sm validate-btn"
              :disabled="validating"
              @click="validateAllScripts"
              title="Re-validate all script configurations"
            >
              {{ validating ? 'Validating...' : 'Validate Scripts' }}
            </button>
          </div>
          <div v-if="loading" class="loading">Loading projects...</div>
          <div v-else-if="projects.length === 0" class="no-projects">
            No projects imported yet. Use the Import tab to add a project.
          </div>
          <div v-else class="projects-grid">
            <div
              v-for="project in projects"
              :key="project.id"
              :class="['project-card', { selected: selectedProject?.id === project.id }]"
              @click="selectProject(project)"
            >
              <!-- Action icons in upper right -->
              <div class="card-actions">
                <button
                  class="btn-icon-small"
                  @click.stop="configureProject(project)"
                  title="Configure"
                >
                  <i class="material-icons">settings</i>
                </button>
                <button
                  class="btn-icon-small delete-btn"
                  :disabled="deleting === project.id"
                  @click.stop="deleteProject(project.id)"
                  title="Delete"
                >
                  <i class="material-icons">{{ deleting === project.id ? 'hourglass_empty' : 'delete' }}</i>
                </button>
              </div>

              <div class="card-header">
                <div class="card-title">{{ project.name }}</div>
                <div class="card-date">{{ formatDate(project.imported_at) }}</div>
              </div>
              <div class="card-body">
                <!-- Source badge above path -->
                <span class="card-badge-inline">{{ project.import_type }}</span>
                <div v-if="project.source_url" class="card-description">
                  {{ truncateUrl(project.source_url) }}
                </div>

                <!-- Configuration details (always shown) -->
                <div class="config-details">
                  <!-- Instances -->
                  <div class="config-section">
                    <div class="config-section-label">
                      Instances ({{ getProjectInstances(project.id).length }}):
                    </div>
                    <div class="config-list">
                      <div
                        v-for="instance in getProjectInstances(project.id)"
                        :key="instance"
                        class="config-list-item"
                      >
                        {{ instance }}
                      </div>
                      <div v-if="getProjectInstances(project.id).length === 0" class="config-list-empty">
                        None
                      </div>
                    </div>
                  </div>

                  <!-- Parameters -->
                  <div class="config-section">
                    <div class="config-section-label">
                      Parameters ({{ project.parameters?.length || 0 }}):
                    </div>
                    <div class="config-list">
                      <div
                        v-for="param in project.parameters"
                        :key="param.name"
                        class="config-list-item"
                        :title="param.description"
                      >
                        {{ param.name }}
                      </div>
                      <div v-if="!project.parameters || project.parameters.length === 0" class="config-list-empty">
                        None
                      </div>
                    </div>
                  </div>

                  <!-- Verbs -->
                  <div class="config-section">
                    <div class="config-section-label">
                      Verbs ({{ project.verbs?.options?.length || 0 }}):
                    </div>
                    <div class="config-list">
                      <div
                        v-for="verb in project.verbs?.options"
                        :key="verb.name"
                        class="config-list-item"
                        :title="verb.description"
                      >
                        {{ verb.name }}
                      </div>
                      <div v-if="!project.verbs || !project.verbs.options || project.verbs.options.length === 0" class="config-list-empty">
                        None
                      </div>
                    </div>
                  </div>
                </div>
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
        </div>

        <!-- Configure Tab -->
        <div v-if="activeTab === 'configure' && selectedProject" class="tab-content">
          <div class="configure-section">
            <h6>{{ selectedProject.name }}</h6>

            <!-- Project Configuration -->
            <div class="config-group highlighted-section">
              <div class="config-group-header">
                <span class="config-label">Project Configuration</span>
              </div>
              <div class="config-info">
                <p>
                  Define parameters and verbs at the project level. Script instances can then
                  select which parameters to include and override default values.
                </p>
                <div class="config-stats">
                  <span class="stat-badge">
                    <i class="material-icons">list</i>
                    {{ selectedProject.parameters?.length || 0 }} Parameters
                  </span>
                  <span class="stat-badge">
                    <i class="material-icons">code</i>
                    {{ selectedProject.verbs?.options?.length || 0 }} Verbs
                  </span>
                </div>
                <button
                  class="btn btn-sm btn-primary config-btn-inline"
                  @click="openProjectConfig"
                >
                  <i class="material-icons btn-icon-sm">tune</i>
                  Configure Parameters & Verbs
                </button>
              </div>
            </div>

            <!-- Dependencies -->
            <div class="config-group">
              <div class="config-group-header">
                <span class="config-label">
                  Dependencies ({{ selectedProject.dependencies?.length || 0 }})
                  <span v-if="loadingPackages" class="loading-indicator">checking...</span>
                  <span v-else-if="allDependenciesInstalled" class="all-installed-badge">All Installed</span>
                </span>
                <button
                  v-if="selectedProject.dependencies?.length > 0 && missingDependencies.length > 0"
                  class="btn btn-sm"
                  :disabled="installingDeps || loadingPackages"
                  @click="installAllDependencies"
                >
                  {{ installingDeps ? 'Installing...' : `Install Missing (${missingDependencies.length})` }}
                </button>
              </div>
              <div v-if="selectedProject.dependencies?.length > 0" class="deps-list">
                <span
                  v-for="dep in selectedProject.dependencies"
                  :key="dep"
                  :class="['dep-tag', { 'dep-installed': isPackageInstalled(dep) }]"
                >
                  <i v-if="isPackageInstalled(dep)" class="material-icons dep-check">check_circle</i>
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
              <button
                type="button"
                class="btn-link advanced-toggle"
                @click="showCustomEntryPoint = !showCustomEntryPoint"
              >
                {{ showCustomEntryPoint ? '− Hide custom entry point' : '+ Custom entry point' }}
              </button>
              <div v-if="showCustomEntryPoint" class="custom-entry-point">
                <input
                  v-model="customEntryPoint"
                  type="text"
                  placeholder="module.main:app"
                  class="form-input"
                />
                <div class="form-help">
                  Use if the detected entry points don't include what you need
                </div>
              </div>
            </div>

            <!-- Create Script Instance Button -->
            <div class="config-actions">
              <button
                class="btn btn-primary"
                :disabled="!effectiveEntryPoint"
                @click="openCreateScriptInstance"
              >
                <i class="material-icons btn-icon">add</i>
                Create Script Instance
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn waves-effect" @click="close">Close</button>
      </div>
    </div>

    <!-- Project Configuration Modal -->
    <ProjectConfigPlaygroundModal
      :visible="showProjectConfig"
      :project="selectedProject"
      @close="closeProjectConfig"
      @saved="onProjectConfigSaved"
    />

    <!-- Create Script Instance Modal -->
    <CreateScriptInstanceModal
      :visible="showCreateScriptInstance"
      :project="selectedProject"
      :entryPoint="effectiveEntryPoint"
      @close="closeCreateScriptInstance"
      @created="onScriptInstanceCreated"
    />

  </div>
</template>

<script>
import {axiosInstance} from '@/common/utils/axios_utils';
import DirectoryBrowserModal from './common/DirectoryBrowserModal.vue';
import ProjectConfigPlaygroundModal from '@/admin/components/projects/ProjectConfigPlaygroundModal.vue';
import CreateScriptInstanceModal from './CreateScriptInstanceModal.vue';

export default {
  name: 'ProjectsModalPlayground',

  components: {
    DirectoryBrowserModal,
    ProjectConfigPlaygroundModal,
    CreateScriptInstanceModal
  },

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
      validating: false,
      error: null,
      success: null,
      // Import form
      importType: 'git',
      gitUrl: '',
      gitBranch: '',
      selectedFile: null,
      localPath: '',
      showDirBrowser: false,

      // Configure form
      selectedProject: null,
      configEntryPoint: '',
      customEntryPoint: '',
      showCustomEntryPoint: false,
      configScriptName: '',
      configDescription: '',
      installedPackages: [],
      loadingPackages: false,

      // Modals
      showProjectConfig: false,
      showCreateScriptInstance: false
    };
  },

  computed: {
    effectiveEntryPoint() {
      return this.customEntryPoint || this.configEntryPoint;
    },

    missingDependencies() {
      if (!this.selectedProject?.dependencies) return [];
      const installedLower = this.installedPackages.map(p => p.toLowerCase());
      return this.selectedProject.dependencies.filter(
        dep => !installedLower.includes(dep.toLowerCase())
      );
    },

    allDependenciesInstalled() {
      return this.selectedProject?.dependencies?.length > 0 &&
             this.missingDependencies.length === 0;
    },

    existingScriptNames() {
      const adminScripts = this.$store.state.adminScripts?.scripts || [];
      return adminScripts.map(s => s.name.toLowerCase());
    },

    scriptNameError() {
      if (!this.configScriptName || !this.configScriptName.trim()) {
        return null; // Don't show error for empty field
      }
      const nameLower = this.configScriptName.toLowerCase();
      const exists = this.existingScriptNames.includes(nameLower);
      console.log('[ProjectsModalPlayground] Checking script name:', this.configScriptName);
      console.log('[ProjectsModalPlayground] Existing names:', this.existingScriptNames);
      console.log('[ProjectsModalPlayground] Duplicate found:', exists);
      if (exists) {
        return 'A script with this name already exists';
      }
      return null;
    }
  },

  watch: {
    visible(newVal) {
      if (newVal) {
        this.error = null;
        this.success = null;
        this.loadProjects();
        // Load adminScripts store for name validation
        if (this.$store.state.adminScripts) {
          this.$store.dispatch('adminScripts/init');
        }
      }
    },

    selectedProject(newVal) {
      if (newVal) {
        console.log('Selected project:', newVal);
        console.log('Entry points:', newVal.entry_points);
        // Use nextTick to ensure dropdown options are rendered before setting value
        this.$nextTick(() => {
          this.configEntryPoint = newVal.entry_points?.[0] || '';
          console.log('Set configEntryPoint to:', this.configEntryPoint);
        });
        this.customEntryPoint = '';
        this.configScriptName = newVal.name || '';
        this.configDescription = '';
        this.loadInstalledPackages();
      }
    }
  },

  methods: {
    close() {
      this.$emit('close');
    },

    getProjectInstances(projectId) {
      // Get all scripts and filter for instances created from this project
      const allScripts = this.$store.state.scripts?.scripts || [];
      const adminScripts = this.$store.state.adminScripts?.scripts || [];

      // Try both stores (scripts for main app, adminScripts for admin view)
      const scripts = allScripts.length > 0 ? allScripts : adminScripts;

      return scripts
        .filter(script => {
          // Check if script has project_id field matching this project
          return script.project_id === projectId;
        })
        .map(script => script.name);
    },

    async loadInstalledPackages() {
      this.loadingPackages = true;
      try {
        const response = await axiosInstance.get('admin/venv/packages');
        // Extract package names from the response
        this.installedPackages = (response.data.packages || []).map(p => p.name || p);
      } catch (e) {
        console.warn('Failed to load installed packages:', e);
        this.installedPackages = [];
      } finally {
        this.loadingPackages = false;
      }
    },

    isPackageInstalled(dep) {
      const depLower = dep.toLowerCase();
      return this.installedPackages.some(p => p.toLowerCase() === depLower);
    },

    async loadProjects() {
      this.loading = true;
      this.error = null;
      try {
        const response = await axiosInstance.get('admin/projects');
        console.log('Projects API response:', response.data);
        this.projects = response.data.projects || [];
        console.log('Loaded projects:', this.projects);
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

    async validateAllScripts() {
      this.validating = true;
      this.error = null;
      this.success = null;
      try {
        const response = await axiosInstance.post('admin/scripts/validate');
        const { validated, invalid_count } = response.data;

        if (invalid_count > 0) {
          this.success = `Validated ${validated} scripts. Found ${invalid_count} invalid script(s). Check sidebar for warnings.`;
        } else {
          this.success = `All ${validated} scripts validated successfully!`;
        }

        // Refresh scripts list to show updated validation status
        await this.$store.dispatch('scripts/init');
      } catch (e) {
        this.error = 'Failed to validate scripts: ' + (e.response?.data?.message || e.message);
        console.error('Failed to validate scripts:', e);
      } finally {
        this.validating = false;
      }
    },

    selectProject(project) {
      this.selectedProject = project;
    },

    configureProject(project) {
      this.selectedProject = project;
      this.activeTab = 'configure';
    },

    openProjectConfig() {
      this.showProjectConfig = true;
    },

    closeProjectConfig() {
      this.showProjectConfig = false;
    },

    onProjectConfigSaved() {
      this.success = 'Project configuration saved successfully!';
      setTimeout(() => {
        this.success = null;
      }, 3000);
      // Reload projects to get updated parameter/verb counts
      this.loadProjects();
    },

    openCreateScriptInstance() {
      this.showCreateScriptInstance = true;
    },

    closeCreateScriptInstance() {
      this.showCreateScriptInstance = false;
    },

    onScriptInstanceCreated() {
      this.success = 'Script instance created successfully!';
      setTimeout(() => {
        this.success = null;
      }, 3000);
      this.showCreateScriptInstance = false;
      // Don't close the main Script Manager modal - keep it open
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

    async importFromLocal() {
      if (!this.localPath) return;

      this.importing = true;
      this.error = null;
      this.success = null;

      try {
        const response = await axiosInstance.post('admin/projects/import', {
          type: 'local',
          path: this.localPath.trim()
        });

        this.success = `Successfully imported ${response.data.name}`;
        this.localPath = '';
        this.selectedProject = response.data;
        await this.loadProjects();
        this.activeTab = 'configure';
      } catch (e) {
        this.error = e.response?.data || 'Failed to import from local path';
      } finally {
        this.importing = false;
      }
    },

    onDirectorySelected(path) {
      this.localPath = path;
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
      if (!confirm('Are you sure you want to delete this project? This will also remove any associated scripts.')) {
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
      const toInstall = this.missingDependencies;
      if (!toInstall.length) return;

      this.installingDeps = true;
      this.error = null;
      this.success = null;

      let installed = 0;
      let failed = 0;

      try {
        for (const dep of toInstall) {
          try {
            await axiosInstance.post('admin/venv/packages/install', {
              package: dep
            });
            installed++;
          } catch (e) {
            // Continue with other packages even if one fails
            console.warn(`Failed to install ${dep}:`, e);
            failed++;
          }
        }

        // Reload installed packages to update UI
        await this.loadInstalledPackages();

        if (failed === 0) {
          this.success = `Successfully installed ${installed} package${installed !== 1 ? 's' : ''}`;
        } else {
          this.success = `Installed ${installed} package${installed !== 1 ? 's' : ''}, ${failed} failed`;
        }
      } catch (e) {
        this.error = 'Failed to install dependencies';
      } finally {
        this.installingDeps = false;
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
            script_name: this.configScriptName,
            description: this.configDescription || undefined
          }
        );

        this.success = `Script "${this.configScriptName}" created successfully! It should now appear in your script list.`;

        // Reload project to get updated metadata
        await this.loadProjects();
        const updated = this.projects.find(p => p.id === this.selectedProject.id);
        if (updated) {
          this.selectedProject = updated;
        }

        // Refresh scripts list in sidebar
        await this.$store.dispatch('scripts/init');

        // Refresh adminScripts store to update validation
        if (this.$store.state.adminScripts) {
          await this.$store.dispatch('adminScripts/init');
        }

        // Reset form
        this.configScriptName = '';
        this.configDescription = '';
      } catch (e) {
        this.error = e.response?.data || 'Failed to create script';
      } finally {
        this.generating = false;
      }
    }
  }
};
</script>

<style scoped>
/* CSS Variables - Compact Playground Design */
.projects-modal-overlay {
  /* Define CSS variables on component root */
  --dialog-bg: #1a1a1a;
  --card-bg: #222222;
  --accent: #5dade2;
  --border: #333333;
  --text: #e0e0e0;
  --text-muted: #999999;
  --radius: 6px;
  --header-padding: 16px;
  --content-padding: 20px;
  --card-gap: 12px;
  --header-size: 20px;
  --tab-size: 14px;
  --card-title-size: 16px;
  --card-desc-size: 13px;

  /* Component styles */
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
  background: var(--dialog-bg);
  border-radius: var(--radius);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  width: 90%;
  max-width: 900px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--header-padding);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.modal-title {
  font-size: var(--header-size);
  font-weight: 500;
  color: var(--text);
}

.modal-tabs {
  display: flex;
  border-bottom: 1px solid var(--border);
  padding: 0 var(--content-padding);
  flex-shrink: 0;
}

.tab-btn {
  padding: 12px 20px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--text-muted);
  cursor: pointer;
  font-size: var(--tab-size);
  transition: all 0.2s;
}

.tab-btn:hover {
  color: var(--text);
}

.tab-btn.active {
  color: var(--accent);
  border-bottom-color: var(--accent);
}

.modal-body {
  padding: var(--content-padding);
  overflow-y: auto;
  flex: 1;
}

.tab-content {
  min-height: 200px;
}

.projects-header {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 16px;
}

.validate-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  font-size: 13px;
  background: var(--card-bg);
  border: 1px solid var(--border);
  color: var(--text);
  border-radius: var(--radius);
  cursor: pointer;
  transition: all 0.2s;
}

.validate-btn:hover:not(:disabled) {
  background: #2a2a2a;
  border-color: var(--accent);
}

.validate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.validate-btn .btn-icon-sm {
  font-size: 18px;
  margin: 0;
  line-height: 1;
}

.error-message {
  padding: 12px 16px;
  margin-bottom: 16px;
  background: rgba(244, 67, 54, 0.15);
  color: #f44336;
  border-radius: var(--radius);
  font-size: 13px;
  border-left: 3px solid #f44336;
}

.success-message {
  padding: 12px 16px;
  margin-bottom: 16px;
  background: rgba(76, 175, 80, 0.15);
  color: #4caf50;
  border-radius: var(--radius);
  font-size: 13px;
  border-left: 3px solid #4caf50;
}

.loading,
.no-projects {
  padding: 40px 20px;
  text-align: center;
  color: var(--text-muted);
  font-size: 14px;
}

/* Projects Grid - Card Layout */
.projects-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--card-gap);
}

.project-card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  gap: 12px;
  position: relative;
}

.project-card:hover {
  border-color: var(--accent);
  transform: translateY(-2px);
}

.project-card.selected {
  border-color: var(--accent);
  background: #252525;
}

.card-actions {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  gap: 6px;
  z-index: 10;
}

.btn-icon-small {
  background: transparent;
  border: none;
  padding: 4px;
  cursor: pointer;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  border-radius: 4px;
}

.btn-icon-small:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
  color: var(--accent);
}

.btn-icon-small.delete-btn:hover:not(:disabled) {
  color: #f44336;
}

.btn-icon-small:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-icon-small i {
  font-size: 20px;
}

.card-header {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-right: 60px;
}

.card-title {
  font-size: var(--card-title-size);
  font-weight: 500;
  color: var(--text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-badge-inline {
  background: #2a2a2a;
  color: var(--accent);
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 11px;
  text-transform: uppercase;
  font-weight: 500;
  width: fit-content;
}

.card-date {
  font-size: 12px;
  color: var(--text-muted);
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.card-description {
  font-size: var(--card-desc-size);
  color: var(--text-muted);
  font-family: monospace;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.config-details {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 12px;
}

.config-section {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.config-section-label {
  font-size: 11px;
  color: var(--text-muted);
  font-weight: 500;
  text-transform: uppercase;
  white-space: nowrap;
}

.config-list {
  display: flex;
  flex-direction: column;
  max-height: 60px;
  overflow-y: auto;
  gap: 0;
  padding: 0;
  border: 1px solid var(--border);
  border-radius: 3px;
  background: rgba(0, 0, 0, 0.2);
}

.config-list::-webkit-scrollbar {
  width: 4px;
}

.config-list::-webkit-scrollbar-track {
  background: transparent;
}

.config-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}

.config-list-item {
  font-size: 11px;
  color: var(--accent);
  font-family: monospace;
  padding: 4px 6px;
  cursor: help;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  height: 20px;
  line-height: 12px;
  flex-shrink: 0;
}

.config-list-item:hover {
  background: rgba(93, 173, 226, 0.15);
}

.config-list-empty {
  font-size: 11px;
  color: var(--text-muted);
  font-style: italic;
  padding: 4px 6px;
  height: 20px;
  line-height: 12px;
  flex-shrink: 0;
}

/* Old card-footer and btn-icon-action styles removed - now using card-actions with btn-icon-small */

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
  background: var(--card-bg);
  border: 2px solid transparent;
  border-radius: var(--radius);
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s;
}

.type-btn:hover {
  background: #2a2a2a;
}

.type-btn.active {
  border-color: var(--accent);
  color: var(--accent);
}

.type-btn i {
  font-size: 24px;
}

.import-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.path-input-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.path-input-row .form-input {
  flex: 1;
}

.btn-browse {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 10px 12px;
  cursor: pointer;
  color: var(--text);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-browse:hover:not(:disabled) {
  background: #2a2a2a;
  border-color: var(--accent);
  color: var(--accent);
}

.btn-browse:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-browse i {
  font-size: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-muted);
}

.form-input,
.form-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--card-bg);
  color: var(--text);
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-select {
  opacity: 1;
  -webkit-appearance: menulist;
  -moz-appearance: menulist;
  appearance: menulist;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: var(--accent);
}

.form-input:disabled,
.form-select:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-help {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 4px;
}

.form-input.input-error {
  border-color: #f44336;
}

.validation-error {
  font-size: 12px;
  color: #f44336;
  margin-top: 4px;
}

.btn-link {
  background: none;
  border: none;
  color: var(--accent);
  font-size: 12px;
  cursor: pointer;
  padding: 4px 0;
  margin-top: 6px;
}

.btn-link:hover {
  text-decoration: underline;
}

.advanced-toggle {
  display: block;
}

.custom-entry-point {
  margin-top: 8px;
}

.custom-entry-point .form-help {
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
  border: 2px dashed var(--border);
  border-radius: var(--radius);
  cursor: pointer;
  transition: all 0.2s;
  background: var(--card-bg);
}

.file-input-display:hover {
  border-color: var(--accent);
  background: #2a2a2a;
}

.file-input-display i {
  font-size: 32px;
  color: var(--text-muted);
}

.file-input-display span {
  color: var(--text-muted);
}

.import-btn {
  align-self: flex-start;
}

/* Configure Section */
.configure-section h6 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 500;
  color: var(--text);
}

.config-group {
  margin-bottom: 20px;
}

.config-group.highlighted-section {
  background: rgba(93, 173, 226, 0.08);
  border: 1px solid rgba(93, 173, 226, 0.3);
  border-radius: var(--radius);
  padding: 16px;
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
  color: var(--text-muted);
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
  background: #2a2a2a;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
  color: var(--text);
  font-family: monospace;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border: 1px solid var(--border);
}

.dep-tag.dep-installed {
  background: rgba(76, 175, 80, 0.15);
  color: #4caf50;
  border-color: #4caf50;
}

.dep-check {
  font-size: 14px;
}

.loading-indicator {
  font-size: 11px;
  font-weight: normal;
  color: var(--text-muted);
  font-style: italic;
}

.all-installed-badge {
  font-size: 11px;
  font-weight: normal;
  background: rgba(76, 175, 80, 0.15);
  color: #4caf50;
  padding: 2px 8px;
  border-radius: 4px;
  margin-left: 8px;
}

.no-deps {
  font-size: 13px;
  color: var(--text-muted);
  font-style: italic;
}

.config-actions {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--border);
}

/* Footer */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: var(--header-padding);
  border-top: 1px solid var(--border);
  flex-shrink: 0;
  background: var(--card-bg);
}

.btn {
  padding: 10px 20px;
  border-radius: var(--radius);
  font-size: 14px;
  line-height: 1.2;
  cursor: pointer;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text);
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.btn:hover:not(:disabled) {
  background: #2a2a2a;
  border-color: var(--accent);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--accent);
  color: #000;
  border-color: var(--accent);
}

.btn-primary:hover:not(:disabled) {
  background: #4a9fd6;
  border-color: #4a9fd6;
}

.btn-primary:disabled {
  background: var(--accent);
  opacity: 0.5;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.btn-icon {
  font-size: 18px;
}

.btn-icon-sm {
  font-size: 16px;
}

.config-info {
  padding: 12px;
  background: #2a2a2a;
  border-radius: var(--radius);
  border: 1px solid var(--border);
}

.config-info p {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: var(--text-muted);
  line-height: 1.5;
}

.config-stats {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.stat-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text);
}

.stat-badge .material-icons {
  font-size: 16px;
  color: var(--accent);
}

.config-btn-inline {
  margin-top: 12px;
  width: 100%;
}

@media screen and (max-width: 768px) {
  .projects-modal {
    width: 95%;
    max-height: 95vh;
  }

  .projects-grid {
    grid-template-columns: 1fr;
  }

  .import-type-selector {
    flex-direction: column;
  }
}
</style>
