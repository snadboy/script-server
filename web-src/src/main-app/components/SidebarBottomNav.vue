<template>
  <div class="sidebar-bottom-nav">
    <router-link
        class="nav-tab waves-effect"
        to="/"
        :class="{ active: isActivityActive }">
      <i class="material-icons">schedule</i>
      <span class="nav-label">Activity</span>
    </router-link>

    <button v-if="adminUser"
       class="nav-tab waves-effect"
       @click="showUsersModal = true">
      <i class="material-icons">people</i>
      <span class="nav-label">Users</span>
    </button>

    <UserManagementModal
      :visible="showUsersModal"
      @close="showUsersModal = false"
    />
  </div>
</template>

<script>
import {mapState} from 'vuex';
import UserManagementModal from '@/admin/components/UserManagementModal';

export default {
  name: 'SidebarBottomNav',

  components: {
    UserManagementModal
  },

  data() {
    return {
      showUsersModal: false
    };
  },

  computed: {
    ...mapState('auth', {
      adminUser: 'admin'
    }),
    isActivityActive() {
      // Active when on root path or activity path
      return this.$route.path === '/' || this.$route.path.startsWith('/activity');
    }
  }
}
</script>

<style scoped>
.sidebar-bottom-nav {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: stretch;
  height: 56px;
  width: 100%;
  border-bottom: 1px solid var(--separator-color);
  flex-shrink: 0;
  background: var(--background-color);
  padding: 4px 0;
  gap: 0;
}

.nav-tab {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1 1 0;
  min-width: 0;
  text-decoration: none;
  color: var(--font-color-medium);
  transition: color 0.2s ease, background-color 0.2s ease;
  padding: 4px 2px;
  /* Reset button styles */
  border: none;
  background: transparent;
  cursor: pointer;
  font-family: inherit;
  box-sizing: border-box;
  /* Ensure consistent baseline alignment */
  line-height: normal;
  vertical-align: middle;
  overflow: visible;
}

/* Additional button-specific resets */
button.nav-tab {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
}

.nav-tab:hover {
  background-color: var(--hover-color);
  color: var(--primary-color);
}

.nav-tab.active {
  color: var(--primary-color);
}

.nav-tab i {
  font-size: 24px;
  display: block !important;
  line-height: 1;
  padding: 0 !important;
  min-height: auto !important;
  min-width: auto !important;
  height: 24px;
}

.nav-label {
  font-size: 9px;
  margin-top: 4px;
  text-transform: uppercase;
  letter-spacing: 0;
  display: block;
  line-height: 1;
  white-space: nowrap;
}

/* Hide labels on narrow screens */
@media screen and (max-width: 300px) {
  .nav-label {
    display: none;
  }
}
</style>
