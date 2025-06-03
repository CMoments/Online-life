<template>
  <div class="page-container">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <el-button @click="$router.push('/orders')" class="back-button">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2 class="page-title">创建订单</h2>
      </div>
    </div>

    <el-card class="form-card" shadow="hover">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        @submit.prevent
        class="order-form"
      >
        <!-- 订单类型 -->
        <el-form-item label="订单类型" prop="order_type">
          <el-select
            v-model="form.order_type"
            placeholder="请选择订单类型"
            class="form-select"
          >
            <el-option
              v-for="type in orderTypes"
              :key="type.value"
              :label="type.label"
              :value="type.value"
            >
              <div class="option-content">
                <el-icon>
                  <component :is="type.icon" />
                </el-icon>
                <span>{{ type.label }}</span>
                <el-tag size="small" :type="type.tagType" effect="light">
                  {{ type.description }}
                </el-tag>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <!-- 预约时间 -->
        <el-form-item
          v-if="form.order_type === 'scheduled'"
          label="预约时间"
          prop="scheduled_time"
        >
          <el-date-picker
            v-model="form.scheduled_time"
            type="datetime"
            placeholder="选择预约时间"
            :disabled-date="disabledDate"
            :disabled-time="disabledTime"
            class="form-date-picker"
          />
        </el-form-item>

        <!-- 商家地址 -->
        <el-form-item label="商家地址" prop="shop_address" required>
          <el-input
            v-model="form.shop_address"
            placeholder="请输入商家详细地址"
            clearable
          >
            <template #prefix>
              <el-icon><Shop /></el-icon>
            </template>
          </el-input>
          <div class="form-tip">请确保地址准确，包含详细的门牌号</div>
        </el-form-item>

        <!-- 收货地址 -->
        <el-form-item label="收货地址" prop="orderlocation" required>
          <el-input
            v-model="form.orderlocation"
            placeholder="请输入收货详细地址"
            clearable
          >
            <template #prefix>
              <el-icon><Location /></el-icon>
            </template>
          </el-input>
          <div class="form-tip">请确保地址准确，包含详细的门牌号</div>
        </el-form-item>

        <!-- 订单描述 -->
        <el-form-item label="订单描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请详细描述您的订单要求..."
            :maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <!-- 提交按钮 -->
        <el-form-item class="form-buttons">
          <el-button
            type="primary"
            :loading="loading"
            @click="submitForm(formRef)"
          >
            <el-icon><Check /></el-icon>
            提交订单
          </el-button>
          <el-button @click="resetForm(formRef)">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 提示卡片 -->
    <el-card class="tips-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><InfoFilled /></el-icon>
          <span>温馨提示</span>
        </div>
      </template>
      <div class="tips-content">
        <p><el-icon><Warning /></el-icon> 请确保填写的地址信息准确无误</p>
        <p><el-icon><Timer /></el-icon> 预约订单请提前至少2小时预约</p>
        <p><el-icon><Document /></el-icon> 详细的订单描述有助于快速接单</p>
        <p><el-icon><Bell /></el-icon> 订单创建后会通过系统通知告知进展</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { createOrder } from '@/api/order';
import { getProfile } from '@/api/user';
import { ElMessage } from 'element-plus';
import {
  ArrowLeft,
  Check,
  Refresh,
  Location,
  Shop,
  InfoFilled,
  Warning,
  Timer,
  Document,
  Bell,
  Van,
  Calendar
} from '@element-plus/icons-vue';

const router = useRouter();
const formRef = ref();
const loading = ref(false);
const userProfile = ref(null);

const orderTypes = [
  {
    label: '立即配送',
    value: 'immediate',
    icon: 'Van',
    description: '立即处理',
    tagType: 'danger'
  },
  {
    label: '预约配送',
    value: 'scheduled',
    icon: 'Calendar',
    description: '指定时间',
    tagType: 'warning'
  }
];

