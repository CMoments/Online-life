<template>
  <div class="points-page">
    <el-row :gutter="20">
      <!-- Points Overview Card -->
      <el-col :xs="24" :sm="24" :md="8">
        <el-card class="points-card overview-card">
          <div class="points-header">
            <el-icon class="points-icon"><Wallet /></el-icon>
            <h2>我的积分</h2>
          </div>
          <div class="points-value">
            {{ balance.points_balance || 0 }}
          </div>
          <div class="points-actions">
            <el-button type="primary" @click="fetchBalance" :loading="loading.balance">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </el-card>
      </el-col>

      <!-- Transfer Card -->
      <el-col :xs="24" :sm="24" :md="16">
        <el-card class="points-card">
          <template #header>
            <div class="card-header">
              <h2>积分转账</h2>
            </div>
          </template>
          
          <el-form :model="transferForm" label-width="100px" :rules="transferRules" ref="transferFormRef">
            <el-form-item label="目标用户" prop="target_user_id">
              <el-select
                v-model="transferForm.target_user_id"
                filterable
                remote
                reserve-keyword
                placeholder="请输入用户名搜索"
                :remote-method="searchUser"
                :loading="loading.user"
                style="width: 100%"
                placement="bottom-start"
                popper-class="force-dropdown-down"
                :popper-options="noFlipPopperOptions"
              >
                <el-option
                  v-for="user in userOptions"
                  :key="user.user_id"
                  :label="user.username"
                  :value="user.user_id"
                >
                  <span style="float: left">{{ user.username }}</span>
                  <span style="float: right; color: var(--el-text-color-secondary); font-size: 13px">
                    ID: {{ user.user_id }}
                  </span>
                </el-option>
              </el-select>
            </el-form-item>
            
            <el-form-item label="转账积分" prop="points">
              <el-input-number 
                v-model="transferForm.points" 
                :min="1"
                :max="Math.max(1, balance.points_balance || 0)"
                style="width: 100%"
                placeholder="请输入转账积分数量"
                :disabled="!balance.points_balance"
                @change="(val) => transferForm.points = val ? Number(val) : null"
              />
            </el-form-item>
            
            <el-form-item label="转账说明" prop="message">
              <el-input 
                v-model="transferForm.message" 
                type="textarea" 
                placeholder="请输入转账说明（选填）"
                :rows="2"
              />
            </el-form-item>

            <el-form-item>
              <el-button 
                type="primary" 
                @click="onTransfer" 
                :loading="loading.transfer"
                :disabled="!transferForm.target_user_id || !transferForm.points"
              >
                确认转账
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- History Card -->
      <el-col :span="24">
        <el-card class="points-card">
          <template #header>
            <div class="card-header">
              <h2>积分历史</h2>
              <el-button type="primary" @click="fetchHistory" :loading="loading.history">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>
          
          <el-table 
            :data="history" 
            style="width: 100%"
            v-loading="loading.history"
            border
          >
            <el-table-column label="变动" width="120">
              <template #default="{ row }">
                <span :class="{ 
                  'points-increase': row.points_change > 0,
                  'points-decrease': row.points_change < 0 
                }">
                  {{ row.points_change > 0 ? '+' : '' }}{{ row.points_change }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="transaction_type" label="类型" width="120">
              <template #default="{ row }">
                <el-tag :type="getTransactionType(row.transaction_type)" size="small">
                  {{ getTransactionTypeText(row.transaction_type) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="reason" label="原因" min-width="200" show-overflow-tooltip />
            <el-table-column prop="balance_after" label="变动后余额" width="120" />
            <el-table-column prop="created_at" label="时间" width="180">
              <template #default="{ row }">
                <div class="time-cell">
                  <el-icon><Calendar /></el-icon>
                  <span>{{ formatTime(row.created_at) }}</span>
                </div>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination-container">
            <el-pagination
              v-model:current-page="page"
              :page-size="perPage"
              :total="total"
              @current-change="fetchHistory"
              layout="total, prev, pager, next"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getPointsBalance, getPointsHistory, transferPoints } from '@/api/points';
import { getUserList } from '@/api/user';
import { ElMessage } from 'element-plus';
import { Wallet, Refresh, Calendar } from '@element-plus/icons-vue';
import dayjs from 'dayjs';

const balance = ref({});
const history = ref([]);
const page = ref(1);
const perPage = ref(10);
const total = ref(0);
const transferFormRef = ref(null);
const transferForm = ref({
  target_user_id: '',
  points: null,
  message: ''
});
const userOptions = ref([]);

const loading = ref({
  balance: false,
  history: false,
  transfer: false,
  user: false
});

// Form validation rules
const transferRules = {
  target_user_id: [
    { required: true, message: '请选择目标用户', trigger: 'change' }
  ],
  points: [
    { required: true, message: '请输入转账积分数量', trigger: 'change' },
    { type: 'number', min: 1, message: '积分必须大于0', trigger: 'change' },
    { 
      validator: (rule, value, callback) => {
        if (value > (balance.value.points_balance || 0)) {
          callback(new Error('转账积分不能超过当前余额'));
        } else {
          callback();
        }
      },
      trigger: 'change'
    }
  ]
};

// 禁止 el-select 下拉自动向上弹出
const noFlipPopperOptions = {
  modifiers: [
    {
      name: 'flip',
      enabled: false,
    },
  ],
};

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss');
};

const getTransactionType = (type) => {
  const types = {
    'transfer_in': 'success',
    'transfer_out': 'danger',
    'order_payment': 'warning',
    'order_refund': 'info',
    'system_grant': 'primary'
  };
  return types[type] || 'info';
};

const getTransactionTypeText = (type) => {
  const texts = {
    'transfer_in': '转入',
    'transfer_out': '转出',
    'order_payment': '订单支付',
    'order_refund': '订单退款',
    'system_grant': '系统发放'
  };
  return texts[type] || type;
};

const fetchBalance = async () => {
  loading.value.balance = true;
  try {
    const res = await getPointsBalance();
    if (res.data.success) {
      balance.value = {
        points_balance: res.data.data.points_balance,
        user_id: res.data.data.user_id
      };
    }
  } catch (error) {
    ElMessage.error('获取积分余额失败');
  } finally {
    loading.value.balance = false;
  }
};

const fetchHistory = async () => {
  loading.value.history = true;
  try {
    const res = await getPointsHistory({ page: page.value, per_page: perPage.value });
    if (res.data.success) {
      history.value = res.data.data.records.map(item => ({
        points_change: item.points_change,
        transaction_type: item.transaction_type,
        reason: item.reason,
        balance_after: item.balance_after,
        created_at: item.created_at,
      }));
      total.value = res.data.data.total_records;
    }
  } catch (error) {
    ElMessage.error('获取积分历史失败');
  } finally {
    loading.value.history = false;
  }
};

const onTransfer = async () => {
  if (!transferFormRef.value) return;
  
  try {
    await transferFormRef.value.validate();
    
    loading.value.transfer = true;
    const payload = {
      target_user_id: transferForm.value.target_user_id,
      points: Number(transferForm.value.points),
      message: transferForm.value.message
    };
    
    const res = await transferPoints(payload);
    if (res.data.success) {
      ElMessage.success('转账成功');
      transferForm.value = { target_user_id: '', points: null, message: '' };
      await Promise.all([
        fetchBalance(),
        fetchHistory()
      ]);
    } else {
      ElMessage.error(res.data.message || '转账失败');
    }
  } catch (error) {
    if (error.message) {
      ElMessage.error(error.message);
    }
  } finally {
    loading.value.transfer = false;
  }
};

const searchUser = async (query) => {
  if (!query) {
    userOptions.value = [];
    return;
  }
  
  loading.value.user = true;
  try {
    const res = await getUserList({ username: query });
    if (res.data && res.data.data) {
      userOptions.value = res.data.data;
    } else {
      userOptions.value = [];
    }
  } catch (error) {
    ElMessage.error('搜索用户失败');
  } finally {
    loading.value.user = false;
  }
};

onMounted(() => {
  Promise.all([
    fetchBalance(),
    fetchHistory()
  ]);
});
</script>

<style scoped>
.points-page {
  padding: 20px;
  min-height: 100%;
}

.points-card {
  margin-bottom: 20px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  background: white;
}

.points-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

/* 积分概览卡片 */
.overview-card.points-card {
  text-align: center;
  padding: 16px;
  background: linear-gradient(135deg, 
    rgba(64, 158, 255, 0.8), /* Element UI 主色调 */
    rgba(100, 182, 255, 0.9)
  );
}

.overview-card .points-header h2,
.overview-card .points-value {
  color: #2c5282; /* 深蓝色 */
}

.overview-card .points-actions :deep(.el-button) {
  color: #2c5282;
  border: 1px solid rgba(64, 158, 255, 0.3);
  background: rgba(255, 255, 255, 0.9);
}

.overview-card .points-actions :deep(.el-button:hover) {
  background: white;
  border-color: #409eff;
}

/* 转账卡片 */
.el-row > .el-col:nth-child(2) .points-card {
  background: linear-gradient(135deg,
    rgba(103, 194, 58, 0.7), /* Element UI 成功色 */
    rgba(149, 212, 117, 0.8)
  );
}

.el-row > .el-col:nth-child(2) .points-card .card-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.95);
}

