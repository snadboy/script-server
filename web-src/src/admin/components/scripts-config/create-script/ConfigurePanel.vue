<template>
  <div class="configure-panel">
    <h6>{{ project.name }}</h6>

    <!-- Dependencies -->
    <div class="config-group">
      <div class="config-group-header">
        <span class="config-label">
          Dependencies ({{ project.dependencies?.length || 0 }})
          <span v-if="loadingPackages" class="loading-indicator">checking...</span>
          <span v-else-if="allDependenciesInstalled" class="all-installed-badge">All Installed</span>
        </span>
        <button
          v-if="project.dependencies?.length > 0 && missingDependencies.length > 0"
          class="btn btn-sm"
          :disabled="installingDeps || loadingPackages"
          @click="installAllDependencies"
        >
          {{ installingDeps ? 'Installing...' : `Install Missing (${missingDependencies.length})` }}
        </button>
      </div>
      <div v-if="project.dependencies?.length > 0" class="deps-list">
        <span
          v-for="dep in project.dependencies"
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
      <select v-model="entryPoint" class="form-select">
        <option value="">Select an entry point...</option>
        <option v-for="ep in project.entry_points" :key="ep" :value="ep">
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

    <!-- Script Name -->
    <div class="config-group">
      <label class="config-label">Script Name</label>
      <input
        v-model="scriptName"
        type="text"
        :placeholder="project.name"
        class="form-input"
      />
    </div>

    <!-- Description -->
    <div class="config-group">
      <label class="config-label">Description</label>
      <input
        v-model="description"
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
  </div>
</template>

<script>
import {axiosInstance} from '@/common/utils/axios_utils';

export default {
  name: 'ConfigurePanel',

  props: {
    project: {
      type: Object,
      required: true
    },
    installedPackages: {
      type: Array,
      default: () => []
    }
  },

  emits: ['configure-complete', 'error', 'packages-updated'],

  data() {
    return {
      entryPoint: '',
      customEntryPoint: '',
      showCustomEntryPoint: false,
      scriptName: '',
      description: '',
      configPath: '',
      configCmd: '',
      wrapperPreview: '',
      installingDeps: false,
      loadingPackages: false
    };
  },

  computed: {
    effectiveEntryPoint() {
      return this.customEntryPoint || this.entryPoint;
    },

    missingDependencies() {
      if (!this.project?.dependencies) return [];
      const installedLower = this.installedPackages.map(p => p.toLowerCase());
      return this.project.dependencies.filter(
        dep => !installedLower.includes(dep.toLowerCase())
      );
    },

    allDependenciesInstalled() {
      return this.project?.dependencies?.length > 0 &&
             this.missingDependencies.length === 0;
    },

    configData() {
      return {
        entryPoint: this.effectiveEntryPoint,
        scriptName: this.scriptName,
        description: this.description,
        configPath: this.configPath,
        configCmd: this.configCmd
      };
    }
  },

  watch: {
    project: {
      immediate: true,
      handler(newVal) {
        if (newVal) {
          this.$nextTick(() => {
            this.entryPoint = newVal.entry_points?.[0] || '';
          });
          this.customEntryPoint = '';
          this.scriptName = newVal.name || '';
          this.description = '';
          this.configPath = '';
          this.configCmd = '';
          this.wrapperPreview = '';
        }
      }
    },

    configData: {
      deep: true,
      handler(newVal) {
        this.$emit('configure-complete', newVal);
      }
    }
  },

  methods: {
    isPackageInstalled(dep) {
      const depLower = dep.toLowerCase();
      return this.installedPackages.some(p => p.toLowerCase() === depLower);
    },

    async installAllDependencies() {
      const toInstall = this.missingDependencies;
      if (!toInstall.length) return;

      this.installingDeps = true;

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
            console.warn(`Failed to install ${dep}:`, e);
            failed++;
          }
        }

        this.$emit('packages-updated');

        if (failed === 0) {
          this.$emit('success', `Successfully installed ${installed} package${installed !== 1 ? 's' : ''}`);
        } else {
          this.$emit('success', `Installed ${installed} package${installed !== 1 ? 's' : ''}, ${failed} failed`);
        }
      } catch (e) {
        this.$emit('error', 'Failed to install dependencies');
      } finally {
        this.installingDeps = false;
      }
    },

    async previewWrapper() {
      if (!this.effectiveEntryPoint || !this.project) return;

      try {
        const response = await axiosInstance.post(
          `admin/projects/${encodeURIComponent(this.project.id)}/wrapper-preview`,
          {
            entry_point: this.effectiveEntryPoint,
            config_path: this.configPath || undefined,
            config_cmd: this.configCmd || undefined
          }
        );
        this.wrapperPreview = response.data.wrapper_content;
      } catch (e) {
        this.$emit('error', e.response?.data || 'Failed to generate preview');
      }
    }
  }
}
</script>

<style scoped>
.configure-panel {
  padding: 1.5rem;
  max-width: 800px;
  margin: 0 auto;
}

.configure-panel h6 {
  margin: 0 0 1.5rem 0;
  font-size: 1.25rem;
  font-weight: 500;
}

.config-group {
  margin-bottom: 1.5rem;
}

.config-group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.config-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.loading-indicator {
  font-size: 0.85rem;
  color: var(--text-color-secondary, #666);
  margin-left: 0.5rem;
}

.all-installed-badge {
  font-size: 0.85rem;
  color: var(--success-color, #4caf50);
  margin-left: 0.5rem;
}

.deps-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.dep-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.75rem;
  border-radius: var(--border-radius, 4px);
  background: var(--tag-bg, #f5f5f5);
  border: 1px solid var(--border-color, #ddd);
  font-size: 0.875rem;
}

.dep-tag.dep-installed {
  background: var(--success-bg, #e8f5e9);
  border-color: var(--success-color, #4caf50);
  color: var(--success-color, #4caf50);
}

.dep-check {
  font-size: 16px !important;
}

.no-deps {
  color: var(--text-color-secondary, #666);
  font-style: italic;
}

.form-select,
.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color, #ddd);
  border-radius: var(--border-radius, 4px);
  font-size: 1rem;
  /* Override Materialize CSS opacity quirk */
  opacity: 1 !important;
  appearance: menulist;
}

.btn-link {
  background: none;
  border: none;
  color: var(--primary-color, #1976d2);
  cursor: pointer;
  font-size: 0.875rem;
  padding: 0.5rem 0;
  text-decoration: underline;
}

.btn-link:hover {
  color: var(--primary-color-dark, #1565c0);
}

.advanced-toggle {
  margin-top: 0.5rem;
}

.custom-entry-point {
  margin-top: 0.75rem;
}

.form-help {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-color-secondary, #666);
}

.wrapper-preview {
  margin-top: 0.75rem;
  padding: 1rem;
  background: var(--code-bg, #f5f5f5);
  border: 1px solid var(--border-color, #ddd);
  border-radius: var(--border-radius, 4px);
  max-height: 300px;
  overflow-y: auto;
}

.wrapper-preview pre {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
  white-space: pre-wrap;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: var(--border-radius, 4px);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-icon-sm {
  font-size: 18px !important;
  vertical-align: middle;
  margin-right: 0.25rem;
}
</style>
