<template>
  <div class="page-container">
    <!-- Statistics Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="12" :sm="12" :md="6">
        <el-card shadow="hover" class="stats-card">
          <template #header>
            <div class="stats-header">
              <el-icon class="stats-icon"><Document /></el-icon>
              <span>全部订单</span>
            </div>
          </template>
          <div class="stats-value">{{ total }}</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6">
        <el-card shadow="hover" class="stats-card pending">
          <template #header>
            <div class="stats-header">
              <el-icon class="stats-icon"><Timer /></el-icon>
              <span>待处理</span>
            </div>
          </template>
          <div class="stats-value">{{ stats.pending || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6">
        <el-card shadow="hover" class="stats-card in-progress">
          <template #header>
            <div class="stats-header">
              <el-icon class="stats-icon"><Loading /></el-icon>
              <span>进行中</span>
            </div>
          </template>
          <div class="stats-value">{{ stats.in_progress || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6">
        <el-card shadow="hover" class="stats-card completed">
          <template #header>
            <div class="stats-header">
              <el-icon class="stats-icon"><CircleCheck /></el-icon>
              <span>已完成</span>
            </div>
          </template>
          <div class="stats-value">{{ stats.completed || 0 }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Main Content -->
    <el-card class="order-card" shadow="never">
      <!-- Toolbar -->
      <div class="toolbar">
        <div class="left-tools">
          <el-button type="primary" @click="$router.push('/create-order')" class="create-btn">
            <el-icon><Plus /></el-icon>
            创建新订单
          </el-button>
          <el-button @click="fetchOrders" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
        <div class="right-tools">
          <el-input
            v-model="searchQuery"
            placeholder="搜索订单..."
            clearable
            @clear="onSearch"
            @input="onSearch"
            class="search-input"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select 
            v-model="filterStatus" 
            placeholder="订单状态" 
            clearable 
            @change="onFilterChange"
            class="filter-select"
          >
            <el-option label="待处理" value="pending" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </div>
      </div>

      <!-- Table -->
      <el-table 
        :data="filteredOrders" 
        style="width: 100%"
        :empty-text="loading ? '加载中...' : '暂无订单'"
        v-loading="loading"
        row-key="order_id"
        :default-sort="{ prop: 'creation_time', order: 'descending' }"
      >
        <el-table-column prop="order_status" label="状态" width="100" sortable>
          <template #default="scope">
            <el-tag
              :type="getStatusType(scope.row.order_status)"
              :effect="scope.row.order_status === 'in_progress' ? 'dark' : 'light'"
              size="small"
              class="status-tag"
            >
              {{ getStatusText(scope.row.order_status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="地址" min-width="280">
          <template #default="scope">
            <div class="address-cell">
              <el-icon><Location /></el-icon>
              <el-tooltip 
                :content="scope.row.shop_address ? scope.row.shop_address + ' → ' + scope.row.order_location : scope.row.order_location"
                placement="top"
              >
                <span class="address-text">
                  {{ scope.row.shop_address ? scope.row.shop_address + ' → ' : '' }}{{ scope.row.order_location }}
                </span>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="creation_time" label="创建时间" width="160" sortable>
          <template #default="scope">
            <div class="time-cell">
              <el-icon><Calendar /></el-icon>
              <span>{{ formatTime(scope.row.creation_time) }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="completion_time" label="完成时间" width="160" sortable>
          <template #default="scope">
            <div class="time-cell">
              <el-icon><Timer /></el-icon>
              <span>{{ scope.row.completion_time ? formatTime(scope.row.completion_time) : '-' }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="assignment_status" label="分配状态" width="120">
          <template #default="scope">
            <el-tag
              :type="getAssignmentStatusType(scope.row.assignment_status)"
              size="small"
              effect="light"
              class="assignment-tag"
            >
              {{ getAssignmentStatusText(scope.row.assignment_status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="estimated_time" label="预计时间" width="120">
          <template #default="scope">
            <div class="time-estimate" v-if="scope.row.estimated_time">
              <span :class="{ 'estimated': scope.row.estimated_time_status === 'estimated' }">
                {{ Math.round(Number(scope.row.estimated_time) / 60) }}分钟
                <el-tooltip
                  v-if="scope.row.estimated_time_status === 'estimated'"
                  content="这是系统预估的默认时间"
                  placement="top"
                >
                  <el-icon class="info-icon"><InfoFilled /></el-icon>
                </el-tooltip>
              </span>
            </div>
            <span v-else>-</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <div class="action-buttons">
              <el-button
                v-if="scope.row.order_status === 'pending'"
                type="danger"
                size="small"
                plain
                @click="cancelOrderHandler(scope.row.order_id)"
              >
                取消
              </el-button>
              <el-button
                v-if="scope.row.order_status === 'completed'"
                type="success"
                size="small"
                @click="payOrderHandler(scope.row.order_id)"
              >
                支付
              </el-button>
              <el-button
                type="primary"
                size="small"
                plain
                @click="viewDetail(scope.row.order_id)"
              >
                详情
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="page"
          :page-size="perPage"
          :total="total"
          @current-change="fetchOrders"
          layout="total, prev, pager, next, jumper"
          background
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { getOrderList, cancelOrder } from '@/api/order';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { 
  Plus, 
  Location, 
  Calendar, 
  Timer, 
  InfoFilled, 
  Document,
  Loading,
  CircleCheck,
  Search,
  Refresh
} from '@element-plus/icons-vue';
import dayjs from 'dayjs';

const router = useRouter();
const orders = ref([]);
const page = ref(1);
const perPage = ref(10);
const total = ref(0);
const loading = ref(false);
const searchQuery = ref('');
const filterStatus = ref('');

// 订单统计
const stats = ref({
  pending: 0,
  in_progress: 0,
  completed: 0,
  cancelled: 0
});

// 过滤后的订单列表
const filteredOrders = computed(() => {
  let result = orders.value;
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(order => 
      order.order_location?.toLowerCase().includes(query) ||
      order.shop_address?.toLowerCase().includes(query)
    );
  }
  
  if (filterStatus.value) {
    result = result.filter(order => order.order_status === filterStatus.value);
  }
  
  return result;
});

const getStatusType = (status) => {
  const types = {
    'pending': 'warning',
    'in_progress': 'primary',
    'completed': 'success',
    'cancelled': 'danger'
  };
  return types[status] || 'info';
};

const getStatusText = (status) => {
  const texts = {
    'pending': '待处理',
    'in_progress': '进行中',
    'completed': '已完成',
    'cancelled': '已取消'
  };
  return texts[status] || status;
};

const getAssignmentStatusType = (status) => {
  const types = {
    'unassigned': 'info',
    'assigned': 'success',
    'rejected': 'danger'
  };
  return types[status] || 'info';
};

const getAssignmentStatusText = (status) => {
  const texts = {
    'unassigned': '未分配',
    'assigned': '已分配',
    'rejected': '已拒绝'
  };
  return texts[status] || status;
};

const formatTime = (time) => {
  return time ? dayjs(time).format('YYYY-MM-DD HH:mm') : '-';
};

const updateStats = (orderList) => {
  const newStats = {
    pending: 0,
    in_progress: 0,
    completed: 0,
    cancelled: 0
  };
  
  orderList.forEach(order => {
    if (newStats[order.order_status] !== undefined) {
      newStats[order.order_status]++;
    }
  });
  
  stats.value = newStats;
};

const fetchOrders = async () => {
  loading.value = true;
  try {
    const res = await getOrderList({ page: page.value, per_page: perPage.value });
    if (res.data.success) {
      orders.value = res.data.data.orders || [];
      total.value = res.data.data.pagination?.total || 0;
      updateStats(orders.value);
    }
  } catch (e) {
    ElMessage.error('获取订单失败');
  } finally {
    loading.value = false;
  }
};

const cancelOrderHandler = async (orderId) => {
  try {
    const res = await cancelOrder(orderId);
    if (res.data.success) {
      ElMessage.success('订单已取消');
      fetchOrders();
    } else {
      ElMessage.error(res.data.message || '取消失败');
    }
  } catch (error) {
    ElMessage.error('操作失败');
  }
};

const payOrderHandler = (orderId) => {
  router.push(`/orders/${orderId}`);
};

const viewDetail = (orderId) => {
  router.push(`/orders/${orderId}`);
};

const onSearch = () => {
  // 使用防抖处理搜索
  if (window.searchTimeout) {
    clearTimeout(window.searchTimeout);
  }
  window.searchTimeout = setTimeout(() => {
    page.value = 1;
    fetchOrders();
  }, 300);
};

const onFilterChange = () => {
  page.value = 1;
  fetchOrders();
};

onMounted(fetchOrders);
</script>

<style scoped>
.page-container {
  padding: 20px;
  min-height: 100%;
}

.stats-row {
  margin-bottom: 24px;
}

.stats-card {
  height: 100%;
  transition: transform 0.3s;
}

.stats-card:hover {
  transform: translateY(-5px);
}

.stats-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  color: var(--el-text-color-regular);
}

.stats-icon {
  font-size: 20px;
}

.stats-value {
  font-size: 32px;
  font-weight: 600;
  color: var(--el-color-primary);
  margin-top: 8px;
}

.pending .stats-value {
  color: var(--el-color-warning);
}

.in-progress .stats-value {
  color: var(--el-color-primary);
}

.completed .stats-value {
  color: var(--el-color-success);
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 16px;
}

.left-tools,
.right-tools {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-input {
  width: 240px;
}

.filter-select {
  width: 120px;
}

.order-card {
  background-color: white;
  border-radius: 8px;
}

.address-cell,
.time-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.address-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.time-estimate {
  display: flex;
  align-items: center;
}

.estimated {
  color: var(--el-color-warning);
  display: flex;
  align-items: center;
  gap: 4px;
}

.info-icon {
  font-size: 14px;
  color: var(--el-color-info);
  cursor: help;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.pagination-container {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

.status-tag {
  min-width: 58px;
  text-align: center;
}

.assignment-tag {
  min-width: 58px;
  text-align: center;
}

:deep(.el-table) {
  --el-table-border-color: var(--border-color);
  --el-table-header-bg-color: #f8fafc;
  border-radius: 8px;
}

:deep(.el-table th) {
  font-weight: 600;
  background-color: #f8fafc;
}

:deep(.el-table .cell) {
  padding: 8px 12px;
}

:deep(.el-pagination.is-background .el-pager li:not(.is-disabled).is-active) {
  background-color: var(--el-color-primary);
}

@media (max-width: 768px) {
  .page-container {
    padding: 12px;
  }

  .stats-row {
    margin-bottom: 16px;
  }

  .stats-card {
    margin-bottom: 12px;
  }

  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .left-tools,
  .right-tools {
    flex-direction: column;
    width: 100%;
  }

  .search-input,
  .filter-select,
  .create-btn {
    width: 100%;
  }

  .action-buttons {
    flex-direction: column;
  }

  .action-buttons .el-button {
    width: 100%;
    margin-left: 0;
  }

  .el-table {
    font-size: 14px;
  }
}
</style>