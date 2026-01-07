<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@shared/stores/auth'
import { useScriptsStore } from '../stores/scripts'
import ScriptsList from './ScriptsList.vue'
import ThemeToggle from '@shared/components/ThemeToggle.vue'

const router = useRouter()
const authStore = useAuthStore()
const scriptsStore = useScriptsStore()

const username = computed(() => authStore.username)
const isAdmin = computed(() => authStore.isAdmin)

onMounted(() => {
  scriptsStore.loadScripts()
})

function handleLogout() {
  authStore.logout()
}

function goToAdmin() {
  window.location.href = '/admin.html'
}

function goToHistory() {
  router.push('/history')
}
</script>

<template>
  <aside class="w-72 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
    <!-- Logo / Title -->
    <div class="h-16 flex items-center px-4 border-b border-gray-200 dark:border-gray-700">
      <h1 class="text-xl font-medium text-primary">
        Script Server
      </h1>
    </div>

    <!-- Script List -->
    <div class="flex-1 overflow-auto">
      <ScriptsList />
    </div>

    <!-- Bottom Actions -->
    <div class="border-t border-gray-200 dark:border-gray-700 p-4 space-y-2">
      <!-- User info -->
      <div v-if="username" class="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400 mb-3">
        <span class="flex items-center gap-2">
          <span class="material-icons text-lg">person</span>
          {{ username }}
        </span>
        <span v-if="isAdmin" class="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded">
          Admin
        </span>
      </div>

      <!-- Action buttons -->
      <div class="flex items-center gap-2">
        <button
          @click="goToHistory"
          class="flex-1 btn btn-secondary text-sm flex items-center justify-center gap-1"
          title="Execution History"
        >
          <span class="material-icons text-lg">history</span>
          History
        </button>

        <ThemeToggle />

        <button
          v-if="isAdmin"
          @click="goToAdmin"
          class="p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400"
          title="Admin Panel"
        >
          <span class="material-icons">settings</span>
        </button>

        <button
          @click="handleLogout"
          class="p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400"
          title="Logout"
        >
          <span class="material-icons">logout</span>
        </button>
      </div>
    </div>
  </aside>
</template>
