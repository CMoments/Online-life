<template>
    <el-container>
      <el-header>
        <el-menu :default-active="active" mode="horizontal" @select="onSelect">
          <el-menu-item index="/">首页</el-menu-item>
          <el-menu-item index="/orders" v-if="userRole !== 'staff'">订单</el-menu-item>
          <el-menu-item index="/tasks" v-if="userRole !== 'client'">任务</el-menu-item>
          <el-menu-item index="/points" v-if="userRole !== 'staff'">积分</el-menu-item>
          <el-menu-item index="/profile">个人中心</el-menu-item>
          <el-menu-item index="/reputation" v-if="userRole !== 'client'">信誉</el-menu-item>
          <el-menu-item index="/users" v-if="userRole === 'admin'">用户管理</el-menu-item>
          <el-menu-item index="/login" @click="logout">退出</el-menu-item>
        </el-menu>
      </el-header>
      <el-main>
        <h2>欢迎来到网上代办系统</h2>
        <p>请选择上方菜单进行操作</p>
      </el-main>
    </el-container>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue';
  import { useRouter } from 'vue-router';
  import LogoutButton from '@/components/LogoutButton.vue'
  import { ElMessage } from 'element-plus';
  
  const router = useRouter();
  const active = ref('/');
  const userRole = ref(localStorage.getItem('role') || '');
  
  const onSelect = (index) => {
    router.push(index);
  };
  
  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    router.push('/login');
  };
  
  // 登录/注册 catch 里的错误处理
  const handleError = (error) => {
    // 401 未授权，用户名或密码错误
    if (error.response && error.response.status === 401) {
      const msg = error.response.data && error.response.data.message;
      if (msg && msg.includes('用户名')) {
        ElMessage.error('用户名不存在');
      } else if (msg && msg.includes('密码')) {
        ElMessage.error('密码错误');
      } else {
        ElMessage.error(msg || '用户名或密码错误');
      }
    } else if (error.response && error.response.data && error.response.data.message) {
      ElMessage.error(error.response.data.message);
    } else {
      ElMessage.error('请求失败，请稍后重试');
    }
  };

  const onSubmit = async () => {
    try {
      const res = await login(form.value);
      // 登录成功逻辑...
    } catch (error) {
      handleError(error); // 这里调用
    }
  };
  </script>

<style scoped>
</style>