<template>
  <div class="profile-page">
    <el-row :gutter="20">
      <!-- User Info Card -->
      <el-col :xs="24" :sm="24" :md="16">
        <el-card class="profile-card">
          <template #header>
            <div class="card-header">
              <h2>个人信息</h2>
              <el-button type="primary" @click="onUpdate" :loading="loading.update">
                <el-icon><Check /></el-icon>
                保存修改
              </el-button>
            </div>
          </template>
          
          <el-form :model="profile" label-width="100px">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="用户名">
                  <el-input v-model="profile.username" disabled />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="用户角色">
                  <el-tag :type="getRoleType(profile.role)" effect="light">
                    {{ getRoleText(profile.role) }}
                  </el-tag>
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="邮箱">
                  <el-input v-model="profile.email" placeholder="请输入邮箱" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="电话">
                  <el-input v-model="profile.phone" placeholder="请输入电话" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item label="地址">
              <el-input v-model="profile.address" placeholder="请输入地址" />
            </el-form-item>
          </el-form>
        </el-card>

        <!-- Password Card -->
        <el-card class="profile-card">
          <template #header>
            <div class="card-header">
              <h2>修改密码</h2>
              <el-button type="primary" @click="onChangePwd" :loading="loading.password">
                <el-icon><Key /></el-icon>
                确认修改
              </el-button>
            </div>
          </template>
          
          <el-form :model="pwdForm" label-width="100px">
            <el-form-item label="原密码">
              <el-input v-model="pwdForm.old_password" type="password" placeholder="请输入原密码" show-password />
            </el-form-item>
            <el-form-item label="新密码">
              <el-input v-model="pwdForm.new_password" type="password" placeholder="请输入新密码" show-password />
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- Stats Column -->
      <el-col :xs="24" :sm="24" :md="8" class="right-column">
        <div class="stats-container">
          <!-- Points Card -->
          <el-card class="profile-card mini-stats-card">
            <template #header>
              <div class="card-header">
                <h2>我的积分</h2>
                <el-button text type="primary" @click="$router.push('/points')">
                  查看详情
                  <el-icon class="el-icon--right"><ArrowRight /></el-icon>
                </el-button>
              </div>
            </template>
            
            <div class="mini-stats-value">
              <el-icon class="stats-icon"><Coin /></el-icon>
              <span class="points">{{ points.points_balance || 0 }}</span>
            </div>
          </el-card>

          <!-- Reputation Card -->
          <el-card v-if="userRole === 'staff'" class="profile-card mini-stats-card">
            <template #header>
              <div class="card-header">
                <h2>信誉评分</h2>
                <el-button text type="primary" @click="$router.push('/reputation')">
                  查看详情
                  <el-icon class="el-icon--right"><ArrowRight /></el-icon>
                </el-button>
              </div>
            </template>
            
            <div class="mini-stats-value">
              <el-icon class="stats-icon"><Star /></el-icon>
              <span class="reputation">{{ reputation.average_score || 0 }}</span>
            </div>
            <div class="stats-subtitle">
              共 {{ reputation.total_reviews || 0 }} 次评价
            </div>
          </el-card>
        </div>

        <!-- Recent Activity Card -->
        <el-card class="profile-card activity-card">
          <template #header>
            <div class="card-header">
              <h2>最近活动</h2>
            </div>
          </template>
          
          <el-timeline>
            <el-timeline-item
              v-for="(activity, index) in recentActivities"
              :key="index"
              :type="activity.type"
              :timestamp="activity.time"
              :hollow="activity.hollow"
            >
              {{ activity.content }}
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getProfile, updateProfile, changePassword, getReputation } from '@/api/user';
import { getPointsBalance } from '@/api/points';
import { ElMessage } from 'element-plus';
import { Check, Key, ArrowRight, Coin, Star } from '@element-plus/icons-vue';

const profile = ref({});
const pwdForm = ref({ old_password: '', new_password: '' });
const points = ref({});
const reputation = ref({});
const userRole = ref(localStorage.getItem('role'));
const loading = ref({
  update: false,
  password: false
});

const recentActivities = ref([
  {
    content: '更新了个人信息',
    time: '刚刚',
    type: 'primary'
  },
  {
    content: '完成了一个订单',
    time: '23分钟前',
    type: 'success',
    hollow: true
  },
  {
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

const fetchProfile = async () => {
  try {
    const res = await getProfile();
    if (res.data.success) {
      profile.value = res.data.data;
    }
  } catch (error) {
    ElMessage.error('获取个人信息失败');
  }
};

const fetchPoints = async () => {
  try {
    const res = await getPointsBalance();
    if (res.data.success) {
      points.value = res.data.data;
    }
  } catch (error) {
    ElMessage.error('获取积分信息失败');
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
    ElMessage.error('获取信誉信息失败');
  }
};

const onUpdate = async () => {
  loading.value.update = true;
  try {
    const res = await updateProfile(profile.value);
    if (res.data.success) {
      ElMessage.success('个人信息更新成功');
    } else {
      ElMessage.error(res.data.message || '更新失败');
    }
  } catch (error) {
    ElMessage.error('更新个人信息失败');
  } finally {
    loading.value.update = false;
  }
};

const onChangePwd = async () => {
  if (!pwdForm.value.old_password || !pwdForm.value.new_password) {
    ElMessage.warning('请填写完整的密码信息');
    return;
  }

  loading.value.password = true;
  try {
    const res = await changePassword(pwdForm.value);
    if (res.data.success) {
      ElMessage.success('密码修改成功');
      pwdForm.value = { old_password: '', new_password: '' };
    } else {
      ElMessage.error(res.data.message || '修改失败');
    }
  } catch (error) {
    ElMessage.error('修改密码失败');
  } finally {
    loading.value.password = false;
  }
};

onMounted(() => {
  Promise.all([
    fetchProfile(),
    fetchPoints(),
    fetchReputation()
  ]);
});
</script>

<style scoped>
.profile-page {
  padding: 20px;
  min-height: 100%;
}

.profile-card {
  margin-bottom: 20px;
  border-radius: 8px;
  overflow: hidden;
}

.profile-card:last-child {
  margin-bottom: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px !important;
}

.card-header h2 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.right-column {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.stats-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  flex-shrink: 0;
}

.mini-stats-card {
  margin-bottom: 0 !important;
}

.mini-stats-card :deep(.el-card__header) {
  padding: 8px 12px !important;
}

.mini-stats-card :deep(.el-card__body) {
  padding: 8px 12px !important;
}

.mini-stats-value {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.stats-icon {
  font-size: 20px;
  color: var(--el-color-primary);
}

.points,
.reputation {
  font-size: 24px;
  font-weight: 600;
  color: var(--el-color-primary);
}

.stats-subtitle {
  margin-top: 8px;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.activity-card {
  margin-bottom: 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.activity-card :deep(.el-card__body) {
  flex: 1;
  overflow-y: auto;
  padding: 16px !important;
}

@media (max-width: 768px) {
  .profile-page {
    padding: 12px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .card-header .el-button {
    width: 100%;
  }
}
</style>