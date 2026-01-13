<template>
  <div v-if="visible" class="packages-modal-overlay" @click.self="close">
    <div class="packages-modal">
      <div class="modal-header">
        <span class="modal-title">Package Manager</span>
      </div>

      <div class="modal-body">
        <!-- Status Section -->
        <div class="status-section">
          <div class="status-row">
            <span class="status-label">Venv Status:</span>
            <span :class="['status-value', status.exists ? 'status-active' : 'status-inactive']">
              {{ status.exists ? 'Active' : 'Not Created' }}
            </span>
          </div>
          <div v-if="status.python_version" class="status-row">
            <span class="status-label">Python:</span>
            <span class="status-value">{{ status.python_version }}</span>
          </div>
          <div v-if="status.path" class="status-row">
            <span class="status-label">Path:</span>
            <span class="status-value status-path">{{ status.path }}</span>
          </div>
        </div>

        <!-- Install Section -->
        <div class="install-section">
          <h6>Install Package</h6>
          <div class="install-form">
            <input
              v-model="newPackage"
              type="text"
              placeholder="Package name (e.g., requests)"
              class="package-input"
              :disabled="installing"
              @keyup.enter="installPackage"
            />
            <input
              v-model="newVersion"
              type="text"
              placeholder="Version (optional)"
              class="version-input"
              :disabled="installing"
              @keyup.enter="installPackage"
            />
            <button
              class="btn btn-primary install-btn"
              :disabled="!newPackage || installing"
              @click="installPackage"
            >
              {{ installing ? 'Installing...' : 'Install' }}
            </button>
          </div>
        </div>

        <!-- Error Display -->
        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <!-- Success Display -->
        <div v-if="success" class="success-message">
          {{ success }}
        </div>

        <!-- Packages List -->
        <div class="packages-section">
          <h6>Installed Packages ({{ packages.length }})</h6>
          <div v-if="loading" class="loading">Loading packages...</div>
          <div v-else-if="packages.length === 0" class="no-packages">
            No packages installed. Install a package to create the venv.
          </div>
          <div v-else class="packages-list">
            <div
              v-for="pkg in packages"
              :key="pkg.name"
              class="package-row"
            >
              <div class="package-info">
                <span class="package-name">{{ pkg.name }}</span>
                <span class="package-version">{{ pkg.version }}</span>
              </div>
              <button
                class="btn-delete"
                :disabled="uninstalling === pkg.name"
                @click="uninstallPackage(pkg.name)"
                title="Uninstall"
              >
                <i class="material-icons">{{ uninstalling === pkg.name ? 'hourglass_empty' : 'delete' }}</i>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn waves-effect" @click="close">Close</button>
        <button class="btn waves-effect" @click="refreshPackages" :disabled="loading">
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
  name: 'PackagesModal',

  props: {
    visible: {
      type: Boolean,
      default: false
    }
  },

  data() {
    return {
      status: {exists: false, python_version: null, path: null},
      packages: [],
      loading: false,
      installing: false,
      uninstalling: null,
      newPackage: '',
      newVersion: '',
      error: null,
      success: null
    };
  },

  watch: {
    visible(newVal) {
      if (newVal) {
        this.error = null;
        this.success = null;
        this.loadData();
      }
    }
  },

  methods: {
    close() {
      this.$emit('close');
    },

    async loadData() {
      this.error = null;
      await Promise.all([
        this.loadStatus(),
        this.loadPackages()
      ]);
    },

    async loadStatus() {
      try {
        const response = await axiosInstance.get('admin/venv/status');
        this.status = response.data;
      } catch (e) {
        console.error('Failed to load venv status:', e);
        this.error = 'Failed to load venv status';
      }
    },

    async loadPackages() {
      this.loading = true;
      try {
        const response = await axiosInstance.get('admin/venv/packages');
        this.packages = response.data.packages || [];
      } catch (e) {
        // Venv might not exist yet - that's okay
        this.packages = [];
      } finally {
        this.loading = false;
      }
    },

    async refreshPackages() {
      await this.loadData();
    },

    async installPackage() {
      if (!this.newPackage) return;

      this.installing = true;
      this.error = null;
      this.success = null;

      try {
        const packageName = this.newPackage.trim();
        const version = this.newVersion.trim() || undefined;

        await axiosInstance.post('admin/venv/packages/install', {
          package: packageName,
          version: version
        });

        this.success = `Successfully installed ${packageName}${version ? '==' + version : ''}`;
        this.newPackage = '';
        this.newVersion = '';
        await this.loadData();
      } catch (e) {
        this.error = e.response?.data || 'Failed to install package';
      } finally {
        this.installing = false;
      }
    },

    async uninstallPackage(name) {
      this.uninstalling = name;
      this.error = null;
      this.success = null;

      try {
        await axiosInstance.delete(`admin/venv/packages/${encodeURIComponent(name)}`);
        this.success = `Successfully uninstalled ${name}`;
        await this.loadPackages();
      } catch (e) {
        this.error = e.response?.data || 'Failed to uninstall package';
      } finally {
        this.uninstalling = null;
      }
    }
  }
};
</script>

