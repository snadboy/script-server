<template>
  <div class="admin-layout">
    <div class="admin-header primary-color-dark">
      <router-link class="btn-flat back-button" to="/">
        <i class="material-icons">arrow_back</i>
        <span class="back-label">Back</span>
      </router-link>
      <div class="page-label">{{ pageLabel }}</div>
      <div class="header-spacer"></div>
    </div>
    <div class="admin-content">
      <router-view/>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminLayout',

  computed: {
    pageLabel() {
      const path = this.$route.path;
      if (path.includes('/admin/scripts/new') || path.includes('/admin/scripts/_new')) return 'Add Script';
      if (path.match(/\/admin\/scripts\/.+/)) return 'Edit Script';
      if (path.includes('/admin/scripts')) return 'Scripts';
      if (path.includes('/admin/users')) return 'Users';
      if (path.includes('/admin/logs')) return 'Logs';
      return 'Admin';
    }
  }
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: var(--background-color);
}

.admin-header {
  display: flex;
  align-items: center;
  height: 48px;
  flex-shrink: 0;
  box-shadow: var(--shadow-4dp);
}

.back-button {
  height: 100%;
  padding: 0 16px;
  display: flex;
  align-items: center;
  color: var(--font-on-primary-color-dark-main);
  text-decoration: none;
}

.back-button:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.back-button i {
  font-size: 24px;
}

.back-label {
  margin-left: 4px;
  font-size: 14px;
}

.page-label {
  font-size: 1.25em;
  font-weight: 500;
  color: var(--font-on-primary-color-dark-main);
  margin-left: 8px;
}

.header-spacer {
  flex: 1;
}

.admin-content {
  flex: 1 1 auto;
  overflow-y: auto;
  /* Let content determine height, remove flex shrinking */
}
</style>
