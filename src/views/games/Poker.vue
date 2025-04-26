<template>
  <GameLayout title="پوکر تگزاس هولدم">
    <div class="flex flex-col lg:flex-row gap-6">
      <!-- Game Area -->
      <div class="flex-1">
        <div class="bg-dark-light rounded-xl p-6">
          <!-- Poker Table -->
          <div class="relative h-96 bg-green-800 rounded-full mb-6 overflow-hidden border-4 border-green-700 flex items-center justify-center">
            <!-- Community Cards -->
            <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 flex space-x-2">
              <div 
                v-for="(card, index) in communityCards"
                :key="index"
                class="w-16 h-24 bg-white rounded-md shadow-lg"
              >
                <img 
                  v-if="card"
                  :src="`/images/cards/${card.suit}_${card.rank}.png`" 
                  :alt="`${card.rank} of ${card.suit}`"
                  class="w-full h-full object-cover"
                >
                <div v-else class="w-full h-full bg-dark/20 rounded-md"></div>
              </div>
            </div>

            <!-- Players -->
            <div 
              v-for="player in tablePositions"
              :key="player.position"
              class="absolute"
              :style="player.style"
            >
              <PokerPlayer 
                :player="getPlayer(player.position)"
                :is-current="currentPlayer === player.position"
                :is-active="activePlayer === player.position"
                :is-dealer="dealerPosition === player.position"
                :is-small-blind="smallBlindPosition === player.position"
                :is-big-blind="bigBlindPosition === player.position"
                :cards="playerCards[player.position]"
                :bet="currentBets[player.position]"
                :chips="playerChips[player.position]"
                :is-folded="foldedPlayers.includes(player.position)"
                :show-cards="showPlayerCards(player.position)"
              />
            </div>
          </div>

          <!-- Game Controls -->
          <div v-if="gameState.status !== 'waiting'" class="mt-6">
            <div v-if="isPlayerTurn" class="bg-dark rounded-lg p-4">
              <div class="flex items-center justify-between mb-4">
                <h3 class="font-medium">نوبت شما</h3>
                <div class="flex items-center space-x-2">
                  <span class="text-sm text-gray-400">پول موجود:</span>
                  <span class="font-medium">{{ formatCurrency(playerStack) }}</span>
                </div>
              </div>

              <div class="grid grid-cols-3 gap-3 mb-4">
                <button
                  v-for="action in availableActions"
                  :key="action.type"
                  @click="performAction(action.type)"
                  class="btn py-2"
                  :class="{
                    'btn-primary': action.type === 'raise',
                    'btn-secondary': action.type === 'call',
                    'bg-red-500 hover:bg-red-600': action.type === 'fold'
                  }"
                  :disabled="action.type === 'call' && !action.amount"
                >
                  {{ action.label }}
                  <span v-if="action.amount">
                    ({{ formatCurrency(action.amount) }})
                  </span>
                </button>
              </div>

              <div v-if="canRaise" class="space-y-2">
                <label class="block text-sm text-gray-400">مبلغ افزایش ({{ formatCurrency(minRaise) }} - {{ formatCurrency(maxRaise) }})</label>
                <div class="flex space-x-3">
                  <input
                    v-model.number="raiseAmount"
                    type="number"
                    :min="minRaise"
                    :max="maxRaise"
                    class="input-field flex-1"
                  >
                  <button
                    @click="performAction('raise')"
                    class="btn btn-primary px-4"
                  >
                    تایید
                  </button>
                </div>
              </div>
            </div>

            <div v-else class="text-center py-4 text-gray-400">
              {{ statusMessages[gameState.status] }}
              <span v-if="activePlayerName"> - نوبت {{ activePlayerName }}</span>
            </div>
          </div>

          <div v-else class="text-center py-6">
            <button
              @click="joinTable"
              class="btn btn-primary px-6"
              :disabled="joiningTable"
            >
              <span v-if="joiningTable">
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </span>
              پیوستن به میز
            </button>
          </div>
        </div>

        <!-- Game History -->
        <div class="mt-6 bg-dark-light rounded-xl p-6">
          <h3 class="text-lg font-medium mb-4">تاریخچه دست‌ها</h3>
          <div class="space-y-3">
            <div
              v-for="(hand, index) in gameHistory"
              :key="index"
              class="bg-dark rounded-lg p-3"
            >
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm text-gray-400">دست #{{ hand.id }}</span>
                <span class="text-sm font-medium" :class="hand.winner === 'player' ? 'text-green-500' : 'text-red-500'">
                  {{ hand.winner === 'player' ? `+${formatCurrency(hand.pot)}` : `-${formatCurrency(hand.loss)}` }}
                </span>
              </div>
              <div class="flex items-center space-x-2">
                <span class="text-xs text-gray-400">برنده:</span>
                <span class="text-xs">{{ hand.winnerName }}</span>
                <span class="text-xs text-gray-400">با:</span>
                <span class="text-xs font-medium">{{ hand.handRank }}</span>
              </div>
            </div>

            <div v-if="gameHistory.length === 0" class="text-center py-4 text-gray-400 text-sm">
              تاریخچه‌ای ثبت نشده است
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
              <span class="text-gray-400">دست فعلی</span>
              <span class="font-medium">#{{ currentHandId }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-gray-400">مرحله بازی</span>
              <span class="font-medium">{{ roundNames[gameState.round] }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-gray-400">پول فعلی</span>
              <span class="font-medium text-primary">{{ formatCurrency(currentPot) }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-gray-400">حداقل شرط</span>
              <span class="font-medium">{{ formatCurrency(currentBet) }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-gray-400">بلایند کوچک</span>
              <span class="font-medium">{{ formatCurrency(smallBlind) }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-gray-400">بلایند بزرگ</span>
              <span class="font-medium">{{ formatCurrency(bigBlind) }}</span>
            </div>
          </div>
        </div>

        <!-- Players List -->
        <div class="bg-dark-light rounded-xl p-6">
          <h3 class="text-lg font-medium mb-4">بازیکنان</h3>
          <div class="space-y-3">
            <div
              v-for="player in players"
              :key="player.position"
              class="flex items-center justify-between p-3 bg-dark rounded-lg"
            >
              <div class="flex items-center space-x-3">
                <div 
                  class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold"
                  :class="{
                    'bg-primary/10 text-primary': player.position === 'player',
                    'bg-dark-lighter': player.position !== 'player'
                  }"
                >
                  {{ player.initials }}
                </div>
                <div>
                  <p class="text-sm">{{ player.name }}</p>
                  <p class="text-xs text-gray-400">{{ formatCurrency(player.chips) }}</p>
                </div>
              </div>
              <span 
                class="text-xs px-2 py-1 rounded"
                :class="{
                  'bg-green-500/20 text-green-500': player.status === 'active',
                  'bg-red-500/20 text-red-500': player.status === 'folded',
                  'bg-gray-500/20 text-gray-500': player.status === 'waiting'
                }"
              >
                {{ playerStatuses[player.status] }}
              </span>
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
import { formatCurrency } from '@/utils/helpers'
import GameLayout from '@/layouts/GameLayout.vue'
import PokerPlayer from '@/components/games/poker/Player.vue'
import GameChat from '@/components/games/Chat.vue'

const gameStore = useGameStore()

// Game state
const gameState = ref({
  status: 'waiting', // waiting, preflop, flop, turn, river, showdown, finished
  round: 'preflop',
  currentHandId: 0,
  currentPot: 0,
  currentBet: 0,
  smallBlind: 100,
  bigBlind: 200,
  dealerPosition: 'east',
  smallBlindPosition: 'south',
  bigBlindPosition: 'west',
  activePlayer: null,
  winningPlayers: []
})

const players = ref([])
const playerCards = ref({
  player: [],
  north: [],
  east: [],
  south: [],
  west: []
})
const communityCards = ref([null, null, null, null, null])
const currentBets = ref({})
const playerChips = ref({})
const foldedPlayers = ref([])
const chatMessages = ref([])
const joiningTable = ref(false)
const raiseAmount = ref(0)

// Table positions
const tablePositions = ref([
  { position: 'north', style: { top: '10%', left: '50%', transform: 'translateX(-50%)' } },
  { position: 'east', style: { top: '50%', right: '10%', transform: 'translateY(-50%)' } },
  { position: 'south', style: { bottom: '10%', left: '50%', transform: 'translateX(-50%)' } },
  { position: 'west', style: { top: '50%', left: '10%', transform: 'translateY(-50%)' } },
  { position: 'player', style: { bottom: '15%', left: '50%', transform: 'translateX(-50%)' } }
])

// Game constants
const roundNames = {
  preflop: 'پری فلاپ',
  flop: 'فلاپ',
  turn: 'ترن',
  river: 'ریور',
  showdown: 'نمایش کارت‌ها'
}

const playerStatuses = {
  active: 'فعال',
  folded: 'فولد',
  waiting: 'منتظر'
}

const statusMessages = {
  waiting: 'در انتظار شروع بازی',
  preflop: 'پری فلاپ',
  flop: 'فلاپ',
  turn: 'ترن',
  river: 'ریور',
  showdown: 'نمایش کارت‌ها',
  finished: 'دست تمام شد'
}

// Computed properties
const currentPlayer = computed(() => {
  return 'player' // In a real app, this would come from game state
})

const isPlayerTurn = computed(() => {
  return gameState.value.activePlayer === currentPlayer.value
})

const activePlayerName = computed(() => {
  if (!gameState.value.activePlayer) return ''
  const player = players.value.find(p => p.position === gameState.value.activePlayer)
  return player ? player.name : ''
})

const playerStack = computed(() => {
  return playerChips.value.player || 0
})

const availableActions = computed(() => {
  const actions = []
  const callAmount = gameState.value.currentBet - (currentBets.value.player || 0)

  if (gameState.value.status === 'waiting') return actions

  // Fold action
  actions.push({
    type: 'fold',
    label: 'فولد',
    amount: 0
  })

  // Check/Call action
  if (callAmount > 0) {
    actions.push({
      type: 'call',
      label: 'کال',
      amount: callAmount
    })
  } else {
    actions.push({
      type: 'call',
      label: 'چک',
      amount: 0
    })
  })

  // Raise action
  if (canRaise.value) {
    actions.push({
      type: 'raise',
      label: 'ریز',
      amount: minRaise.value
    })
  }

  return actions
})

const canRaise = computed(() => {
  const playerBet = currentBets.value.player || 0
  const maxPossibleRaise = playerStack.value - (gameState.value.currentBet - playerBet)
  return maxPossibleRaise >= minRaise.value
})

const minRaise = computed(() => {
  return gameState.value.currentBet > 0 
    ? Math.max(gameState.value.bigBlind, gameState.value.currentBet)
    : gameState.value.bigBlind
})

const maxRaise = computed(() => {
  const playerBet = currentBets.value.player || 0
  return playerStack.value - (gameState.value.currentBet - playerBet)
})

const gameHistory = computed(() => {
  // In a real app, this would come from the server
  return [
    {
      id: 1234,
      winner: 'player',
      winnerName: 'شما',
      handRank: 'فول هاوس',
      pot: 12500,
      loss: 0
    },
    {
      id: 1233,
      winner: 'opponent',
      winnerName: 'حریف ۱',
      handRank: 'فلاش',
      pot: 0,
      loss: 7500
    }
  ]
})

// Methods
const getPlayer = (position) => {
  return players.value.find(p => p.position === position) || {
    position,
    name: position === 'player' ? 'شما' : `حریف ${position}`,
    initials: position === 'player' ? 'ش' : position.charAt(0).toUpperCase(),
    chips: 10000,
    status: 'waiting'
  }
}

const showPlayerCards = (position) => {
  return position === 'player' || gameState.value.status === 'showdown'
}

const joinTable = async () => {
  try {
    joiningTable.value = true
    await gameStore.joinPokerTable()
    
    // In a real app, this would be handled via WebSocket updates
    gameState.value.status = 'preflop'
    initializeNewHand()
  } catch (error) {
    console.error('Failed to join table:', error)
  } finally {
    joiningTable.value = false
  }
}

const initializeNewHand = () => {
  // Mock data - in a real app this would come from the server
  players.value = [
    { position: 'player', name: 'شما', initials: 'ش', chips: 10000, status: 'active' },
    { position: 'north', name: 'حریف ۱', initials: 'ح', chips: 8500, status: 'active' },
    { position: 'east', name: 'حریف ۲', initials: 'ح', chips: 12000, status: 'active' },
    { position: 'south', name: 'حریف ۳', initials: 'ح', chips: 7500, status: 'active' },
    { position: 'west', name: 'حریف ۴', initials: 'ح', chips: 15000, status: 'active' }
  ]

  playerCards.value = {
    player: [
      { suit: 'hearts', rank: 'A' },
      { suit: 'diamonds', rank: 'A' }
    ],
    north: [],
    east: [],
    south: [],
    west: []
  }

  communityCards.value = [null, null, null, null, null]
  currentBets.value = {
    player: 200,
    north: 100,
    east: 0,
    south: 0,
    west: 0
  }

  playerChips.value = {
    player: 9800,
    north: 8400,
    east: 12000,
    south: 7500,
    west: 15000
  }

  foldedPlayers.value = []
  gameState.value.activePlayer = 'player'
}

const performAction = (action) => {
  switch (action) {
    case 'fold':
      handleFold()
      break
    case 'call':
      handleCall()
      break
    case 'raise':
      handleRaise()
      break
  }
}

const handleFold = () => {
  foldedPlayers.value.push(currentPlayer.value)
  // In a real app, this would be sent to the server
  advanceGame()
}

const handleCall = () => {
  const callAmount = gameState.value.currentBet - (currentBets.value.player || 0)
  if (callAmount > 0) {
    currentBets.value.player = gameState.value.currentBet
    playerChips.value.player -= callAmount
    gameState.value.currentPot += callAmount
  }
  // In a real app, this would be sent to the server
  advanceGame()
}

const handleRaise = () => {
  const raiseToAmount = Math.min(Math.max(raiseAmount.value, minRaise.value), maxRaise.value)
  const totalBet = (currentBets.value.player || 0) + raiseToAmount
  
  currentBets.value.player = totalBet
  playerChips.value.player -= raiseToAmount
  gameState.value.currentBet = totalBet
  gameState.value.currentPot += raiseToAmount
  
  // In a real app, this would be sent to the server
  advanceGame()
}

const advanceGame = () => {
  // Mock advancing game - in a real app this would come from the server
  if (gameState.value.round === 'preflop') {
    gameState.value.round = 'flop'
    communityCards.value = [
      { suit: 'hearts', rank: 'K' },
      { suit: 'diamonds', rank: 'Q' },
      { suit: 'clubs', rank: 'J' },
      null,
      null
    ]
  } else if (gameState.value.round === 'flop') {
    gameState.value.round = 'turn'
    communityCards.value[3] = { suit: 'spades', rank: '10' }
  } else if (gameState.value.round === 'turn') {
    gameState.value.round = 'river'
    communityCards.value[4] = { suit: 'hearts', rank: '9' }
  } else if (gameState.value.round === 'river') {
    gameState.value.round = 'showdown'
    gameState.value.winningPlayers = ['player']
  } else {
    initializeNewHand()
  }
}

const sendChatMessage = (message) => {
  gameStore.sendPokerChatMessage(message)
  chatMessages.value.push({
    sender: 'شما',
    message,
    timestamp: new Date().toLocaleTimeString()
  })
}

// Lifecycle hooks
onMounted(() => {
  // Connect to WebSocket for real-time updates
  gameStore.connectToPokerGame({
    onGameUpdate: (data) => {
      gameState.value = data.gameState
      players.value = data.players
      playerCards.value = data.playerCards
      communityCards.value = data.communityCards
      currentBets.value = data.currentBets
      playerChips.value = data.playerChips
      foldedPlayers.value = data.foldedPlayers
    },
    onChatMessage: (message) => {
      chatMessages.value.push(message)
    }
  })
})

onUnmounted(() => {
  gameStore.disconnectFromPokerGame()
})
</script>
