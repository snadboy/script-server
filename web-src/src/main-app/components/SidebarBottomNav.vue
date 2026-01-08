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

    <router-link v-if="adminUser"
       class="nav-tab waves-effect"
       to="/admin/scripts/_new"
       :class="{ active: isAddScriptActive }">
      <i class="material-icons">add_circle_outline</i>
      <span class="nav-label">Add Script</span>
    </router-link>

    <router-link v-if="adminUser"
       class="nav-tab waves-effect"
       to="/admin/users"
       :class="{ active: isUsersActive }">
      <i class="material-icons">people</i>
      <span class="nav-label">Users</span>
    </router-link>
  </div>
</template>

<script>
import {mapState} from 'vuex';

export default {
  name: 'SidebarBottomNav',

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
    isAddScriptActive() {
      return this.$route.path.includes('/admin/scripts');
    },
    isUsersActive() {
      return this.$route.path.includes('/admin/users');
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
