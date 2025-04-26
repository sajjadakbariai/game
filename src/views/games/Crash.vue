<template>
  <GameLayout title="بازی انفجار">
    <div class="flex flex-col lg:flex-row gap-6">
      <!-- Game Area -->
      <div class="flex-1">
        <div class="bg-dark-light rounded-xl p-6">
          <!-- Game Canvas -->
          <div class="relative h-64 bg-dark rounded-lg mb-6 overflow-hidden">
            <div ref="canvas" class="h-full w-full relative">
              <!-- Multiplier Line -->
              <div class="absolute top-0 left-0 right-0 h-px bg-gray-600"></div>
              
              <!-- Multiplier Indicator -->
              <div 
                v-if="gameState.currentMultiplier > 1"
                class="absolute left-1/2 transform -translate-x-1/2 bg-primary text-white px-3 py-1 rounded-full text-sm font-bold"
                :style="{ bottom: `${(gameState.currentMultiplier / 10) * 100}%` }"
              >
                {{ gameState.currentMultiplier.toFixed(2) }}x
              </div>
              
              <!-- Crashed Indicator -->
              <div 
                v-if="gameState.crashedAt"
                class="absolute left-0 right-0 bg-red-500/20 border-t-2 border-red-500"
                :style="{ bottom: `${(gameState.crashedAt / 10) * 100}%` }"
              >
                <div class="absolute left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-bold">
                  {{ gameState.crashedAt.toFixed(2) }}x
                </div>
              </div>
              
              <!-- History Graph -->
              <svg class="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
                <polyline 
                  v-if="historyPath"
                  :points="historyPath"
                  fill="none"
                  stroke="#6366f1"
                  stroke-width="0.5"
                />
              </svg>
            </div>
          </div>
          
          <!-- Betting Panel -->
          <CrashBetPanel
            :game-state="gameState"
            :user-bet="userBet"
            @place-bet="placeBet"
            @cash-out="cashOut"
          />
        </div>
        
        <!-- Game History -->
        <div class="mt-6 bg-dark-light rounded-xl p-6">
          <h3 class="text-lg font-medium mb-4">تاریخچه بازی‌ها</h3>
          <div class="flex space-x-2 overflow-x-auto pb-2">
            <div 
              v-for="(game, index) in gameHistory"
              :key="index"
              class="flex-shrink-0 w-12 h-12 rounded-lg flex items-center justify-center"
              :class="game.crashedAt < 2 ? 'bg-red-500/20 text-red-500' : game.crashedAt < 5 ? 'bg-orange-500/20 text-orange-500' : 'bg-green-500/20 text-green-500'"
            >
              <span class="text-sm font-bold">{{ game.crashedAt.toFixed(1) }}x</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Sidebar -->
      <div class="lg:w-80 space-y-6">
        <!-- Player Bets -->
        <div class="bg-dark-light rounded-xl p-6">
          <h3 class="text-lg font-medium mb-4">شرط‌های بازیکنان</h3>
          <div class="space-y-3">
            <div 
              v-for="bet in activeBets"
              :key="bet.id"
              class="flex items-center justify-between p-3 bg-dark rounded-lg"
            >
              <div class="flex items-center space-x-3">
                <div class="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary text-xs font-bold">
                  {{ bet.user.initials }}
                </div>
                <span class="text-sm">{{ bet.user.username }}</span>
              </div>
              <span class="text-sm font-medium">{{ formatCurrency(bet.amount) }}</span>
            </div>
            
            <div v-if="activeBets.length === 0" class="text-center py-4 text-gray-400 text-sm">
              هیچ شرط فعالی وجود ندارد
            </div>
          </div>
        </div>
        
        <!-- Game Chat -->
        <GameChat :messages="chatMessages" @send-message="sendChatMessage" />
      </div>
    </div>
  </GameLayout>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useGameStore } from '@/stores/game.store'
import { useWalletStore } from '@/stores/wallet.store'
import { formatCurrency } from '@/utils/helpers'
import GameLayout from '@/layouts/GameLayout.vue'
import CrashBetPanel from '@/components/games/crash/BetPanel.vue'
import GameChat from '@/components/games/Chat.vue'

const gameStore = useGameStore()
const walletStore = useWalletStore()

const gameState = ref({
  status: 'waiting', // waiting, betting, in-progress, crashed
  countdown: 0,
  currentMultiplier: 1,
  crashedAt: null,
  players: []
})

const userBet = ref(null)
const gameHistory = ref([])
const activeBets = ref([])
const chatMessages = ref([])
const canvas = ref(null)

// Generate history path for SVG
const historyPath = computed(() => {
  if (gameHistory.value.length === 0) return null
  
  const points = []
  const maxGames = 10
  const startIndex = Math.max(0, gameHistory.value.length - maxGames)
  
  for (let i = startIndex; i < gameHistory.value.length; i++) {
    const x = ((i - startIndex) / (maxGames - 1)) * 100
    const y = 100 - (gameHistory.value[i].crashedAt / 10) * 100
    points.push(`${x},${y}`)
  }
  
  return points.join(' ')
})

// Connect to WebSocket when component mounts
onMounted(() => {
  connectToWebSocket()
  fetchGameHistory()
})

// Clean up WebSocket when component unmounts
onUnmounted(() => {
  disconnectWebSocket()
})

const connectToWebSocket = () => {
  gameStore.connectToCrashGame({
    onGameUpdate: (data) => {
      gameState.value = data.gameState
      activeBets.value = data.activeBets
      
      // Update user bet if exists
      if (data.userBet) {
        userBet.value = data.userBet
      }
      
      // If game crashed and user didn't cash out
      if (data.gameState.status === 'crashed' && userBet.value && !userBet.value.cashedOut) {
        userBet.value = null
      }
    },
    onChatMessage: (message) => {
      chatMessages.value.push(message)
    }
  })
}

const disconnectWebSocket = () => {
  gameStore.disconnectFromCrashGame()
}

const fetchGameHistory = async () => {
  try {
    const response = await gameStore.getCrashHistory()
    gameHistory.value = response.data
  } catch (error) {
    console.error('Failed to fetch game history:', error)
  }
}

const placeBet = async (amount) => {
  try {
    if (walletStore.balance < amount) {
      throw new Error('موجودی کیف پول شما کافی نیست')
    }
    
    if (gameState.value.status !== 'betting') {
      throw new Error('زمان شرط بندی به پایان رسیده است')
    }
    
    const bet = await gameStore.placeCrashBet(amount)
    userBet.value = bet
  } catch (error) {
    console.error('Failed to place bet:', error)
    // Show error to user
  }
}

const cashOut = async () => {
  try {
    if (!userBet.value || userBet.value.cashedOut) {
      return
    }
    
    const result = await gameStore.cashOutCrash(userBet.value.gameId)
    userBet.value.cashedOut = true
    userBet.value.cashOutMultiplier = result.cashOutMultiplier
    userBet.value.winAmount = result.winAmount
    
    // Update wallet balance
    walletStore.fetchBalance()
  } catch (error) {
    console.error('Failed to cash out:', error)
    // Show error to user
  }
}

const sendChatMessage = (message) => {
  gameStore.sendCrashChatMessage(message)
}
</script>
