<script setup lang="ts">
import { onMounted } from 'vue'
import { useTheme } from '@shared/composables/useTheme'

const { initTheme } = useTheme()

onMounted(() => {
  initTheme()
})

function goBack() {
  window.location.href = '/'
}
</script>

<template>
  <div class="min-h-screen bg-gray-100 dark:bg-gray-900">
    <!-- Header -->
    <header class="bg-white dark:bg-gray-800 shadow-sm">
      <div class="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <h1 class="text-xl font-medium text-gray-800 dark:text-gray-200">
          Admin Panel
        </h1>
        <button
          @click="goBack"
          class="btn btn-secondary text-sm flex items-center gap-1"
        >
          <span class="material-icons text-lg">arrow_back</span>
          Back to App
        </button>
      </div>
    </header>

    <!-- Content -->
    <main class="max-w-7xl mx-auto px-4 py-8">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-8 text-center">
        <span class="material-icons text-6xl text-gray-300 dark:text-gray-600 mb-4">
          construction
        </span>
        <h2 class="text-xl font-medium text-gray-700 dark:text-gray-300 mb-2">
          Admin Panel Coming Soon
        </h2>
        <p class="text-gray-500 dark:text-gray-400">
          This feature is part of the post-MVP development phase.
        </p>
      </div>
    </main>
  </div>
</template>
