import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api/wallet'

export const useWalletStore = defineStore('wallet', () => {
  const balance = ref(0)
  const transactions = ref([])
  const isLoading = ref(false)
  const error = ref(null)

  async function fetchBalance() {
    try {
      isLoading.value = true
      const response = await api.getBalance()
      balance.value = response.data.balance
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to fetch balance'
    } finally {
      isLoading.value = false
    }
  }

  async function deposit(amount) {
    try {
      isLoading.value = true
      const response = await api.deposit(amount)
      balance.value += amount
      return response.data.payment_url
    } catch (err) {
      error.value = err.response?.data?.message || 'Deposit failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function withdraw(amount, address) {
    try {
      isLoading.value = true
      const response = await api.withdraw({ amount, address })
      balance.value -= amount
      return response.data
    } catch (err) {
      error.value = err.response?.data?.message || 'Withdrawal failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchTransactions(page = 1) {
    try {
      isLoading.value = true
      const response = await api.getTransactions(page)
      transactions.value = response.data
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to fetch transactions'
    } finally {
      isLoading.value = false
    }
  }

  return {
    balance,
    transactions,
    isLoading,
    error,
    fetchBalance,
    deposit,
    withdraw,
    fetchTransactions
  }
})
