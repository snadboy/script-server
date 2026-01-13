<template>
  <div class="main-app-sidebar">
    <div class="list-header">
      <router-link :class="{
                    'header-gt-15-chars' : serverName && serverName.length >= 15,
                   'header-gt-18-chars' : serverName && serverName.length >= 18,
                   'header-gt-21-chars' : serverName && serverName.length >= 21
      }" :title="versionString"
                   class="header server-header"
                   to="/">
        {{ serverName || 'Script server' }}
      </router-link>

      <SearchPanel v-model="searchText"/>
      <button v-if="adminUser" class="packages-btn waves-effect waves-circle" @click="showPackages = true" title="Package Manager">
        <i class="material-icons">inventory_2</i>
      </button>
      <button class="settings-btn waves-effect waves-circle" @click="showSettings = true" title="Settings">
        <i class="material-icons">settings</i>
      </button>
    </div>

    <SettingsModal :visible="showSettings" @close="showSettings = false" />
    <PackagesModal v-if="adminUser" :visible="showPackages" @close="showPackages = false" />

    <SidebarBottomNav />

    <ScriptsList :search-text="searchText"/>

    <div class="bottom-panels">
      <div class="fork-version"><strong>snadboy-fork</strong> v1.0.0 <span class="build-number">build {{ buildTimestamp }}</span></div>
      <div class="logout-panel">
        <ThemeToggle />
        <span v-if="authEnabled" class="username">{{ username }}</span>
        <a v-if="authEnabled" class="btn-icon-flat waves-effect logout-button waves-circle" @click="logout">
          <i class="material-icons primary-color-text">power_settings_new</i>
        </a>
      </div>
    </div>
  </div>
</template>

<script>
import {mapActions, mapState} from 'vuex';
import ScriptsList from './scripts/ScriptsList'
import SearchPanel from './SearchPanel';
import SidebarBottomNav from './SidebarBottomNav';
import SettingsModal from './SettingsModal';
import PackagesModal from './PackagesModal';
import ThemeToggle from '@/common/components/ThemeToggle';

export default {
  name: 'MainAppSidebar',
  components: {
    SearchPanel,
    ScriptsList,
    SidebarBottomNav,
    SettingsModal,
    PackagesModal,
    ThemeToggle
  },

  data() {
    return {
      searchText: '',
      showSettings: false,
      showPackages: false
    }
  },

  computed: {
    ...mapState('serverConfig', {
      versionString: state => state.version ? 'v' + state.version : null,
      serverName: 'serverName'
    }),
    ...mapState('auth', {
      adminUser: 'admin',
      username: 'username',
      authEnabled: 'enabled'
    }),
    buildTimestamp() {
      return process.env.VUE_APP_BUILD_TIMESTAMP || 'dev';
    }
  },

  methods: {
    ...mapActions(['logout'])
  }
}
</script>

<style scoped>
.list-header {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-end;

  border-bottom: 5px solid transparent; /* This is to make the header on the same level as the script header */

  flex-shrink: 0;

  position: relative;
}

.server-header {
  flex-grow: 1;
  margin-left: 0.4rem;

  font-size: 1.64rem;
  padding: 0.8rem;
  font-weight: 300;
  line-height: 110%;
  color: var(--font-color-main);
  min-width: 0;

  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  word-break: break-all;
}

.server-header.header-gt-15-chars {
  font-size: 1.45rem;
}

.server-header.header-gt-18-chars {
  font-size: 1.25rem;
}

.server-header.header-gt-21-chars {
  font-size: 1.2rem;
}

.main-app-sidebar {
  height: 100%;

  background: var(--background-color);

  display: flex;
  flex-direction: column;
}

.bottom-panels {
  flex-shrink: 0;
  border-top: 1px solid var(--separator-color);
}

.fork-version {
  font-size: 0.75rem;
  color: var(--font-color-medium);
  text-align: center;
  padding: 6px 8px 2px;
}

.fork-version .build-number {
  font-weight: bold;
  color: var(--primary-color);
}

.logout-panel {
  height: 2.5em;
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
}

.logout-button {
  margin-left: 4px;
}

.username {
  margin-left: 8px;
}

.settings-btn,
.packages-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  margin-right: 4px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.settings-btn:hover,
.packages-btn:hover {
  background: var(--background-color-high-emphasis);
}

.settings-btn i,
.packages-btn i {
  font-size: 24px;
  color: var(--font-color-medium);
}

</style>