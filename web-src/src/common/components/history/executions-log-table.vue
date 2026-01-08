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
      <!-- Mobile sort dropdown -->
      <div class="mobile-sort">
        <select v-model="mobileSortOption" class="sort-select">
          <option value="id-desc">Newest first</option>
          <option value="id-asc">Oldest first</option>
          <option value="script-asc">Script A-Z</option>
          <option value="user-asc">User A-Z</option>
        </select>
      </div>
    </div>

    <!-- Desktop/Tablet: Table view with horizontal scroll -->
    <div class="table-wrapper">
      <table class="highlight striped desktop-table">
        <thead>
        <tr>
          <th class="id-column" :class="showSort('id')" @click="sortBy('id')">ID</th>
          <th class="start_time-column" :class="showSort('startTimeString')" @click="sortBy('startTimeString')">Start Time</th>
          <th class="user-column" :class="showSort('user')" @click="sortBy('user')">User</th>
          <th class="script-column" :class="showSort('script')" @click="sortBy('script')">Script</th>
          <th class="status-column" :class="showSort('fullStatus')" @click="sortBy('fullStatus')">Status</th>
          <th class="params-header-column"></th>
        </tr>
        </thead>
        <tbody v-if="!loading">
        <template v-for="row in filteredRows">
          <tr :key="row.id" @click="rowClick(row)">
            <td>{{ row.id }}</td>
            <td>{{ row.startTimeString }}</td>
            <td>{{ row.user }}</td>
            <td>{{ row.script }}</td>
            <td>{{ row.fullStatus }}</td>
            <td class="params-column">
              <button v-if="hasParams(row)"
                      class="btn-flat waves-effect params-btn"
                      :class="{ active: expandedParams === row.id }"
                      @click.stop="toggleParams(row.id)"
                      title="Show parameters">
                <i class="material-icons">tune</i>
              </button>
            </td>
          </tr>
          <tr v-if="expandedParams === row.id" :key="'params-' + row.id" class="params-row">
            <td colspan="6">
              <div class="params-panel">
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
            </td>
          </tr>
        </template>
        </tbody>
      </table>
    </div>

    <!-- Mobile: Card view -->
    <div class="mobile-cards" v-if="!loading">
      <div v-for="row in filteredRows" :key="'card-' + row.id"
           class="execution-card"
           @click="rowClick(row)">
        <div class="card-header">
          <span class="card-script">{{ row.script }}</span>
          <span class="card-status" :class="getStatusClass(row.fullStatus)">{{ row.fullStatus }}</span>
        </div>
        <div class="card-body">
          <div class="card-row">
            <span class="card-label">ID:</span>
            <span class="card-value">{{ row.id }}</span>
          </div>
          <div class="card-row">
            <span class="card-label">User:</span>
            <span class="card-value">{{ row.user }}</span>
          </div>
          <div class="card-row">
            <span class="card-label">Time:</span>
            <span class="card-value">{{ row.startTimeString }}</span>
          </div>
        </div>
        <div class="card-actions" v-if="hasParams(row)">
          <button class="btn-flat waves-effect params-btn"
                  :class="{ active: expandedParams === row.id }"
                  @click.stop="toggleParams(row.id)"
                  title="Show parameters">
            <i class="material-icons">tune</i>
            <span>Parameters</span>
          </button>
        </div>
        <div v-if="expandedParams === row.id" class="card-params">
          <div v-for="(value, name) in row.parameterValues" :key="name" class="param-row">
            <span class="param-name">{{ name }}:</span>
            <span class="param-value">{{ formatParamValue(value) }}</span>
          </div>
        </div>
      </div>
    </div>

    <p v-if="loading" class="loading-text">History will appear here</p>
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
  min-height: 44px;
  padding: 8px 12px;
  font-size: 14px;
}

.search-button {
  align-self: center;
  min-width: 44px;
  min-height: 44px;
  padding: 10px;
}

/* Mobile sort dropdown - hidden on desktop */
.mobile-sort {
  display: none;
}

.sort-select {
  min-height: 44px;
  padding: 8px 12px;
  font-size: 14px;
  border: 1px solid var(--separator-color);
  border-radius: 4px;
  background: var(--background-color);
  color: var(--font-color-main);
}

