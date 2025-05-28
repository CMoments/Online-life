<template>
  <el-form :model="form" style="max-width: 400px; margin: 100px auto;">
    <el-form-item label="用户名" required>
      <el-input v-model="form.username" />
    </el-form-item>
    <el-form-item label="密码" required>
      <el-input v-model="form.password" type="password" />
    </el-form-item>
    <el-form-item label="邮箱">
      <el-input v-model="form.email" />
    </el-form-item>
    <el-form-item label="电话">
      <el-input v-model="form.phone" />
    </el-form-item>
    <el-form-item label="地址">
      <el-input v-model="form.address" />
    </el-form-item>
    <el-form-item label="角色" required>
      <el-select v-model="form.role" placeholder="请选择角色">
        <el-option label="管理员" value="admin" />
        <el-option label="客户" value="client" />
        <el-option label="代办人员" value="staff" />
      </el-select>
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="onSubmit">注册</el-button>
      <el-button @click="$router.push('/login')">返回登录</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { ref } from 'vue';
import { register } from '@/api/auth';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';

const router = useRouter();
const form = ref({
  username: '',
  password: '',
  email: '',
  phone: '',
  address: '',
  role: ''
});

const onSubmit = async () => {
  // 简单校验
  if (!form.value.username || !form.value.password || !form.value.role) {
    ElMessage.error('请填写用户名、密码和角色');
    return;
  }
  try {
    const res = await register(form.value);
    console.log('注册返回:', res.data);
    // 兼容 code: 0 或 code: 200
    if (res.data.code === 0 || res.data.code === 200) {
      ElMessage.success('注册成功，请登录');
      router.push('/login');
    } else if (res.data.message && res.data.message.includes('用户名已存在')) {
      ElMessage.error('用户名已存在');
    } else {
      ElMessage.error(res.data.message || '注册失败');
    }
  } catch (error) {
    if (error.response && error.response.data && error.response.data.message) {
      if (error.response.data.message.includes('用户名已存在')) {
        ElMessage.error('用户名已存在');
      } else {
        ElMessage.error(error.response.data.message);
      }
    } else {
      ElMessage.error('注册失败');
    }
  }
};
</script>