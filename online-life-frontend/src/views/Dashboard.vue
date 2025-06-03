<template>
  <div class="dashboard-container">
    <!-- Welcome Section -->
    <el-row :gutter="20" class="welcome-row">
      <el-col :xs="24" :sm="24" :md="16">
        <el-card class="welcome-card" shadow="hover">
          <div class="welcome-header">
            <div class="user-info">
              <el-avatar :size="64" :src="userInfo.avatar">
                {{ userInfo.username?.charAt(0)?.toUpperCase() }}
              </el-avatar>
              <div class="user-details">
                <h2>{{ greeting }}，{{ userInfo.username }}</h2>
                <div class="user-role">
                  <el-tag :type="getRoleType(userRole)" effect="light">
                    {{ getRoleText(userRole) }}
                  </el-tag>
                  <el-tag type="info" effect="plain">ID: {{ userInfo.user_id }}</el-tag>
                </div>
              </div>
            </div>
            <div class="quick-actions">
              <el-button
                v-if="userRole === 'client'"
                type="primary"
                @click="router.push('/create-order')"
              >
                <el-icon><Plus /></el-icon>
                创建订单
              </el-button>
              <el-button
                v-if="userRole === 'staff'"
                type="success"
                @click="router.push('/available-orders')"
              >
                <el-icon><Van /></el-icon>
                接单大厅
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="24" :md="8">
        <el-card class="stats-card points-card" shadow="hover">
          <div class="stats-header">
            <h3>我的积分</h3>
            <el-button text type="primary" @click="router.push('/points')">
              查看明细
              <el-icon class="el-icon--right"><ArrowRight /></el-icon>
            </el-button>
          </div>
          <div class="stats-content">
            <el-icon class="stats-icon"><Wallet /></el-icon>
            <span class="stats-value">{{ points.points_balance || 0 }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Stats Section -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="12" :sm="12" :md="6">
        <el-card class="stats-card" shadow="hover">
          <div class="stats-content">
            <el-icon class="stats-icon"><Document /></el-icon>
            <div class="stats-info">
              <span class="stats-label">总订单</span>
              <span class="stats-value">{{ stats.total_orders || 0 }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6">
        <el-card class="stats-card" shadow="hover">
          <div class="stats-content">
            <el-icon class="stats-icon"><Timer /></el-icon>
            <div class="stats-info">
              <span class="stats-label">进行中</span>
              <span class="stats-value accent-warning">{{ stats.in_progress || 0 }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6">
        <el-card class="stats-card" shadow="hover">
          <div class="stats-content">
            <el-icon class="stats-icon"><CircleCheck /></el-icon>
            <div class="stats-info">
              <span class="stats-label">已完成</span>
              <span class="stats-value accent-success">{{ stats.completed || 0 }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6">
        <el-card class="stats-card" shadow="hover">
          <div class="stats-content">
            <el-icon class="stats-icon"><Star /></el-icon>
            <div class="stats-info">
              <span class="stats-label">信誉分</span>
              <span class="stats-value accent-primary">{{ reputation.average_score || 0 }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Recent Activities -->
    <el-row :gutter="20">
      <el-col :xs="24" :sm="24" :md="16">
        <el-card class="recent-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <h3>最近活动</h3>
              <el-button text @click="fetchRecentActivities">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="activity in recentActivities"
              :key="activity.id"
              :type="activity.type"
              :timestamp="activity.time"
              :hollow="activity.hollow"
            >
              {{ activity.content }}
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>

      <!-- Quick Links -->
      <el-col :xs="24" :sm="24" :md="8">
        <el-card class="quick-links-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <h3>快捷操作</h3>
            </div>
          </template>
          <div class="quick-actions-section">
            <h3 class="section-title">快捷操作</h3>
            <div class="quick-actions-grid">
              <div class="action-item">
                <el-button class="action-btn create-task" @click="router.push('/create-group-task')">
                  <el-icon><Plus /></el-icon>
                  <span>发起团办任务</span>
                </el-button>
              </div>
              <div class="action-item">
                <el-button class="action-btn my-tasks" @click="router.push('/my-group-tasks')">
                  <el-icon><List /></el-icon>
                  <span>我的团办任务</span>
                </el-button>
              </div>
              <div class="action-item">
                <el-button class="action-btn profile" @click="router.push('/profile')">
                  <el-icon><User /></el-icon>
                  <span>个人中心</span>
                </el-button>
              </div>
              <div class="action-item">
                <el-button class="action-btn points" @click="router.push('/points')">
                  <el-icon><Wallet /></el-icon>
                  <span>积分管理</span>
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getProfile, getReputation } from '@/api/user';
import { getPointsBalance } from '@/api/points';
import { getOrderList } from '@/api/order';
import { ElMessage } from 'element-plus';
import {
  Plus,
  Van,
  Wallet,
  ArrowRight,
  Document,
  Timer,
  CircleCheck,
  Star,
  Refresh,
  List,
  Tickets,
  User
} from '@element-plus/icons-vue';

const router = useRouter();
const userRole = ref(localStorage.getItem('role') || '');
const userInfo = ref({});
const points = ref({});
const reputation = ref({});
const stats = ref({
  total_orders: 0,
  in_progress: 0,
  completed: 0
});

const greeting = computed(() => {
  const hour = new Date().getHours();
  if (hour < 6) return '凌晨好';
  if (hour < 9) return '早上好';
  if (hour < 12) return '上午好';
  if (hour < 14) return '中午好';
  if (hour < 17) return '下午好';
  if (hour < 19) return '傍晚好';
  if (hour < 22) return '晚上好';
  return '夜深了';
});

const recentActivities = ref([
  {
    id: 1,
    content: '更新了个人信息',
    time: '刚刚',
    type: 'primary'
  },
  {
    id: 2,
    content: '完成了一个订单',
    time: '23分钟前',
    type: 'success',
    hollow: true
  },
  {
    id: 3,
    content: '收到了新的评价',
    time: '2小时前',
    type: 'warning',
    hollow: true
  }
]);

const getRoleType = (role) => {
  const types = {
    'admin': 'danger',
    'client': 'success',
    'staff': 'primary'
  };
  return types[role] || 'info';
};

const getRoleText = (role) => {
  const texts = {
    'admin': '管理员',
    'client': '客户',
    'staff': '代办人员'
  };
  return texts[role] || role;
};

const fetchUserInfo = async () => {
  try {
    const res = await getProfile();
    if (res.data.success) {
      userInfo.value = res.data.data;
    }
  } catch (error) {
    console.error('获取用户信息失败:', error);
  }
};

const fetchPoints = async () => {
  try {
    const res = await getPointsBalance();
    if (res.data.success) {
      points.value = res.data.data;
    }
  } catch (error) {
    console.error('获取积分信息失败:', error);
  }
};

const fetchReputation = async () => {
  if (userRole.value !== 'staff') return;
  try {
    const res = await getReputation();
    if (res.data.success) {
      reputation.value = res.data.data;
    }
  } catch (error) {
    console.error('获取信誉信息失败:', error);
  }
};

const fetchStats = async () => {
  try {
    const res = await getOrderList({ page: 1, per_page: 1 });
    if (res.data.success) {
      const data = res.data.data;
      stats.value = {
        total_orders: data.pagination?.total || 0,
        in_progress: data.stats?.in_progress || 0,
        completed: data.stats?.completed || 0
      };
    }
  } catch (error) {
    console.error('获取统计信息失败:', error);
  }
};

const fetchRecentActivities = async () => {
  // TODO: 实现获取最近活动的API
  ElMessage.success('活动列表已更新');
};

onMounted(() => {
  Promise.all([
    fetchUserInfo(),
    fetchPoints(),
    fetchReputation(),
    fetchStats()
  ]);
});
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
  min-height: 100%;
  background-color: var(--el-bg-color-page, #f5f7fa);
}

.welcome-row {
  margin-bottom: 24px;
}

.welcome-card {
  height: 100%;
  background-color: #ffffff;
  border: none;
}

.welcome-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.user-details h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.user-role {
  display: flex;
  gap: 8px;
  align-items: center;
}

.user-role .el-tag {
  padding: 4px 8px;
  font-size: 12px;
  border: none;
}

.user-role .el-tag:first-child {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.user-role .el-tag:last-child {
  background-color: #f5f5f5;
  color: #616161;
}

.quick-actions {
  display: flex;
  gap: 12px;
}

.quick-actions .el-button {
  background-color: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
  border: none;
  padding: 8px 16px;
  transition: all 0.3s;
}

.quick-actions .el-button:hover {
  background-color: var(--el-color-primary-light-8);
  transform: translateY(-2px);
}

.quick-actions .el-button .el-icon {
  margin-right: 4px;
}

.stats-row {
  margin-bottom: 24px;
}

.stats-card {
  height: 100%;
  transition: all 0.3s;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.stats-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.stats-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.stats-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.stats-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stats-icon {
  font-size: 32px;
  background: linear-gradient(135deg, var(--el-color-primary-light-8) 0%, var(--el-color-primary-light-9) 100%);
  color: var(--el-color-primary);
  padding: 12px;
  border-radius: 12px;
  transition: all 0.3s;
}

.stats-card:hover .stats-icon {
  background: linear-gradient(135deg, var(--el-color-primary-light-7) 0%, var(--el-color-primary-light-8) 100%);
}

.stats-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stats-label {
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.stats-value {
  font-size: 24px;
  font-weight: 600;
  background: linear-gradient(120deg, #2c3e50, #3498db);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.accent-warning {
  background: linear-gradient(120deg, #f39c12, #f1c40f);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.accent-success {
  background: linear-gradient(120deg, #27ae60, #2ecc71);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.accent-primary {
  background: linear-gradient(120deg, #2980b9, #3498db);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.points-card {
  background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
}

.points-card .stats-content {
  margin-top: 20px;
  justify-content: center;
}

.points-card .stats-value {
  font-size: 36px;
  background: linear-gradient(120deg, #16a085, #2ecc71);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.points-card .stats-icon {
  background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%);
  color: #00acc1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.recent-card {
  margin-bottom: 24px;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border: none;
}

.quick-links-card {
  height: 100%;
}

.quick-actions-section {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05);
}

.section-title {
  margin: 0 0 20px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.action-item {
  width: 100%;
}

.action-btn {
  width: 100%;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s;
  padding: 0;
  color: white;
}

.action-btn:hover {
  transform: translateY(-2px);
  opacity: 0.9;
}

.action-btn .el-icon {
  font-size: 18px;
}

.action-btn.create-task {
  background: linear-gradient(135deg, #20B2AA, #3CB371);
}

.action-btn.my-tasks {
  background: linear-gradient(135deg, #778899, #708090);
}

.action-btn.profile {
  background: linear-gradient(135deg, #E6A23C, #F56C6C);
}

.action-btn.points {
  background: linear-gradient(135deg, #6495ED, #4169E1);
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 12px;
  }

  .welcome-header {
    flex-direction: column;
    text-align: center;
  }

  .user-info {
    flex-direction: column;
  }

  .user-details {
    align-items: center;
  }

  .quick-actions {
    width: 100%;
    flex-direction: column;
  }

  .quick-actions .el-button {
    width: 100%;
  }

  .stats-card {
    margin-bottom: 12px;
  }

  .quick-actions-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .quick-actions-section {
    padding: 16px;
  }
}
</style>