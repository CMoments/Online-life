<template>
  <div class="page-container">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <el-button @click="goBack" class="back-button">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2 class="page-title">订单详情</h2>
      </div>
      <div class="header-right">
        <el-button
          type="danger"
          v-if="isClient && orderDetail.order_status === 'pending'"
          @click="cancelOrderHandler"
          :loading="loading.cancel"
        >
          <el-icon><Close /></el-icon>
          取消订单
        </el-button>
        <el-button
          type="success"
          v-if="isClient && orderDetail.order_status === 'completed'"
          @click="showPayDialog = true"
          :loading="loading.pay"
        >
          <el-icon><Wallet /></el-icon>
          支付订单
        </el-button>
        <el-button
          type="primary"
          v-if="isClient && showReviewButton"
          @click="openReviewDialog"
          :loading="loading.review"
        >
          <el-icon><Star /></el-icon>
          评价
        </el-button>
      </div>
    </div>

    <el-row :gutter="20">
      <!-- Order Info -->
      <el-col :xs="24" :sm="24" :md="16">
        <el-card class="detail-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <h3>基本信息</h3>
              <el-tag
                :type="getStatusType(orderDetail.order_status)"
                :effect="orderDetail.order_status === 'in_progress' ? 'dark' : 'light'"
                size="large"
                class="status-tag"
              >
                {{ getStatusText(orderDetail.order_status) }}
              </el-tag>
            </div>
          </template>

          <div class="info-grid">
            <div class="info-item">
              <span class="label">订单ID</span>
              <span class="value">
                <el-tag size="small" effect="plain">{{ orderDetail.order_id }}</el-tag>
              </span>
            </div>
            <div class="info-item">
              <span class="label">订单类型</span>
              <span class="value">
                <el-tag size="small" type="info">{{ orderDetail.order_type }}</el-tag>
              </span>
            </div>
            <div class="info-item full-width">
              <span class="label">商家地址</span>
              <span class="value address">
                <el-icon><Location /></el-icon>
                {{ orderDetail.shop_address || '-' }}
              </span>
            </div>
            <div class="info-item full-width">
              <span class="label">收货地址</span>
              <span class="value address">
                <el-icon><Location /></el-icon>
                {{ orderDetail.order_location }}
              </span>
            </div>
            <div class="info-item">
              <span class="label">创建时间</span>
              <span class="value time">
                <el-icon><Calendar /></el-icon>
                {{ formatTime(orderDetail.creation_time) }}
              </span>
            </div>
            <div class="info-item">
              <span class="label">完成时间</span>
              <span class="value time">
                <el-icon><Timer /></el-icon>
                {{ orderDetail.completion_time ? formatTime(orderDetail.completion_time) : '-' }}
              </span>
            </div>
            <div class="info-item">
              <span class="label">分配状态</span>
              <span class="value">
                <el-tag
                  :type="getAssignmentStatusType(orderDetail.assignment_status)"
                  size="small"
                  effect="light"
                >
                  {{ getAssignmentStatusText(orderDetail.assignment_status) }}
                </el-tag>
              </span>
            </div>
            <div class="info-item">
              <span class="label">分配类型</span>
              <span class="value">
                <el-tag size="small" type="info" effect="light">
                  {{ orderDetail.assignment_type }}
                </el-tag>
              </span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- User Info -->
      <el-col :xs="24" :sm="24" :md="8">
        <el-card class="detail-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <h3>用户信息</h3>
            </div>
          </template>

          <div class="user-info">
            <div class="info-item">
              <span class="label">客户ID</span>
              <span class="value">
                <el-tag size="small" effect="plain">
                  {{ orderDetail.client_id || orderDetail.user_id }}
                </el-tag>
              </span>
            </div>
            <div class="info-item">
              <span class="label">客户名</span>
              <span class="value">{{ orderDetail.client_name || orderDetail.user_name }}</span>
            </div>
            <div class="info-item" v-if="isClient">
              <span class="label">可用积分</span>
              <span class="value points">{{ points }}</span>
            </div>
            <div class="info-item" v-if="staffId">
              <span class="label">配送员ID</span>
              <span class="value">
                <el-tag size="small" effect="plain">{{ staffId }}</el-tag>
              </span>
            </div>
            <div class="info-item" v-if="staffId">
              <span class="label">配送员评分</span>
              <span class="value">
                <el-rate
                  v-model="reputationAvg"
                  :max="5"
                  :colors="['#F7BA2A', '#F7BA2A', '#F7BA2A']"
                  disabled
                  show-score
                  text-color="#ff9900"
                  score-template="{value}"
                />
              </span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Payment Dialog -->
    <el-dialog
      v-model="showPayDialog"
      title="选择支付方式"
      width="400px"
      destroy-on-close
      :close-on-click-modal="false"
    >
      <el-form :model="paymentForm" label-width="100px">
        <el-form-item label="支付方式">
          <el-select
            v-model="payMethod"
            placeholder="请选择"
            style="width: 100%"
            @change="onPaymentMethodChange"
          >
            <el-option label="积分支付" value="points">
              <el-icon><Coin /></el-icon>
              <span>积分支付</span>
            </el-option>
            <el-option label="支付宝" value="alipay">
              <el-icon><Money /></el-icon>
              <span>支付宝</span>
            </el-option>
            <el-option label="微信支付" value="wechat">
              <el-icon><ChatDotRound /></el-icon>
              <span>微信支付</span>
            </el-option>
            <el-option label="银行卡" value="bank_card">
              <el-icon><CreditCard /></el-icon>
              <span>银行卡</span>
            </el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="支付金额">
          <el-input-number
            v-model="payAmount"
            :min="0"
            :precision="2"
            :step="0.01"
            style="width: 100%"
            :disabled="payMethod === 'points' || amountFixed"
          />
        </el-form-item>

        <div v-if="payMethod === 'points' && pointsInfo" class="points-info">
          <el-alert
            :title="pointsInfo.points_payment_available ? `可用积分：${pointsInfo.available_points}，最大可抵扣：${pointsInfo.max_deductible_amount}元` : pointsInfo.reason"
            :type="pointsInfo.points_payment_available ? 'success' : 'error'"
            :closable="false"
            show-icon
          />
        </div>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showPayDialog = false">取消</el-button>
          <el-button
            type="primary"
            :disabled="!payMethod || (payMethod === 'points' && (!pointsInfo || !pointsInfo.points_payment_available))"
            :loading="loading.pay"
            @click="payOrderHandler"
          >
            确认支付
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- Review Dialog -->
    <el-dialog
      v-model="reviewDialogVisible"
      title="订单评价"
      width="400px"
      destroy-on-close
      :close-on-click-modal="false"
    >
      <el-form :model="reviewForm" label-width="80px">
        <el-form-item label="信誉分">
          <el-rate
            v-model="reviewForm.score"
            :max="5"
            :colors="['#F7BA2A', '#F7BA2A', '#F7BA2A']"
            show-score
            text-color="#ff9900"
            score-template="{value}"
            style="margin-top: 8px"
          />
        </el-form-item>
        <el-form-item label="评价内容" required>
          <el-input
            v-model="reviewForm.review"
            type="textarea"
            :rows="4"
            placeholder="请输入您的评价内容..."
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="reviewDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="loading.review"
            @click="submitReview"
          >
            提交评价
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { getOrderDetail, cancelOrder, processPayment, reviewOrder, getOrderPointsInfo } from '@/api/order';
import { getPoints, addOrderReputation, getReputation, getOrderReputation } from '@/api/user';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import {
  ArrowLeft,
  Close,
  Wallet,
  Star,
  Location,
  Calendar,
  Timer,
  Money,
  ChatDotRound,
  CreditCard,
  Coin
} from '@element-plus/icons-vue';

