<template>
  <el-card>
    <h2>创建订单</h2>
    <el-form :model="form" label-width="80px">
      <el-form-item label="类型">
        <el-select v-model="form.order_type" placeholder="请选择类型">
          <el-option label="立即" value="immediate" />
          <el-option label="预约" value="scheduled" />
        </el-select>
      </el-form-item>
      <el-form-item label="描述">
        <el-input v-model="form.description" />
      </el-form-item>
      <el-form-item label="商家地址">
        <el-input v-model="form.shop_address" placeholder="请输入商家详细地址" />
      </el-form-item>
      <el-form-item label="收货地址">
        <el-input v-model="form.orderlocation" placeholder="请输入收货详细地址" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onSubmit">提交</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { createOrder } from '@/api/order';
import { ElMessage } from 'element-plus';

const form = ref({
  order_type: '',
  description: '',
  shop_address: '',
  orderlocation: '',
});

onMounted(() => {
  form.value.shop_address = '';
  form.value.orderlocation = '';
});

const onSubmit = async () => {
  console.log('提交前表单内容', form.value);
  if (!form.value.shop_address || !form.value.orderlocation) {
    ElMessage.error('请填写完整的商家地址和收货地址');
    return;
  }
  try {
    const res = await createOrder(form.value);
    if (res.data.success) {
      ElMessage.success('订单创建成功');
      // 可跳转到订单列表或详情页
    } else {
      ElMessage.error(res.data.message || '订单创建失败');
    }
  } catch (error) {
    ElMessage.error('订单创建失败，请检查网络或后端服务');
  }
};
</script>