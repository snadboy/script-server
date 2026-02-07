<template>
  <BaseModal
    :visible="visible"
    title="Python Packages"
    modal-class="python-packages-modal"
    overlay-class="python-packages-modal-overlay"
    :show-close-button="false"
    @close="close"
  >
    <template #default>
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

        <!-- Messages -->
        <div v-if="error" class="error-message">{{ error }}</div>
        <div v-if="success" class="success-message">{{ success }}</div>

        <!-- Packages List with Actions -->
        <div class="packages-section">
          <div class="packages-header">
            <h6>Installed Packages ({{ filteredRequirements.length }})</h6>
            <div class="header-actions">
              <!-- View Toggle -->
              <div class="view-toggle">
                <button
                  :class="['view-btn', { active: viewMode === 'package' }]"
                  @click="viewMode = 'package'"
                  title="Group by package"
                >
                  <i class="material-icons">apps</i>
                  By Package
                </button>
                <button
                  :class="['view-btn', { active: viewMode === 'script' }]"
                  @click="viewMode = 'script'"
                  title="Group by script"
                >
                  <i class="material-icons">description</i>
                  By Script
                </button>
              </div>

              <label v-if="viewMode === 'package'" class="filter-checkbox">
                <input type="checkbox" v-model="excludeStdlib" @change="applyFilter" />
                Exclude stdlib
              </label>
              <button class="btn-icon" @click="copyRequirements" title="Copy to clipboard">
                <i class="material-icons">content_copy</i>
              </button>
              <button class="btn-icon" @click="exportRequirements" title="Download requirements.txt">
                <i class="material-icons">download</i>
              </button>
            </div>
          </div>

          <!-- Package View -->
          <div v-if="viewMode === 'package'">
            <div v-if="loading" class="loading">Loading packages...</div>
            <div v-else-if="error && !success" class="error-message">{{ error }}</div>
            <div v-else-if="filteredRequirements.length === 0" class="no-packages">
              No packages installed. Install a package to create the venv.
            </div>
            <div v-else class="packages-list">
              <div
                v-for="req in filteredRequirements"
                :key="req.name"
                class="package-row"
              >
                <div class="package-main">
                  <div class="package-info">
                    <span class="package-name">{{ req.name }}</span>
                    <span class="package-version">{{ req.version }}</span>
                  </div>
                  <div v-if="req.used_by && req.used_by.length > 0" class="package-usage">
                    <i class="material-icons usage-icon">description</i>
                    <span class="usage-text">Used by: {{ req.used_by.join(', ') }}</span>
                  </div>
                </div>
                <button
                  v-if="req.used_by && req.used_by.length > 0"
                  class="btn-warn-delete"
                  @click="confirmUninstall(req.name, req.used_by)"
                  title="Uninstall (used by scripts)"
                  :disabled="uninstalling === req.name"
                >
                  <i class="material-icons">{{ uninstalling === req.name ? 'hourglass_empty' : 'delete' }}</i>
                </button>
                <button
                  v-else
                  class="btn-delete"
                  @click="uninstallPackage(req.name)"
                  title="Uninstall"
                  :disabled="uninstalling === req.name"
                >
                  <i class="material-icons">{{ uninstalling === req.name ? 'hourglass_empty' : 'delete' }}</i>
                </button>
              </div>
            </div>
          </div>

          <!-- Script View -->
          <div v-else-if="viewMode === 'script'">
            <div v-if="loading" class="loading">Loading packages...</div>
            <div v-else class="script-view">
              <!-- Missing Packages Section -->
              <div v-if="missingPackages.length > 0" class="script-group missing-group">
                <div class="script-group-header missing-header">
                  <i class="material-icons">warning</i>
                  <span class="script-name">Missing Packages ({{ missingPackages.length }})</span>
                </div>
                <div class="script-packages">
                  <div
                    v-for="pkg in missingPackages"
                    :key="pkg.name"
                    class="script-package-row missing-row"
                  >
                    <div class="package-main">
                      <div class="package-info">
                        <span class="package-name">{{ pkg.name }}</span>
                        <span class="package-status missing">Not installed</span>
                      </div>
                      <div class="package-usage">
                        <i class="material-icons usage-icon">description</i>
                        <span class="usage-text">Needed by: {{ pkg.needed_by.join(', ') }}</span>
                      </div>
                    </div>
                    <button
                      class="btn-install"
                      @click="newPackage = pkg.name; installPackage()"
                      :disabled="installing"
                      title="Install package"
                    >
                      <i class="material-icons">{{ installing && newPackage === pkg.name ? 'hourglass_empty' : 'download' }}</i>
                    </button>
                  </div>
                </div>
              </div>

              <!-- Scripts with Dependencies -->
              <div
                v-for="(packages, scriptName) in filteredScriptDependencies"
                :key="scriptName"
                v-if="packages.length > 0"
                class="script-group"
              >
                <div class="script-group-header">
                  <i class="material-icons">description</i>
                  <span class="script-name">{{ scriptName }}</span>
                  <span class="package-count">({{ packages.length }} package{{ packages.length !== 1 ? 's' : '' }})</span>
                </div>
                <div class="script-packages">
                  <div
                    v-for="pkgName in packages"
                    :key="pkgName"
                    class="script-package-row"
                  >
                    <div class="package-info">
                      <span class="package-name">{{ pkgName }}</span>
                      <span class="package-version">{{ getPackageVersion(pkgName) }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Unused Packages -->
              <div v-if="unusedPackages.length > 0" class="script-group unused-group">
                <div class="script-group-header unused-header">
                  <i class="material-icons">remove_circle_outline</i>
                  <span class="script-name">Unused Packages ({{ unusedPackages.length }})</span>
                </div>
                <div class="script-packages">
                  <div
                    v-for="pkg in unusedPackages"
                    :key="pkg.name"
                    class="script-package-row"
                  >
                    <div class="package-info">
                      <span class="package-name">{{ pkg.name }}</span>
                      <span class="package-version">{{ pkg.version }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
    </template>

    <template #footer>
      <button class="btn waves-effect" @click="close">Close</button>
      <button class="btn waves-effect" @click="loadAll" :disabled="loading">
        <i class="material-icons btn-icon">refresh</i>
        Refresh
      </button>
    </template>
  </BaseModal>
</template>

<script>
import {axiosInstance} from '@/common/utils/axios_utils'
import BaseModal from '@/common/components/BaseModal.vue';
import {SUCCESS_MESSAGE_TIMEOUT_MS} from '@/common/ui-constants';

export default {
  name: 'PythonPackagesModal',

  components: {
    BaseModal
  },

  props: {
    visible: {
      type: Boolean,
      default: false
    }
  },

  data() {
    return {
      status: {
        exists: false,
        python_version: null,
        path: null
      },
      newPackage: '',
      newVersion: '',
      loading: false,
      installing: false,
      uninstalling: null,
      error: null,
      success: null,
      viewMode: 'package', // 'package' or 'script'
      allRequirements: [],
      filteredRequirements: [],
      missingPackages: [],
      scriptDependencies: {},
      excludeStdlib: true,
      requirementsFilter: false
    }
  },

  computed: {
    unusedPackages() {
      return this.allRequirements.filter(req =>
        !req.is_stdlib && (!req.used_by || req.used_by.length === 0)
      )
    },

    filteredScriptDependencies() {
      // Filter out stdlib modules and missing packages from script dependencies
      const stdlib = new Set([
        'abc', 'aifc', 'argparse', 'array', 'ast', 'asynchat', 'asyncio', 'asyncore',
        'atexit', 'base64', 'binascii', 'builtins', 'calendar', 'collections',
        'contextlib', 'copy', 'csv', 'datetime', 'decimal', 'email', 'functools',
        'gc', 'glob', 'hashlib', 'html', 'http', 'inspect', 'io', 'itertools',
        'json', 'logging', 'math', 'os', 'pathlib', 're', 'shutil', 'socket',
        'sqlite3', 'string', 'struct', 'subprocess', 'sys', 'tempfile', 'threading',
        'time', 'traceback', 'typing', 'unittest', 'urllib', 'uuid', 'warnings', 'xml'
      ])

      // Build set of missing package names
      const missingSet = new Set(this.missingPackages.map(pkg => pkg.name.toLowerCase()))

      const filtered = {}
      for (const [scriptName, packages] of Object.entries(this.scriptDependencies)) {
        // Filter out stdlib modules AND missing packages (missing packages show in their own section)
        filtered[scriptName] = packages.filter(pkg =>
          !stdlib.has(pkg.toLowerCase()) && !missingSet.has(pkg.toLowerCase())
        )
      }
      return filtered
    }
  },

  watch: {
    visible(newVal) {
      if (newVal) {
        this.loadAll()
      }
    }
  },

  methods: {
    getPackageVersion(pkgName) {
      const pkg = this.allRequirements.find(r =>
        r.name.toLowerCase() === pkgName.toLowerCase() ||
        r.name.replace('-', '_').toLowerCase() === pkgName.toLowerCase()
      )
      return pkg ? pkg.version : 'not installed'
    },

    async loadAll() {
      this.loading = true
      this.error = null

      try {
        // Load both status and requirements in parallel
        const [statusResponse, reqResponse] = await Promise.all([
          axiosInstance.get('/admin/venv/packages'),
          axiosInstance.get('/admin/venv/requirements')
        ])

        this.status = statusResponse.data.status
        this.allRequirements = reqResponse.data.requirements || []
        this.missingPackages = reqResponse.data.missing_packages || []
        this.scriptDependencies = reqResponse.data.script_dependencies || {}
        this.applyFilter()
      } catch (err) {
        this.error = err.response?.data?.reason || 'Failed to load packages'
        console.error('Failed to load packages:', err)
      } finally {
        this.loading = false
      }
    },

    async installPackage() {
      if (!this.newPackage) return

      this.installing = true
      this.error = null
      this.success = null

      try {
        const packageSpec = this.newVersion
          ? `${this.newPackage}==${this.newVersion}`
          : this.newPackage

        await axiosInstance.post('/admin/venv/packages/install', {
          package: packageSpec
        })

        this.success = `Successfully installed ${packageSpec}`
        this.newPackage = ''
        this.newVersion = ''
        await this.loadAll()
      } catch (err) {
        this.error = err.response?.data?.reason || 'Failed to install package'
        console.error('Failed to install package:', err)
      } finally {
        this.installing = false
      }
    },

    async uninstallPackage(packageName) {
      this.uninstalling = packageName
      this.error = null
      this.success = null

      try {
        await axiosInstance.post('/admin/venv/packages/uninstall', {
          package: packageName
        })

        this.success = `Successfully uninstalled ${packageName}`
        await this.loadAll()
      } catch (err) {
        this.error = err.response?.data?.reason || 'Failed to uninstall package'
        console.error('Failed to uninstall package:', err)
      } finally {
        this.uninstalling = null
      }
    },

    applyFilter() {
      if (this.excludeStdlib) {
        this.filteredRequirements = this.allRequirements.filter(req => !req.is_stdlib)
        this.requirementsFilter = true
      } else {
        this.filteredRequirements = this.allRequirements
        this.requirementsFilter = false
      }
    },

    confirmUninstall(packageName, usedBy) {
      const scripts = usedBy.join(', ')
      if (confirm(`Package "${packageName}" is used by: ${scripts}\n\nUninstall anyway?`)) {
        this.uninstallPackage(packageName)
      }
    },

    copyRequirements() {
      const text = this.filteredRequirements
        .map(req => `${req.name}==${req.version}`)
        .join('\n')

      navigator.clipboard.writeText(text).then(() => {
        this.success = 'Copied to clipboard!'
        setTimeout(() => { this.success = null }, SUCCESS_MESSAGE_TIMEOUT_MS)
      }).catch(err => {
        this.error = 'Failed to copy to clipboard'
        console.error('Copy failed:', err)
      })
    },

    exportRequirements() {
      const text = this.filteredRequirements
        .map(req => `${req.name}==${req.version}`)
        .join('\n')

      const blob = new Blob([text], { type: 'text/plain' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'requirements.txt'
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    },

    close() {
      this.$emit('update:visible', false)
    }
  }
}
</script>

<style scoped>
.python-packages-modal {
  width: 90%;
  max-width: 900px;
  max-height: 90vh;
}

/* Status Section */
.status-section {
  background: var(--background-color-slight-emphasis, #f5f5f5);
  padding: 12px;
  border-radius: var(--border-radius, 4px);
  margin-bottom: 20px;
}

.status-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 4px 0;
}

.status-label {
  font-weight: 500;
  color: var(--font-color-medium, #666);
}

.status-value {
  color: var(--font-color-main, black);
}

.status-active {
  color: #4caf50;
  font-weight: 500;
}

.status-inactive {
  color: #f44336;
  font-weight: 500;
}

.status-path {
  font-family: monospace;
  font-size: 0.9em;
}

/* Install Section */
.install-section {
  margin-bottom: 20px;
}

.install-section h6 {
  margin: 0 0 12px 0;
  font-size: 1rem;
  font-weight: 500;
}

.install-form {
  display: flex;
  gap: 12px;
}

.package-input {
  flex: 2;
  padding: 8px 12px;
  border: 1px solid var(--border-color, #ddd);
  border-radius: var(--border-radius, 4px);
  background: var(--background-color, white);
  color: var(--font-color-main, black);
}

.version-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid var(--border-color, #ddd);
  border-radius: var(--border-radius, 4px);
  background: var(--background-color, white);
  color: var(--font-color-main, black);
}

.install-btn {
  flex-shrink: 0;
}

/* Messages */
.error-message {
  padding: 12px;
  background: #ffebee;
  color: #c62828;
  border-radius: var(--border-radius, 4px);
  border: 1px solid #ef5350;
  margin-bottom: 16px;
}

.success-message {
  padding: 12px;
  background: #e8f5e9;
  color: #2e7d32;
  border-radius: var(--border-radius, 4px);
  border: 1px solid #66bb6a;
  margin-bottom: 16px;
}

/* Packages Section */
.packages-section {
  margin-top: 20px;
}

.packages-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.packages-header h6 {
  margin: 0;
  font-size: 1rem;
  font-weight: 500;
}

.loading,
.no-packages {
  padding: 20px;
  text-align: center;
  color: var(--font-color-medium, #666);
}

.packages-list {
  border: 1px solid var(--border-color, #ddd);
  border-radius: var(--border-radius, 4px);
  overflow: hidden;
}

.package-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  border-bottom: 1px solid var(--border-color, #ddd);
}

.package-row:last-child {
  border-bottom: none;
}

.package-row:hover {
  background: var(--hover-color, rgba(0,0,0,0.04));
}

.package-main {
  flex: 1;
}

.package-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 4px;
}

.package-name {
  font-weight: 500;
  color: #424242 !important;
}

.package-version {
  color: var(--font-color-medium, #666);
  font-size: 0.9rem;
}

.package-usage {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--font-color-medium, #666);
  font-size: 0.85rem;
  margin-top: 4px;
}

.usage-icon {
  font-size: 16px;
}

.usage-text {
  font-style: italic;
}

.btn-delete {
  background: none;
  border: none;
  color: #f44336;
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-delete:hover {
  background: rgba(244, 67, 54, 0.1);
}

.btn-delete:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.view-toggle {
  display: flex;
  gap: 4px;
  border: 1px solid var(--border-color, #ddd);
  border-radius: var(--border-radius, 4px);
  padding: 2px;
}

.view-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: none;
  border: none;
  border-radius: var(--border-radius, 4px);
  color: var(--font-color-medium, #666);
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}

.view-btn i {
  font-size: 18px;
}

.view-btn:hover {
  background: var(--hover-color, rgba(0,0,0,0.04));
}

.view-btn.active {
  background: var(--primary-color, #4caf50);
  color: white;
}

.filter-checkbox {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--font-color-main, black);
  cursor: pointer;
}

.btn-icon {
  background: none;
  border: none;
  color: var(--font-color-medium, #666);
  cursor: pointer;
  padding: 6px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon:hover {
  background: var(--hover-color, rgba(0,0,0,0.04));
  color: var(--font-color-main, black);
}

.btn-warn-delete {
  background: none;
  border: none;
  color: #ff9800;
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-warn-delete:hover {
  background: rgba(255, 152, 0, 0.1);
}

.btn-warn-delete:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-install {
  background: none;
  border: none;
  color: var(--primary-color, #4caf50);
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-install:hover {
  background: rgba(76, 175, 80, 0.1);
}

.btn-install:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Script View */
.script-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.script-group {
  border: 1px solid var(--border-color, #ddd);
  border-radius: var(--border-radius, 4px);
  overflow: hidden;
}

.script-group-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: var(--background-color-slight-emphasis, #f5f5f5);
  border-bottom: 1px solid var(--border-color, #ddd);
}

.script-group-header i {
  font-size: 20px;
  color: var(--font-color-medium, #666);
}

.script-name {
  font-weight: 500;
  color: #424242 !important;
}

.package-count {
  color: var(--font-color-medium, #666);
  font-size: 0.85rem;
  margin-left: auto;
}

.script-packages {
  background: var(--background-color, white);
}

.script-package-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-bottom: 1px solid var(--border-color, #ddd);
}

.script-package-row:last-child {
  border-bottom: none;
}

.script-package-row:hover {
  background: var(--hover-color, rgba(0,0,0,0.02));
}

.package-status {
  color: var(--font-color-medium, #666);
  font-size: 0.85rem;
  font-style: italic;
}

.package-status.missing {
  color: #f44336;
}

/* Missing Packages Group */
.missing-group {
  border-color: #ffcc80;
}

.missing-header {
  background: #fff3e0;
  border-bottom-color: #ffcc80;
}

.missing-header i {
  color: #ff9800;
}

.missing-row {
  background: #fffbf5;
}

/* Unused Packages Group */
.unused-group {
  border-color: #e0e0e0;
}

.unused-header {
  background: #fafafa;
}

.unused-header i {
  color: #9e9e9e;
}

.unused-header .script-name {
  color: #424242 !important;
  font-weight: 500;
}

/* Button Icons */
.btn-icon {
  font-size: 18px;
  margin-right: 4px;
  vertical-align: middle;
}
</style>
