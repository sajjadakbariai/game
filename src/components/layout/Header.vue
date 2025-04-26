<template>
  <header class="bg-dark-light border-b border-dark-lighter">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <div class="flex items-center">
          <RouterLink to="/dashboard" class="text-xl font-bold text-primary">
            GamePlatform
          </RouterLink>
        </div>
        
        <div class="flex items-center space-x-4">
          <WalletBalance />
          <UserDropdown />
          <NotificationBell />
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import WalletBalance from '@/components/wallet/Balance.vue'
import UserDropdown from '@/components/user/Dropdown.vue'
import NotificationBell from '@/components/notifications/Bell.vue'
</script>
