<template>
  <div>
    <div class="flex items-center justify-between mb-8">
      <h1 class="text-2xl font-bold">کیف پول</h1>
      <div class="flex space-x-3">
        <RouterLink
          to="/wallet/deposit"
          class="btn btn-primary"
        >
          واریز وجه
        </RouterLink>
        <RouterLink
          to="/wallet/withdraw"
          class="btn btn-secondary"
        >
          برداشت وجه
        </RouterLink>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="bg-dark-light rounded-lg p-6 shadow">
        <h3 class="text-gray-400 text-sm font-medium mb-2">موجودی فعلی</h3>
        <p class="text-3xl font-bold">
          {{ formatCurrency(walletStore.balance) }}
        </p>
      </div>
      
      <div class="bg-dark-light rounded-lg p-6 shadow">
        <h3 class="text-gray-400 text-sm font-medium mb-2">کل واریز‌ها</h3>
        <p class="text-3xl font-bold text-green-500">
          {{ formatCurrency(walletStats.totalDeposit) }}
        </p>
      </div>
      
      <div class="bg-dark-light rounded-lg p-6 shadow">
        <h3 class="text-gray-400 text-sm font-medium mb-2">کل برداشت‌ها</h3>
        <p class="text-3xl font-bold text-red-500">
          {{ formatCurrency(walletStats.totalWithdraw) }}
        </p>
      </div>
    </div>

    <div class="bg-dark-light rounded-lg shadow overflow-hidden">
      <div class="px-6 py-4 border-b border-dark-lighter">
        <h2 class="text-lg font-medium">تاریخچه تراکنش‌ها</h2>
      </div>
      
      <div class="divide-y divide-dark-lighter">
        <div v-if="walletStore.isLoading && walletStore.transactions.length === 0" class="p-6 text-center">
          <p class="text-gray-400">در حال دریافت اطلاعات...</p>
        </div>
        
        <div v-else-if="walletStore.transactions.length === 0" class="p-6 text-center">
          <p class="text-gray-400">تراکنشی یافت نشد</p>
        </div>
        
        <div v-else v-for="transaction in walletStore.transactions" :key="transaction.id" class="p-6">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4">
              <div
                class="p-3 rounded-full"
                :class="transaction.type === 'deposit' ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'"
              >
                <ArrowDownIcon v-if="transaction.type === 'deposit'" class="h-6 w-6" />
                <ArrowUpIcon v-else class="h-6 w-6" />
              </div>
              
              <div>
                <p class="font-medium">
                  {{ transaction.type === 'deposit' ? 'واریز' : 'برداشت' }}
                </p>
                <p class="text-sm text-gray-400">
                  {{ formatDate(transaction.created_at) }}
                </p>
              </div>
            </div>
            
            <div class="text-right">
              <p
                class="font-medium"
                :class="transaction.type === 'deposit' ? 'text-green-500' : 'text-red-500'"
              >
                {{ transaction.type === 'deposit' ? '+' : '-' }}
                {{ formatCurrency(transaction.amount) }}
              </p>
              <p class="text-sm text-gray-400">
                {{ transaction.status === 'completed' ? 'تکمیل شده' : 
                   transaction.status === 'pending' ? 'در حال بررسی' : 'ناموفق' }}
              </p>
            </div>
          </div>
        </div>
      </div>
      
      <div v-if="walletStore.transactions.length > 0" class="px-6 py-4 border-t border-dark-lighter flex justify-between">
        <button
          @click="loadPreviousPage"
          :disabled="currentPage === 1"
          class="btn btn-secondary px-4 py-2"
          :class="{ 'opacity-50 cursor-not-allowed': currentPage === 1 }"
        >
          قبلی
        </button>
        
        <div class="text-gray-400 text-sm">
          صفحه {{ currentPage }}
        </div>
        
        <button
          @click="loadNextPage"
          :disabled="walletStore.transactions.length < perPage"
          class="btn btn-secondary px-4 py-2"
          :class="{ 'opacity-50 cursor-not-allowed': walletStore.transactions.length < perPage }"
        >
          بعدی
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useWalletStore } from '@/stores/wallet.store'
import { ArrowDownIcon, ArrowUpIcon } from '@heroicons/vue/outline'
import { formatCurrency, formatDate } from '@/utils/helpers'

const walletStore = useWalletStore()

const currentPage = ref(1)
const perPage = 10

const walletStats = ref({
  totalDeposit: 0,
  totalWithdraw: 0
})

onMounted(async () => {
  await walletStore.fetchBalance()
  await loadTransactions()
  await fetchWalletStats()
})

const loadTransactions = async () => {
  await walletStore.fetchTransactions(currentPage.value)
}

const fetchWalletStats = async () => {
  // In a real app, this would be an API call
  walletStats.value = {
    totalDeposit: 1500000,
    totalWithdraw: 500000
  }
}

const loadNextPage = async () => {
  currentPage.value++
  await loadTransactions()
}

const loadPreviousPage = async () => {
  if (currentPage.value > 1) {
    currentPage.value--
    await loadTransactions()
  }
}
</script>
