<template>
  <el-card>
    <h2>订单详情</h2>
    <el-descriptions :column="1" border>
      <el-descriptions-item label="订单ID">{{ orderDetail.order_id }}</el-descriptions-item>
      <el-descriptions-item label="类型">{{ orderDetail.order_type }}</el-descriptions-item>
      <el-descriptions-item label="状态">{{ orderDetail.order_status }}</el-descriptions-item>
      <el-descriptions-item label="地址">
        {{ orderDetail.shop_address ? orderDetail.shop_address + ' - ' : '' }}{{ orderDetail.order_location }}
      </el-descriptions-item>
      <el-descriptions-item label="创建时间">{{ orderDetail.creation_time }}</el-descriptions-item>
      <el-descriptions-item label="完成时间">{{ orderDetail.completion_time || '未完成' }}</el-descriptions-item>
      <el-descriptions-item label="分配状态">{{ orderDetail.assignment_status }}</el-descriptions-item>
      <el-descriptions-item label="分配类型">{{ orderDetail.assignment_type }}</el-descriptions-item>
      <el-descriptions-item label="客户ID">{{ orderDetail.client_id || orderDetail.user_id }}</el-descriptions-item>
      <el-descriptions-item label="客户名">{{ orderDetail.client_name || orderDetail.user_name }}</el-descriptions-item>
      <el-descriptions-item v-if="isClient" label="可用积分">{{ points }}</el-descriptions-item>
    </el-descriptions>
    <el-button type="primary" @click="goBack">返回</el-button>
    <el-button
      type="danger"
      v-if="isClient && orderDetail.order_status === 'pending'"
      @click="cancelOrderHandler"
    >
      取消订单
    </el-button>
    <el-button
      type="success"
      v-if="isClient && orderDetail.order_status === 'completed'"
      @click="showPayDialog = true"
    >
      支付订单
    </el-button>

    <!-- 支付方式选择弹窗 -->
    <el-dialog v-model="showPayDialog" title="选择支付方式" width="350px">
      <el-form>
        <el-form-item label="支付方式">
          <el-select v-model="payMethod" placeholder="请选择" @change="onPaymentMethodChange">
            <el-option label="积分" value="points" />
            <el-option label="支付宝" value="alipay" />
            <el-option label="微信" value="wechat" />
            <el-option label="银行卡" value="bank_card" />
          </el-select>
        </el-form-item>
        <el-form-item label="支付金额">
          <el-input v-model="payAmount" type="number" :disabled="payMethod === 'points' || amountFixed" />
        </el-form-item>
        <div v-if="payMethod === 'points' && pointsInfo">
          <el-alert
            :title="pointsInfo.points_payment_available ? `可用积分：${pointsInfo.available_points}，最大可抵扣：${pointsInfo.max_deductible_amount}元` : pointsInfo.reason"
            :type="pointsInfo.points_payment_available ? 'success' : 'error'"
            show-icon
          />
        </div>
      </el-form>
      <template #footer>
        <el-button @click="showPayDialog = false">取消</el-button>
        <el-button type="primary" :disabled="payMethod === 'points' && (!pointsInfo || !pointsInfo.points_payment_available)" @click="payOrderHandler">确认支付</el-button>
      </template>
    </el-dialog>

    <div>
      <el-button v-if="isClient && showReviewButton" type="primary" @click="openReviewDialog">评价</el-button>
    </div>

    <el-dialog v-model="reviewDialogVisible" title="订单评价" width="400px">
      <el-form :model="reviewForm">
        <el-form-item label="信誉分">
          <el-input-number v-model="reviewForm.score" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="评价内容">
          <el-input v-model="reviewForm.review" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reviewDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReview">提交</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { getOrderDetail, cancelOrder, processPayment, reviewOrder, getOrderPointsInfo } from '@/api/order';
import { getPoints, addOrderReputation, getReputation, getOrderReputation } from '@/api/user';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';

const orderDetail = ref({});
const review = ref({ rating: 0, comment: '' });
const points = ref(0);

