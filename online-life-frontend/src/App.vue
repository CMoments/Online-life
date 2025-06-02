<template>
  <el-container>
    <el-header>
      <el-menu :default-active="$route.path" mode="horizontal" @select="onSelect">
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/orders" v-if="userStore.role !== 'staff'">订单</el-menu-item>
        <el-menu-item index="/points" v-if="userStore.role !== 'staff'">积分</el-menu-item>
        <el-menu-item index="/profile">个人中心</el-menu-item>
        <el-menu-item index="/reputation" v-if="userStore.role !== 'client'">信誉</el-menu-item>
        <el-menu-item index="/users" v-if="userStore.role === 'admin'">用户管理</el-menu-item>
        <el-menu-item index="/available-orders" v-if="userStore.role === 'staff'">可接单列表</el-menu-item>
        <el-menu-item index="/staff/group-tasks" v-if="userStore.role === 'staff'">可竞标团办任务</el-menu-item>
        <el-menu-item index="/my-group-tasks" v-if="userStore.role === 'client'">我的团办任务</el-menu-item>
        <el-menu-item index="/my-bid-records" v-if="userStore.role === 'staff'">我的竞标记录</el-menu-item>
        <el-menu-item index="/login" @click="logout">退出</el-menu-item>
      </el-menu>
    </el-header>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';

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