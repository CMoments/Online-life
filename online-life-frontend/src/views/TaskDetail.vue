<template>
    <el-card>
      <h2>团办任务详情</h2>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="团办ID">{{ detail.group_task_id }}</el-descriptions-item>
        <el-descriptions-item label="类型">{{ detail.task_type }}</el-descriptions-item>
        <el-descriptions-item label="描述">{{ detail.description }}</el-descriptions-item>
        <el-descriptions-item label="参与用户">{{ detail.participating_user_id }}</el-descriptions-item>
        <el-descriptions-item label="加入时间">{{ detail.join_time }}</el-descriptions-item>
      </el-descriptions>
      <el-button type="primary" @click="joinTask" v-if="!detail.joined">参加任务</el-button>
      <el-button type="danger" @click="leaveTask" v-if="detail.joined">退出任务</el-button>
    </el-card>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue';
  import { getGroupTaskDetail, joinGroupTask, leaveGroupTask } from '@/api/task';
  import { useRoute } from 'vue-router';
  
  const route = useRoute();
  const detail = ref({});
  
  const fetchDetail = async () => {
    const res = await getGroupTaskDetail(route.params.id);
    if (res.data.code === 0) {
      detail.value = res.data.data;
    }
  };
  
  const joinTask = async () => {
    const res = await joinGroupTask(detail.value.group_task_id);
    if (res.data.code === 0) {
      ElMessage.success('已参加任务');
      fetchDetail();
    } else {
      ElMessage.error(res.data.message);
    }
  };
  
  const leaveTask = async () => {
    const res = await leaveGroupTask(detail.value.group_task_id);
    if (res.data.code === 0) {
      ElMessage.success('已退出任务');
      fetchDetail();
    } else {
      ElMessage.error(res.data.message);
    }
  };
  
  onMounted(fetchDetail);
  </script>