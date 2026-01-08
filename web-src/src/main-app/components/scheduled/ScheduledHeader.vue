<template>
  <div class="scheduled-header primary-color-dark">
    <h5 class="header">Scheduled Executions</h5>
  </div>
</template>

<script>
export default {
  name: 'ScheduledHeader'
}
</script>

<style scoped>
.scheduled-header {
  padding: 0 1rem;
  display: flex;
  align-items: center;
}

.scheduled-header .header {
  color: var(--font-on-primary-color-dark-main);
  margin: 0;
}
</style>
