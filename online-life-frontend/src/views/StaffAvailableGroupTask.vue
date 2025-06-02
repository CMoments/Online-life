<template>
  <el-card>
    <h2>可竞标团办任务</h2>
    <el-table :data="tasks" style="width: 100%">
      <el-table-column prop="task_id" label="任务ID" />
      <el-table-column prop="description" label="描述" />
      <el-table-column prop="participants_count" label="参与人数" />
      <el-table-column prop="status" label="状态" />
      <el-table-column prop="bid_deadline" label="竞标截止" />
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="small" @click="handleBid(scope.row.task_id)">竞标</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getStaffAvailableTasks, bidStaffTask } from '@/api/task';
import { ElMessage } from 'element-plus';

const tasks = ref([]);

const fetchTasks = async () => {
  const res = await getStaffAvailableTasks();
  if (res.data.success) {
    const rawTasks = res.data.data.tasks || res.data.data;
    console.log('后端返回的tasks:', rawTasks);
    tasks.value = rawTasks.map(task => ({
      ...task,
      participants_count: task.participants_count ?? task.participant_count ?? 0
    }));
    console.log('前端处理后的tasks:', tasks.value);
  } else {
    ElMessage.error(res.data.message || '获取可竞标任务失败');
  }
};

const handleBid = async (taskId) => {
  try {
    const res = await bidStaffTask(taskId);
    console.log('竞标响应:', res);
    if (res.data && res.data.success) {
      ElMessage.success('竞标成功');
      fetchTasks();
    } else {
      // 直接弹出后端 message 字段
      const msg = res.data?.message || '竞标失败';
      ElMessage.error(msg);
    }
  } catch (e) {
    console.log('竞标异常:', e);
    console.log('竞标异常 response.data:', e?.response?.data);
    const msg = e?.response?.data?.message || e?.message || '竞标失败';
    ElMessage.error(msg);
  }
};

onMounted(fetchTasks);
</script> 