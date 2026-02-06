<template>
  <div v-if="visible" class="projects-modal-overlay">
    <div class="projects-modal">
      <div class="modal-header">
        <h2 class="modal-title">Script Manager</h2>
        <div class="header-actions">
          <button class="btn btn-secondary" @click="openImportModal">
            <i class="material-icons">add</i>
            Import Project
          </button>
          <button
            class="btn btn-secondary"
            :disabled="validating"
            @click="validateAllScripts"
          >
            <i class="material-icons">check_circle</i>
            {{ validating ? 'Validating...' : 'Validate Scripts' }}
          </button>
        </div>
        <button class="btn-close" @click="close">×</button>
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

        <!-- Loading State -->
        <div v-if="loading" class="loading">Loading projects...</div>

        <!-- Empty State -->
        <div v-else-if="projects.length === 0" class="no-projects">
          No projects imported yet. Click "Import Project" to add a project.
        </div>

        <!-- Projects Table -->
        <div v-else class="projects-table-container">
          <table class="projects-table">
            <thead>
              <tr>
                <th class="col-project">Project</th>
                <th class="col-actions">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="project in projects"
                :key="project.id"
                class="project-row"
              >
                <td class="project-info">
                  <!-- Header: Name + Metadata -->
                  <div class="project-header">
                    <div class="project-title">{{ project.name }}</div>
                    <div class="project-meta">
                      <span class="badge-type">{{ project.import_type }}</span>
                      <span class="project-date">{{ formatDate(project.imported_at) }}</span>
                    </div>
                  </div>

                  <!-- Source URL (if applicable) -->
                  <div v-if="project.source_url" class="project-source">
                    {{ truncateUrl(project.source_url) }}
                  </div>

                  <!-- Stats Grid: 2x2 layout -->
                  <div class="project-stats">
                    <!-- Row 1 -->
                    <div class="stat-block stat-instances">
                      <div class="stat-label">Instances ({{ getInstanceCount(project.id) }})</div>
                      <div class="stat-list">
                        <span
                          v-for="inst in getProjectInstances(project.id)"
                          :key="inst"
                          class="stat-item"
                        >
                          {{ inst }}
                        </span>
                        <span v-if="getProjectInstances(project.id).length === 0" class="stat-empty">
                          None
                        </span>
                      </div>
                    </div>

                    <div class="stat-block stat-connections">
                      <div class="stat-label">Connections ({{ getConnectionCount(project) }})</div>
                      <div class="stat-list">
                        <span
                          v-for="conn in project.supported_connections"
                          :key="conn"
                          class="stat-item"
                        >
                          {{ getConnectionLabel(conn) }}
                        </span>
                        <span v-if="!project.supported_connections?.length" class="stat-empty">
                          All connections
                        </span>
                      </div>
                    </div>

                    <!-- Row 2 -->
                    <div class="stat-block stat-parameters">
                      <div class="stat-label">Parameters ({{ project.parameters?.length || 0 }})</div>
                      <div class="stat-list">
                        <code
                          v-for="param in (project.parameters || []).slice(0, 3)"
                          :key="param.name"
                          class="stat-item"
                        >
                          {{ param.name }}
                        </code>
                        <span v-if="(project.parameters?.length || 0) > 3" class="stat-more">
                          +{{ project.parameters.length - 3 }}
                        </span>
                        <span v-if="!project.parameters?.length" class="stat-empty">
                          None
                        </span>
                      </div>
                    </div>

                    <div class="stat-block stat-verbs">
                      <div class="stat-label">Verbs ({{ project.verbs?.options?.length || 0 }})</div>
                      <div class="stat-list">
                        <code
                          v-for="verb in (project.verbs?.options || []).slice(0, 3)"
                          :key="verb.name"
                          class="stat-item"
                        >
                          {{ verb.name }}
                        </code>
                        <span v-if="(project.verbs?.options?.length || 0) > 3" class="stat-more">
                          +{{ project.verbs.options.length - 3 }}
                        </span>
                        <span v-if="!project.verbs?.options?.length" class="stat-empty">
                          None
                        </span>
                      </div>
                    </div>
                  </div>
                </td>

                <td class="project-actions">
                  <button
                    class="btn-icon"
                    @click="configureProject(project)"
                    title="Configure"
                  >
                    <i class="material-icons">settings</i>
                  </button>
                  <button
                    class="btn-icon btn-delete"
                    :disabled="deleting === project.id"
                    @click="deleteProject(project.id)"
                    title="Delete"
                  >
                    <i class="material-icons">{{ deleting === project.id ? 'hourglass_empty' : 'delete' }}</i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn" @click="close">Close</button>
      </div>
    </div>

    <!-- Import Modal -->
    <ImportProjectModal
      :visible="showImportModal"
      @close="closeImportModal"
      @imported="onProjectImported"
    />

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
import ImportProjectModal from './ImportProjectModal.vue';
import ProjectConfigPlaygroundModal from '@/admin/components/projects/ProjectConfigPlaygroundModal.vue';
import CreateScriptInstanceModal from './CreateScriptInstanceModal.vue';

