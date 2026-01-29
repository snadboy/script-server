<template>
  <div v-if="visible" class="requirements-modal-overlay" @click.self="close">
    <div class="requirements-modal">
      <div class="modal-header">
        <span class="modal-title">Requirements Editor</span>
      </div>

      <div class="modal-tabs">
        <button
          :class="['tab-button', { active: activeTab === 'editor' }]"
          @click="activeTab = 'editor'"
        >
          <i class="material-icons">edit</i>
          Editor
        </button>
        <button
          :class="['tab-button', { active: activeTab === 'status' }]"
          @click="activeTab = 'status'; loadStatus()"
        >
          <i class="material-icons">checklist</i>
          Status
        </button>
      </div>

      <div class="modal-body">
        <!-- Editor Tab -->
        <div v-if="activeTab === 'editor'" class="editor-tab">
          <div class="editor-header">
            <span class="info-text">Edit requirements.txt - one package per line</span>
            <span class="info-text">{{ lineCount }} lines</span>
          </div>

          <textarea
            v-model="requirementsContent"
            class="requirements-editor"
            placeholder="# Add Python packages here, one per line&#10;# Examples:&#10;requests&#10;pyyaml>=6.0&#10;google-api-python-client==2.100.0"
            spellcheck="false"
          ></textarea>

          <div class="editor-footer">
            <button class="btn waves-effect" @click="loadRequirements" :disabled="loading">
              <i class="material-icons btn-icon">refresh</i>
              Reload
            </button>
            <button class="btn btn-primary waves-effect" @click="saveRequirements" :disabled="saving || !hasChanges">
              <i class="material-icons btn-icon">save</i>
              {{ saving ? 'Saving...' : 'Save' }}
            </button>
            <button class="btn btn-primary waves-effect" @click="syncRequirements" :disabled="syncing || !requirementsContent.trim()">
              <i class="material-icons btn-icon">sync</i>
              {{ syncing ? 'Syncing...' : 'Sync All' }}
            </button>
          </div>
        </div>

        <!-- Status Tab -->
        <div v-if="activeTab === 'status'" class="status-tab">
          <div v-if="statusLoading" class="loading">Loading status...</div>
          <div v-else>
            <div class="status-summary">
              <div class="summary-card">
                <div class="summary-number">{{ status.total_required }}</div>
                <div class="summary-label">Required</div>
              </div>
              <div class="summary-card missing" v-if="status.missing_count > 0">
                <div class="summary-number">{{ status.missing_count }}</div>
                <div class="summary-label">Missing</div>
              </div>
              <div class="summary-card extra" v-if="status.extra_count > 0">
                <div class="summary-number">{{ status.extra_count }}</div>
                <div class="summary-label">Extra</div>
              </div>
            </div>

            <!-- Required Packages -->
            <div v-if="status.required && status.required.length > 0" class="packages-section">
              <h6>Required Packages</h6>
              <div class="packages-list">
                <div
                  v-for="pkg in status.required"
                  :key="pkg.name"
                  :class="['package-row', { 'package-missing': !pkg.installed }]"
                >
                  <div class="package-info">
                    <span class="package-name">{{ pkg.name }}</span>
                    <span class="package-version">{{ pkg.spec || '(any version)' }}</span>
                  </div>
                  <div class="package-status">
                    <i v-if="pkg.installed" class="material-icons status-icon installed" title="Installed">check_circle</i>
                    <span v-if="pkg.installed" class="installed-version">{{ pkg.installed_version }}</span>
                    <i v-else class="material-icons status-icon missing" title="Missing">error</i>
                  </div>
                </div>
              </div>
            </div>

            <!-- Extra Packages -->
            <div v-if="status.extra && status.extra.length > 0" class="packages-section">
              <h6>Extra Packages (not in requirements.txt)</h6>
              <div class="packages-list">
                <div
                  v-for="pkg in status.extra"
                  :key="pkg.name"
                  class="package-row package-extra"
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

        <!-- Error Display -->
        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <!-- Success Display -->
        <div v-if="success" class="success-message">
          {{ success }}
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn waves-effect" @click="close">Close</button>
      </div>
    </div>
  </div>
