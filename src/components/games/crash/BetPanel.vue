<template>
  <div class="space-y-4">
    <!-- Bet Controls -->
    <div v-if="gameState.status === 'waiting' || gameState.status === 'betting'">
      <div class="flex items-center justify-between mb-2">
        <label class="text-sm text-gray-400">مبلغ شرط (تومان)</label>
        <div class="flex space-x-2">
          <button
            v-for="amount in quickBetAmounts"
            :key="amount"
            @click="betAmount = amount"
            class="px-2 py-1 text-xs bg-dark rounded"
            :class="{ 'bg-primary text-white': betAmount === amount }"
          >
            {{ amount.toLocaleString() }}
          </button>
        </div>
      </div>
      
      <div class="relative">
        <input
          v-model.number="betAmount"
          type="number"
          min="1000"
          :max="maxBetAmount"
          class="input-field w-full pl-12"
        >
        <span class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">تومان</span>
      </div>
      
      <div class="grid grid-cols-2 gap-3 mt-4">
        <button
          @click="betAmount = Math.min(betAmount + 10000, maxBetAmount)"
          class="btn btn-secondary py-2"
        >
          +10,000
        </button>
        <button
          @click="betAmount = Math.min(betAmount + 100000, maxBetAmount)"
          class="btn btn-secondary py-2"
        >
          +100,000
        </button>
      </div>
      
      <div class="grid grid-cols-2 gap-3 mt-2">
        <button
          @click="betAmount = Math.max(betAmount - 10000, 1000)"
          class="btn btn-secondary py-2"
        >
          -10,000
        </button>
        <button
          @click="betAmount = Math.max(betAmount - 100000, 1000)"
          class="btn btn-secondary py-2"
        >
          -100,000
        </button>
      </div>
      
      <button
        @click="placeBet"
        class="btn btn-primary w-full mt-4 py-3"
        :disabled="!canPlaceBet || isPlacingBet"
      >
        <span v-if="isPlacingBet">
          <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </span>
        {{ gameState.status === 'waiting' ? 'شرط پیش‌بندی' : 'ثبت شرط' }}
      </button>
    </div>
    
    <!-- Game In Progress -->
    <div v-else-if="gameState.status === 'in-progress' && userBet">
      <div class="bg-dark rounded-lg p-4 mb-4">
        <div class="flex items-center justify-between mb-2">
          <span class="text-gray-400">شرط شما</span>
          <span class="font-medium">{{ formatCurrency(userBet.amount) }}</span>
        </div>
        <div class="flex items-center justify-between mb-2">
          <span class="text-gray-400">ضریب فعلی</span>
          <span class="font-medium text-primary">{{ gameState.currentMultiplier.toFixed(2) }}x</span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-gray-400">سود احتمالی</span>
          <span class="font-medium text-green-500">
            {{ formatCurrency(userBet.amount * gameState.currentMultiplier) }}
          </span>
        </div>
      </div>
      
      <button
        @click="cashOut"
        class="btn btn-primary w-full py-3"
      >
        خروج با {{ gameState.currentMultiplier.toFixed(2) }}x
      </button>
    </div>
    
    <!-- Cashed Out -->
    <div v-if="userBet?.cashedOut" class="bg-green-500/10 border border-green-500/30 rounded-lg p-4">
      <div class="flex items-center justify-between mb-2">
        <span class="text-gray-300">شرط شما</span>
        <span class="font-medium">{{ formatCurrency(userBet.amount) }}</span>
      </div>
      <div class="flex items-center justify-between mb-2">
        <span class="text-gray-300">ضریب خروج</span>
        <span class="font-medium text-green-500">{{ userBet.cashOutMultiplier.toFixed(2) }}x</span>
      </div>
      <div class="flex items-center justify-between">
        <span class="text-gray-300">سود شما</span>
        <span class="font-bold text-green-500">+{{ formatCurrency(userBet.winAmount) }}</span>
      </div>
    </div>
    
    <!-- Crashed -->
    <div v-if="gameState.status === 'crashed' && !userBet?.cashedOut && !userBet">
      <div class="text-center py-6">
        <p class="text-gray-400 mb-4">بازی در ضریب {{ gameState.crashedAt.toFixed(2) }}x متوقف شد</p>
        <button
          @click="prepareNextGame"
          class="btn btn-primary px-6"
        >
          بازی بعدی
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { formatCurrency } from '@/utils/helpers'

const props = defineProps({
  gameState: {
    type: Object,
    required: true
  },
  userBet: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['place-bet', 'cash-out'])

const quickBetAmounts = [1000, 5000, 10000, 50000, 100000]
const betAmount = ref(1000)
const isPlacingBet = ref(false)

const maxBetAmount = computed(() => {
  // In a real app, this would come from wallet balance or game limits
  return 1000000
})

const canPlaceBet = computed(() => {
  return betAmount.value >= 1000 && betAmount.value <= maxBetAmount.value
})

const placeBet = async () => {
  isPlacingBet.value = true
  try {
    await emit('place-bet', betAmount.value)
  } finally {
    isPlacingBet.value = false
  }
}

const cashOut = () => {
  emit('cash-out')
}

const prepareNextGame = () => {
  // Reset for next game
  betAmount.value = 1000
}
</script>
