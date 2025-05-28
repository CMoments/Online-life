<template>
    <el-card>
      <h2>我的信誉</h2>
      <el-table :data="reputation" style="width: 100%">
        <el-table-column prop="score" label="分数" />
        <el-table-column prop="review" label="评价" />
        <el-table-column prop="r_user_id" label="评价人ID" />
      </el-table>
      <el-divider />
      <h3>添加信誉评价</h3>
      <el-form :model="form" inline>
        <el-form-item label="目标用户ID">
          <el-input v-model="form.target_user_id" />
        </el-form-item>
        <el-form-item label="分数">
          <el-input v-model="form.score" type="number" />
        </el-form-item>
        <el-form-item label="评价">
          <el-input v-model="form.review" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="onAdd">添加</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue';
  import { getReputation, addReputation } from '@/api/user';
  
  const reputation = ref([]);
  const form = ref({ target_user_id: '', score: '', review: '' });
  
  const fetchReputation = async () => {
    const res = await getReputation();
    if (res.data.code === 0) {
      reputation.value = res.data.data.items || [];
    }
  };
  
  const onAdd = async () => {
    const res = await addReputation(form.value);
    if (res.data.code === 0) {
      ElMessage.success('评价成功');
      fetchReputation();
    } else {
      ElMessage.error(res.data.message);
    }
  };
  
  onMounted(fetchReputation);
  </script>