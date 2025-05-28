<template>
    <el-card>
      <h2>我的积分</h2>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="当前积分">{{ balance.points_balance }}</el-descriptions-item>
      </el-descriptions>
      <el-divider />
      <h3>积分历史</h3>
      <el-table :data="history" style="width: 100%">
        <el-table-column prop="change" label="变动" />
        <el-table-column prop="reason" label="原因" />
        <el-table-column prop="time" label="时间" />
      </el-table>
      <el-pagination
        v-model:current-page="page"
        :page-size="perPage"
        :total="total"
        @current-change="fetchHistory"
        layout="prev, pager, next"
        style="margin-top: 20px;"
      />
      <el-divider />
      <h3>积分转账</h3>
      <el-form :model="transferForm" inline>
        <el-form-item label="目标用户ID">
          <el-input v-model="transferForm.target_user_id" />
        </el-form-item>
        <el-form-item label="积分">
          <el-input v-model="transferForm.points" type="number" />
        </el-form-item>
        <el-form-item label="留言">
          <el-input v-model="transferForm.message" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="onTransfer">转账</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue';
  import { getPointsBalance, getPointsHistory, transferPoints } from '@/api/points';
  
  const balance = ref({});
  const history = ref([]);
  const page = ref(1);
  const perPage = ref(10);
  const total = ref(0);
  const transferForm = ref({ target_user_id: '', points: '', message: '' });
  
  const fetchBalance = async () => {
    const res = await getPointsBalance();
    if (res.data.code === 0) {
      balance.value = res.data.data;
    }
  };
  
  const fetchHistory = async () => {
    const res = await getPointsHistory({ page: page.value, per_page: perPage.value });
    if (res.data.code === 0) {
      history.value = res.data.data.items || [];
      total.value = res.data.data.total || 0;
    }
  };
  
  const onTransfer = async () => {
    const res = await transferPoints(transferForm.value);
    if (res.data.code === 0) {
      ElMessage.success('转账成功');
      fetchBalance();
      fetchHistory();
    } else {
      ElMessage.error(res.data.message);
    }
  };
  
  onMounted(() => {
    fetchBalance();
    fetchHistory();
  });
  </script>