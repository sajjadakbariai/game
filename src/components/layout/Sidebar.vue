<template>
  <aside class="w-64 bg-dark-light border-r border-dark-lighter flex-shrink-0">
    <div class="p-4">
      <nav class="space-y-2">
        <RouterLink 
          v-for="item in navItems" 
          :key="item.to" 
          :to="item.to"
          class="flex items-center px-4 py-2 rounded-lg transition-colors"
          active-class="bg-primary text-white"
          :class="[isActive(item.to) ? 'bg-primary text-white' : 'hover:bg-dark-lighter']"
        >
          <component :is="item.icon" class="w-5 h-5 mr-3" />
          {{ item.label }}
        </RouterLink>
      </nav>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { 
  HomeIcon,
  CurrencyDollarIcon,
  CubeIcon,
  SparklesIcon,
  UserGroupIcon,
  CogIcon
} from '@heroicons/vue/outline'

const route = useRoute()

const navItems = computed(() => [
  { to: '/dashboard', label: 'Dashboard', icon: HomeIcon },
  { to: '/wallet', label: 'Wallet', icon: CurrencyDollarIcon },
  { to: '/games', label: 'Games', icon: CubeIcon },
  ...(isAdmin.value ? [
    { to: '/admin', label: 'Admin', icon: CogIcon }
  ] : [])
])

const isActive = (path) => {
  return route.path.startsWith(path)
}

const isAdmin = computed(() => {
  const authStore = useAuthStore()
  return authStore.user?.is_admin
})
</script>
