<template>
  <transition name="fade" appear>
    <div class="page-progress">
      <div class="progress-content">
        <div class="spinner-container">
          <div class="spinner"></div>
        </div>
        <p v-if="message" class="progress-message">{{ message }}</p>
        <p v-else class="progress-message">Loading...</p>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'PageProgress',
  props: {
    message: {
      type: String,
      default: ''
    }
  }
}
</script>

<style scoped>
.page-progress {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 16px;
  min-height: 200px;
}

.progress-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.spinner-container {
  margin-bottom: 16px;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--separator-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.progress-message {
  color: var(--font-color-medium);
  font-size: 14px;
  margin: 0;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

/* Fade transition */
.fade-enter-active {
  transition: opacity var(--transition-normal);
}

.fade-enter {
  opacity: 0;
}
</style>
