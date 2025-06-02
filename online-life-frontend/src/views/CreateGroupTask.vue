<template>
  <el-card>
    <h2>发起团办任务</h2>
    <el-form :model="form" label-width="100px" style="max-width: 500px;">
      <el-form-item label="任务描述">
        <el-input v-model="form.description" placeholder="请输入任务描述" />
      </el-form-item>
      <el-form-item label="任务地点">
        <el-input v-model="form.task_location" placeholder="请输入任务地点" />
      </el-form-item>
      <el-form-item label="任务类型">
        <el-select v-model="form.task_type" placeholder="请选择任务类型">
          <el-option label="团办任务" value="group" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSubmit">提交</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { ref } from 'vue';
import { ElMessage } from 'element-plus';
import { useRouter } from 'vue-router';
import { createGroupTask } from '@/api/task';

const router = useRouter();
const form = ref({
  description: '',
  task_type: 'group',
  task_location: '',
});

const handleSubmit = async () => {
  try {
    const payload = {
      description: form.value.description,
      task_type: form.value.task_type,
      task_location: form.value.task_location,
    };
    const res = await createGroupTask(payload);
    if (res.data.success) {
      ElMessage.success('团办任务创建成功');
      router.push('/tasks');
    } else {
      ElMessage.error(res.data.message || '创建失败');
    }
  } catch (e) {
    ElMessage.error('创建失败');
  }
};
</script> 