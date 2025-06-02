<template>
  <el-card>
    <h2>我的竞标记录</h2>
    <el-table :data="bids" style="width: 100%">
      <el-table-column prop="bid_id" label="竞标ID" width="100" />
      <el-table-column prop="task_id" label="任务ID" width="100" />
      <el-table-column prop="description" label="描述" />
      <el-table-column prop="bid_status" label="状态" />
      <el-table-column prop="bid_time" label="竞标时间" />
      <el-table-column prop="bid_deadline" label="截止时间" />
      <el-table-column prop="is_current_bidder" label="是否中标">
        <template #default="scope">
          <el-tag v-if="scope.row.is_current_bidder" type="success">中标</el-tag>
          <el-tag v-else type="info">未中标</el-tag>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      v-model:current-page="page"
      :page-size="perPage"
      :total="total"
      @current-change="fetchBids"
      layout="prev, pager, next"
      style="margin-top: 20px;"
    />
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getMyBids } from '@/api/task';
import { ElMessage } from 'element-plus';

const bids = ref([]);
const page = ref(1);
const perPage = ref(10);
const total = ref(0);

const fetchBids = async () => {
  try {
    const res = await getMyBids({ page: page.value, per_page: perPage.value });
    if (res.data.success || res.data.code === 0) {
      const data = res.data.data;
      bids.value = data.bids || data.items || [];
      total.value = data.total_records || data.total || 0;
    } else {
      ElMessage.error(res.data.message || '获取竞标记录失败');
    }
  } catch (e) {
    ElMessage.error('获取竞标记录失败');
  }
};

onMounted(fetchBids);
</script> 