</template>

<script>
import {axiosInstance} from '@/common/utils/axios_utils'

export default {
  name: 'RequirementsModal',

  props: {
    visible: {
      type: Boolean,
      default: false
    }
  },

  data() {
    return {
      activeTab: 'editor',
      requirementsContent: '',
      originalContent: '',
      status: {
        required: [],
        extra: [],
        missing_count: 0,
        extra_count: 0,
        total_required: 0
      },
      loading: false,
      saving: false,
      syncing: false,
      statusLoading: false,
      error: null,
      success: null
    }
  },

  computed: {
    hasChanges() {
      return this.requirementsContent !== this.originalContent
    },
    lineCount() {
      const lines = this.requirementsContent.trim().split('\n').filter(line => {
        const trimmed = line.trim()
        return trimmed && !trimmed.startsWith('#')
      })
      return lines.length
    }
  },

  watch: {
    visible(newVal) {
      if (newVal) {
        this.loadRequirements()
        this.activeTab = 'editor'
        this.clearMessages()
      }
    }
  },

  methods: {
    async loadRequirements() {
      this.loading = true
      this.clearMessages()

      try {
        const response = await axiosInstance.get('/admin/venv/requirements')
        this.requirementsContent = response.data.content
        this.originalContent = response.data.content
      } catch (err) {
        this.error = err.response?.data?.reason || 'Failed to load requirements.txt'
        console.error('Failed to load requirements:', err)
      } finally {
        this.loading = false
      }
    },

    async saveRequirements() {
      this.saving = true
      this.clearMessages()

      try {
        await axiosInstance.put('/admin/venv/requirements/update', {
          content: this.requirementsContent
        })
        this.originalContent = this.requirementsContent
        this.success = 'Requirements saved successfully'
      } catch (err) {
        this.error = err.response?.data?.reason || 'Failed to save requirements.txt'
        console.error('Failed to save requirements:', err)
      } finally {
        this.saving = false
      }
    },

    async syncRequirements() {
      if (!this.hasChanges) {
        // Save first if no changes, otherwise ask user to save
        if (!confirm('Sync requirements? This will install all packages listed in requirements.txt.')) {
          return
        }
      } else {
        if (!confirm('You have unsaved changes. Save and sync requirements?')) {
          return
        }
        // Save first
        await this.saveRequirements()
        if (this.error) return
      }

      this.syncing = true
      this.clearMessages()

      try {
        await axiosInstance.post('/admin/venv/requirements/sync')
        this.success = 'Successfully synced all requirements'
        // Reload status if on status tab
        if (this.activeTab === 'status') {
          await this.loadStatus()
        }
      } catch (err) {
        this.error = err.response?.data?.reason || 'Failed to sync requirements'
        console.error('Failed to sync requirements:', err)
      } finally {
        this.syncing = false
      }
    },

    async loadStatus() {
      this.statusLoading = true
      this.clearMessages()

      try {
        const response = await axiosInstance.get('/admin/venv/requirements/status')
        this.status = response.data
      } catch (err) {
        this.error = err.response?.data?.reason || 'Failed to load requirements status'
        console.error('Failed to load status:', err)
      } finally {
        this.statusLoading = false
      }
    },

    clearMessages() {
      this.error = null
      this.success = null
    },

    close() {
      if (this.hasChanges) {
        if (!confirm('You have unsaved changes. Close anyway?')) {
          return
        }
      }
      this.$emit('update:visible', false)
    }
  }
}
</script>

<style scoped>
.requirements-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.requirements-modal {
  background: var(--background-color, white);
  color: var(--font-color-main, black);
  border-radius: var(--border-radius, 8px);
  box-shadow: var(--shadow-large, 0 8px 32px rgba(0,0,0,0.3));
  width: 90%;
  max-width: 1000px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color, #ddd);
  flex-shrink: 0;
}

.modal-title {
  font-size: 1.3rem;
  font-weight: 500;
}

