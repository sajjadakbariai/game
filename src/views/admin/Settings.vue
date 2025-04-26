<template>
  <AdminLayout>
    <div class="space-y-6">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <h1 class="text-2xl font-bold">تنظیمات سیستم</h1>
        <button
          @click="saveSettings"
          class="btn btn-primary"
          :disabled="!hasChanges"
        >
          ذخیره تغییرات
        </button>
      </div>

      <!-- Tabs -->
      <div class="border-b border-dark-lighter">
        <nav class="-mb-px flex space-x-8">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="currentTab = tab.id"
            class="whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm"
            :class="{
              'border-primary text-primary': currentTab === tab.id,
              'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300': currentTab !== tab.id
            }"
          >
            {{ tab.name }}
          </button>
        </nav>
      </div>

      <!-- General Settings -->
      <div v-if="currentTab === 'general'" class="bg-dark-light rounded-xl p-6 space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-1">نام سایت</label>
            <input
              v-model="settings.site_name"
              type="text"
              class="input-field"
            >
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-1">لوگو سایت</label>
            <div class="flex items-center space-x-4">
              <img
                v-if="settings.site_logo"
                :src="settings.site_logo"
                class="h-10 w-auto"
              >
              <input
                type="file"
                accept="image/*"
                @change="handleLogoUpload"
                class="hidden"
                ref="logoInput"
              >
              <button
                @click="$refs.logoInput.click()"
                class="btn btn-secondary"
              >
                آپلود لوگو
              </button>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-1">واحد پول</label>
            <select v-model="settings.currency" class="input-field">
              <option value="toman">تومان</option>
              <option value="rial">ریال</option>
              <option value="usd">دلار</option>
              <option value="eur">یورو</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-1">نماد پول</label>
            <input
              v-model="settings.currency_symbol"
              type="text"
              class="input-field"
            >
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-300 mb-1">توضیحات سایت</label>
          <textarea
            v-model="settings.site_description"
            rows="3"
            class="input-field"
          ></textarea>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="flex items-center space-x-3">
              <input
                v-model="settings.site_active"
                type="checkbox"
                class="h-4 w-4 text-primary focus:ring-primary border-dark-lighter rounded"
              >
              <span class="text-sm text-gray-300">سایت فعال باشد</span>
            </label>
          </div>
          <div>
            <label class="flex items-center space-x-3">
              <input
                v-model="settings.registration_open"
                type="checkbox"
                class="h-4 w-4 text-primary focus:ring-primary border-dark-lighter rounded"
              >
              <span class="text-sm text-gray-300">ثبت نام کاربران جدید فعال باشد</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Game Settings -->
      <div v-if="currentTab === 'games'" class="bg-dark-light rounded-xl p-6 space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 class="text-lg font-medium mb-4">بازی انفجار</h3>
            <div class="space-y-4">