<style scoped>
.packages-modal-overlay {
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

.packages-modal {
  background: var(--background-color);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  width: 90%;
  max-width: 550px;
  max-height: 85vh;
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

.modal-body {
  padding: 16px 24px;
  overflow-y: auto;
  flex: 1;
}

.status-section {
  margin-bottom: 20px;
  padding: 12px;
  background: var(--background-color-level-4dp);
  border-radius: var(--radius-sm);
}

.status-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.status-row:last-child {
  margin-bottom: 0;
}

.status-label {
  font-size: 13px;
  color: var(--font-color-medium);
  min-width: 80px;
}

.status-value {
  font-size: 13px;
  color: var(--font-color-main);
  font-weight: 500;
}

.status-path {
  font-family: monospace;
  font-size: 12px;
  font-weight: normal;
  word-break: break-all;
}

.status-active {
  color: var(--status-success-color);
}

.status-inactive {
  color: var(--font-color-disabled);
}

.install-section,
.packages-section {
  margin-bottom: 20px;
}

.install-section h6,
.packages-section h6 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 500;
  color: var(--primary-color);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.install-form {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.package-input {
  flex: 2;
  min-width: 150px;
}

.version-input {
  flex: 1;
  min-width: 100px;
}

.package-input,
.version-input {
  padding: 10px 12px;
  border: 1px solid var(--separator-color);
  border-radius: var(--radius-sm);
  background: var(--background-color-level-4dp);
  color: var(--font-color-main);
  font-size: 14px;
  transition: border-color 0.2s;
}

.package-input:focus,
.version-input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.package-input:disabled,
.version-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.install-btn {
  white-space: nowrap;
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
.no-packages {
  padding: 20px;
  text-align: center;
  color: var(--font-color-medium);
  font-size: 14px;
}

.packages-list {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid var(--separator-color);
  border-radius: var(--radius-sm);
}

.package-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-bottom: 1px solid var(--separator-color);
}

.package-row:last-child {
  border-bottom: none;
}

.package-row:hover {
  background: var(--background-color-level-4dp);
}

.package-info {
  display: flex;
  align-items: baseline;
  gap: 8px;
  min-width: 0;
  flex: 1;
}

.package-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--font-color-main);
}

.package-version {
  font-size: 12px;
  color: var(--font-color-medium);
  font-family: monospace;
}

.btn-delete {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: var(--radius-sm);
  color: var(--font-color-medium);
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-delete:hover {
  background: rgba(244, 67, 54, 0.15);
  color: #f44336;
}

.btn-delete:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-delete i {
  font-size: 20px;
}

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

.btn-icon {
  font-size: 18px;
}

@media screen and (max-width: 768px) {
  .packages-modal {
    width: 95%;
    max-height: 95vh;
  }

  .install-form {
    flex-direction: column;
  }

  .package-input,
  .version-input {
    min-width: 100%;
  }
}
</style>
