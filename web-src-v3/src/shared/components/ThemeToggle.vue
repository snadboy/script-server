<script setup lang="ts">
import { useTheme } from '@shared/composables/useTheme'

const { currentTheme, toggleTheme } = useTheme()

const icons: Record<string, string> = {
  light: 'light_mode',
  dark: 'dark_mode',
  system: 'contrast',
}

const labels: Record<string, string> = {
  light: 'Light mode',
  dark: 'Dark mode',
  system: 'System theme',
}
</script>

<template>
  <button
    @click="toggleTheme"
    class="p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400"
    :title="labels[currentTheme]"
  >
    <span class="material-icons">{{ icons[currentTheme] }}</span>
  </button>
</template>
