<template>
  <div class="min-h-screen flex items-center justify-center bg-dark p-4">
    <div class="w-full max-w-md bg-dark-light rounded-xl shadow-lg p-8">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-primary mb-2">ورود به حساب کاربری</h1>
        <p class="text-gray-400">لطفا اطلاعات حساب خود را وارد کنید</p>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-6">
        <div>
          <label for="email" class="block text-sm font-medium text-gray-300 mb-1">ایمیل</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            class="input-field"
            :class="{ 'border-red-500': errors.email }"
            placeholder="example@example.com"
          />
          <p v-if="errors.email" class="mt-1 text-sm text-red-500">{{ errors.email }}</p>
        </div>

        <div>
          <label for="password" class="block text-sm font-medium text-gray-300 mb-1">رمز عبور</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            class="input-field"
            :class="{ 'border-red-500': errors.password }"
            placeholder="••••••••"
          />
          <p v-if="errors.password" class="mt-1 text-sm text-red-500">{{ errors.password }}</p>
        </div>

        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <input
              id="remember"
              v-model="form.remember"
              type="checkbox"
              class="h-4 w-4 text-primary focus:ring-primary border-dark-lighter rounded"
            />
            <label for="remember" class="mr-2 block text-sm text-gray-400">مرا به خاطر بسپار</label>
          </div>

          <RouterLink
            to="/forgot-password"
            class="text-sm text-primary hover:text-primary-dark"
          >
            فراموشی رمز عبور؟
          </RouterLink>
        </div>

        <div>
          <button
            type="submit"
            class="btn btn-primary w-full py-3"
            :disabled="isLoading"
          >
            <span v-if="isLoading">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </span>
            ورود به حساب
          </button>
        </div>
      </form>

      <div class="mt-6 text-center">
        <p class="text-gray-400">
          حساب کاربری ندارید؟
          <RouterLink
            to="/register"
            class="text-primary hover:text-primary-dark font-medium"
          >
            ثبت نام کنید
          </RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'
import { validateEmail, validatePassword } from '@/utils/validation'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  email: '',
  password: '',
  remember: false
})

const errors = ref({})
const isLoading = ref(false)

const handleSubmit = async () => {
  // Validate form
  errors.value = {}
  
  if (!form.value.email) {
    errors.value.email = 'وارد کردن ایمیل الزامی است'
  } else if (!validateEmail(form.value.email)) {
    errors.value.email = 'ایمیل وارد شده معتبر نیست'
  }
  
  if (!form.value.password) {
    errors.value.password = 'وارد کردن رمز عبور الزامی است'
  } else if (!validatePassword(form.value.password)) {
    errors.value.password = 'رمز عبور باید حداقل 6 کاراکتر داشته باشد'
  }
  
  if (Object.keys(errors.value).length > 0) return
  
  try {
    isLoading.value = true
    await authStore.login({
      email: form.value.email,
      password: form.value.password
    })
    
    // Redirect to dashboard or previous page
    const redirect = router.currentRoute.value.query.redirect || '/dashboard'
    router.push(redirect)
  } catch (error) {
    errors.value.form = error.response?.data?.message || 'خطا در ورود به سیستم'
  } finally {
    isLoading.value = false
  }
}
</script>
