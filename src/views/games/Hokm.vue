<template>
  <GameLayout title="بازی حکم">
    <div class="flex flex-col lg:flex-row gap-6">
      <!-- Game Area -->
      <div class="flex-1">
        <div class="bg-dark-light rounded-xl p-6">
          <!-- Game Table -->
          <div class="relative h-96 bg-green-800 rounded-lg mb-6 overflow-hidden border-4 border-green-700">
            <!-- Players -->
            <div class="absolute top-4 left-1/2 transform -translate-x-1/2 text-center">
              <div class="bg-dark/80 rounded-lg px-4 py-2 inline-block">
                <p class="font-medium">{{ opponents[0]?.name || 'حریف' }}</p>
                <p class="text-sm text-gray-400">{{ opponents[0]?.score || 0 }} امتیاز</p>
              </div>
            </div>
            
            <div class="absolute right-4 top-1/2 transform -translate-y-1/2 text-center">
              <div class="bg-dark/80 rounded-lg px-4 py-2 inline-block">
                <p class="font-medium">{{ opponents[1]?.name || 'حریف' }}</p>
                <p class="text-sm text-gray-400">{{ opponents[1]?.score || 0 }} امتیاز</p>
              </div>
            </div>
            
            <div class="absolute bottom-4 left-1/2 transform -translate-x-1/2 text-center">
              <div class="bg-dark/80 rounded-lg px-4 py-2 inline-block">
                <p class="font-medium">{{ opponents[2]?.name || 'حریف' }}</p>
                <p class="text-sm text-gray-400">{{ opponents[2]?.score || 0 }} امتیاز</p>
              </div>
            </div>
            
            <!-- Played Cards -->
            <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 flex space-x-2">
              <div 
                v-for="(card, index) in playedCards"
                :key="index"
                class="w-16 h-24 bg-white rounded-md shadow-lg transform"
                :class="{
                  'rotate-2': index === 0,
                  '-rotate-2': index === 1,
                  'rotate-6': index === 2,
                  '-rotate-6': index === 3
                }"
              >
                <img 
                  :src="`/images/cards/${card.suit}_${card.rank}.png`" 
                  :alt="`${card.rank} of ${card.suit}`"
                  class="w-full h-full object-cover"
                >
              </div>
            </div>
            
            <!-- Trump Card -->
            <div 
              v-if="trumpCard"
              class="absolute top-4 right-4 w-12 h-16 bg-white rounded-md shadow-lg"
            >
              <img 
                :src="`/images/cards/${trumpCard.suit}_${trumpCard.rank}.png`" 
                :alt="`${trumpCard.rank} of ${trumpCard.suit}`"
                class="w-full h-full object-cover"
              >
            </div>
          </div>
          
          <!-- Player Controls -->
          <div class="mt-6">
            <div v-if="gameState.status === 'waiting'">
              <button
                @click="startNewGame"
                class="btn btn-primary w-full py-3"
              >
                شروع بازی جدید
              </button>
            </div>
            
            <div v-else-if="gameState.status === 'bidding' && isPlayerTurn">
              <h3 class="text-lg font-medium mb-4">نوبت پیشنهاد حکم</h3>
              <div class="grid grid-cols-4 gap-3">
                <button
                  v-for="suit in suits"
                  :key="suit"
                  @click="placeBid(suit)"
                  class="btn btn-secondary py-3"
                >
                  {{ suitNames[suit] }}
                </button>
              </div>
            </div>
            
            <div v-else-if="gameState.status === 'playing' && isPlayerTurn">
              <h3 class="text-lg font-medium mb-4">نوبت شما برای بازی</h3>
              <div class="flex flex-wrap gap-2 justify-center">
                <div
                  v-for="card in playerCards"
                  :key="`${card.suit}_${card.rank}`"
                  @click="playCard(card)"
                  class="w-16 h-24 bg-white rounded-md shadow-lg cursor-pointer transform hover:-translate-y-2 transition-transform"
                >
                  <img 
                    :src="`/images/cards/${card.suit}_${card.rank}.png`" 
                    :alt="`${card.rank} of ${card.suit}`"
                    class="w-full h-full object-cover"
                  >
                </div>
              </div>
            </div>
            
            <div v-else>
              <p class="text-center py-4 text-gray-400">
                {{ statusMessages[gameState.status] }}
              </p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Sidebar -->
      <div class="lg:w-80 space-y-6">
        <!-- Game Info -->
        <div class="bg-dark-light rounded-xl p-6">
          <h3 class="text-lg font-medium mb-4">اطلاعات بازی</h3>
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-gray-400">حکم فعلی</span>
              <span class="font-medium" :class="`text-${suitColors[gameState.trumpSuit]}-500`">
                {{ gameState.trumpSuit ? suitNames[gameState.trumpSuit] : 'تعیین نشده' }}
              </span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-gray-400">تیم حکم</span>
              <span class="font-medium">{{ gameState.bidderTeam || '-' }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-gray-400">دسته‌های برداشته</span>
              <span class="font-medium">{{ gameState.tricksTaken }}/7</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-gray-400">امتیاز تیم شما</span>
              <span class="font-medium text-primary">{{ playerScore }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-gray-400">امتیاز حریفان</span>
              <span class="font-medium text-secondary">{{ opponentScore }}</span>
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
import GameLayout from '@/layouts/GameLayout.vue'
import GameChat from '@/components/games/Chat.vue'

const gameStore = useGameStore()

// Game state
const gameState = ref({
  status: 'waiting', // waiting, bidding, playing, finished
  trumpSuit: null,
  bidderTeam: null,
  currentPlayer: null,
  tricksTaken: 0,
  scores: {
    team1: 0,
    team2: 0
  }
})

const playerCards = ref([])
const playedCards = ref([])
const trumpCard = ref(null)
const opponents = ref([
  { id: 1, name: 'حریف ۱', score: 0 },
  { id: 2, name: 'حریف ۲', score: 0 },
  { id: 3, name: 'حریف ۳', score: 0 }
])
const chatMessages = ref([])

// Game constants
const suits = ['hearts', 'diamonds', 'clubs', 'spades']
const suitNames = {
  hearts: 'گل',
  diamonds: 'خشت',
  clubs: 'پیک',
  spades: 'دل'
}
const suitColors = {
  hearts: 'red',
  diamonds: 'red',
  clubs: 'black',
  spades: 'black'
}
const statusMessages = {
  waiting: 'در انتظار شروع بازی',
  bidding: 'در حال پیشنهاد حکم',
  playing: 'در حال بازی',
  finished: 'بازی به پایان رسید'
}

// Computed properties
const isPlayerTurn = computed(() => {
  return gameState.value.currentPlayer === 'player'
})

const playerScore = computed(() => {
  return gameState.value.scores.team1
})

const opponentScore = computed(() => {
  return gameState.value.scores.team2
})

// Methods
const startNewGame = async () => {
  try {
    await gameStore.startHokmGame()
    // In a real app, this would be handled via WebSocket updates
    gameState.value.status = 'bidding'
    dealCards()
  } catch (error) {
    console.error('Failed to start game:', error)
  }
}

const dealCards = () => {
  // Mock dealing cards - in a real app this would come from the server
  const ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
  playerCards.value = []
  
  for (let i = 0; i < 13; i++) {
    const suit = suits[Math.floor(Math.random() * suits.length)]
    const rank = ranks[Math.floor(Math.random() * ranks.length)]
    playerCards.value.push({ suit, rank })
  }
  
  trumpCard.value = {
    suit: suits[Math.floor(Math.random() * suits.length)],
    rank: ranks[Math.floor(Math.random() * ranks.length)]
  }
}

const placeBid = (suit) => {
  gameState.value.trumpSuit = suit
  gameState.value.status = 'playing'
  // In a real app, this would be sent to the server
}

const playCard = (card) => {
  // Remove card from player's hand
  playerCards.value = playerCards.value.filter(c => 
    !(c.suit === card.suit && c.rank === card.rank)
  )
  
  // Add to played cards
  playedCards.value.push(card)
  
  // In a real app, this would be sent to the server
  // and the server would respond with the next game state
}

const sendChatMessage = (message) => {
  gameStore.sendHokmChatMessage(message)
  chatMessages.value.push({
    sender: 'شما',
    message,
    timestamp: new Date().toLocaleTimeString()
  })
}

// Lifecycle hooks
onMounted(() => {
  // Connect to WebSocket for real-time updates
  gameStore.connectToHokmGame({
    onGameUpdate: (data) => {
      gameState.value = data.gameState
      playerCards.value = data.playerCards
      playedCards.value = data.playedCards
      trumpCard.value = data.trumpCard
      opponents.value = data.opponents
    },
    onChatMessage: (message) => {
      chatMessages.value.push(message)
    }
  })
})

onUnmounted(() => {
  gameStore.disconnectFromHokmGame()
})
</script>
