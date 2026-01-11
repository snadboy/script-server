<template>
  <div class="activity-page">
    <RunningSection :showScriptName="true" />
    <ScheduledSection :showScriptName="true" :showParams="true" />
    <CompletedSection :limit="completedExecutionsLimit" />
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
    ...mapState('settings', ['completedExecutionsLimit'])
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
