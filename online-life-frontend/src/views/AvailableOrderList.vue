<template>
  <el-card>
    <h2>可接单列表</h2>
    <el-table :data="orders" border>
      <el-table-column prop="client_name" label="客户" />
      <el-table-column label="地址">
        <template #default="{ row }">
          {{ row.shop_address || '' }} - {{ row.order_location }}
        </template>
      </el-table-column>
      <el-table-column prop="creation_time" label="创建时间" />
      <el-table-column prop="assignment_type" label="分配类型" />
      <el-table-column prop="order_status" label="订单状态" />
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="small" @click="handleAccept(scope.row)">接单</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增：当前接单列表 -->
    <h2 style="margin-top: 32px;">当前接单</h2>
    <el-table :data="currentAssignments" border>
      <el-table-column prop="type" label="类型">
        <template #default="scope">
          <el-tag v-if="scope.row.type === 'group_task'" type="success">团办</el-tag>
          <span v-else>普通</span>
        </template>
      </el-table-column>
      <el-table-column label="ID">
        <template #default="scope">
          <span v-if="scope.row.type === 'group_task'">{{ scope.row.task_id }}</span>
          <span v-else>{{ scope.row.order_id }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" />
      <el-table-column label="订单/任务地点">
        <template #default="scope">
          {{ scope.row.order_location || scope.row.task_location }}
        </template>
      </el-table-column>
      <el-table-column prop="creation_time" label="创建时间" />
      <el-table-column prop="bid_deadline" label="竞标截止" />
      <el-table-column prop="participants_count" label="参与人数" />
      <el-table-column prop="order_status" label="订单状态" />
      <el-table-column label="操作">
        <template #default="scope">
          <el-button
            v-if="scope.row.type === 'order' && scope.row.order_status === 'assigned'"
            size="small"
            type="primary"
            @click="handleComplete(scope.row)"
          >完成订单</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增：已完成订单列表 -->
    <h2 style="margin-top: 32px;">已完成订单</h2>
    <el-table :data="completedOrders" border>
      <el-table-column prop="order_status" label="状态">
        <template #default="{ row }">
          {{ row.order_status }}
        </template>
      </el-table-column>
      <el-table-column label="地址">
        <template #default="{ row }">
          {{ row.shop_address ? row.shop_address.replace(/^- /, '') : '' }} - {{ row.order_location }}
        </template>
      </el-table-column>
      <el-table-column prop="creation_time" label="创建时间" />
      <el-table-column prop="completion_time" label="完成时间" />
      <el-table-column prop="assignment_type" label="分配类型" />
      <el-table-column prop="estimated_time" label="预计时间(分钟)">
        <template #default="{ row }">
          {{ Math.floor((row.estimated_time || 0) / 60) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button 
            size="small" 
            @click="showOrderDetail(row)"
          >详情</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
  <ReviewDialog ref="reviewDialogRef" />
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
import ReviewDialog from './ReviewDialog.vue';

const router = useRouter();
const orders = ref([]);
const assignedGroupTasks = ref([]);
const currentAssignments = ref([]);
const completedOrders = ref([]);
const reviewDialogRef = ref();

const fetchOrders = async () => {
  try {
    const res = await getAvailableOrders();
    if (res.data.success) {
      orders.value = res.data.data.orders;
    } else {
      ElMessage.error('获取可接订单失败');
    }
  } catch (error) {
    ElMessage.error('获取可接订单出错');
  }
};

const fetchCurrentAssignments = async () => {
  try {
    // 获取当前staff所有assigned订单
    const res1 = await getMyOrders({ status: 'assigned' });
    let orderList = [];
    if (res1.data.success) {
      orderList = (res1.data.data.orders || [])
        .filter(o => o.order_status !== 'completed' && o.order_status !== 'paid') // 只显示未完成且未支付的
        .map(o => ({
          ...o,
          type: 'order',
          description: o.order_type,
          bid_deadline: '',
          participants_count: '',
        }));
    }
    // 获取assigned团办任务
    const res2 = await getStaffAvailableTasks();
    let groupList = [];
    if (res2.data.success) {
      groupList = (res2.data.data.tasks || []).filter(t => t.type === 'group_task' && t.status === 'assigned');
    }
    currentAssignments.value = [...orderList, ...groupList];
  } catch (e) {
    currentAssignments.value = [];
  }
};

const handleAccept = async (row) => {
  const res = await acceptOrder(row.order_id);
  if (res.data.success) {
    ElMessage.success('接单成功');
    fetchOrders();
    fetchCurrentAssignments();
  } else {
    ElMessage.error(res.data.message || '接单失败');
  }
};

const handleComplete = async (row) => {
  const res = await completeOrder(row.order_id);
  if (res.data.success) {
    ElMessage.success('订单已完成');
    fetchCurrentAssignments();
    getCompletedOrders(); // 完成订单后刷新已完成订单表格
  } else {
    ElMessage.error(res.data.message || '完成订单失败');
  }
};

const getCompletedOrders = async () => {
  try {
    console.log('开始获取已完成订单...');
    // 使用统一的API获取已完成和已支付的订单
    const res = await getStaffAllOrders({ 
      status: 'completed',  // 后端会处理completed和paid状态
      page: 1,
      per_page: 50
    });

    console.log('订单响应:', res.data);

    if (!res.data.success) {
      throw new Error(res.data.message || '获取订单失败');
    }

    const allOrders = res.data.data.orders || [];
    console.log('订单列表:', allOrders);

    // 处理每个订单的评价状态
    for (const order of allOrders) {
      try {
        const repRes = await getOrderReputation(order.order_id);
        console.log(`订单 ${order.order_id} 的评价信息:`, repRes.data);
        const rep = repRes.data.data;
        if (rep && rep.client_to_staff) {
          order.reviewed = true;
          order.review_score = rep.client_to_staff.score;
        } else {
          order.reviewed = false;
          order.review_score = null;
        }
      } catch (e) {
        console.error(`获取订单 ${order.order_id} 评价失败:`, e);
        order.reviewed = false;
        order.review_score = null;
      }
    }

    // 按创建时间倒序排序
    allOrders.sort((a, b) => new Date(b.creation_time) - new Date(a.creation_time));
    console.log('最终显示的订单列表:', allOrders);
    completedOrders.value = allOrders;
  } catch (error) {
    console.error('获取已完成订单失败:', error);
    ElMessage.error('获取已完成订单失败');
    completedOrders.value = [];
  }
};

async function openReviewDialog(order) {
  // 获取订单详情，拿到 staff 的 user_id
  const detail = await getOrderDetail(order.order_id);
  const staffUserId = detail.data.staff_id; // 你后端返回的字段
  reviewDialogRef.value.openReview(order, staffUserId);
}

const showOrderDetail = (row) => {
  // 跳转到订单详情页面
  if (!row.order_id) {
    ElMessage.error('订单ID不存在');
    return;
  }
  // 使用 order_id 字段
  const orderId = row.order_id || row.OrderID;
  router.push(`/orders/${orderId}`);
};

onMounted(() => {
  fetchOrders();
  fetchCurrentAssignments();
  getCompletedOrders();
});
</script>