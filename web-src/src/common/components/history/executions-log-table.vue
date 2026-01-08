<template>
  <div class="executions-log-table">
    <div class="search-container">
      <div class="search-panel">
        <input ref="searchField" autocomplete="off" class="search-field"
               name="searchField"
               placeholder="Search"
               v-model="searchText">
        <input :alt="isClearSearchButton ? 'Clear search' : 'Search'" :src="searchImage"
             class="search-button"
             type="image"
             @click="searchIconClickHandler">
      </div>
    </div>
    <table class="highlight striped">
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
    }
  },

  computed: {
    ...mapState('history', ['loading']),

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
  }
}
</script>

<style scoped>
/* Improved font size for readability */
.executions-log-table {
  font-size: 14px;
}

.executions-log-table th  {
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
  width: 25%;
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
  content: ""
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

.search-container {
  min-width: 200px;
  width: 50%;
}

.search-panel {
  display: flex;
}

.search-button {
  align-self: center;
}

.params-header-column,
.params-column {
  width: 48px;
  text-align: center;
}

.params-btn {
  padding: 4px 8px;
  min-width: auto;
  line-height: 1;
}

.params-btn i {
  color: var(--font-color-medium);
  font-size: 20px;
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
</style>
