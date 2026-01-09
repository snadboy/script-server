<template>
  <div class="container scripts-list">
    <PageProgress v-if="loading"/>
    <transition name="fade" mode="out-in">
      <div v-if="!loading" key="content">
        <button class="waves-effect waves-light btn add-script-btn" @click="showAddScriptModal = true">
          <i class="material-icons left">add</i>
          Add Script
        </button>
        <div class="collection card-flat">
          <transition-group name="list" tag="div">
            <router-link v-for="script in scripts"
                         :key="script.name"
                         :class="{'parsing-failed': script.parsingFailed}"
                         :to="script.path"
                         append
                         class="collection-item">
              <i class="material-icons script-icon">description</i>
              <span class="script-name">{{ script.name }}</span>
              <i class="material-icons chevron">chevron_right</i>
            </router-link>
          </transition-group>
        </div>
      </div>
    </transition>

    <AddScriptModal
      :visible="showAddScriptModal"
      @close="showAddScriptModal = false"
      @saved="onScriptSaved"
    />
  </div>
</template>

<script>
import PageProgress from '@/common/components/PageProgress';
import AddScriptModal from './AddScriptModal';
import {mapActions, mapState} from 'vuex';

export default {
  name: 'ScriptsList',

  mounted: function () {
    this.init();
  },

  data() {
    return {
      showAddScriptModal: false
    }
  },

  computed: {
    ...mapState('adminScripts', {
      scripts: state => {
        return state.scripts
            ? state.scripts.map(s => ({
              name: s.name,
              path: encodeURIComponent(s.name),
              parsingFailed: s.parsingFailed
            }))
            : []
      },
      loading: 'loading'
    })
  },

  components: {
    PageProgress,
    AddScriptModal
  },

  methods: {
    ...mapActions('adminScripts', ['init']),

    onScriptSaved(scriptName) {
      this.showAddScriptModal = false;
      this.init();  // Refresh the scripts list
    }
  }
}
</script>

<style scoped>
.scripts-list {
  margin-top: 1.5em;
  margin-bottom: 1em;
}

.add-script-btn {
  margin-bottom: 1em;
}

/* Enhanced collection styling */
.scripts-list .collection {
  border-radius: var(--radius-md);
  overflow: hidden;
}

.scripts-list .collection-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  transition: background-color var(--transition-fast), transform var(--transition-fast);
}

.scripts-list .collection-item:hover {
  background-color: var(--hover-color);
}

.scripts-list .collection-item:active {
  transform: scale(0.995);
}

.script-icon {
  color: var(--font-color-medium);
  margin-right: 12px;
  font-size: 20px;
}

.script-name {
  flex: 1;
}

.chevron {
  color: var(--font-color-medium);
  font-size: 20px;
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.collection-item:hover .chevron {
  opacity: 1;
}

.scripts-list .collection-item.parsing-failed {
  color: var(--error-color);
  pointer-events: none;
}

.scripts-list .collection-item.parsing-failed .script-icon {
  color: var(--error-color);
}

.scripts-list .collection-item.parsing-failed .script-name::after {
  content: ' (failed to parse config file)';
  font-size: 0.85em;
  opacity: 0.8;
}

/* List transition animations */
.list-enter-active,
.list-leave-active {
  transition: all var(--transition-normal);
}

.list-enter,
.list-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}

.list-move {
  transition: transform var(--transition-normal);
}

/* Fade transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-normal);
}

.fade-enter,
.fade-leave-to {
  opacity: 0;
}
</style>