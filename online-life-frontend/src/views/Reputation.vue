<template>
  <div class="reputation-page">
    <el-row :gutter="20">
      <el-col :xs="24" :sm="24" :md="8">
        <el-card class="reputation-card overview-card">
          <div class="reputation-header">
            <el-icon class="reputation-icon"><Star /></el-icon>
            <h2>我的信誉</h2>
          </div>
          <div class="reputation-value">
            {{ reputationData.average_score || 0 }}
          </div>
          <div class="reputation-subtitle">
            共 {{ reputationData.total_reviews || 0 }} 次评价
          </div>
        </el-card>

        <el-card class="reputation-card distribution-card" v-if="reputationData.score_distribution && Object.keys(reputationData.score_distribution).length > 0">
          <template #header>
            <div class="card-header">
              <h2>分数分布</h2>
            </div>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item 
              v-for="(count, score) in reputationData.score_distribution" 
              :key="score" 
              :label="score + '分'"
            >
              <div class="distribution-bar">
                <div class="bar-value">{{ count }}次</div>
                <div class="bar-wrapper">
                  <div 
                    class="bar-fill" 
                    :style="{ width: (count / Math.max(...Object.values(reputationData.score_distribution)) * 100) + '%' }"
                  ></div>
                </div>
              </div>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="24" :md="16">
        <el-card class="reputation-card">
          <template #header>
            <div class="card-header">
              <h2>最近评价</h2>
            </div>
          </template>
          <el-table 
            :data="reputationData.recent_reviews || []" 
            style="width: 100%"
            :empty-text="'暂无评价记录'"
          >
            <el-table-column prop="score" label="分数" width="100">
              <template #default="{ row }">
                <span class="score-value">{{ row.score }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="review" label="评价" min-width="200" show-overflow-tooltip />
            <el-table-column prop="reviewer" label="评价人" width="120" />
            <el-table-column prop="created_at" label="时间" width="180">
              <template #default="{ row }">
                <div class="time-cell">
                  <el-icon><Calendar /></el-icon>
                  <span>{{ formatTime(row.created_at) }}</span>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getReputation } from '@/api/user';
import { ElMessage } from 'element-plus';
import { Star, Calendar } from '@element-plus/icons-vue';
import dayjs from 'dayjs';

const reputationData = ref({
  average_score: 0,
  total_reviews: 0,
  recent_reviews: [],
  score_distribution: {}
});

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss');
};

const fetchReputation = async () => {
  try {
    const res = await getReputation();
    if (res.data.success) {
      reputationData.value = res.data.data;
    } else {
      ElMessage.error(res.data.message || '获取信誉信息失败');
    }
  } catch (error) {
    ElMessage.error('获取信誉信息失败，请检查网络连接');
  }
};

onMounted(() => {
  fetchReputation();
});
</script>

<style scoped>
.reputation-page {
  padding: 20px;
  min-height: 100%;
}

.reputation-card {
  margin-bottom: 20px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.reputation-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.reputation-card:last-child {
  margin-bottom: 0;
}

.overview-card {
  text-align: center;
  padding: 16px;
  background: linear-gradient(135deg, var(--el-color-primary-light-7), var(--el-color-primary-light-9));
}

.reputation-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 12px;
}

.reputation-icon {
  font-size: 28px;
  color: var(--el-color-primary);
  background: white;
  border-radius: 50%;
  padding: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.reputation-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--el-color-primary-dark-2);
}

.reputation-value {
  font-size: 42px;
  font-weight: 600;
  color: var(--el-color-primary-dark-2);
  margin: 16px 0;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
}

.reputation-subtitle {
  font-size: 14px;
  color: var(--el-color-primary-dark-2);
  opacity: 0.8;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px !important;
  border-bottom: 1px solid var(--el-border-color-lighter);
  background-color: var(--el-bg-color-page);
}

.card-header h2 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.distribution-card :deep(.el-descriptions__cell) {
  padding: 12px 16px;
}

.distribution-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.bar-value {
  min-width: 50px;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.bar-wrapper {
  flex: 1;
  height: 8px;
  background-color: var(--el-border-color-lighter);
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background-color: var(--el-color-primary);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.score-value {
  font-weight: 600;
  color: var(--el-color-primary);
}

.time-cell {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--el-text-color-secondary);
}

:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table th) {
  background-color: var(--el-bg-color-page);
  font-weight: 600;
}

@media (max-width: 768px) {
  .reputation-page {
    padding: 12px;
  }
  
  .reputation-card {
    margin-bottom: 16px;
  }
  
  .reputation-value {
    font-size: 36px;
  }
  
  .card-header {
    padding: 12px !important;
  }
  
  .distribution-card :deep(.el-descriptions__cell) {
    padding: 8px 12px;
  }
}
</style>