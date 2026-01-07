<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { useScriptsStore } from '../stores/scripts'
import { storeToRefs } from 'pinia'
import SearchPanel from './SearchPanel.vue'

const router = useRouter()
const route = useRoute()
const scriptsStore = useScriptsStore()

const { groupedScripts, sortedGroups, loading, searchQuery } = storeToRefs(scriptsStore)

function selectScript(name: string) {
  scriptsStore.selectScript(name)
  router.push({ name: 'script', params: { name } })
}

function isSelected(name: string): boolean {
  return route.params.name === name
}
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Search -->
    <SearchPanel
      :model-value="searchQuery"
      @update:model-value="scriptsStore.setSearchQuery"
    />

    <!-- Loading state -->
    <div v-if="loading" class="p-4 text-center text-gray-500">
      <span class="material-icons animate-spin">refresh</span>
      <p class="mt-2 text-sm">Loading scripts...</p>
    </div>

    <!-- Empty state -->
    <div
      v-else-if="sortedGroups.length === 0"
      class="p-4 text-center text-gray-500"
    >
      <span class="material-icons text-4xl mb-2">folder_off</span>
      <p class="text-sm">
        {{ searchQuery ? 'No scripts match your search' : 'No scripts available' }}
      </p>
    </div>

    <!-- Script groups -->
    <div v-else class="flex-1 overflow-auto py-2">
      <div v-for="group in sortedGroups" :key="group" class="mb-2">
        <!-- Group header -->
        <div
          v-if="sortedGroups.length > 1 || group !== 'Ungrouped'"
          class="px-4 py-1 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider"
        >
          {{ group }}
        </div>

        <!-- Scripts in group -->
        <button
          v-for="script in groupedScripts[group]"
          :key="script.name"
          @click="selectScript(script.name)"
          class="w-full px-4 py-2 text-left flex items-center gap-2 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          :class="{
            'bg-primary/10 text-primary border-r-2 border-primary': isSelected(script.name),
            'text-gray-700 dark:text-gray-300': !isSelected(script.name),
          }"
        >
          <span class="material-icons text-lg">
            {{ script.parsing_failed ? 'error' : 'description' }}
          </span>
          <span class="truncate">{{ script.name }}</span>
          <span
            v-if="script.parsing_failed"
            class="ml-auto text-xs text-red-500"
            title="Configuration error"
          >
            Error
          </span>
        </button>
      </div>
    </div>
  </div>
</template>