.el-row > .el-col:nth-child(2) .points-card .card-header h2 {
  color: #2c5282;
}

/* 历史记录卡片 */
.el-row > .el-col:last-child .points-card {
  background: linear-gradient(135deg,
    rgba(144, 147, 153, 0.4), /* Element UI 信息色 */
    rgba(200, 201, 204, 0.5)
  );
}

.el-row > .el-col:last-child .points-card .card-header {
  border-bottom: 1px solid rgba(144, 147, 153, 0.2);
  background: rgba(255, 255, 255, 0.95);
}

.el-row > .el-col:last-child .points-card .card-header h2 {
  color: #2c5282;
}

.el-row > .el-col:last-child .points-card .card-header :deep(.el-button) {
  color: #2c5282;
  border: 1px solid rgba(144, 147, 153, 0.3);
  background: rgba(255, 255, 255, 0.9);
}

.el-row > .el-col:last-child .points-card .card-header :deep(.el-button:hover) {
  color: #409eff;
  border-color: #409eff;
  background: white;
}

.points-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 12px;
}

.points-icon {
  font-size: 28px;
  color: #409eff;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 50%;
  padding: 8px;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
}

.points-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.points-value {
  font-size: 42px;
  font-weight: 600;
  margin: 16px 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px !important;
}