const form = ref({
  order_type: '',
  description: '',
  shop_address: '',
  orderlocation: '',
  scheduled_time: null
});

// 获取用户信息
const fetchUserProfile = async () => {
  try {
    const res = await getProfile();
    if (res.data.success) {
      userProfile.value = res.data.data;
      // 如果用户有地址信息，设置为默认商家地址
      if (userProfile.value.address) {
        form.value.shop_address = userProfile.value.address;
      }
    }
  } catch (error) {
    console.error('获取用户信息失败:', error);
  }
};

const rules = {
  order_type: [
    { required: true, message: '请选择订单类型', trigger: 'change' }
  ],
  shop_address: [
    { required: true, message: '请输入商家地址', trigger: 'blur' },
    { min: 5, message: '地址长度至少5个字符', trigger: 'blur' }
  ],
  orderlocation: [
    { required: true, message: '请输入收货地址', trigger: 'blur' },
    { min: 5, message: '地址长度至少5个字符', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入订单描述', trigger: 'blur' },
    { min: 10, message: '描述至少10个字符', trigger: 'blur' }
  ],
  scheduled_time: [
    {
      required: true,
      message: '请选择预约时间',
      trigger: 'change',
      type: 'date'
    }
  ]
};

const disabledDate = (time) => {
  return time.getTime() < Date.now() - 8.64e7; // 禁用过去的日期
};

const disabledTime = (date) => {
  if (!date) return;
  const now = new Date();
  const hours = [];
  const minutes = [];
  
  // 如果是今天，禁用过去的小时
  if (date.toDateString() === now.toDateString()) {
    for (let i = 0; i < now.getHours(); i++) {
      hours.push(i);
    }
    if (date.getHours() === now.getHours()) {
      for (let i = 0; i < now.getMinutes(); i++) {
        minutes.push(i);
      }
    }
  }

  return {
    disabledHours: () => hours,
    disabledMinutes: () => minutes
  };
};

const submitForm = async (formEl) => {
  if (!formEl) return;
  
  await formEl.validate(async (valid, fields) => {
    if (valid) {
      loading.value = true;
      try {
        const res = await createOrder(form.value);
        if (res.data.success) {
          ElMessage.success('订单创建成功');
          router.push('/orders');
        } else {
          ElMessage.error(res.data.message || '订单创建失败');
        }
      } catch (error) {
        ElMessage.error('订单创建失败，请稍后重试');
      } finally {
        loading.value = false;
      }
    } else {
      ElMessage.error('请完善表单信息');
    }
  });
};

const resetForm = (formEl) => {
  if (!formEl) return;
  formEl.resetFields();
  // 重置后恢复默认商家地址
  if (userProfile.value?.address) {
    form.value.shop_address = userProfile.value.address;
  }
};

onMounted(() => {
  fetchUserProfile();
});
</script>

<style scoped>
.page-container {
  padding: 20px;
  min-height: 100%;
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}

.page-header {
  grid-column: 1 / -1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.form-card,
.tips-card {
  border-radius: 8px;
  transition: all 0.3s;
}

.form-card:hover,
.tips-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.order-form {
  max-width: 800px;
  margin: 0 auto;
}

.form-select,
.form-date-picker {
  width: 100%;
}

.option-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-tip {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

.form-buttons {
  margin-top: 32px;
  display: flex;
  justify-content: center;
  gap: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.tips-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tips-content p {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--el-text-color-regular);
}

:deep(.el-select-dropdown__item) {
  padding: 8px 12px;
}

@media (max-width: 768px) {
  .page-container {
    grid-template-columns: 1fr;
    padding: 12px;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
  }

  .header-left {
    width: 100%;
    flex-direction: column;
  }

  .back-button {
    width: 100%;
  }

  .form-buttons {
    flex-direction: column;
  }

  .form-buttons .el-button {
    width: 100%;
  }
}
</style>