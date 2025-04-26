<template>
  <div 
    class="text-center transform transition-all duration-300"
    :class="{
      'scale-110': isActive,
      'opacity-50': isFolded
    }"
  >
    <!-- Player Info -->
    <div class="mb-2">
      <div class="relative inline-block">
        <div 
          class="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold"
          :class="{
            'bg-primary': isCurrent,
            'bg-dark-lighter': !isCurrent
          }"
        >
          {{ player.initials }}
        </div>
        
        <!-- Dealer Button -->
        <div 
          v-if="isDealer"
          class="absolute -top-2 -right-2 bg-yellow-500 text-dark text-xs font-bold w-6 h-6 rounded-full flex items-center justify-center"
        >
          D
        </div>
        
        <!-- Blind Indicators -->
        <div 
          v-if="isSmallBlind"
          class="absolute -bottom-2 -left-2 bg-blue-500 text-white text-xs font-bold w-6 h-6 rounded-full flex items-center justify-center"
        >
          S
        </div>
        
        <div 
          v-if="isBigBlind"
          class="absolute -bottom-2 -left-2 bg-red-500 text-white text-xs font-bold w-6 h-6 rounded-full flex items-center justify-center"
        >
          B
        </div>
      </div>
      
      <p class="text-sm mt-1">{{ player.name }}</p>
      <p class="text-xs text-gray-400">{{ formatCurrency(player.chips) }}</p>
    </div>
    
    <!-- Player Cards -->
    <div class="flex justify-center space-x-1">
      <div 
        v-for="(card, index) in cards"
        :key="index"
        class="w-8 h-12 rounded-sm shadow"
        :class="{
          'bg-white': card,
          'bg-dark/20': !card,
          'transform -rotate-12': index === 0,
          'transform rotate-12': index === 1
        }"
      >
        <img 
          v-if="card && showCards"
          :src="`/images/cards/${card.suit}_${card.rank}.png`"
          class="w-full h-full object-cover"
        >
        <div v-else-if="card" class="w-full h-full bg-primary/10"></div>
      </div>
    </div>
    
    <!-- Player Bet -->
    <div 
      v-if="bet > 0"
      class="mt-2 inline-block bg-dark/80 rounded-full px-2 py-1 text-xs font-medium"
    >
      {{ formatCurrency(bet) }}
    </div>
  </div>
</template>

<script setup>
import { formatCurrency } from '@/utils/helpers'

const props = defineProps({
  player: {
    type: Object,
    required: true
  },
  isCurrent: {
    type: Boolean,
    default: false
  },
  isActive: {
    type: Boolean,
    default: false
  },
  isDealer: {
    type: Boolean,
    default: false
  },
  isSmallBlind: {
    type: Boolean,
    default: false
  },
  isBigBlind: {
    type: Boolean,
    default: false
  },
  cards: {
    type: Array,
    default: () => []
  },
  bet: {
    type: Number,
    default: 0
  },
  chips: {
    type: Number,
    default: 0
  },
  isFolded: {
    type: Boolean,
    default: false
  },
  showCards: {
    type: Boolean,
    default: false
  }
})
</script>
