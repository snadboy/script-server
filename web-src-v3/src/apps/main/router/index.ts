import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@shared/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/script/:name',
      name: 'script',
      component: () => import('../views/ScriptView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/history',
      name: 'history',
      component: () => import('../views/HistoryView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/history/:id',
      name: 'history-detail',
      component: () => import('../views/HistoryDetailView.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

router.beforeEach(async (to) => {
  if (to.meta.requiresAuth) {
    const authStore = useAuthStore()

    // Wait for auth to initialize if needed
    if (!authStore.initialized) {
      await authStore.init()
    }

    if (!authStore.isAuthenticated) {
      // Redirect to login with return URL
      const returnUrl = encodeURIComponent(to.fullPath)
      window.location.href = `/login.html?next=${returnUrl}`
      return false
    }
  }
})

export default router
