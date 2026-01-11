<template>
  <div class="script-header main-content-header">
    <h2 v-show="selectedScript" class="header">{{ selectedScript }}</h2>
    <!-- ExecutionInstanceTabs removed - replaced by ScriptExecutionsPanel -->
    <div class="spacer"></div>
    <button class="button-history btn btn-flat"
            @click="openParameterHistory"
            title="Parameter History">
      <i class="material-icons">history</i>
    </button>
    <ParameterHistoryModal ref="parameterHistoryModal" :scriptName="selectedScript" @use-parameters="handleUseParameters"/>
  </div>
</template>

<script>
import ParameterHistoryModal from '@/main-app/components/scripts/ParameterHistoryModal';
import {mapState} from 'vuex';

export default {
  name: 'ScriptHeader',

  components: {ParameterHistoryModal},
  computed: {
    ...mapState('scripts', {
      selectedScript: 'selectedScript'
    })
  },
  methods: {
    openParameterHistory() {
      this.$refs.parameterHistoryModal.open();
    },

    handleUseParameters(values) {
      // Set all parameter values using the scriptSetup store
      for (const [parameterName, value] of Object.entries(values)) {
        this.$store.dispatch('scriptSetup/setParameterValue', { parameterName, value });
      }
    }
  }
}
</script>

<style scoped>
.script-header {
  display: flex;
  align-items: center;
  height: 56px;
}

.script-header h2.header {
  padding: 0;
  margin-right: 24px;
  flex: 0 0 auto;

  line-height: 1.7em;
  font-size: 1.7em;
}

.spacer {
  flex: 1 1 0;
}

.button-history {
  margin-right: 16px;
  width: 40px;
  height: 40px;
  line-height: 40px;
  padding: 0;
  min-width: 40px;
  color: var(--font-color-medium);
}

.button-history i {
  font-size: 24px;
}
</style>