.card-header h2 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

/* 表单样式 */
:deep(.el-form) {
  background: rgba(255, 255, 255, 0.95);
  padding: 20px;
  border-radius: 8px;
  margin: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
}

/* 表格样式 */
:deep(.el-table) {
  background: rgba(255, 255, 255, 0.95) !important;
  margin: 16px;
  border-radius: 8px;
}

:deep(.el-table th) {
  background-color: rgba(245, 247, 250, 0.9) !important;
  font-weight: 600;
}

:deep(.el-table td) {
  background-color: transparent !important;
}

:deep(.el-pagination) {
  background: rgba(255, 255, 255, 0.95);
  padding: 12px;
  margin: 16px;
  border-radius: 8px;
}

/* 积分变动样式 */
.points-increase {
  color: #67c23a;
  font-weight: 600;
}

.points-decrease {
  color: #f56c6c;
  font-weight: 600;
}

.time-cell {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #909399;
}

.pagination-container {
  margin-top: 16px;
  padding-top: 16px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

@media (max-width: 768px) {
  .points-page {
    padding: 12px;
  }
  
  .points-card {
    margin-bottom: 16px;
  }
  
  .points-value {
    font-size: 36px;
  }
  
  .card-header {
    padding: 12px !important;
  }
  
  :deep(.el-form),
  :deep(.el-table),
  :deep(.el-pagination) {
    margin: 12px;
  }
}
</style>