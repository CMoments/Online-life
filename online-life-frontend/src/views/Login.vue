<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <img :src="logoUrl" alt="Logo" class="login-logo" />
        <h1 class="login-title">欢迎回来</h1>
        <p class="login-subtitle">登录您的账户以继续</p>
      </div>
      
      <el-form
        :model="form"
        @submit.native.prevent="onSubmit"
        class="login-form"
        :rules="rules"
        ref="formRef"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            prefix-icon="User"
            :size="'large'"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            :size="'large'"
            @keyup.enter="onSubmit"
          />
        </el-form-item>

        <div class="form-actions">
          <el-button
            type="primary"
            @click="onSubmit"
            :loading="loading"
            class="submit-btn"
            :size="'large'"
          >
            登录
          </el-button>
          
          <el-button
            @click="$router.push('/register')"
            class="register-btn"
            :size="'large'"
          >
            注册新账户
          </el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { login } from '@/api/auth';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { useUserStore } from '@/stores/user';
import logoUrl from '@/assets/logo.svg';

const router = useRouter();
const userStore = useUserStore();
const formRef = ref(null);
const loading = ref(false);
const form = ref({ username: '', password: '' });

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, message: '用户名长度至少为3个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 3, message: '密码长度至少为3个字符', trigger: 'blur' }
  ]
};

const handleError = (error) => {
  if (error.response?.data?.message) {
    ElMessage.error(error.response.data.message);
  } else if (error.message) {
    ElMessage.error(error.message);
  } else {
    ElMessage.error('登录失败');
  }
};

const onSubmit = async () => {
  if (!formRef.value) return;
  
  try {
    await formRef.value.validate();
    loading.value = true;
    
    const res = await login(form.value);
    if (res.data.data?.token) {
      userStore.clearUserData();
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
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7eb 100%);
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-logo {
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
}

.login-title {
  color: var(--text-color);
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 8px;
}

.login-subtitle {
  color: var(--info-color);
  font-size: 14px;
  margin: 0;
}

.login-form {
  margin-top: 24px;
}

.form-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 24px;
}

.submit-btn {
  width: 100%;
}

.register-btn {
  width: 100%;
}

:deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px var(--border-color) !important;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--primary-color) !important;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--primary-color) !important;
}

@media (max-width: 768px) {
  .login-card {
    padding: 24px;
  }
  
  .login-logo {
    width: 48px;
    height: 48px;
  }
  
  .login-title {
    font-size: 20px;
  }
}
</style>