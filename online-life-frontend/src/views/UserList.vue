<template>
  <el-card>
    <h2>开发者人员</h2>
    <el-table :data="developers" style="width: 100%">
      <el-table-column prop="name" label="姓名" />
      <el-table-column prop="role" label="角色" />
      <el-table-column prop="email" label="邮箱" />
      <el-table-column prop="github" label="GitHub" />
    </el-table>
  </el-card>
</template>

<script setup>
import { ref } from 'vue';

const developers = ref([
  {
    name: '张三',
    role: '前端开发',
    email: 'zhangsan@example.com',
    github: 'https://github.com/zhangsan'
  },
  {
    name: '李四',
    role: '后端开发',
    email: 'lisi@example.com',
    github: 'https://github.com/lisi'
  },
  {
    name: '王五',
    role: '全栈开发',
    email: 'wangwu@example.com',
    github: 'https://github.com/wangwu'
  }
]);
</script> 