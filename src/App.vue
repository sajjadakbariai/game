<template>
  <RouterView />
</template>

<script setup>
import { RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'
import { onMounted } from 'vue'

const authStore = useAuthStore()

onMounted(() => {
  // Initialize auth state when app mounts
  authStore.initialize()
})
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

body {
  @apply bg-dark text-gray-100 font-sans;
}
</style>
