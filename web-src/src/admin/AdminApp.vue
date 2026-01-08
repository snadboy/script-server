<template>
  <div class="admin-page">
    <div class="page-title primary-color-dark">
      <div class="main-header">
        <a class="btn-flat left home-button" href="index.html">
          <i class="material-icons">arrow_back</i>
          <span class="back-label">Back</span>
        </a>
        <div class="page-label">{{ pageLabel }}</div>
        <div class="header-actions">
          <ThemeToggle />
        </div>
      </div>
    </div>
    <router-view class="page-content"/>
  </div>
</template>

<script>
import executions from '@/common/store/executions-module';
import Vue from 'vue';
import Vuex, {mapActions} from 'vuex';
import scriptConfig from './store/script-config-module';
import scripts from './store/scripts-module';
import File_upload from '@/common/components/file_upload'
import authModule from '@/common/store/auth';
import ThemeToggle from '@/common/components/ThemeToggle';

Vue.use(Vuex);

const store = new Vuex.Store({
  modules: {
    'history': executions(),
    scripts: scripts,
    scriptConfig: scriptConfig,
    auth: authModule
  }
});

export default {
  name: 'AdminApp',
  components: {File_upload, ThemeToggle},
  store,

  mounted() {
    this.init()
  },

  computed: {
    pageLabel() {
      const path = this.$route.path;
      if (path.startsWith('/scripts/new')) return 'Add Script';
      if (path.startsWith('/scripts/')) return 'Edit Script';
      if (path.startsWith('/scripts')) return 'Scripts';
      if (path.startsWith('/users')) return 'Users';
      if (path.startsWith('/logs')) return 'Logs';
      return 'Admin';
    }
  },

  methods: {
    ...mapActions('auth', ['init'])
  }
}
</script>

<style scoped>
.admin-page {
  display: flex;
  flex-direction: column;

  background: var(--background-color);
  font-family: "Roboto", sans-serif;
  font-weight: normal;

  height: 100vh;
}

.page-title {
  flex: 0 0 0;
  width: 100%;

  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;

  box-shadow: var(--shadow-4dp);
}

.main-header {
  display: flex;
  align-items: center;
  height: 48px;
}

.page-label {
  font-size: 1.25em;
  font-weight: 500;
  color: var(--font-on-primary-color-dark-main);
  margin-left: 8px;
}

.page-content {
  flex: 1 1 0;
  overflow-y: auto;
}

.home-button {
  height: 100%;
  padding-left: 16px;
  padding-right: 16px;
  display: flex;
  align-items: center;
  color: var(--font-on-primary-color-dark-main);
}

.home-button i {
  font-size: 1.5em;
}

.back-label {
  margin-left: 4px;
  font-size: 1em;
}

.header-actions {
  margin-left: auto;
  margin-right: 16px;
  display: flex;
  align-items: center;
}

.header-actions >>> .theme-button i {
  color: var(--font-on-primary-color-dark-main) !important;
}
</style>