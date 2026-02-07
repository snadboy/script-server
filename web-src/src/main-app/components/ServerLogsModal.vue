<template>
  <BaseModal
    :visible="visible"
    title="Server Logs"
    modal-class="server-logs-modal"
    overlay-class="server-logs-modal-overlay"
    :show-close-button="false"
    @close="close"
  >
    <template #default>
        <!-- Filters Section -->
        <div class="filters-section">
          <div class="filter-row">
            <select v-model="logLevel" class="log-level-select" @change="refreshLogs">
              <option value="">All Levels</option>
              <option value="ERROR">Errors Only</option>
              <option value="WARNING">Warnings</option>
              <option value="INFO">Info</option>
              <option value="DEBUG">Debug</option>
            </select>

            <input
              v-model="searchTerm"
              type="text"
              placeholder="Search logs..."
              class="search-input"
              @input="debouncedSearch"
            />

            <select v-model="lineCount" class="lines-select" @change="refreshLogs">
              <option value="100">Last 100 lines</option>
              <option value="500">Last 500 lines</option>
              <option value="1000">Last 1000 lines</option>
              <option value="5000">Last 5000 lines</option>
            </select>
          </div>

          <div class="info-row">
            <span class="info-text">{{ filteredLines }} / {{ totalLines }} lines</span>
            <span v-if="logFile" class="info-text">{{ logFile }}</span>
          </div>
        </div>

        <!-- Error Display -->
        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <!-- Logs Display -->
        <div class="logs-section">
          <div v-if="loading" class="loading">Loading logs...</div>
          <pre v-else class="logs-content">{{ logs }}</pre>
        </div>
    </template>

    <template #footer>
      <button class="btn waves-effect" @click="close">Close</button>
      <button class="btn waves-effect" @click="refreshLogs" :disabled="loading">
        <i class="material-icons btn-icon">refresh</i>
        Refresh
      </button>
      <button class="btn waves-effect" @click="downloadLogs" :disabled="!logs">
        <i class="material-icons btn-icon">download</i>
        Download
      </button>
    </template>
  </BaseModal>
</template>

<script>
import {axiosInstance} from '@/common/utils/axios_utils'
import BaseModal from '@/common/components/BaseModal.vue';

export default {
  name: 'ServerLogsModal',

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
      logs: '',
      totalLines: 0,
      filteredLines: 0,
      logFile: '',
      logLevel: '',
      searchTerm: '',
      lineCount: '500',
      loading: false,
      error: null,
      searchTimeout: null
    }
  },

  watch: {
    visible(newVal) {
      if (newVal) {
        this.refreshLogs()
      }
    }
  },

  methods: {
    async refreshLogs() {
      this.loading = true
      this.error = null

      try {
        const params = {
          lines: this.lineCount
        }
        if (this.logLevel) {
          params.level = this.logLevel
        }
        if (this.searchTerm) {
          params.search = this.searchTerm
        }

        const response = await axiosInstance.get('/admin/logs/server', { params })
        this.logs = response.data.logs
        this.totalLines = response.data.total_lines
        this.filteredLines = response.data.filtered_lines
        this.logFile = response.data.log_file
      } catch (err) {
        this.error = err.response?.data?.reason || 'Failed to load logs'
        console.error('Failed to load logs:', err)
      } finally {
        this.loading = false
      }
    },

    debouncedSearch() {
      if (this.searchTimeout) {
        clearTimeout(this.searchTimeout)
      }
      this.searchTimeout = setTimeout(() => {
        this.refreshLogs()
      }, 500)
    },

    downloadLogs() {
      const blob = new Blob([this.logs], { type: 'text/plain' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `server-logs-${new Date().toISOString()}.log`
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
.server-logs-modal {
  width: 90%;
  max-width: 1200px;
  max-height: 90vh;
}

.filters-section {
  flex-shrink: 0;
}

.filter-row {
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
}

.log-level-select,
.lines-select {
  flex-shrink: 0;
  padding: 8px 12px;
  border: 1px solid var(--border-color, #ddd);
  border-radius: var(--border-radius, 4px);
  background: var(--background-color, white);
  color: var(--font-color-main, black);
  opacity: 1;
  appearance: menulist;
}

.search-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid var(--border-color, #ddd);
  border-radius: var(--border-radius, 4px);
  background: var(--background-color, white);
  color: var(--font-color-main, black);
}

.info-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: var(--font-color-medium, #666);
}

.logs-section {
  flex: 1;
  overflow: hidden;
  border: 1px solid var(--border-color, #ddd);
  border-radius: var(--border-radius, 4px);
  background: var(--code-background-color, #1e1e1e);
}

.loading {
  padding: 20px;
  text-align: center;
  color: var(--font-color-medium, #666);
}

.logs-content {
  margin: 0;
  padding: 12px;
  height: 100%;
  overflow: auto;
  font-family: 'Roboto Mono', 'Courier New', monospace;
  font-size: 0.9rem;
  line-height: 1.5;
  color: var(--code-color, #d4d4d4);
  background: var(--code-background-color, #1e1e1e);
  white-space: pre-wrap;
  word-wrap: break-word;
}

.error-message {
  padding: 12px;
  background: #ffebee;
  color: #c62828;
  border-radius: var(--border-radius, 4px);
  border: 1px solid #ef5350;
  flex-shrink: 0;
}

.btn-icon {
  font-size: 18px;
  margin-right: 4px;
  vertical-align: middle;
}
</style>