.modal-tabs {
  display: flex;
  border-bottom: 1px solid var(--border-color, #ddd);
  flex-shrink: 0;
}

.tab-button {
  flex: 1;
  padding: 12px;
  border: none;
  background: transparent;
  color: var(--font-color-medium, #666);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s;
  font-size: 1rem;
}

.tab-button:hover {
  background: var(--hover-background-color, rgba(0,0,0,0.05));
}

.tab-button.active {
  color: var(--primary-color, #2196f3);
  border-bottom: 2px solid var(--primary-color, #2196f3);
}

.tab-button .material-icons {
  font-size: 20px;
}

.modal-body {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.editor-tab,
.status-tab {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 20px;
  gap: 16px;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: var(--font-color-medium, #666);
  flex-shrink: 0;
}

.requirements-editor {
  flex: 1;
  font-family: 'Roboto Mono', 'Courier New', monospace;
  font-size: 0.95rem;
  line-height: 1.5;
  padding: 12px;
  border: 1px solid var(--border-color, #ddd);
  border-radius: var(--border-radius, 4px);
  background: var(--code-background-color, #1e1e1e);
  color: var(--code-color, #d4d4d4);
  resize: none;
  overflow: auto;
}

.requirements-editor::placeholder {
  color: var(--font-color-medium, #666);
  opacity: 0.5;
}

.editor-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  flex-shrink: 0;
}

.status-tab {
  overflow-y: auto;
}

.loading {
  padding: 20px;
  text-align: center;
  color: var(--font-color-medium, #666);
}

.status-summary {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.summary-card {
  flex: 1;
  padding: 20px;
  border-radius: var(--border-radius, 8px);
  background: var(--card-background-color, #f5f5f5);
  text-align: center;
}

.summary-card.missing {
  background: rgba(244, 67, 54, 0.1);
}

.summary-card.extra {
  background: rgba(255, 152, 0, 0.1);
}

.summary-number {
  font-size: 2rem;
  font-weight: 500;
  color: var(--font-color-main, black);
}

.summary-card.missing .summary-number {
  color: #f44336;
}

.summary-card.extra .summary-number {
  color: #ff9800;
}

.summary-label {
  font-size: 0.9rem;
  color: var(--font-color-medium, #666);
  margin-top: 4px;
}

.packages-section {
  margin-bottom: 24px;
}

.packages-section h6 {
  margin: 0 0 12px 0;
  font-size: 1.1rem;
  font-weight: 500;
}

.packages-list {
  border: 1px solid var(--border-color, #ddd);
  border-radius: var(--border-radius, 4px);
  max-height: 400px;
  overflow-y: auto;
}

.package-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color, #ddd);
}

.package-row:last-child {
  border-bottom: none;
}

.package-row.package-missing {
  background: rgba(244, 67, 54, 0.05);
}

.package-row.package-extra {
  background: rgba(255, 152, 0, 0.05);
}

.package-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.package-name {
  font-weight: 500;
}

.package-version {
  font-size: 0.9rem;
  color: var(--font-color-medium, #666);
}

.package-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-icon {
  font-size: 20px;
}

.status-icon.installed {
  color: #4caf50;
}

.status-icon.missing {
  color: #f44336;
}

.installed-version {
  font-size: 0.85rem;
  color: var(--font-color-medium, #666);
}

.error-message {
  padding: 12px;
  background: #ffebee;
  color: #c62828;
  border-radius: var(--border-radius, 4px);
  border: 1px solid #ef5350;
  margin: 0 20px 20px 20px;
  flex-shrink: 0;
}

.success-message {
  padding: 12px;
  background: #e8f5e9;
  color: #2e7d32;
  border-radius: var(--border-radius, 4px);
  border: 1px solid #66bb6a;
  margin: 0 20px 20px 20px;
  flex-shrink: 0;
}

.modal-footer {
  padding: 12px 20px;
  border-top: 1px solid var(--border-color, #ddd);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  flex-shrink: 0;
}

.btn-icon {
  font-size: 18px;
  margin-right: 4px;
  vertical-align: middle;
}
</style>
