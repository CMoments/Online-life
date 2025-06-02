<template>
  <el-card>
    <h2>欢迎来到网上代办系统</h2>
    <el-descriptions :column="2" border>
      <el-descriptions-item label="用户名">{{ userInfo.username }}</el-descriptions-item>
      <el-descriptions-item label="用户ID">{{ userInfo.user_id }}</el-descriptions-item>
      <el-descriptions-item label="当前积分">{{ points.points_balance }}</el-descriptions-item>
      <el-descriptions-item label="信誉分">{{ reputation.average_score }}</el-descriptions-item>
    </el-descriptions>
    <el-divider />
    <div>请选择上方菜单进行操作</div>
    <div v-if="userRole === 'client'" style="margin-top: 24px;">
      <el-button type="primary" @click="router.push('/create-order')">创建订单</el-button>
      <el-button type="success" @click="router.push('/create-group-task')" style="margin-left: 12px;">发起团办任务</el-button>
      <el-button type="info" @click="router.push('/my-group-tasks')" style="margin-left: 12px;">我的团办任务</el-button>
    </div>
    <div v-else-if="userRole === 'staff'" style="margin-top: 24px;">
      <el-button type="primary" @click="router.push('/my-bid-records')">我的竞标记录</el-button>
    </div>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getProfile, getReputation } from '@/api/user'
import { getPointsBalance } from '@/api/points'
import { ElMessage } from 'element-plus';

const router = useRouter();
const userRole = ref(localStorage.getItem('role') || '');
const userInfo = ref({})
const points = ref({})
const reputation = ref({})

const fetchAll = async () => {
  const [profileRes, pointsRes, repRes] = await Promise.all([
    getProfile(),
    getPointsBalance(),
    getReputation()
  ])
  if (profileRes.data.success) userInfo.value = profileRes.data.data
  if (pointsRes.data.success) points.value = pointsRes.data.data
  if (repRes.data.code === 0 || repRes.data.success) reputation.value = repRes.data.data
}

onMounted(fetchAll)
</script>

<style scoped>
</style>