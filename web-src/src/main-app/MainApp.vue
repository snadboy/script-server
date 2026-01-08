<template xmlns:v-slot="http://www.w3.org/1999/XSL/Transform">
  <div id="main-app">
    <!-- Admin pages use a different layout -->
    <template v-if="isAdminRoute">
      <router-view/>
    </template>
    <!-- Regular pages use AppLayout with sidebar -->
    <template v-else>
      <AppLayout ref="appLayout" :loading="pageLoading">
        <template v-slot:sidebar>
          <MainAppSidebar/>
        </template>
        <template v-slot:header>
          <router-view name="header"/>
        </template>
        <template v-slot:content>
          <transition name="fade" mode="out-in">
            <router-view/>
          </transition>
        </template>
      </AppLayout>
    </template>
    <DocumentTitleManager/>
    <FaviconManager/>
  </div>
</template>

<script>
import '@/assets/css/index.css';
import AppLayout from '@/common/components/AppLayout';
import {isEmptyString} from '@/common/utils/common';
import {mapActions, mapState} from 'vuex';
import AppWelcomePanel from './components/AppWelcomePanel';
import DocumentTitleManager from './components/DocumentTitleManager';
import FaviconManager from './components/FaviconManager';
import MainAppSidebar from './components/MainAppSidebar';
import MainAppContent from './components/scripts/MainAppContent';

export default {
  name: 'App',
  components: {
    AppLayout,
    MainAppSidebar,
    MainAppContent,
    AppWelcomePanel,
    DocumentTitleManager,
    FaviconManager
  },
  methods: {
    ...mapActions({
      init: 'init'
    })
  },
  computed: {
    ...mapState('page', ['pageLoading']),
    isAdminRoute() {
      return this.$route.path.startsWith('/admin');
    }
  },

  created() {
    this.init();
  },

  mounted() {
    const currentPath = this.$router.currentRoute.path;
    if (this.$refs.appLayout) {
      this.$refs.appLayout.setSidebarVisibility(isEmptyString(currentPath) || (currentPath === '/'));
    }

    this.$router.afterEach((to) => {
      // Don't manipulate sidebar for admin routes
      if (!to.path.startsWith('/admin') && this.$refs.appLayout) {
        // Only collapse sidebar on narrow screens (mobile/tablet)
        // On desktop (> 992px), keep sidebar visible
        const isNarrowScreen = window.innerWidth <= 992;
        if (isNarrowScreen) {
          this.$refs.appLayout.setSidebarVisibility(false);
        }
      }
    });
  }
}
</script>

<style>
h1, h2, h3, h4, h5, h6 {
  margin: 0;
}
</style>