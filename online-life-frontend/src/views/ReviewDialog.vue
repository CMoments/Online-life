<template>
  <el-dialog v-model="visible" title="订单评价" width="400px" @close="resetForm">
    <el-form :model="form" label-width="70px">
      <el-form-item label="信誉分">
        <el-input-number v-model="form.score" :min="0" :max="100" style="width: 100%;" />
      </el-form-item>
      <el-form-item label="评价内容">
        <el-input v-model="form.review" type="textarea" :rows="3" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="submitReview">提交</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref } from 'vue'
import { reviewOrder } from '@/api/order'
import { ElMessage } from 'element-plus'

const visible = ref(false)
const form = ref({ score: 100, review: '' })
const currentOrder = ref(null)
const staffId = ref('')

function openReview(order, staffUserId) {
  currentOrder.value = order
  staffId.value = staffUserId
  form.value = { score: 100, review: '' }
  visible.value = true
}

function resetForm() {
  form.value = { score: 100, review: '' }
}

async function submitReview() {
  if (!form.value.review) {
    ElMessage.warning('请输入评价内容')
    return
  }
  try {
    await reviewOrder(currentOrder.value.order_id, {
      target_user_id: staffId.value,
      score: form.value.score,
      review: form.value.review
    })
    ElMessage.success('评价成功')
    visible.value = false
    resetForm()
    // 通知父组件刷新
    if (typeof window !== 'undefined' && window.location) {
      window.location.reload()
    }
  } catch (e) {
    ElMessage.error('评价失败')
  }
}

defineExpose({ openReview })
</script>
