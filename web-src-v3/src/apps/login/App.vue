<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useTheme } from '@shared/composables/useTheme'

const { initTheme } = useTheme()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref<string | null>(null)

// Get redirect URL from query params
function getRedirectUrl(): string {
  const params = new URLSearchParams(window.location.search)
  return params.get('next') || '/'
}

async function handleSubmit() {
  if (!username.value || !password.value) {
    error.value = 'Please enter username and password'
    return
  }

  loading.value = true
  error.value = null

  try {
    const formData = new FormData()
    formData.append('username', username.value)
    formData.append('password', password.value)

    await axios.post('/login', formData, {
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
      },
    })

    // Redirect to main app or specified URL
    window.location.href = getRedirectUrl()
  } catch (e: any) {
    if (e.response?.status === 401) {
      error.value = 'Invalid username or password'
    } else if (e.response?.status === 403) {
      error.value = 'Access denied. Please contact administrator.'
    } else {
      error.value = 'Login failed. Please try again.'
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  initTheme()
})
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-gray-900 p-4">
    <div class="w-full max-w-md">
      <!-- Card -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
        <!-- Logo / Title -->
        <div class="text-center mb-8">
          <h1 class="text-3xl font-light text-primary mb-2">Script Server</h1>
          <p class="text-gray-500 dark:text-gray-400">Sign in to continue</p>
        </div>

        <!-- Error message -->
        <div
          v-if="error"
          class="mb-6 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-600 dark:text-red-400 text-sm"
        >
          {{ error }}
        </div>

        <!-- Login form -->
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <!-- Username -->
          <div>
            <label
              for="username"
              class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
            >
              Username
            </label>
            <input
              id="username"
              v-model="username"
              type="text"
              autocomplete="username"
              required
              :disabled="loading"
              class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-colors disabled:opacity-50"
              placeholder="Enter your username"
            />
          </div>

          <!-- Password -->
          <div>
            <label
              for="password"
              class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
            >
              Password
            </label>
            <input
              id="password"
              v-model="password"
              type="password"
              autocomplete="current-password"
              required
              :disabled="loading"
              class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-colors disabled:opacity-50"
              placeholder="Enter your password"
            />
          </div>

          <!-- Submit button -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full py-3 bg-primary hover:bg-primary-dark text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            <span v-if="loading" class="material-icons animate-spin text-lg">refresh</span>
            {{ loading ? 'Signing in...' : 'Sign In' }}
          </button>
        </form>
      </div>

      <!-- Footer -->
      <p class="mt-6 text-center text-sm text-gray-500 dark:text-gray-400">
        Script Server v2.0
      </p>
    </div>
  </div>
</template>
