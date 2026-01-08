<template>
  <div class="executions-log-table">
    <div class="search-container">
      <div class="search-panel">
        <input ref="searchField" autocomplete="off" class="search-field"
               name="searchField"
               placeholder="Search scripts or users..."
               v-model="searchText">
        <input :alt="isClearSearchButton ? 'Clear search' : 'Search'" :src="searchImage"
             class="search-button"
             type="image"
             @click="searchIconClickHandler">
      </div>
      <div class="sort-dropdown">
        <select v-model="mobileSortOption" class="sort-select">
          <option value="id-desc">Newest first</option>
          <option value="id-asc">Oldest first</option>
          <option value="script-asc">Script A-Z</option>
          <option value="user-asc">User A-Z</option>
        </select>
      </div>
    </div>

    <!-- Card view for all screen sizes -->
    <transition-group name="card-list" tag="div" class="execution-cards" v-if="!loading">
      <div v-for="row in filteredRows" :key="'card-' + row.id"
           class="execution-card"
           @click="rowClick(row)">
        <div class="card-header">
          <span class="card-script">{{ row.script }}</span>
          <span class="card-status" :class="getStatusClass(row.fullStatus)">{{ row.fullStatus }}</span>
        </div>
        <div class="card-body">
          <div class="card-row">
            <span class="card-label">User:</span>
            <span class="card-value">{{ row.user }}</span>
          </div>
          <div class="card-row">
            <span class="card-label">Time:</span>
            <span class="card-value">{{ row.startTimeString }}</span>
          </div>
        </div>
        <div class="card-actions">
          <button v-if="hasParams(row)"
                  class="btn-flat waves-effect params-btn"
                  :class="{ active: expandedParams === row.id }"
                  @click.stop="toggleParams(row.id)"
                  title="Show parameters">
            <i class="material-icons">tune</i>
          </button>
        </div>
        <transition name="expand">
          <div v-if="expandedParams === row.id" class="card-params">
            <table class="params-table">
              <thead>
                <tr>
                  <th>Parameter</th>
                  <th>Value</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(value, name) in row.parameterValues" :key="name">
                  <td class="param-name">{{ name }}</td>
                  <td class="param-value">{{ formatParamValue(value) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </transition>
      </div>
    </transition-group>

    <transition name="fade">
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner spinner"></div>
        <p class="loading-text">Loading history...</p>
      </div>
    </transition>
  </div>
</template>

<script>
import {mapState} from 'vuex';
import ClearIcon from '@/assets/clear.png'
import SearchIcon from '@/assets/search.png'

export default {
  name: 'executions-log-table',
  props: {
    rows: Array,
    rowClick: {
      type: Function
    }
  },

  data() {
    return {
      searchText: '',
      sortColumn: 'id',
      ascending: false,
      expandedParams: null
    }
  },

  computed: {
    ...mapState('history', ['loading']),

    // Mobile sort option syncs with sortColumn/ascending
    mobileSortOption: {
      get() {
        return `${this.sortColumn}-${this.ascending ? 'asc' : 'desc'}`;
      },
      set(value) {
        const [column, direction] = value.split('-');
        this.sortColumn = column;
        this.ascending = direction === 'asc';
      }
    },

    isClearSearchButton() {
      return this.searchText !== '';
    },

    searchImage() {
      return this.isClearSearchButton ? ClearIcon : SearchIcon;
    },

    filteredRows() {
      let searchText = (this.searchText || '').trim().toLowerCase();
      let resultRows;
      if(!this.rows) {
        resultRows = [];
      } else if(searchText === '') {
        resultRows = [...this.rows];
      } else {
        resultRows = this.rows.filter((row) => {
          return row.script.toLowerCase().includes(searchText) ||
            row.user.toLowerCase().includes(searchText);
        });
      }

      let ascending = this.ascending;
      let column = this.sortColumn;

      return resultRows.sort((a, b) => {
        if (column === 'id') {
          let id_a = a[column];
          let id_b = b[column];
          return ascending ? id_a - id_b : id_b - id_a

        } else if (column === 'startTimeString') {
          let date_a = new Date(a[column]);
          let date_b = new Date(b[column]);
          return ascending ? date_a - date_b : date_b - date_a

        } else {
          let other_a = a[column].toLowerCase()
          let other_b = b[column].toLowerCase()
          if (other_a > other_b) {
            return ascending ? 1 : -1
          } else if (other_a < other_b) {
            return ascending ? -1 : 1
          }
          return 0;
        }
      });
    }
  },

  methods: {
    showSort: function (sortKey) {
      if (this.sortColumn === sortKey) {
        return this.ascending ? 'sorted asc' : 'sorted desc'
      }
    },

    sortBy: function (sortKey) {
      if (this.sortColumn === sortKey) {
        this.ascending = !this.ascending;
      } else {
        this.ascending = true;
        this.sortColumn = sortKey;
      }
    },

    searchIconClickHandler() {
      if (this.searchText !== '') {
        this.searchText = '';
      }
      this.$nextTick(() => {
        this.$refs.searchField.focus();
      });
    },

    hasParams(row) {
      return row.parameterValues && Object.keys(row.parameterValues).length > 0;
    },

    toggleParams(rowId) {
      this.expandedParams = this.expandedParams === rowId ? null : rowId;
    },

    formatParamValue(value) {
      if (value === null || value === undefined) {
        return '(empty)';
      }
      if (Array.isArray(value)) {
        return value.join(', ');
      }
      if (typeof value === 'boolean') {
        return value ? 'Yes' : 'No';
      }
      return String(value);
    },

    getStatusClass(status) {
      if (!status) return '';
      const lower = status.toLowerCase();
      if (lower.includes('finished') || lower.includes('success')) return 'status-success';
      if (lower.includes('error') || lower.includes('failed')) return 'status-error';
      if (lower.includes('running')) return 'status-running';
      return '';
    }
  }
}
</script>

<style scoped>
/* Base styles */
.executions-log-table {
  font-size: 14px;
  padding: 0 16px;
}

/* Search container */
.search-container {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}

.search-panel {
  display: flex;
  flex: 1;
  min-width: 200px;
}

.search-field {
  flex: 1;
  min-height: 40px;
  padding: 8px 12px;
  font-size: 14px;
  border: 1px solid var(--separator-color);
  border-radius: var(--radius-sm);
  background: var(--background-color);
  color: var(--font-color-main);
}

.search-field:focus {
  border-color: var(--primary-color);
  outline: none;
}

.search-button {
  align-self: center;
  min-width: 40px;
  min-height: 40px;
  padding: 8px;
}

.sort-dropdown {
  flex-shrink: 0;
}

.sort-select {
  min-height: 40px;
  padding: 8px 12px;
  font-size: 14px;
  border: 1px solid var(--separator-color);
  border-radius: var(--radius-sm);
  background: var(--background-color);
  color: var(--font-color-main);
}

/* Loading state */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 16px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--separator-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  margin-bottom: 16px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  color: var(--font-color-medium);
  font-size: 14px;
  text-align: center;
}

/* Card list */
.execution-cards {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.execution-card {
  background: var(--background-color-level-4dp);
  border-radius: var(--radius-md);
  overflow: hidden;
  cursor: pointer;
  transition: box-shadow var(--transition-fast), transform var(--transition-fast);
  box-shadow: var(--shadow-sm);
}

.execution-card:hover {
  box-shadow: var(--shadow-md);
}

.execution-card:active {
  transform: scale(0.995);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  border-bottom: 1px solid var(--separator-color);
}

.card-script {
  font-weight: 500;
  font-size: 14px;
  color: var(--font-color-main);
}

.card-status {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 500;
  background: var(--background-color-high-emphasis);
  color: var(--font-color-medium);
}

.card-status.status-success {
  background: var(--success-color-light);
  color: var(--success-color);
}

.card-status.status-error {
  background: var(--error-color-light);
  color: var(--error-color);
}

.card-status.status-running {
  background: var(--info-color-light);
  color: var(--info-color);
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 10px 14px;
}

.card-row {
  display: flex;
  gap: 8px;
  font-size: 12px;
}

.card-label {
  color: var(--font-color-medium);
  min-width: 45px;
}

.card-value {
  color: var(--font-color-main);
}

.card-actions {
  display: flex;
  justify-content: flex-end;
  padding: 6px 10px;
  border-top: 1px solid var(--separator-color);
}

.params-btn {
  padding: 6px 10px;
  min-width: auto;
  border-radius: var(--radius-sm);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.params-btn i {
  font-size: 18px;
  color: var(--font-color-medium);
}

.params-btn:hover i,
.params-btn.active i {
  color: var(--primary-color);
}

/* Parameters panel */
.card-params {
  padding: 10px 14px;
  background: var(--background-color-high-emphasis);
  border-top: 1px solid var(--separator-color);
}

.params-table {
  width: 100%;
  font-size: 12px;
  border-collapse: collapse;
}

.params-table th,
.params-table td {
  text-align: left;
  padding: 4px 8px;
}

.params-table th {
  color: var(--font-color-medium);
  font-weight: 500;
  border-bottom: 1px solid var(--separator-color);
}

.params-table .param-name {
  font-weight: 500;
  color: var(--font-color-main);
  white-space: nowrap;
  width: 30%;
}

.params-table .param-value {
  color: var(--font-color-medium);
  word-break: break-word;
}

/* Responsive */
@media screen and (max-width: 480px) {
  .executions-log-table {
    padding: 0 12px;
  }

  .search-container {
    flex-direction: column;
  }

  .sort-dropdown {
    width: 100%;
  }

  .sort-select {
    width: 100%;
  }
}

/* Card list transition animations */
.card-list-enter-active,
.card-list-leave-active {
  transition: all var(--transition-normal);
}

.card-list-enter,
.card-list-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

.card-list-move {
  transition: transform var(--transition-normal);
}

/* Expand transition */
.expand-enter-active,
.expand-leave-active {
  transition: all var(--transition-normal);
  overflow: hidden;
}

.expand-enter,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
}

/* Fade transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-normal);
}

.fade-enter,
.fade-leave-to {
  opacity: 0;
}
</style>
