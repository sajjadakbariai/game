<template>
  <AppModal
    :is-open="isOpen"
    :title="user ? 'ویرایش کاربر' : 'ایجاد کاربر جدید'"
    icon="UserIcon"
    @close="$emit('close')"
  >
    <div class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-1">نام</label>
          <input
            v-model="form.name"
            type="text"
            class="input-field"
          >
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-1">نام کاربری</label>
          <input
            v-model="form.username"
            type="text"
            class="input-field"
          >
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-300 mb-1">ایمیل</label>
        <input
          v-model="form.email"
          type="email"
          class="input-field"
        >
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-1">رمز عبور</label>
          <input
            v-model="form.password"
            type="password"
            class="input-field"
            :placeholder="user ? 'در صورت عدم تغییر خالی بگذارید' : ''"
          >
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-1">تکرار رمز عبور</label>
          <input
            v-model="form.password_confirmation"
            type="password"
            class="input-field"
          >
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-1">موجودی (تومان)</label>
          <input
            v-model.number="form.balance"
            type="number"
            min="0"
            class="input-field"
          >
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-1">وضعیت</label>
          <select v-model="form.status" class="input-field">
            <option value="active">فعال</option>
            <option value="banned">مسدود شده</option>
            <option value="unverified">تایید نشده</option>
          </select>
        </div>
      </div>

      <div>
        <label class="flex items-center space-x-3">
          <input
            v-model="form.is_admin"
            type="checkbox"
            class="h-4 w-4 text-primary focus:ring-primary border-dark-lighter rounded"
          >
          <span class="text-sm text-gray-300">دسترسی ادمین</span>
        </label>
      </div>
    </div>

    <template #footer>
      <button
        type="button"
        class="btn btn-primary"
        @click="save"
      >
        ذخیره
      </button>
      <button
        type="button"
        class="btn btn-secondary"
        @click="$emit('close')"
      >
        انصراف
      </button>
    </template>
  </AppModal>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  isOpen: Boolean,
  user: Object
})

const emit = defineEmits(['close', 'save'])

const form = ref({
  name: '',
  username: '',
  email: '',
  password: '',
  password_confirmation: '',
  balance: 0,
  status: 'active',
  is_admin: false
})

watch(() => props.user, (user) => {
  if (user) {
    form.value = {
      name: user.name,
      username: user.username,
      email: user.email,
      password: '',
      password_confirmation: '',
      balance: user.balance,
      status: user.status,
      is_admin: user.is_admin
    }
  } else {
    resetForm()
  }
}, { immediate: true })

const resetForm = () => {
  form.value = {
    name: '',
    username: '',
    email: '',
    password: '',
    password_confirmation: '',
    balance: 0,
    status: 'active',
    is_admin: false
  }
}

const save = () => {
  emit('save', form.value)
  emit('close')
}
</script>