export default {
  name: 'ProjectsModalPlayground',

  components: {
    ImportProjectModal,
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
      projects: [],
      loading: false,
      deleting: null,
      validating: false,
      error: null,
      success: null,

      // Selected project for configure
      selectedProject: null,
      configEntryPoint: '',
      customEntryPoint: '',
      showCustomEntryPoint: false,
      installedPackages: [],
      loadingPackages: false,

      // Modals
      showImportModal: false,
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
        this.$nextTick(() => {
          this.configEntryPoint = newVal.entry_points?.[0] || '';
        });
        this.customEntryPoint = '';
        this.loadInstalledPackages();
      }
    }
  },

  methods: {
    close() {
      this.$emit('close');
    },

    getProjectInstances(projectId) {
      const allScripts = this.$store.state.scripts?.scripts || [];
      const adminScripts = this.$store.state.adminScripts?.scripts || [];
      const scripts = allScripts.length > 0 ? allScripts : adminScripts;

      return scripts
        .filter(script => script.project_id === projectId)
        .map(script => script.name);
    },

    getInstanceCount(projectId) {
      return this.getProjectInstances(projectId).length;
    },

    getConnectionCount(project) {
      return project.supported_connections?.length || 0;
    },

    getConnectionLabel(connType) {
      const labels = {
        'plex': 'Plex',
        'sonarr': 'Sonarr',
        'radarr': 'Radarr',
        'home-assistant': 'Home Assistant',
        'google': 'Google',
        'generic': 'Generic'
      };
      return labels[connType] || connType;
    },

    async loadInstalledPackages() {
      this.loadingPackages = true;
      try {
        const response = await axiosInstance.get('admin/venv/packages');
        this.installedPackages = (response.data.packages || []).map(p => p.name || p);
      } catch (e) {
        console.warn('Failed to load installed packages:', e);
        this.installedPackages = [];
      } finally {
        this.loadingPackages = false;
      }
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

        await this.$store.dispatch('scripts/init');
      } catch (e) {
        this.error = 'Failed to validate scripts: ' + (e.response?.data?.message || e.message);
        console.error('Failed to validate scripts:', e);
      } finally {
        this.validating = false;
      }
    },

    configureProject(project) {
      this.selectedProject = project;
      this.showProjectConfig = true;
    },

    openImportModal() {
      this.showImportModal = true;
    },

    closeImportModal() {
      this.showImportModal = false;
    },

    async onProjectImported(project) {
      this.success = `Successfully imported ${project.name}`;
      this.closeImportModal();
      await this.loadProjects();
      this.selectedProject = project;
      this.showProjectConfig = true; // Auto-open configure for new project
    },

    closeProjectConfig() {
      this.showProjectConfig = false;
    },

    onProjectConfigSaved() {
      this.success = 'Project configuration saved successfully!';
      setTimeout(() => {
        this.success = null;
      }, 3000);
      this.loadProjects();
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
    },

    truncateUrl(url) {
      if (!url) return '';
      if (url.length > 60) {
        return '...' + url.slice(-57);
      }
      return url;
    },

    formatDate(dateStr) {
      if (!dateStr) return '';
      const date = new Date(dateStr);
      return date.toLocaleDateString();
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
        }
        await this.loadProjects();
      } catch (e) {
        this.error = e.response?.data || 'Failed to delete project';
      } finally {
        this.deleting = null;
      }
    }
  }
};
</script>