const route = useRoute();
const router = useRouter();
const orderId = route.params.orderId;

const orderDetail = ref({});
const points = ref(0);
const loading = ref({
  detail: false,
  cancel: false,
  pay: false,
  review: false
});

// Payment related
const showPayDialog = ref(false);
const payMethod = ref('');
const payAmount = ref(0);
const amountFixed = ref(true);
const pointsInfo = ref(null);

// Review related
const reviewDialogVisible = ref(false);
const reviewForm = ref({
  score: 5,
  review: ''
});
const staffId = ref('');
const reputationAvg = ref(0);
const showReviewButton = ref(false);

// 判断当前用户是否是客户
const isClient = computed(() => {
  return localStorage.getItem('role') === 'client';
});

const getStatusType = (status) => {
  const types = {
    'pending': 'warning',
    'in_progress': 'primary',
    'completed': 'success',
    'cancelled': 'danger',
    'paid': 'info'
  };
  return types[status] || 'info';
};

const getStatusText = (status) => {
  const texts = {
    'pending': '待处理',
    'in_progress': '进行中',
    'completed': '已完成',
    'cancelled': '已取消',
    'paid': '已支付'
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
  if (!time) return '-';
  const date = new Date(time);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const fetchPoints = async () => {
  try {
    const res = await getPoints();
    if (res.data.success) {
      points.value = res.data.data.available_points;
    }
  } catch (error) {
    console.error('积分查询失败:', error);
  }
};

const fetchOrderDetail = async () => {
  loading.value.detail = true;
  try {
    if (!orderId) {
      ElMessage.error('订单ID不存在');
      router.push('/orders');
      return;
    }
    const res = await getOrderDetail(orderId);
    if (res.data.success) {
      orderDetail.value = res.data.data || {};
      staffId.value = orderDetail.value.staff_id || orderDetail.value.StaffID || orderDetail.value.staffId;
      
      if (orderDetail.value.can_review !== undefined) {
        showReviewButton.value = orderDetail.value.can_review;
      } else {
        const repRes = await getOrderReputation(orderId);
        showReviewButton.value = !repRes.data.data || !repRes.data.data.client_to_staff;
      }
      
      await Promise.all([
        fetchPoints(),
        fetchReputation()
      ]);
    } else {
      ElMessage.error(res.data.message || '获取订单详情失败');
    }
  } catch (error) {
    ElMessage.error('订单详情加载失败');
  } finally {
    loading.value.detail = false;
  }
};

const cancelOrderHandler = async () => {
  loading.value.cancel = true;
  try {
    const res = await cancelOrder(orderDetail.value.order_id);
    if (res.data.success) {
      ElMessage.success('订单已取消');
      fetchOrderDetail();
    } else {
      ElMessage.error(res.data.message || '取消订单失败');
    }
  } catch (error) {
    ElMessage.error('取消订单失败');
  } finally {
    loading.value.cancel = false;
  }
};

const onPaymentMethodChange = async (val) => {
  if (val === 'points') {
    try {
      const res = await getOrderPointsInfo(orderDetail.value.order_id);
      if (res.data && res.data.data) {
        pointsInfo.value = res.data.data;
        if (pointsInfo.value.points_payment_available) {
          payAmount.value = pointsInfo.value.max_deductible_amount;
        } else {
          payAmount.value = 0;
        }
      }
    } catch (e) {
      pointsInfo.value = null;
      payAmount.value = 0;
    }
    amountFixed.value = true;
  } else {
    pointsInfo.value = null;
    payAmount.value = orderDetail.value.amount || orderDetail.value.total_amount || 1;
    amountFixed.value = true;
  }
};

const payOrderHandler = async () => {
  if (!payMethod.value) {
    ElMessage.warning('请选择支付方式');
    return;
  }
  if (payMethod.value === 'points' && (!pointsInfo.value || !pointsInfo.value.points_payment_available)) {
    ElMessage.error(pointsInfo.value ? pointsInfo.value.reason : '积分支付不可用');
    return;
  }

  loading.value.pay = true;
  try {
    const res = await processPayment(orderDetail.value.order_id, {
      payment_method: payMethod.value,
      amount: payAmount.value
    });
    if (res.data.success) {
      ElMessage.success('支付成功');
      showPayDialog.value = false;
      await Promise.all([
        fetchOrderDetail(),
        fetchPoints()
      ]);
    } else {
      ElMessage.error(res.data.message || '支付失败');
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '支付失败');
  } finally {
    loading.value.pay = false;
  }
};

const fetchReputation = async () => {
  if (!staffId.value) return;
  try {
    const res = await getReputation(staffId.value);
    reputationAvg.value = res.data.data.average_score || 0;
  } catch (error) {
    console.error('获取信誉分失败:', error);
  }
};

const submitReview = async () => {
  if (!reviewForm.value.review) {
    ElMessage.warning('请输入评价内容');
    return;
  }

  loading.value.review = true;
  try {
    await addOrderReputation(orderId, {
      target_user_id: staffId.value,
      score: reviewForm.value.score,
      review: reviewForm.value.review
    });
    ElMessage.success('评价成功');
    reviewDialogVisible.value = false;
    await fetchOrderDetail();
  } catch (error) {
    ElMessage.error('评价失败');
  } finally {
    loading.value.review = false;
  }
};

const goBack = () => {
  const role = localStorage.getItem('role');
  if (role === 'staff') {
    router.push('/available-orders');
  } else {
    router.push('/orders');
  }
};

onMounted(() => {
  fetchOrderDetail();
});
</script>

<style scoped>
.page-container {
  padding: 20px;
  min-height: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-right {
  display: flex;
  gap: 12px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.detail-card {
  margin-bottom: 20px;
  border-radius: 8px;
  transition: all 0.3s;
}

.detail-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item.full-width {
  grid-column: span 2;
}

.label {
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.value {
  font-size: 15px;
  color: var(--el-text-color-primary);
}

.value.address,
.value.time {
  display: flex;
  align-items: center;
  gap: 8px;
}

.value.points {
  color: var(--el-color-primary);
  font-weight: 600;
  font-size: 24px;
}

.status-tag {
  font-size: 14px;
  padding: 8px 16px;
}

.points-info {
  margin: 16px 0;
}

:deep(.el-select-dropdown__item) {
  display: flex;
  align-items: center;
  gap: 8px;
}

:deep(.el-rate) {
  margin-top: -4px;
}

@media (max-width: 768px) {
  .page-container {
    padding: 12px;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .header-left {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .header-right {
    flex-direction: column;
  }

  .header-right .el-button {
    width: 100%;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .info-item.full-width {
    grid-column: auto;
  }

  .back-button {
    width: 100%;
  }
}
</style>