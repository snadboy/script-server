<script setup lang="ts">
import MainAppSidebar from './MainAppSidebar.vue'
</script>

<template>
  <div class="flex h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Sidebar -->
    <MainAppSidebar />

    <!-- Main content area -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Header slot -->
      <header v-if="$slots.header" class="bg-white dark:bg-gray-800 shadow-sm">
        <slot name="header" />
      </header>

      <!-- Content slot -->
      <main class="flex-1 overflow-auto bg-gray-50 dark:bg-gray-900">
        <slot name="content" />
      </main>
    </div>
  </div>
</template>
