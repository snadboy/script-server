<template>
  <div class="script-header main-content-header">
    <h2 v-show="selectedScript" class="header">{{ selectedScript }}</h2>
    <!-- ExecutionInstanceTabs removed - replaced by ScriptExecutionsPanel -->
    <div class="spacer"></div>
  </div>
</template>

<script>
import {mapState} from 'vuex';

export default {
  name: 'ScriptHeader',

  computed: {
    ...mapState('scripts', {
      selectedScript: 'selectedScript'
    })
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
</style>