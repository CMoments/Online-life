<template>
    <el-card>
      <h2>订单详情</h2>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="订单ID">{{ detail.order_id }}</el-descriptions-item>
        <el-descriptions-item label="类型">{{ detail.order_type }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ detail.order_status }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ detail.creation_time }}</el-descriptions-item>
        <el-descriptions-item label="任务描述">{{ detail.description }}</el-descriptions-item>
      </el-descriptions>
      <el-button type="primary" @click="payOrder" v-if="detail.order_status==='待支付'">支付</el-button>
      <el-button type="success" @click="completeOrder" v-if="detail.order_status==='进行中'">完成订单</el-button>
    </el-card>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue';
  import { getOrderDetail, processPayment, completeOrder } from '@/api/order';
  import { useRoute } from 'vue-router';
  
  const route = useRoute();
  const detail = ref({});
  
  const fetchDetail = async () => {
    const res = await getOrderDetail(route.params.id);
    if (res.data.code === 0) {
      detail.value = res.data.data;
    }
  };
  
  const payOrder = async () => {
    const res = await processPayment(detail.value.order_id, { payment_method: '余额', amount: detail.value.amount });
    if (res.data.code === 0) {
      ElMessage.success('支付成功');
      fetchDetail();
    } else {
      ElMessage.error(res.data.message);
    }
  };
  
  const completeOrderHandler = async () => {
    const res = await completeOrder(detail.value.order_id);
    if (res.data.code === 0) {
      ElMessage.success('订单已完成');
      fetchDetail();
    } else {
      ElMessage.error(res.data.message);
    }
  };
  
  onMounted(fetchDetail);
  </script>