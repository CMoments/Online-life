<template>
    <el-card>
      <h2>个人信息</h2>
      <el-form :model="profile" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="profile.username" disabled />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="profile.email" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="profile.phone" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="profile.address" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="onUpdate">保存修改</el-button>
        </el-form-item>
      </el-form>
      <el-divider />
      <h3>修改密码</h3>
      <el-form :model="pwdForm" label-width="80px">
        <el-form-item label="原密码">
          <el-input v-model="pwdForm.old_password" type="password" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="pwdForm.new_password" type="password" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="onChangePwd">修改密码</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue';
  import { getProfile, updateProfile, changePassword } from '@/api/user';
  
  const profile = ref({});
  const pwdForm = ref({ old_password: '', new_password: '' });
  
  const fetchProfile = async () => {
    const res = await getProfile();
    if (res.data.code === 0) {
      profile.value = res.data.data;
    }
  };
  
  const onUpdate = async () => {
    const res = await updateProfile(profile.value);
    if (res.data.code === 0) {
      ElMessage.success('修改成功');
    } else {
      ElMessage.error(res.data.message);
    }
  };
  
  const onChangePwd = async () => {
    const res = await changePassword(pwdForm.value);
    if (res.data.code === 0) {
      ElMessage.success('密码修改成功');
      pwdForm.value = { old_password: '', new_password: '' };
    } else {
      ElMessage.error(res.data.message);
    }
  };
  
  onMounted(fetchProfile);
  </script>