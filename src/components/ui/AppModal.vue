<template>
  <Transition name="modal">
    <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 transition-opacity" @click="close">
          <div class="absolute inset-0 bg-black opacity-75"></div>
        </div>
        
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen">&#8203;</span>
        
        <div class="inline-block align-bottom bg-dark-light rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div v-if="icon" class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full sm:mx-0 sm:h-10 sm:w-10" :class="iconBg">
                <component :is="icon" class="h-6 w-6" :class="iconColor" />
              </div>
              <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                <h3 v-if="title" class="text-lg leading-6 font-medium" :class="titleClass">
                  {{ title }}
                </h3>
                <div class="mt-2">
                  <slot></slot>
                </div>
              </div>
            </div>
          </div>
          <div class="px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <slot name="footer">
              <button type="button" class="btn btn-primary sm:ml-3 sm:w-auto" @click="confirm">
                Confirm
              </button>
              <button type="button" class="btn btn-secondary mt-3 sm:mt-0 sm:w-auto" @click="close">
                Cancel
              </button>
            </slot>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  isOpen: Boolean,
  title: String,
  icon: Object,
  iconBg: {
    type: String,
    default: 'bg-primary-100'
  },
  iconColor: {
    type: String,
    default: 'text-primary-600'
  },
  titleClass: {
    type: String,
    default: 'text-gray-100'
  }
})

const emit = defineEmits(['close', 'confirm'])

function close() {
  emit('close')
}

function confirm() {
  emit('confirm')
}
</script>

<style>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
