<script setup lang="ts">
import AppLayout from '../components/AppLayout.vue'
</script>

<template>
  <AppLayout>
    <template #content>
      <div class="flex items-center justify-center h-full">
        <div class="text-center">
          <h1 class="text-3xl font-light text-gray-700 dark:text-gray-300 mb-4">
            Welcome to Script Server
          </h1>
          <p class="text-gray-500 dark:text-gray-400">
            Select a script from the sidebar to get started
          </p>
        </div>
      </div>
    </template>
  </AppLayout>
</template>