/* Table wrapper for horizontal scroll on tablet */
.table-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  /* Scroll shadow indicators */
  background:
    linear-gradient(to right, var(--background-color) 30%, transparent),
    linear-gradient(to left, var(--background-color) 30%, transparent),
    linear-gradient(to right, rgba(0,0,0,0.15), transparent 15px),
    linear-gradient(to left, rgba(0,0,0,0.15), transparent 15px);
  background-position: left, right, left, right;
  background-repeat: no-repeat;
  background-size: 40px 100%, 40px 100%, 15px 100%, 15px 100%;
  background-attachment: local, local, scroll, scroll;
}

/* Desktop table */
.desktop-table {
  min-width: 600px;
}

.executions-log-table th {
  cursor: pointer;
  font-weight: 500;
}

.executions-log-table tbody > tr {
  cursor: pointer;
}

.executions-log-table .id-column {
  width: 10%;
}

.executions-log-table .start_time-column {
  width: 25%;
}

.executions-log-table .user-column {
  width: 20%;
}

.executions-log-table .script-column {
  width: 25%;
}

.executions-log-table .status-column {
  width: 15%;
}

.loading-text {
  color: var(--font-color-medium);
  font-size: 1.2em;
  text-align: center;
  margin-top: 1em;
}

.executions-log-table .sorted:after {
  display: inline-block;
  vertical-align: middle;
  width: 0;
  height: 0;
  margin-left: 5px;
  content: "";
}

.executions-log-table .sorted.asc:after {
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-bottom: 4px solid var(--font-color-main);
}

.executions-log-table .sorted.desc:after {
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-top: 4px solid var(--font-color-main);
}

.params-header-column,
.params-column {
  width: 48px;
  text-align: center;
}

.params-btn {
  padding: 8px;
  min-width: 44px;
  min-height: 44px;
  line-height: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.params-btn i {
  color: var(--font-color-medium);
  font-size: 20px;
}

.params-btn span {
  display: none;
}

.params-btn:hover i,
.params-btn.active i {
  color: var(--primary-color);
}

.params-row {
  cursor: default;
}

.params-row:hover {
  background-color: inherit !important;
}

.params-panel {
  padding: 8px 16px;
  background-color: var(--background-color-high-emphasis);
  border-radius: 4px;
  margin: 4px 0;
}

.params-table {
  width: 100%;
  font-size: 14px;
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

/* Mobile cards - hidden on desktop */
.mobile-cards {
  display: none;
}

.execution-card {
  background: var(--background-color-level-4dp);
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.execution-card:hover {
  background: var(--hover-color);
}

.execution-card:active {
  background: var(--background-color-high-emphasis);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.card-script {
  font-weight: 500;
  font-size: 16px;
  color: var(--font-color-main);
}

.card-status {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 12px;
  background: var(--background-color-high-emphasis);
  color: var(--font-color-medium);
}

.card-status.status-success {
  background: rgba(76, 175, 80, 0.2);
  color: #4caf50;
}

.card-status.status-error {
  background: rgba(244, 67, 54, 0.2);
  color: #f44336;
}

.card-status.status-running {
  background: rgba(33, 150, 243, 0.2);
  color: #2196f3;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.card-row {
  display: flex;
  font-size: 13px;
}

.card-label {
  color: var(--font-color-medium);
  width: 50px;
  flex-shrink: 0;
}

.card-value {
  color: var(--font-color-main);
}

.card-actions {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--separator-color);
}

.card-actions .params-btn {
  width: 100%;
  justify-content: center;
}

.card-actions .params-btn span {
  display: inline;
  margin-left: 4px;
}

.card-params {
  margin-top: 8px;
  padding: 8px;
  background: var(--background-color-high-emphasis);
  border-radius: 4px;
}

.card-params .param-row {
  display: flex;
  gap: 8px;
  padding: 4px 0;
  font-size: 13px;
}

.card-params .param-name {
  color: var(--font-color-medium);
  flex-shrink: 0;
}

.card-params .param-value {
  color: var(--font-color-main);
  word-break: break-word;
}

/* Responsive: Mobile (< 768px) - Show cards, hide table */
@media screen and (max-width: 767px) {
  .table-wrapper {
    display: none;
  }

  .mobile-cards {
    display: block;
  }

  .mobile-sort {
    display: block;
  }

  .search-container {
    width: 100%;
  }

  .search-panel {
    flex: 1;
  }
}

/* Responsive: Tablet (768px - 992px) - Show table with scroll */
@media screen and (min-width: 768px) and (max-width: 992px) {
  .table-wrapper {
    margin: 0 -16px;
    padding: 0 16px;
  }
}
</style>
