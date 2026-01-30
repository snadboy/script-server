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
      <button v-if="adminUser" class="scripts-btn waves-effect waves-circle" @click="showScripts = true" title="Script Manager">
        <i class="material-icons">description</i>
      </button>
      <button v-if="adminUser" class="packages-btn waves-effect waves-circle" @click="showPackages = true" title="Package Manager">
        <i class="material-icons">storage</i>
      </button>
      <button v-if="adminUser" class="requirements-btn waves-effect waves-circle" @click="showRequirements = true" title="Requirements">
        <i class="material-icons">list_alt</i>
      </button>
      <button v-if="adminUser" class="logs-btn waves-effect waves-circle" @click="showLogs = true" title="Server Logs">
        <i class="material-icons">subject</i>
      </button>
      <button class="settings-btn waves-effect waves-circle" @click="showSettings = true" title="Settings">
        <i class="material-icons">settings</i>
      </button>
    </div>

    <SettingsModal :visible="showSettings" @close="showSettings = false" />
    <ProjectsModal v-if="adminUser" :visible="showScripts" @close="showScripts = false" />
    <PackagesModal v-if="adminUser" :visible="showPackages" @close="showPackages = false" />
    <RequirementsModal v-if="adminUser" :visible="showRequirements" @update:visible="showRequirements = $event" />
    <ServerLogsModal v-if="adminUser" :visible="showLogs" @update:visible="showLogs = $event" />

    <SidebarBottomNav />

    <ScriptsList :search-text="searchText"/>

    <div class="bottom-panels">
      <div class="fork-version"><strong>snadboy-fork</strong> v1.0.0 <span class="build-number">build {{ buildTimestamp }}</span></div>
      <div class="local-time">{{ currentDateTime }}</div>
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
import ProjectsModal from './ProjectsModal';
import PackagesModal from './PackagesModal';
import RequirementsModal from './RequirementsModal';
import ServerLogsModal from './ServerLogsModal';
import ThemeToggle from '@/common/components/ThemeToggle';

export default {
  name: 'MainAppSidebar',
  components: {
    SearchPanel,
    ScriptsList,
    SidebarBottomNav,
    SettingsModal,
    ProjectsModal,
    PackagesModal,
    RequirementsModal,
    ServerLogsModal,
    ThemeToggle
  },

  data() {
    return {
      searchText: '',
      showSettings: false,
      showScripts: false,
      showPackages: false,
      showRequirements: false,
      showLogs: false,
      currentTime: new Date(),
      timeInterval: null
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
    },
    currentDateTime() {
      const options = {
        month: 'numeric',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      };
      return this.currentTime.toLocaleString('en-US', options).replace(',', ' @');
    }
  },

  mounted() {
    this.timeInterval = setInterval(() => {
      this.currentTime = new Date();
    }, 1000);
  },

  beforeDestroy() {
    if (this.timeInterval) {
      clearInterval(this.timeInterval);
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

.local-time {
  font-size: 0.75rem;
  color: var(--font-color-medium);
  text-align: center;
  padding: 2px 8px 6px;
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
.packages-btn,
.scripts-btn,
.requirements-btn,
.logs-btn {
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
.packages-btn:hover,
.scripts-btn:hover,
.requirements-btn:hover,
.logs-btn:hover {
  background: var(--background-color-high-emphasis);
}

.settings-btn i,
.packages-btn i,
.scripts-btn i,
.requirements-btn i,
.logs-btn i {
  font-size: 24px;
  color: var(--font-color-main);
}

</style>