<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@shared/stores/auth'
import { useTheme } from '@shared/composables/useTheme'

const authStore = useAuthStore()
const { initTheme } = useTheme()

onMounted(async () => {
  initTheme()
  await authStore.init()
})
</script>

<template>
  <router-view />
</template>
