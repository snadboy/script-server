<template>
  <div class="activity-page">
    <!-- Show execution details if viewing a specific execution -->
    <router-view v-if="showExecutionDetail" />

    <!-- Show activity sections when at base /activity route -->
    <template v-else>
      <RunningSection :showScriptName="true" />
      <ScheduledSection :showScriptName="true" :showParams="true" />
      <CompletedSection :limit="completedExecutionsLimit" />
    </template>
  </div>
</template>

<script>
import {mapState} from 'vuex';
import RunningSection from '../common/RunningSection';
import ScheduledSection from '../common/ScheduledSection';
import CompletedSection from '../common/CompletedSection';

export default {
  name: 'ActivityPage',

  components: {
    RunningSection,
    ScheduledSection,
    CompletedSection
  },

  computed: {
    ...mapState('settings', ['completedExecutionsLimit']),

    showExecutionDetail() {
      // Show execution details when route has an executionId param
      return !!this.$route.params.executionId;
    }
  }
};
</script>

<style scoped>
.activity-page {
  height: 100%;
  overflow-y: auto;
  background: var(--background-color);
  padding: 16px 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
