import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/auth'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))
  const isAuthenticated = computed(() => !!token.value)

  async function login(credentials) {
    try {
      const response = await api.login(credentials)
      user.value = response.user
      token.value = response.token
      localStorage.setItem('token', response.token)
      router.push('/dashboard')
    } catch (error) {
      throw error
    }
  }

  async function register(userData) {
    try {
      const response = await api.register(userData)
      user.value = response.user
      token.value = response.token
      localStorage.setItem('token', response.token)
      router.push('/dashboard')
    } catch (error) {
      throw error
    }
  }

  async function logout() {
    try {
      await api.logout()
      user.value = null
      token.value = null
      localStorage.removeItem('token')
      router.push('/login')
    } catch (error) {
      throw error
    }
  }

  async function fetchUser() {
    try {
      if (token.value) {
        const response = await api.getUser()
        user.value = response.data
      }
    } catch (error) {
      logout()
    }
  }

  function initialize() {
    if (token.value) {
      fetchUser()
    }
  }

  return {
    user,
    token,
    isAuthenticated,
    login,
    register,
    logout,
    fetchUser,
    initialize
  }
})
