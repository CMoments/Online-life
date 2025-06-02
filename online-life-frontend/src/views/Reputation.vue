<template>
  <el-card>
    <h2>我的信誉</h2>
    <el-descriptions :column="1" border>
      <el-descriptions-item label="平均分">
        {{ reputationData.average_score || 0 }}
      </el-descriptions-item>
      <el-descriptions-item label="总评价数">
        {{ reputationData.total_reviews || 0 }}
      </el-descriptions-item>
    </el-descriptions>

    <h3 style="margin-top: 20px;">最近评价</h3>
    <el-table :data="reputationData.recent_reviews || []" style="width: 100%">
      <el-table-column prop="score" label="分数" />
      <el-table-column prop="review" label="评价" />
      <el-table-column prop="reviewer" label="评价人" />
    </el-table>

    <div v-if="reputationData.score_distribution && Object.keys(reputationData.score_distribution).length > 0">
      <h3 style="margin-top: 20px;">分数分布</h3>
      <el-descriptions :column="1" border>
        <el-descriptions-item v-for="(count, score) in reputationData.score_distribution" :key="score" :label="score + '分'">
          {{ count }}次
        </el-descriptions-item>
      </el-descriptions>
    </div>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getReputation } from '@/api/user';
import { ElMessage } from 'element-plus';

const reputationData = ref({
  average_score: 0,
  total_reviews: 0,
  recent_reviews: [],
  score_distribution: {}
});

const fetchReputation = async () => {
  try {
    console.log('开始获取信誉信息...');
    const res = await getReputation();
    console.log('信誉信息响应:', res.data);
    
    if (res.data.success) {
      reputationData.value = res.data.data;
      console.log('更新后的信誉数据:', reputationData.value);
    } else {
      console.error('获取信誉信息失败:', res.data.message);
      ElMessage.error(res.data.message || '获取信誉信息失败');
    }
  } catch (error) {
    console.error('获取信誉信息异常:', error);
    ElMessage.error('获取信誉信息失败，请检查网络连接');
  }
};

onMounted(() => {
  console.log('组件加载，开始获取信誉信息');
  fetchReputation();
});
</script>