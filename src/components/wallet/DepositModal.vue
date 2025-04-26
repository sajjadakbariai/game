<template>
  <AppModal
    :is-open="isOpen"
    title="واریز وجه به حساب"
    icon="CurrencyDollarIcon"
    @close="closeModal"
  >
    <div class="space-y-4">
      <div>
        <label for="amount" class="block text-sm font-medium text-gray-300 mb-1">مبلغ (تومان)</label>
        <input
          id="amount"
          v-model="amount"
          type="number"
          class="input-field"
          placeholder="مبلغ مورد نظر را وارد کنید"
        />
        <p v-if="error" class="mt-1 text-sm text-red-500">{{ error }}</p>
      </div>
      
      <div v-if="paymentMethods.length > 0">
        <label class="block text-sm font-medium text-gray-300 mb-2">روش پرداخت</label>
        <div class="grid grid-cols-3 gap-3">
          <button
            v-for="method in paymentMethods"
            :key="method.id"
            @click="selectedMethod = method.id"
            class="p-3 border rounded-lg flex flex-col items-center"
            :class="selectedMethod === method.id ? 'border-primary bg-primary/10' : 'border-dark-lighter hover:border-gray-500'"
          >
            <img :src="method.icon" :alt="method.name" class="h-8 w-8 mb-2" />
            <span class="text-xs">{{ method.name }}</span>
          </button>
        </div>
      </div>
    </div>
    
    <template #footer>
      <button
        type="button"
        class="btn btn-primary"
        :disabled="!amount || !selectedMethod || isLoading"
        @click="handleDeposit"
      >
        <span v-if="isLoading">
          <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </span>
        پرداخت
      </button>
      <button type="button" class="btn btn-secondary" @click="closeModal">
        انصراف
      </button>
    </template>
  </AppModal>
</template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue'
import { useWalletStore } from '@/stores/wallet.store'

const props = defineProps({
  isOpen: Boolean
})

const emit = defineEmits(['close'])

const walletStore = useWalletStore()

const amount = ref('')
const selectedMethod = ref(null)
const isLoading = ref(false)
const error = ref(null)

const paymentMethods = ref([
  {
    id: 1,
    name: 'درگاه بانکی',
    icon: '/images/bank-icon.png'
  },
  {
    id: 2,
    name: 'رمز ارز',
    icon: '/images/crypto-icon.png'
  },
  {
    id: 3,
    name: 'کیف پول دیجیتال',
    icon: '/images/digital-wallet-icon.png'
  }
])

const closeModal = () => {
  amount.value = ''
  selectedMethod.value = null
  error.value = null
  emit('close')
}

const handleDeposit = async () => {
  if (!amount.value || amount.value < 10000) {
    error.value = 'حداقل مبلغ واریز 10,000 تومان می‌باشد'
    return
  }

  try {
    isLoading.value = true
    const paymentUrl = await walletStore.deposit(parseInt(amount.value))
    
    // Redirect to payment gateway
    window.location.href = paymentUrl
  } catch (err) {
    error.value = err.message || 'خطا در انجام عملیات واریز'
  } finally {
    isLoading.value = false
  }
}
</script>
