<template>
    <el-card>
      <h2>我的订单</h2>
      <el-table :data="orders" style="width: 100%">
        <el-table-column prop="order_id" label="订单ID" width="120" />
        <el-table-column prop="order_type" label="类型" />
        <el-table-column prop="order_status" label="状态" />
        <el-table-column prop="creation_time" label="创建时间" />
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button size="small" @click="viewDetail(scope.row)">详情</el-button>
            <el-button size="small" type="danger" @click="cancelOrder(scope.row)" v-if="scope.row.order_status==='未完成'">取消</el-button>
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
  
  const orders = ref([]);
  const page = ref(1);
  const perPage = ref(10);
  const total = ref(0);
  const router = useRouter();
  
  const fetchOrders = async () => {
    const res = await getOrderList({ page: page.value, per_page: perPage.value });
    if (res.data.code === 0) {
      orders.value = res.data.data.items || [];
      total.value = res.data.data.total || 0;
    }
  };
  
  const viewDetail = (row) => {
    router.push(`/orders/${row.order_id}`);
  };
  
  const cancelOrderHandler = async (row) => {
    const res = await cancelOrder(row.order_id);
    if (res.data.code === 0) {
      ElMessage.success('订单已取消');
      fetchOrders();
    } else {
      ElMessage.error(res.data.message);
    }
  };
  
  onMounted(fetchOrders);
  </script>