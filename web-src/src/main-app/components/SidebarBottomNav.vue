<template>
  <div class="sidebar-bottom-nav">
    <router-link
        class="nav-tab waves-effect"
        to="/"
        :class="{ active: isHistoryActive }">
      <i class="material-icons">history</i>
      <span class="nav-label">History</span>
    </router-link>

    <router-link
        class="nav-tab waves-effect"
        to="/scheduled"
        :class="{ active: isScheduledActive }">
      <i class="material-icons">schedule</i>
      <span class="nav-label">Scheduled</span>
    </router-link>

    <button v-if="adminUser"
       class="nav-tab waves-effect"
       @click="showAddScriptModal = true">
      <i class="material-icons">add_circle_outline</i>
      <span class="nav-label">Add Script</span>
    </button>

    <router-link v-if="adminUser"
       class="nav-tab waves-effect"
       to="/admin/users"
       :class="{ active: isUsersActive }">
      <i class="material-icons">people</i>
      <span class="nav-label">Users</span>
    </router-link>

    <AddScriptModal
      :visible="showAddScriptModal"
      @close="showAddScriptModal = false"
      @saved="onScriptSaved"
    />
  </div>
</template>

<script>
import {mapState} from 'vuex';
import AddScriptModal from '@/admin/components/scripts-config/AddScriptModal';

export default {
  name: 'SidebarBottomNav',

  components: {
    AddScriptModal
  },

  data() {
    return {
      showAddScriptModal: false
    };
  },

  computed: {
    ...mapState('auth', {
      adminUser: 'admin'
    }),
    isHistoryActive() {
      // Active when on root path or history path
      return this.$route.path === '/' || this.$route.path === '/history';
    },
    isScheduledActive() {
      return this.$route.path === '/scheduled';
    },
    isUsersActive() {
      return this.$route.path.includes('/admin/users');
    }
  },

  methods: {
    onScriptSaved(scriptName) {
      this.showAddScriptModal = false;
      // Refresh scripts list if we're on the scripts page
      if (this.$route.path.includes('/admin/scripts')) {
        this.$store.dispatch('adminScripts/init');
      }
    }
  }
}
</script>

<style scoped>
.sidebar-bottom-nav {
  display: flex;
  flex-direction: row;
  justify-content: space-around;
  align-items: center;
  height: 48px;
  width: 100%;
  border-bottom: 1px solid var(--separator-color);
  flex-shrink: 0;
  background: var(--background-color);
}

.nav-tab {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  height: 100%;
  text-decoration: none;
  color: var(--font-color-medium);
  transition: color 0.2s ease, background-color 0.2s ease;
  padding: 4px 8px;
  /* Reset button styles */
  border: none;
  background: transparent;
  cursor: pointer;
  font-family: inherit;
}

.nav-tab:hover {
  background-color: var(--hover-color);
  color: var(--primary-color);
}

.nav-tab.active {
  color: var(--primary-color);
}

.nav-tab i {
  font-size: 20px;
  line-height: 1;
}

.nav-label {
  font-size: 10px;
  margin-top: 2px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

/* Hide labels on narrow screens */
@media screen and (max-width: 300px) {
  .nav-label {
    display: none;
  }

  .nav-tab i {
    font-size: 24px;
  }
}
</style>
