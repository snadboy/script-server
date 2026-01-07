import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@shared/services/api'
import type { AuthInfo } from '@shared/types/api'

export const useAuthStore = defineStore('auth', () => {
  const info = ref<AuthInfo | null>(null)
  const initialized = ref(false)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => {
    if (!info.value) return false
    if (!info.value.enabled) return true // Auth disabled = everyone authenticated
    return !!info.value.username
  })

  const isAdmin = computed(() => info.value?.admin ?? false)
  const username = computed(() => info.value?.username ?? null)
  const canEditCode = computed(() => info.value?.canEditCode ?? false)

  async function init() {
    if (initialized.value) return

    loading.value = true
    error.value = null

    try {
      const response = await api.getAuthInfo()
      info.value = response
      initialized.value = true
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to load auth info'
      // If 401, user is not authenticated - this is expected
      if ((e as any)?.response?.status === 401) {
        info.value = { enabled: true, admin: false, canEditCode: false }
        initialized.value = true
        error.value = null
      }
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    try {
      await api.logout()
    } finally {
      // Always redirect to login page
      window.location.href = '/login.html'
    }
  }

  return {
    info,
    initialized,
    loading,
    error,
    isAuthenticated,
    isAdmin,
    username,
    canEditCode,
    init,
    logout,
  }
})
