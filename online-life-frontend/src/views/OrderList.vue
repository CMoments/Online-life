<template>
  <el-card>
    <h2>我的订单列表</h2>
    <el-table :data="orders" style="width: 100%">
      <el-table-column prop="order_status" label="状态" />
      <el-table-column label="地址">
        <template #default="scope">
          {{ scope.row.shop_address ? scope.row.shop_address + ' - ' : '' }}{{ scope.row.order_location }}
        </template>
      </el-table-column>
      <el-table-column prop="creation_time" label="创建时间" />
      <el-table-column prop="completion_time" label="完成时间" />
      <el-table-column prop="assignment_status" label="分配状态" />
      <el-table-column prop="assignment_type" label="分配类型" />
      <el-table-column prop="estimated_time" label="预计时间(分钟)">
        <template #default="scope">
          <span v-if="scope.row.estimated_time">
            <span :style="{ color: scope.row.estimated_time_status === 'estimated' ? 'orange' : 'inherit' }">
              {{ Math.round(Number(scope.row.estimated_time) / 60) }}
              <span v-if="scope.row.estimated_time_status === 'estimated'">(默认)</span>
            </span>
          </span>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180">
        <template #default="scope">
          <el-button size="small" v-if="scope.row.order_status === 'pending'" @click="cancelOrderHandler(scope.row.order_id)">取消</el-button>
          <el-button size="small" v-if="scope.row.order_status === 'completed'" @click="payOrderHandler(scope.row.order_id)">支付</el-button>
          <el-button size="small" @click="viewDetail(scope.row.order_id)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      v-model:current-page="page"
      :page-size="perPage"
      :total="total"
      @current-change="fetchOrders"
      layout="prev, pager, next"
      style="margin-top: 20px;"
    />
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getOrderList, cancelOrder } from '@/api/order';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';

const orders = ref([]);
const page = ref(1);
const perPage = ref(10);
const total = ref(0);
const router = useRouter();

const fetchOrders = async () => {
  try {
    // 只获取订单列表
    const res = await getOrderList({ page: page.value, per_page: perPage.value });
    if (res.data.success) {
      orders.value = res.data.data.orders || [];
      total.value = res.data.data.pagination?.total || 0;
    }
  } catch (e) {
    ElMessage.error('获取订单失败');
  }
};

const cancelOrderHandler = async (orderId) => {
  const res = await cancelOrder(orderId);
  if (res.data.success) {
    ElMessage.success('订单已取消');
    fetchOrders();
  } else {
    ElMessage.error(res.data.message || '取消失败');
  }
};

const payOrderHandler = (orderId) => {
  // 跳转到支付页面或弹窗
  ElMessage.info('请在订单详情页支付');
  router.push(`/orders/${orderId}`);
};

const viewDetail = (orderId) => {
  router.push(`/orders/${orderId}`);
};

onMounted(fetchOrders);
</script>