const route = useRoute();
const router = useRouter();

const showPayDialog = ref(false);
const payMethod = ref('');
const payAmount = ref(0);
const amountFixed = ref(true);
const pointsInfo = ref(null);

const canReview = ref(false);
const reviewDialogVisible = ref(false);
const reviewForm = ref({ score: 80, review: '' });
const staffId = ref('');
const reputationAvg = ref(0);
const showReviewButton = ref(false);

// 判断当前用户是否是客户
const isClient = computed(() => {
  return localStorage.getItem('role') === 'client';
});

const orderId = route.params.orderId;

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
      console.log('订单详情', orderDetail.value);
      console.log('can_review', orderDetail.value.can_review);
      if (orderDetail.value.can_review !== undefined) {
        canReview.value = orderDetail.value.can_review;
      } else {
        const repRes = await getOrderReputation(orderId);
        console.log('订单评价记录', repRes.data.data);
        canReview.value = !repRes.data.data || repRes.data.data.length === 0;
      }
      fetchPoints();
      fetchReputation();
      if (orderDetail.value.order_status === 'paid') {
        const repRes = await getOrderReputation(orderId);
        const repData = repRes.data.data || {};
        showReviewButton.value = !repData.client_to_staff;
        console.log('order_status:', orderDetail.value.order_status, 'showReviewButton:', showReviewButton.value);
      } else {
        showReviewButton.value = false;
      }
    } else {
      ElMessage.error(res.data.message || '获取订单详情失败');
    }
  } catch (error) {
    console.error('订单详情接口调用失败:', error);
    ElMessage.error('订单详情加载失败，请检查网络或后端服务');
  }
};

const cancelOrderHandler = async () => {
  try {
    const res = await cancelOrder(orderDetail.value.order_id);
    if (res.data.success) {
      ElMessage.success('订单已取消');
      fetchOrderDetail();
    } else {
      ElMessage.error(res.data.message || '取消订单失败');
    }
  } catch (error) {
    console.error('取消订单接口调用失败:', error);
    ElMessage.error('取消订单失败，请检查网络或后端服务');
  }
};

const onPaymentMethodChange = async (val) => {
  if (val === 'points') {
    // 查询积分支付信息
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
  try {
    const res = await processPayment(orderDetail.value.order_id, {
      payment_method: payMethod.value,
      amount: payAmount.value
    });
    if (res.data.success) {
      ElMessage.success('支付成功');
      showPayDialog.value = false;
      fetchOrderDetail();
      fetchPoints();
    } else {
      ElMessage.error(res.data.message || '支付失败');
    }
  } catch (e) {
    if (e.response && e.response.data && e.response.data.message) {
      ElMessage.error(e.response.data.message);
    } else {
      ElMessage.error('支付失败');
    }
  }
};

const fetchReputation = async () => {
  if (!staffId.value) return;
  const res = await getReputation(staffId.value);
  reputationAvg.value = res.data.data.average_score || 0;
};

function openReviewDialog() {
  reviewDialogVisible.value = true;
}

async function submitReview() {
  // 确保 staffId 有值
  if (!staffId.value) {
    staffId.value = orderDetail.value.staff_id || orderDetail.value.StaffID || orderDetail.value.staffId;
  }
  if (!staffId.value) {
    ElMessage.error('无法获取被评价职员ID，无法提交评价');
    return;
  }
  if (!reviewForm.value.score || reviewForm.value.score < 1 || reviewForm.value.score > 100) {
    alert('请输入1-100的信誉分');
    return;
  }
  console.log('提交评价参数', {
    orderId,
    target_user_id: staffId.value,
    score: reviewForm.value.score,
    review: reviewForm.value.review
  });
  await addOrderReputation(orderId, {
    target_user_id: staffId.value,
    score: reviewForm.value.score,
    review: reviewForm.value.review
  });
  reviewDialogVisible.value = false;
  await fetchOrderDetail();
}

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