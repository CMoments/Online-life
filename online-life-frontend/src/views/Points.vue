<template>
  <el-card>
    <h2>我的积分</h2>
    <el-descriptions :column="1" border>
      <el-descriptions-item label="当前积分">{{ balance.points_balance }}</el-descriptions-item>
    </el-descriptions>
    <el-divider />
    <h3>积分历史</h3>
    <el-table :data="history" style="width: 100%">
      <el-table-column prop="points_change" label="变动" />
      <el-table-column prop="transaction_type" label="类型" />
      <el-table-column prop="reason" label="原因" />
      <el-table-column prop="balance_after" label="变动后余额" />
      <el-table-column prop="created_at" label="时间" />
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
      <el-form-item label="目标用户名">
        <el-select
          v-model="transferForm.target_user_id"
          filterable
          remote
          reserve-keyword
          placeholder="请输入用户名"
          :remote-method="searchUser"
          :loading="userLoading"
          style="width: 220px;"
          placement="bottom-start"
          popper-class="force-dropdown-down"
          :popper-options="noFlipPopperOptions"
        >
          <el-option
            v-for="user in userOptions"
            :key="user.user_id"
            :label="user.username"
            :value="user.user_id"
          />
        </el-select>
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
import { getUserList } from '@/api/user';
import { ElMessage } from 'element-plus';

const balance = ref({});
const history = ref([]);
const page = ref(1);
const perPage = ref(10);
const total = ref(0);
const transferForm = ref({ target_user_id: '', points: '', message: '' });
const userOptions = ref([]);
const userLoading = ref(false);

// 禁止 el-select 下拉自动向上弹出
const noFlipPopperOptions = {
  modifiers: [
    {
      name: 'flip',
      enabled: false,
    },
  ],
};

const fetchBalance = async () => {
  const res = await getPointsBalance();
  if (res.data.success) {
    balance.value = {
      points_balance: res.data.data.points_balance,
      user_id: res.data.data.user_id
    };
  }
};

const fetchHistory = async () => {
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
};

const onTransfer = async () => {
  // 校验
  if (!transferForm.value.target_user_id) {
    ElMessage.error('请选择目标用户');
    return;
  }
  if (!transferForm.value.points || isNaN(Number(transferForm.value.points)) || Number(transferForm.value.points) <= 0) {
    ElMessage.error('请输入有效的积分数量');
    return;
  }
  // 确保 points 是整数
  const payload = {
    ...transferForm.value,
    points: parseInt(transferForm.value.points, 10)
  };
  const res = await transferPoints(payload);
  if (res.data.success) {
    ElMessage.success('转账成功');
    fetchBalance();
    fetchHistory();
  } else {
    ElMessage.error(res.data.message);
  }
};

const searchUser = async (query) => {
  if (!query) {
    userOptions.value = [];
    return;
  }
  userLoading.value = true;
  const res = await getUserList({ username: query });
  if (res.data && res.data.data) {
    userOptions.value = res.data.data;
  } else {
    userOptions.value = [];
  }
  userLoading.value = false;
};

onMounted(() => {
  fetchBalance();
  fetchHistory();
});
</script>

<style>
.force-dropdown-down .el-select-dropdown__wrap {
  max-height: 200px !important;
  overflow-y: auto !important;
}
</style>