<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <div class="header-content">
        <div class="logo">
          <img :src="logoUrl" alt="Logo" class="logo-image" />
          <span class="logo-text">Online Life</span>
        </div>
        <el-menu
          :default-active="$route.path"
          mode="horizontal"
          class="main-menu"
          @select="onSelect"
        >
          <el-menu-item index="/">首页</el-menu-item>
          <el-menu-item index="/orders" v-if="userStore.role === 'client'">订单</el-menu-item>
          <el-menu-item index="/points" v-if="userStore.role === 'client'">积分</el-menu-item>
          <el-menu-item index="/profile" v-if="userStore.role !== 'admin'">个人中心</el-menu-item>
          <el-menu-item index="/reputation" v-if="userStore.role === 'staff'">信誉</el-menu-item>
          <el-menu-item index="/users" v-if="userStore.role === 'admin'">用户管理</el-menu-item>
          <el-menu-item index="/developers" v-if="userStore.role === 'admin'">开发者人员</el-menu-item>
          <el-menu-item index="/available-orders" v-if="userStore.role === 'staff'">可接单列表</el-menu-item>
          <el-menu-item index="/staff/group-tasks" v-if="userStore.role === 'staff'">可竞标团办任务</el-menu-item>
          <el-menu-item index="/my-group-tasks" v-if="userStore.role === 'client'">我的团办任务</el-menu-item>
          <el-menu-item index="/my-bid-records" v-if="userStore.role === 'staff'">我的竞标记录</el-menu-item>
          <el-menu-item index="/login" @click="logout">退出</el-menu-item>
        </el-menu>
      </div>
    </el-header>
    <el-main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-main>
  </el-container>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import '@/assets/styles/main.css';
import logoUrl from '@/assets/logo.svg';

const router = useRouter();
const userStore = useUserStore();

const onSelect = (index) => {
  router.push(index);
};

const logout = () => {
  userStore.clearUserData();
  router.push('/login');
};
</script>

<style scoped>
.app-container {
  min-height: 100vh;
}

.app-header {
  padding: 0;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  position: fixed;
  width: 100%;
  z-index: 1000;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.logo {
  display: flex;
  align-items: center;
  margin-right: 40px;
}

.logo-image {
  height: 32px;
  margin-right: 10px;
}

.logo-text {
  font-size: 20px;
  font-weight: 600;
  color: var(--primary-color);
}

.main-menu {
  flex: 1;
  border: none;
}

.app-main {
  padding-top: 80px;
  background-color: var(--background-color);
  min-height: calc(100vh - 60px);
}

@media (max-width: 768px) {
  .header-content {
    padding: 0 16px;
  }

  .logo-text {
    display: none;
  }

  .logo-image {
    height: 28px;
  }
}
</style> 