<template>
  <div class="activity-page">
    <RunningSection :showScriptName="true" />
    <ScheduledSection :showScriptName="true" :showParams="true" />
    <CompletedSection />
  </div>
</template>

<script>
import RunningSection from '../common/RunningSection';
import ScheduledSection from '../common/ScheduledSection';
import CompletedSection from '../common/CompletedSection';

export default {
  name: 'ActivityPage',

  components: {
    RunningSection,
    ScheduledSection,
    CompletedSection
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
