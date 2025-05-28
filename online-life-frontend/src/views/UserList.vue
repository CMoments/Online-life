<template>
    <el-card>
      <h2>用户管理</h2>
      <el-table :data="users" style="width: 100%">
        <el-table-column prop="user_id" label="用户ID" width="120" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="phone" label="电话" />
        <el-table-column prop="role" label="角色" />
      </el-table>
      <el-pagination
        v-model:current-page="page"
        :page-size="perPage"
        :total="total"
        @current-change="fetchUsers"
        layout="prev, pager, next"
        style="margin-top: 20px;"
      />
    </el-card>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue';
  import { getUserList } from '@/api/user';
  
  const users = ref([]);
  const page = ref(1);
  const perPage = ref(10);
  const total = ref(0);
  
  const fetchUsers = async () => {
    const res = await getUserList({ page: page.value, per_page: perPage.value });
    if (res.data.code === 0) {
      users.value = res.data.data.items || [];
      total.value = res.data.data.total || 0;
    }
  };
  
  onMounted(fetchUsers);
  </script>