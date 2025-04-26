<template>
  <AdminLayout>
    <div class="space-y-6">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <h1 class="text-2xl font-bold">مدیریت کاربران</h1>
        <div class="flex space-x-3">
          <button
            @click="openCreateUserModal"
            class="btn btn-primary"
          >
            کاربر جدید
          </button>
          <button
            @click="exportUsers"
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
              placeholder="نام کاربری یا ایمیل"
            >
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-1">وضعیت</label>
            <select v-model="filters.status" class="input-field">
              <option value="">همه</option>
              <option value="active">فعال</option>
              <option value="banned">مسدود شده</option>
              <option value="unverified">تایید نشده</option>
            </select>
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-1">تاریخ ثبت نام</label>
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
        </div>
        <div class="flex justify-end mt-4">
          <button
            @click="resetFilters"
            class="btn btn-secondary px-4"
          >
            بازنشانی فیلترها
          </button>
        </div>
      </div>

      <!-- Users Table -->
      <div class="bg-dark-light rounded-xl shadow overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-dark-lighter">
            <thead class="bg-dark">
              <tr>
                <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
                  کاربر
                </th>
                <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
                  وضعیت
                </th>
                <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
                  موجودی
                </th>
                <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
                  تاریخ ثبت نام
                </th>
                <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
                  آخرین فعالیت
                </th>
                <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
                  اقدامات
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-dark-lighter">
              <tr v-for="user in users" :key="user.id">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="flex-shrink-0 h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                      <span class="text-primary font-medium">{{ getUserInitials(user) }}</span>
                    </div>
                    <div class="mr-4">
                      <div class="text-sm font-medium">{{ user.name }}</div>
                      <div class="text-sm text-gray-400">{{ user.email }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span 
                    class="px-2 py-1 text-xs rounded-full"
                    :class="{
                      'bg-green-500/20 text-green-500': user.status === 'active',
                      'bg-red-500/20 text-red-500': user.status === 'banned',
                      'bg-yellow-500/20 text-yellow-500': user.status === 'unverified'
                    }"
                  >
                    {{ getUserStatus(user) }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  {{ formatCurrency(user.balance) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                  {{ formatDate(user.created_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                  {{ formatDate(user.last_active_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    @click="openEditUserModal(user)"
                    class="text-primary hover:text-primary-dark mr-3"
                  >
                    ویرایش
                  </button>
                  <button
                    v-if="user.status !== 'banned'"
                    @click="banUser(user.id)"
                    class="text-red-500 hover:text-red-700"
                  >
                    مسدود کردن
                  </button>
                  <button
                    v-else
                    @click="unbanUser(user.id)"
                    class="text-green-500 hover:text-green-700"
                  >
                    رفع مسدودیت
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div class="px-6 py-4 border-t border-dark-lighter flex items-center justify-between">
          <div class="text-sm text-gray-400">
            نمایش {{ pagination.from }} تا {{ pagination.to }} از {{ pagination.total }} کاربر
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

    <!-- Create/Edit User Modal -->
    <UserModal
      :is-open="isUserModalOpen"
      :user="selectedUser"
      @close="closeUserModal"
      @save="saveUser"
    />
  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import UserModal from '@/components/admin/UserModal.vue'
import { formatCurrency, formatDate, getUserInitials } from '@/utils/helpers'

// Data
const users = ref([])
const filters = ref({
  search: '',
  status: '',
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
const isUserModalOpen = ref(false)
const selectedUser = ref(null)
const isLoading = ref(false)

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
const fetchUsers = async () => {
  try {
    isLoading.value = true
    // In a real app, this would be an API call with filters and pagination
    // const response = await adminApi.getUsers({
    //   ...filters.value,
    //   page: pagination.value.currentPage
    // })
    
    // Mock data
    const mockUsers = Array.from({ length: 25 }, (_, i) => ({
      id: i + 1,
      name: `کاربر ${i + 1}`,
      email: `user${i + 1}@example.com`,
      status: ['active', 'banned', 'unverified'][Math.floor(Math.random() * 3)],
      balance: Math.floor(Math.random() * 1000000),
      created_at: new Date(Date.now() - Math.floor(Math.random() * 30 * 24 * 60 * 60 * 1000)).toISOString(),
      last_active_at: new Date(Date.now() - Math.floor(Math.random() * 7 * 24 * 60 * 60 * 1000)).toISOString()
    }))
    
    users.value = mockUsers.slice(
      (pagination.value.currentPage - 1) * pagination.value.perPage,
      pagination.value.currentPage * pagination.value.perPage
    )
    
    pagination.value = {
      currentPage: pagination.value.currentPage,
      perPage: pagination.value.perPage,
      total: mockUsers.length,
      lastPage: Math.ceil(mockUsers.length / pagination.value.perPage),
      from: (pagination.value.currentPage - 1) * pagination.value.perPage + 1,
      to: Math.min(pagination.value.currentPage * pagination.value.perPage, mockUsers.length)
    }
  } catch (error) {
    console.error('Failed to fetch users:', error)
  } finally {
    isLoading.value = false
  }
}

const getUserStatus = (user) => {
  const statusMap = {
    active: 'فعال',
    banned: 'مسدود شده',
    unverified: 'تایید نشده'
  }
  return statusMap[user.status] || user.status
}

const openCreateUserModal = () => {
  selectedUser.value = null
  isUserModalOpen.value = true
}

const openEditUserModal = (user) => {
  selectedUser.value = { ...user }
  isUserModalOpen.value = true
}

const closeUserModal = () => {
  isUserModalOpen.value = false
}

const saveUser = async (userData) => {
  try {
    if (userData.id) {
      // Update existing user
      const index = users.value.findIndex(u => u.id === userData.id)
      if (index !== -1) {
        users.value[index] = { ...users.value[index], ...userData }
      }
    } else {
      // Create new user
      const newUser = {
        id: Math.max(...users.value.map(u => u.id)) + 1,
        ...userData,
        status: 'active',
        created_at: new Date().toISOString(),
        last_active_at: new Date().toISOString()
      }
      users.value.unshift(newUser)
    }
    closeUserModal()
  } catch (error) {
    console.error('Failed to save user:', error)
  }
}

const banUser = async (userId) => {
  const user = users.value.find(u => u.id === userId)
  if (user) {
    user.status = 'banned'
  }
}

const unbanUser = async (userId) => {
  const user = users.value.find(u => u.id === userId)
  if (user) {
    user.status = 'active'
  }
}

const exportUsers = () => {
  // In a real app, this would generate an Excel file
  console.log('Exporting users to Excel')
}

const resetFilters = () => {
  filters.value = {
    search: '',
    status: '',
    dateFrom: '',
    dateTo: ''
  }
  fetchUsers()
}

const prevPage = () => {
  if (pagination.value.currentPage > 1) {
    pagination.value.currentPage--
    fetchUsers()
  }
}

const nextPage = () => {
  if (pagination.value.currentPage < pagination.value.lastPage) {
    pagination.value.currentPage++
    fetchUsers()
  }
}

const goToPage = (page) => {
  if (page !== pagination.value.currentPage) {
    pagination.value.currentPage = page
    fetchUsers()
  }
}

// Lifecycle
onMounted(() => {
  fetchUsers()
})
</script>