<style scoped>
/* CSS Variables */
.projects-modal-overlay {
  --dialog-bg: #1a1a1a;
  --card-bg: #222222;
  --accent: #5dade2;
  --border: #333333;
  --text: #e0e0e0;
  --text-muted: #999999;
  --radius: 6px;
  --header-padding: 16px;

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
  max-width: 1100px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

/* Header */
.modal-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: var(--header-padding);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.modal-title {
  font-size: 20px;
  font-weight: 500;
  color: var(--text);
  margin: 0;
  flex: 0 0 auto;
}

.header-actions {
  flex: 1;
  display: flex;
  gap: 8px;
}

.btn-close {
  margin-left: auto;
  background: transparent;
  border: none;
  color: var(--text-muted);
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
  color: var(--text);
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

/* Projects Table */
.projects-table-container {
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
}

.projects-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--card-bg);
}

.projects-table thead {
  background: var(--dialog-bg);
  position: sticky;
  top: 0;
  z-index: 1;
}

.projects-table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  font-size: 13px;
  color: var(--text-muted);
  text-transform: uppercase;
  border-bottom: 2px solid var(--border);
}

.col-project {
  width: 100%;
}

.col-actions {
  width: 100px;
  text-align: center;
}

.projects-table tbody tr {
  border-bottom: 1px solid var(--border);
  transition: background-color 0.2s;
}

.projects-table tbody tr:hover {
  background: rgba(93, 173, 226, 0.05);
}

.projects-table tbody tr:last-child {
  border-bottom: none;
}

.project-info {
  padding: 16px;
}

.project-actions {
  padding: 16px;
  text-align: center;
  white-space: nowrap;
}

/* Project Header */
.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.project-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
}

.project-meta {
  display: flex;
  gap: 8px;
  align-items: center;
}

.badge-type {
  font-size: 10px;
  padding: 2px 8px;
  background: var(--accent);
  color: #000;
  border-radius: 3px;
  text-transform: uppercase;
  font-weight: 600;
}

.project-date {
  font-size: 12px;
  color: var(--text-muted);
}

.project-source {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 12px;
  font-family: monospace;
}

/* Stats Grid (2x2) */
.project-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 12px;
}

.stat-block {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 8px;
}

.stat-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 6px;
  text-transform: uppercase;
}

.stat-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  max-height: 50px;
  overflow-y: auto;
}

.stat-list::-webkit-scrollbar {
  width: 4px;
  height: 4px;
}

.stat-list::-webkit-scrollbar-track {
  background: transparent;
}

.stat-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}

.stat-item {
  font-size: 11px;
  padding: 2px 6px;
  background: rgba(93, 173, 226, 0.15);
  border-radius: 3px;
  color: var(--accent);
}

.stat-more {
  font-size: 11px;
  padding: 2px 6px;
  color: var(--text-muted);
  font-style: italic;
}

.stat-empty {
  font-size: 11px;
  color: var(--text-muted);
  font-style: italic;
}

/* Action Buttons */
.btn-icon {
  background: transparent;
  border: none;
  padding: 8px;
  cursor: pointer;
  color: var(--text-muted);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  border-radius: 4px;
}

.btn-icon:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
  color: var(--accent);
}

.btn-icon.btn-delete:hover:not(:disabled) {
  color: #f44336;
}

.btn-icon:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-icon i {
  font-size: 20px;
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

/* Buttons */
.btn {
  padding: 10px 20px;
  border-radius: var(--radius);
  font-size: 14px;
  line-height: 1.2;
  cursor: pointer;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text);
  display: inline-flex;
  align-items: center;
  justify-content: center;
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

.btn-secondary {
  background: var(--card-bg);
}

.btn-secondary:hover:not(:disabled) {
  background: #2a2a2a;
  border-color: var(--accent);
}

.btn i {
  font-size: 18px;
}

@media screen and (max-width: 768px) {
  .projects-modal {
    width: 95%;
  }

  .modal-header {
    flex-wrap: wrap;
  }

  .header-actions {
    flex-basis: 100%;
    order: 3;
    margin-top: 12px;
  }

  .project-stats {
    grid-template-columns: 1fr;
  }
}
</style>
