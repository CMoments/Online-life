<template>
  <div class="available-orders-page">
    <el-card class="order-card">
      <div class="section">
        <div class="section-header">
          <h2 class="section-title">可接单列表</h2>
          <el-button type="primary" @click="fetchOrders" :loading="loading.available">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
        <el-table 
          :data="orders" 
          v-loading="loading.available"
          border
        >
          <el-table-column prop="client_name" label="客户" width="120" />
          <el-table-column label="地址" min-width="200">
            <template #default="{ row }">
              <div class="address-cell">
                <el-icon><Location /></el-icon>
                <span>{{ row.shop_address || '' }} - {{ row.order_location }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="creation_time" label="创建时间" width="160">
            <template #default="{ row }">
              <div class="time-cell">
                <el-icon><Calendar /></el-icon>
                <span>{{ formatTime(row.creation_time) }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="assignment_type" label="分配类型" width="120">
            <template #default="{ row }">
              <el-tag size="small" effect="light">{{ row.assignment_type }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="order_status" label="订单状态" width="120">
            <template #default="{ row }">
              <el-tag 
                :type="getStatusType(row.order_status)"
                size="small"
                effect="light"
              >
                {{ getStatusText(row.order_status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button 
                type="primary" 
                size="small"
                @click="handleAccept(row)"
                :loading="loading.accept === row.order_id"
              >
                接单
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="section">
        <div class="section-header">
          <h2 class="section-title">当前接单</h2>
          <el-button type="primary" @click="fetchCurrentAssignments" :loading="loading.current">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
        <el-table 
          :data="currentAssignments" 
          v-loading="loading.current"
          border
        >
          <el-table-column prop="type" label="类型" width="100">
            <template #default="{ row }">
              <el-tag 
                :type="row.type === 'group_task' ? 'success' : 'primary'"
                size="small"
                effect="light"
              >
                {{ row.type === 'group_task' ? '团办' : '普通' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="ID" width="180">
            <template #default="{ row }">
              <el-tag size="small" effect="plain">
                {{ row.type === 'group_task' ? row.task_id : row.order_id }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" min-width="120" />
          <el-table-column label="订单/任务地点" min-width="200">
            <template #default="{ row }">
              <div class="address-cell">
                <el-icon><Location /></el-icon>
                <span>{{ row.order_location || row.task_location }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="creation_time" label="创建时间" width="160">
            <template #default="{ row }">
              <div class="time-cell">
                <el-icon><Calendar /></el-icon>
                <span>{{ formatTime(row.creation_time) }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="bid_deadline" label="竞标截止" width="160">
            <template #default="{ row }">
              <span v-if="row.bid_deadline">
                <div class="time-cell">
                  <el-icon><Timer /></el-icon>
                  <span>{{ formatTime(row.bid_deadline) }}</span>
                </div>
              </span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="participants_count" label="参与人数" width="100" align="center">
            <template #default="{ row }">
              <el-tag 
                v-if="row.participants_count"
                type="info" 
                size="small" 
                effect="plain"
              >
                {{ row.participants_count }}
              </el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="order_status" label="状态" width="120">
            <template #default="{ row }">
              <el-tag 
                :type="getStatusType(row.order_status)"
                size="small"
                effect="light"
              >
                {{ getStatusText(row.order_status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button
                v-if="row.type === 'order' && row.order_status === 'assigned'"
                type="success"
                size="small"
                :loading="loading.complete === row.order_id"
                @click="handleComplete(row)"
              >
                完成
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="section">
        <div class="section-header">
          <h2 class="section-title">已完成订单</h2>
          <el-button type="primary" @click="getCompletedOrders" :loading="loading.completed">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
        <el-table 
          :data="completedOrders" 
          v-loading="loading.completed"
          border
        >
          <el-table-column prop="order_status" label="状态" width="120">
            <template #default="{ row }">
              <el-tag 
                :type="getStatusType(row.order_status)"
                size="small"
                effect="light"
              >
                {{ getStatusText(row.order_status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="地址" min-width="200">
            <template #default="{ row }">
              <div class="address-cell">
                <el-icon><Location /></el-icon>
                <span>
                  {{ row.shop_address ? row.shop_address.replace(/^- /, '') : '' }} - {{ row.order_location }}
                </span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="creation_time" label="创建时间" width="160">
            <template #default="{ row }">
              <div class="time-cell">
                <el-icon><Calendar /></el-icon>
                <span>{{ formatTime(row.creation_time) }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="completion_time" label="完成时间" width="160">
            <template #default="{ row }">
              <div class="time-cell">
                <el-icon><Timer /></el-icon>
                <span>{{ formatTime(row.completion_time) }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="assignment_type" label="分配类型" width="120">
            <template #default="{ row }">
              <el-tag size="small" effect="light">{{ row.assignment_type }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="estimated_time" label="预计时间" width="120">
            <template #default="{ row }">
              <div class="time-estimate">
                {{ Math.floor((row.estimated_time || 0) / 60) }}分钟
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button 
                type="primary"
                size="small"
                plain
                @click="showOrderDetail(row)"
              >
                详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
    <ReviewDialog ref="reviewDialogRef" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { 
  getAvailableOrders, 
  acceptOrder, 
  getMyOrders, 
  completeOrder, 
  getOrderDetail, 
  getStaffAllOrders
} from '@/api/order';
import { getStaffAvailableTasks } from '@/api/task';
import { getOrderReputation } from '@/api/user';
import { ElMessage } from 'element-plus';
import { Refresh, Location, Calendar, Timer } from '@element-plus/icons-vue';
import dayjs from 'dayjs';
import ReviewDialog from './ReviewDialog.vue';

const router = useRouter();
const orders = ref([]);
const assignedGroupTasks = ref([]);
const currentAssignments = ref([]);
const completedOrders = ref([]);
const reviewDialogRef = ref();

const loading = ref({
  available: false,
  current: false,
  completed: false,
  accept: null,
  complete: null
});

const getStatusType = (status) => {
  const types = {
    'pending': 'warning',
    'in_progress': 'primary',
    'completed': 'success',
    'paid': 'info',
    'cancelled': 'danger'
  };
  return types[status] || 'info';
};

const getStatusText = (status) => {
  const texts = {
    'pending': '待处理',
    'in_progress': '进行中',
    'completed': '已完成',
    'paid': '已支付',
    'cancelled': '已取消'
  };
  return texts[status] || status;
};

const formatTime = (time) => {
  return time ? dayjs(time).format('YYYY-MM-DD HH:mm') : '-';
};

const fetchOrders = async () => {
  loading.value.available = true;
  try {
    const res = await getAvailableOrders();
    if (res.data.success) {
      orders.value = res.data.data.orders;
    } else {
      ElMessage.error('获取可接订单失败');
    }
  } catch (error) {
    ElMessage.error('获取可接订单出错');
  } finally {
    loading.value.available = false;
  }
};

const fetchCurrentAssignments = async () => {
  loading.value.current = true;
  try {
    const res1 = await getMyOrders({ status: 'assigned' });
    let orderList = [];
    if (res1.data.success) {
      orderList = (res1.data.data.orders || [])
        .filter(o => o.order_status !== 'completed' && o.order_status !== 'paid')
        .map(o => ({
          ...o,
          type: 'order',
          description: o.order_type,
          bid_deadline: '',
          participants_count: '',
        }));
    }
    const res2 = await getStaffAvailableTasks();
    let groupList = [];
    if (res2.data.success) {
      groupList = (res2.data.data.tasks || []).filter(t => t.type === 'group_task' && t.status === 'assigned');
    }
    currentAssignments.value = [...orderList, ...groupList];
  } catch (e) {
    currentAssignments.value = [];
    ElMessage.error('获取当前接单失败');
  } finally {
    loading.value.current = false;
  }
};

const handleAccept = async (row) => {
  loading.value.accept = row.order_id;
  try {
    const res = await acceptOrder(row.order_id);
    if (res.data.success) {
      ElMessage.success('接单成功');
      await Promise.all([
        fetchOrders(),
        fetchCurrentAssignments()
      ]);
    } else {
      ElMessage.error(res.data.message || '接单失败');
    }
  } catch (error) {
    ElMessage.error('操作失败');
  } finally {
    loading.value.accept = null;
  }
};

const handleComplete = async (row) => {
  loading.value.complete = row.order_id;
  try {
    const res = await completeOrder(row.order_id);
    if (res.data.success) {
      ElMessage.success('订单已完成');
      await Promise.all([
        fetchCurrentAssignments(),
        getCompletedOrders()
      ]);
    } else {
      ElMessage.error(res.data.message || '完成订单失败');
    }
  } catch (error) {
    ElMessage.error('操作失败');
  } finally {
    loading.value.complete = null;
  }
};

const getCompletedOrders = async () => {
  loading.value.completed = true;
  try {
    const res = await getStaffAllOrders({ 
      status: 'completed',
      page: 1,
      per_page: 50
    });

    if (!res.data.success) {
      throw new Error(res.data.message || '获取订单失败');
    }

    const allOrders = res.data.data.orders || [];

    for (const order of allOrders) {
      try {
        const repRes = await getOrderReputation(order.order_id);
        const rep = repRes.data.data;
        if (rep && rep.client_to_staff) {
          order.reviewed = true;
          order.review_score = rep.client_to_staff.score;
        } else {
          order.reviewed = false;
          order.review_score = null;
        }
      } catch (e) {
        order.reviewed = false;
        order.review_score = null;
      }
    }

    allOrders.sort((a, b) => new Date(b.creation_time) - new Date(a.creation_time));
    completedOrders.value = allOrders;
  } catch (error) {
    ElMessage.error('获取已完成订单失败');
    completedOrders.value = [];
  } finally {
    loading.value.completed = false;
  }
};

const showOrderDetail = (row) => {
  if (!row.order_id) {
    ElMessage.error('订单ID不存在');
    return;
  }
  router.push(`/orders/${row.order_id}`);
};

onMounted(() => {
  Promise.all([
    fetchOrders(),
    fetchCurrentAssignments(),
    getCompletedOrders()
  ]);
});
</script>

<style scoped>
.available-orders-page {
  min-height: 100%;
}

.order-card {
  background-color: white;
  border-radius: 8px;
}

.section {
  margin-bottom: 32px;
}

.section:last-child {
  margin-bottom: 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.address-cell,
.time-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.time-estimate {
  display: flex;
  align-items: center;
}

:deep(.el-table) {
  --el-table-border-color: var(--border-color);
  --el-table-header-bg-color: #f8fafc;
}

:deep(.el-table th) {
  font-weight: 600;
}

@media (max-width: 768px) {
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .section-header .el-button {
    width: 100%;
  }
}
</style>