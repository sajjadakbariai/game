<template>
  <AdminLayout>
    <div class="space-y-6">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <h1 class="text-2xl font-bold">مدیریت تراکنش‌ها</h1>
        <div class="flex space-x-3">
          <button
            @click="exportTransactions"
            class="btn btn-secondary"
          >
            خروجی Excel
          </button>
        </div>
      </div>

      <!-- Filters -->
      <div class="bg-dark-light rounded-xl p-4">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label class="block text-sm text-gray-400 mb-1">جستجو</label>
            <input
              v-model="filters.search"
              type="text"
              class="input-field"
              placeholder="شناسه یا کاربر"
            >
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-1">نوع تراکنش</label>
            <select v-model="filters.type" class="input-field">
              <option value="">همه</option>
              <option value="deposit">واریز</option>
              <option value="withdrawal">برداشت</option>
              <option value="game">بازی</option>
              <option value="bonus">پاداش</option>
            </select>
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-1">وضعیت</label>
            <select v-model="filters.status" class="input-field">
              <option value="">همه</option>
              <option value="pending">در انتظار</option>
              <option value="completed">تکمیل شده</option>
              <option value="failed">ناموفق</option>
              <option value="rejected">رد شده</option>
            </select>
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-1">مبلغ (تومان)</label>
            <input
              v-model="filters.amount"
              type="number"
              class="input-field"
              placeholder="مبلغ دقیق"
            >
          </div>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
          <div>
            <label class="block text-sm text-gray-400 mb-1">از تاریخ</label>
            <input
              v-model="filters.dateFrom"
              type="date"
              class="input-field"
            >
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-1">تا تاریخ</label>
            <input
              v-model="filters.dateTo"
              type="date"
              class="input-field"
            >
          </div>
          <div class="flex items-end">
            <button
              @click="applyFilters"
              class="btn btn-primary w-full"
            >
              اعمال فیلتر
            </button>
          </div>
          <div class="flex items-end">
            <button
              @click="resetFilters"
              class="btn btn-secondary w-full"
            >
              بازنشانی
            </button>
          </div>
        </div>
      </div>

      <!-- Transactions Table -->
      <div class="bg-dark-light rounded-xl shadow overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-dark-lighter">
            <thead class="bg-dark">
              <tr>
                <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
                  شناسه
                </th>
                <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
                  کاربر
                </th>
                <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
                  نوع
                </th>
                <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
                  مبلغ
                </th>
                <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
                  وضعیت
                </th>
                <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
                  تاریخ
                </th>
                <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
                  جزئیات
                </th>
                <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
                  اقدامات
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-dark-lighter">
              <tr v-for="transaction in transactions" :key="transaction.id">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-400">
                  #{{ transaction.id }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="flex-shrink-0 h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                      <span class="text-primary font-medium">{{ getUserInitials(transaction.user) }}</span>
                    </div>
                    <div class="mr-4">
                      <div class="text-sm font-medium">{{ transaction.user.name }}</div>
                      <div class="text-sm text-gray-400">{{ transaction.user.email }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  {{ getTransactionType(transaction.type) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium"
                  :class="{
                    'text-green-500': transaction.type === 'deposit' || transaction.type === 'bonus',
                    'text-red-500': transaction.type === 'withdrawal' || transaction.type === 'game'
                  }"
                >
                  {{ transaction.type === 'deposit' || transaction.type === 'bonus' ? '+' : '-' }}
                  {{ formatCurrency(transaction.amount) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span 
                    class="px-2 py-1 text-xs rounded-full"
                    :class="{
                      'bg-blue-500/20 text-blue-500': transaction.status === 'pending',
                      'bg-green-500/20 text-green-500': transaction.status === 'completed',
                      'bg-red-500/20 text-red-500': transaction.status === 'failed' || transaction.status === 'rejected',
                      'bg-yellow-500/20 text-yellow-500': transaction.status === 'processing'
                    }"
                  >
                    {{ getTransactionStatus(transaction.status) }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                  {{ formatDateTime(transaction.created_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                  <span v-if="transaction.game">بازی: {{ transaction.game }}</span>
                  <span v-else-if="transaction.payment_method">درگاه: {{ transaction.payment_method }}</span>
                  <span v-else>-</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    v-if="transaction.status === 'pending' && transaction.type === 'withdrawal'"
                    @click="approveTransaction(transaction.id)"
                    class="text-green-500 hover:text-green-700 mr-3"
                  >
                    تایید
                  </button>
                  <button
                    v-if="transaction.status === 'pending' && transaction.type === 'withdrawal'"
                    @click="rejectTransaction(transaction.id)"
                    class="text-red-500 hover:text-red-700"
                  >
                    رد
                  </button>
                  <button
                    v-else
                    @click="viewTransactionDetails(transaction)"
                    class="text-primary hover:text-primary-dark"
                  >
                    جزئیات
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div class="px-6 py-4 border-t border-dark-lighter flex items-center justify-between">
          <div class="text-sm text-gray-400">
            نمایش {{ pagination.from }} تا {{ pagination.to }} از {{ pagination.total }} تراکنش
          </div>
          <div class="flex space-x-2">
            <button
              @click="prevPage"
              :disabled="pagination.currentPage === 1"
              class="btn btn-secondary px-3 py-1"
              :class="{ 'opacity-50 cursor-not-allowed': pagination.currentPage === 1 }"
            >
              قبلی
            </button>
            <button
              v-for="page in visiblePages"
              :key="page"
              @click="goToPage(page)"
              class="btn px-3 py-1"
              :class="{
                'btn-primary': page === pagination.currentPage,
                'btn-secondary': page !== pagination.currentPage
              }"
            >
              {{ page }}
            </button>
            <button
              @click="nextPage"
              :disabled="pagination.currentPage === pagination.lastPage"
              class="btn btn-secondary px-3 py-1"
              :class="{ 'opacity-50 cursor-not-allowed': pagination.currentPage === pagination.lastPage }"
            >
              بعدی
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Transaction Details Modal -->
    <TransactionModal
      v-if="selectedTransaction"
      :is-open="isTransactionModalOpen"
      :transaction="selectedTransaction"
      @close="closeTransactionModal"
      @approve="approveTransaction"
      @reject="rejectTransaction"
    />
  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import TransactionModal from '@/components/admin/TransactionModal.vue'
import { formatCurrency, formatDateTime, getUserInitials } from '@/utils/helpers'

// Data
const transactions = ref([])
const filters = ref({
  search: '',
  type: '',
  status: '',
  amount: '',
  dateFrom: '',
  dateTo: ''
})
const pagination = ref({
  currentPage: 1,
  perPage: 10,
  total: 0,
  lastPage: 1,
  from: 0,
  to: 0
})
const isTransactionModalOpen = ref(false)
const selectedTransaction = ref(null)

// Computed
const visiblePages = computed(() => {
  const pages = []
  const maxVisible = 5
  let start = Math.max(1, pagination.value.currentPage - Math.floor(maxVisible / 2))
  let end = Math.min(pagination.value.lastPage, start + maxVisible - 1)
  
  if (end - start + 1 < maxVisible) {
    start = Math.max(1, end - maxVisible + 1)
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

// Methods
const fetchTransactions = async () => {
  try {
    // In a real app, this would be an API call with filters and pagination
    // const response = await adminApi.getTransactions({
    //   ...filters.value,
    //   page: pagination.value.currentPage
    // })
    
    // Mock data
    const mockTransactions = Array.from({ length: 50 }, (_, i) => {
      const types = ['deposit', 'withdrawal', 'game', 'bonus']
      const statuses = ['pending', 'completed', 'failed', 'rejected', 'processing']
      const games = ['انفجار', 'حکم', 'پوکر', null]
      const paymentMethods = ['زرین پال', 'آیدی پی', 'تراست', null]
      
      return {
        id: 1000 + i,
        user: {
          name: `کاربر ${Math.floor(Math.random() * 20) + 1}`,
          email: `user${Math.floor(Math.random() * 20) + 1}@example.com`
        },
        type: types[Math.floor(Math.random() * types.length)],
        amount: Math.floor(Math.random() * 1000000) + 10000,
        status: statuses[Math.floor(Math.random() * statuses.length)],
        created_at: new Date(Date.now() - Math.floor(Math.random() * 7 * 24 * 60 * 60 * 1000)).toISOString(),
        game: Math.random() > 0.5 ? games[Math.floor(Math.random() * games.length)] : null,
        payment_method: Math.random() > 0.5 ? paymentMethods[Math.floor(Math.random() * paymentMethods.length)] : null
      }
    })
    
    // Apply filters (mock)
    let filtered = mockTransactions
    if (filters.value.search) {
      const search = filters.value.search.toLowerCase()
      filtered = filtered.filter(t => 
        t.id.toString().includes(search) ||
        t.user.name.toLowerCase().includes(search) ||
        t.user.email.toLowerCase().includes(search)
      )
    }
    if (filters.value.type) {
      filtered = filtered.filter(t => t.type === filters.value.type)
    }
    if (filters.value.status) {
      filtered = filtered.filter(t => t.status === filters.value.status)
    }
    if (filters.value.amount) {
      filtered = filtered.filter(t => t.amount >= parseInt(filters.value.amount))
    }
    if (filters.value.dateFrom) {
      filtered = filtered.filter(t => new Date(t.created_at) >= new Date(filters.value.dateFrom))
    }
    if (filters.value.dateTo) {
      filtered = filtered.filter(t => new Date(t.created_at) <= new Date(filters.value.dateTo))
    }
    
    transactions.value = filtered.slice(
      (pagination.value.currentPage - 1) * pagination.value.perPage,
      pagination.value.currentPage * pagination.value.perPage
    )
    
    pagination.value = {
      currentPage: pagination.value.currentPage,
      perPage: pagination.value.perPage,
      total: filtered.length,
      lastPage: Math.ceil(filtered.length / pagination.value.perPage),
      from: (pagination.value.currentPage - 1) * pagination.value.perPage + 1,
      to: Math.min(pagination.value.currentPage * pagination.value.perPage, filtered.length)
    }
  } catch (error) {
    console.error('Failed to fetch transactions:', error)
  }
}

const getTransactionType = (type) => {
  const typeMap = {
    deposit: 'واریز',
    withdrawal: 'برداشت',
    game: 'بازی',
    bonus: 'پاداش'
  }
  return typeMap[type] || type
}

const getTransactionStatus = (status) => {
  const statusMap = {
    pending: 'در انتظار',
    completed: 'تکمیل شده',
    failed: 'ناموفق',
    rejected: 'رد شده',
    processing: 'در حال پردازش'
  }
  return statusMap[status] || status
}

const applyFilters = () => {
  pagination.value.currentPage = 1
  fetchTransactions()
}

const resetFilters = () => {
  filters.value = {
    search: '',
    type: '',
    status: '',
    amount: '',
    dateFrom: '',
    dateTo: ''
  }
  fetchTransactions()
}

const viewTransactionDetails = (transaction) => {
  selectedTransaction.value = transaction
  isTransactionModalOpen.value = true
}

const closeTransactionModal = () => {
  isTransactionModalOpen.value = false
  selectedTransaction.value = null
}

const approveTransaction = async (transactionId) => {
  try {
    // In a real app, this would be an API call
    // await adminApi.approveTransaction(transactionId)
    
    const transaction = transactions.value.find(t => t.id === transactionId)
    if (transaction) {
      transaction.status = 'completed'
    }
    
    closeTransactionModal()
  } catch (error) {
    console.error('Failed to approve transaction:', error)
  }
}

const rejectTransaction = async (transactionId) => {
  try {
    // In a real app, this would be an API call
    // await adminApi.rejectTransaction(transactionId)
    
    const transaction = transactions.value.find(t => t.id === transactionId)
    if (transaction) {
      transaction.status = 'rejected'
    }
    
    closeTransactionModal()
  } catch (error) {
    console.error('Failed to reject transaction:', error)
  }
}

const exportTransactions = () => {
  // In a real app, this would generate an Excel file
  console.log('Exporting transactions to Excel')
}

const prevPage = () => {
  if (pagination.value.currentPage > 1) {
    pagination.value.currentPage--
    fetchTransactions()
  }
}

const nextPage = () => {
  if (pagination.value.currentPage < pagination.value.lastPage) {
    pagination.value.currentPage++
    fetchTransactions()
  }
}

const goToPage = (page) => {
  if (page !== pagination.value.currentPage) {
    pagination.value.currentPage = page
    fetchTransactions()
  }
}

// Lifecycle
onMounted(() => {
  fetchTransactions()
})
</script>
