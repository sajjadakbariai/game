<template>
  <AppModal
    :is-open="isOpen"
    :title="'جزئیات تراکنش #' + transaction.id"
    icon="CurrencyDollarIcon"
    @close="$emit('close')"
  >
    <div class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm text-gray-400 mb-1">کاربر</label>
          <p class="font-medium">{{ transaction.user.name }}</p>
          <p class="text-sm text-gray-400">{{ transaction.user.email }}</p>
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-1">نوع تراکنش</label>
          <p class="font-medium">{{ getTransactionType(transaction.type) }}</p>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm text-gray-400 mb-1">مبلغ</label>
          <p class="font-medium" :class="{
            'text-green-500': transaction.type === 'deposit' || transaction.type === 'bonus',
            'text-red-500': transaction.type === 'withdrawal' || transaction.type === 'game'
          }">
            {{ transaction.type === 'deposit' || transaction.type === 'bonus' ? '+' : '-' }}
            {{ formatCurrency(transaction.amount) }}
          </p>
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-1">وضعیت</label>
          <p>
            <span class="px-2 py-1 text-xs rounded-full" :class="{
              'bg-blue-500/20 text-blue-500': transaction.status === 'pending',
              'bg-green-500/20 text-green-500': transaction.status === 'completed',
              'bg-red-500/20 text-red-500': transaction.status === 'failed' || transaction.status === 'rejected',
              'bg-yellow-500/20 text-yellow-500': transaction.status === 'processing'
            }">
              {{ getTransactionStatus(transaction.status) }}
            </span>
          </p>
        </div>
      </div>

      <div>
        <label class="block text-sm text-gray-400 mb-1">تاریخ ایجاد</label>
        <p class="text-sm">{{ formatDateTime(transaction.created_at) }}</p>
      </div>

      <div v-if="transaction.description">
        <label class="block text-sm text-gray-400 mb-1">توضیحات</label>
        <p class="text-sm">{{ transaction.description }}</p>
      </div>

      <div v-if="transaction.payment_method">
        <label class="block text-sm text-gray-400 mb-1">روش پرداخت</label>
        <p class="text-sm">{{ transaction.payment_method }}</p>
      </div>

      <div v-if="transaction.tx_id">
        <label class="block text-sm text-gray-400 mb-1">شناسه تراکنش</label>
        <p class="text-sm">{{ transaction.tx_id }}</p>
      </div>

      <div v-if="transaction.game">
        <label class="block text-sm text-gray-400 mb-1">بازی مربوطه</label>
        <p class="text-sm">{{ transaction.game }}</p>
      </div>
    </div>

    <template v-if="transaction.status === 'pending' && transaction.type === 'withdrawal'" #footer>
      <button
        type="button"
        class="btn btn-primary"
        @click="$emit('approve', transaction.id)"
      >
        تایید برداشت
      </button>
      <button
        type="button"
        class="btn btn-secondary"
        @click="$emit('reject', transaction.id)"
      >
        رد درخواست
      </button>
    </template>
    <template v-else #footer>
      <button
        type="button"
        class="btn btn-primary"
        @click="$emit('close')"
      >
        بستن
      </button>
    </template>
  </AppModal>
</template>

<script setup>
import { formatCurrency, formatDateTime } from '@/utils/helpers'

const props = defineProps({
  isOpen: Boolean,
  transaction: Object
})

const emit = defineEmits(['close', 'approve', 'reject'])

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
</script>
