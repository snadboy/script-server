<template>
  <div class="activity-header">
    <h5 class="header-title">Activity</h5>
  </div>
</template>

<script>
export default {
  name: 'ActivityHeader'
};
</script>

<style scoped>
.activity-header {
  display: flex;
  align-items: center;
  padding: 0 16px;
  height: 100%;
}

.header-title {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
  color: var(--font-color-main);
}
</style>
