<template>
    <el-form :model="form" @submit.native.prevent="onSubmit" style="max-width: 400px; margin: 100px auto;">
      <el-form-item label="用户名">
        <el-input v-model="form.username" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="form.password" type="password" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onSubmit">登录</el-button>
        <el-button @click="$router.push('/register')">注册</el-button>
      </el-form-item>
    </el-form>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  import { login } from '@/api/auth';
  import { useRouter } from 'vue-router';
  import { ElMessage } from 'element-plus';
  import { useUserStore } from '@/stores/user';
  
  const router = useRouter();
  const userStore = useUserStore();
  const form = ref({ username: '', password: '' });
  
  const handleError = (error) => {
    // 优先显示后端返回的 message
    if (error.response && error.response.data && error.response.data.message) {
      ElMessage.error(error.response.data.message);
    } else if (error.message) {
      ElMessage.error(error.message);
    } else {
      ElMessage.error('登录失败');
    }
  };
  
  const onSubmit = async () => {
    try {
      const res = await login(form.value);
      if (res.data.data && res.data.data.token) {
        // 先清除旧的数据
        userStore.clearUserData();
        
        // 设置新的数据
        localStorage.setItem('token', res.data.data.token);
        if (res.data.data.role) {
          userStore.setRole(res.data.data.role);
        }
        
        ElMessage.success('登录成功');
        router.push('/');
      } else {
        ElMessage.error(res.data.message || '登录失败');
      }
    } catch (error) {
      handleError(error);
    }
  };
  </script>