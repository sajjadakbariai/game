import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/dashboard'
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/Login.vue'),
      meta: { guestOnly: true }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/auth/Register.vue'),
      meta: { guestOnly: true }
    },
    {
      path: '/forgot-password',
      name: 'forgot-password',
      component: () => import('@/views/auth/ForgotPassword.vue'),
      meta: { guestOnly: true }
    },
    {
      path: '/reset-password/:token',
      name: 'reset-password',
      component: () => import('@/views/auth/ResetPassword.vue'),
      meta: { guestOnly: true }
    },
    {
      path: '/dashboard',
      component: () => import('@/layouts/DashboardLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'dashboard',
          component: () => import('@/views/dashboard/Home.vue')
        },
        {
          path: 'wallet',
          name: 'wallet',
          component: () => import('@/views/wallet/Index.vue')
        },
        {
          path: 'wallet/deposit',
          name: 'wallet-deposit',
          component: () => import('@/views/wallet/Deposit.vue')
        },
        {
          path: 'wallet/withdraw',
          name: 'wallet-withdraw',
          component: () => import('@/views/wallet/Withdraw.vue')
        },
        {
          path: 'games',
          name: 'games',
          component: () => import('@/views/games/Index.vue')
        },
        {
          path: 'games/crash',
          name: 'crash-game',
          component: () => import('@/views/games/Crash.vue')
        },
        {
          path: 'games/hokm',
          name: 'hokm-game',
          component: () => import('@/views/games/Hokm.vue')
        },
        {
          path: 'games/poker',
          name: 'poker-game',
          component: () => import('@/views/games/Poker.vue')
        }
      ]
    },
    {
      path: '/admin',
      component: () => import('@/layouts/AdminLayout.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
      children: [
        {
          path: '',
          name: 'admin-dashboard',
          component: () => import('@/views/admin/Dashboard.vue')
        },
        {
          path: 'users',
          name: 'admin-users',
          component: () => import('@/views/admin/Users.vue')
        },
        {
          path: 'games',
          name: 'admin-games',
          component: () => import('@/views/admin/Games.vue')
        },
        {
          path: 'transactions',
          name: 'admin-transactions',
          component: () => import('@/views/admin/Transactions.vue')
        }
      ]
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/views/errors/NotFound.vue')
    }
  ]
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Initialize auth state if not already done
  if (!authStore.isInitialized) {
    await authStore.initialize()
  }

  // Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }

  // Check if route is for guests only
  if (to.meta.guestOnly && authStore.isAuthenticated) {
    return next({ name: 'dashboard' })
  }

  // Check admin routes
  if (to.meta.requiresAdmin && (!authStore.user || !authStore.user.is_admin)) {
    return next({ name: 'dashboard' })
  }

  next()
})

export default router
