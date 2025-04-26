<template>
  <AdminLayout>
    <div class="space-y-6">
      <!-- Stats Overview -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard
          title="کاربران فعال"
          :value="stats.activeUsers"
          icon="UserGroupIcon"
          color="primary"
          :change="stats.userChange"
        />
        <StatCard
          title="مجموع تراکنش‌ها"
          :value="stats.totalTransactions"
          icon="CurrencyDollarIcon"
          color="green"
          :change="stats.transactionChange"
        />
        <StatCard
          title="بازی‌های امروز"
          :value="stats.todayGames"
          icon="CubeIcon"
          color="blue"
          :change="stats.gameChange"
        />
        <StatCard
          title="درآمد امروز"
          :value="stats.todayRevenue"
          icon="ChartBarIcon"
          color="purple"
          :change="stats.revenueChange"
        />
      </div>
      
      <!-- Recent Activity -->
      <div class="bg-dark-light rounded-xl shadow overflow-hidden">
        <div class="px-6 py-4 border-b border-dark-lighter flex items-center justify-between">
          <h2 class="text-lg font-medium">فعالیت‌های اخیر</h2>
          <RouterLink to="/admin/activity" class="text-sm text-primary hover:text-primary-dark">
            مشاهده همه
          </RouterLink>
        </div>
        <div class="divide-y divide-dark-lighter">
          <ActivityItem
            v-for="activity in recentActivities"
            :key="activity.id"
            :activity="activity"
          />
          <div v-if="recentActivities.length === 0" class="p-6 text-center text-gray-400">
            هیچ فعالیتی ثبت نشده است
          </div>
        </div>
      </div>
      
      <!-- Charts -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-dark-light rounded-xl shadow p-6">
          <h3 class="text-lg font-medium mb-4">کاربران جدید</h3>
          <LineChart :data="userGrowthData" />
        </div>
        <div class="bg-dark-light rounded-xl shadow p-6">
          <h3 class="text-lg font-medium mb-4">درآمد روزانه</h3>
          <BarChart :data="revenueData" />
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import StatCard from '@/components/admin/StatCard.vue'
import ActivityItem from '@/components/admin/ActivityItem.vue'
import LineChart from '@/components/charts/LineChart.vue'
import BarChart from '@/components/charts/BarChart.vue'

const stats = ref({
  activeUsers: 1243,
  totalTransactions: 5421,
  todayGames: 876,
  todayRevenue: 12500000,
  userChange: 12,
  transactionChange: 5,
  gameChange: -3,
  revenueChange: 8
})

const recentActivities = ref([
  {
    id: 1,
    user: { name: 'کاربر نمونه', email: 'user@example.com' },
    action: 'واریز وجه',
    amount: 50000,
    status: 'completed',
    timestamp: '2023-05-15T14:32:00'
  },
  {
    id: 2,
    user: { name: 'کاربر دوم', email: 'user2@example.com' },
    action: 'ثبت نام',
    amount: 0,
    status: 'completed',
    timestamp: '2023-05-15T12:15:00'
  },
  {
    id: 3,
    user: { name: 'کاربر سوم', email: 'user3@example.com' },
    action: 'برداشت وجه',
    amount: 200000,
    status: 'pending',
    timestamp: '2023-05-15T10:45:00'
  }
])

const userGrowthData = ref({
  labels: ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور'],
  datasets: [
    {
      label: 'کاربران جدید',
      data: [120, 190, 170, 220, 240, 280],
      borderColor: '#6366f1',
      backgroundColor: '#6366f1',
      tension: 0.3
    }
  ]
})

const revenueData = ref({
  labels: ['۱ هفته پیش', '۶ روز پیش', '۵ روز پیش', '۴ روز پیش', '۳ روز پیش', 'دیروز', 'امروز'],
  datasets: [
    {
      label: 'درآمد (میلیون تومان)',
      data: [8, 9, 7, 10, 12, 15, 12.5],
      backgroundColor: '#10b981'
    }
  ]
})

onMounted(async () => {
  // In a real app, fetch data from API
  // await fetchDashboardData()
})
</script>
