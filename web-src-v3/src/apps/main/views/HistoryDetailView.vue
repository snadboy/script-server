<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '../components/AppLayout.vue'

const route = useRoute()
const executionId = computed(() => route.params.id as string)
</script>

<template>
  <AppLayout>
    <template #header>
      <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <h1 class="text-xl font-medium text-gray-800 dark:text-gray-200">
          Execution #{{ executionId }}
        </h1>
      </div>
    </template>
    <template #content>
      <div class="p-6">
        <p class="text-gray-500">Execution detail view - TODO (post-MVP)</p>
      </div>
    </template>
  </AppLayout>
</template>
