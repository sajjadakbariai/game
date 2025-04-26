<template>
  <div class="min-h-screen flex flex-col">
    <AppHeader />
    
    <div class="flex flex-1">
      <AppSidebar />
      
      <main class="flex-1 p-6 overflow-auto">
        <div class="max-w-7xl mx-auto">
          <RouterView />
        </div>
      </main>
    </div>
    
    <AppFooter />
  </div>
</template>

<script setup>
import AppHeader from '@/components/layout/Header.vue'
import AppSidebar from '@/components/layout/Sidebar.vue'
import AppFooter from '@/components/layout/Footer.vue'
</script>
