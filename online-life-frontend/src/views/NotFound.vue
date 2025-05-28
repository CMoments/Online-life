<template>
    <el-result
      icon="warning"
      title="404 Not Found"
      sub-title="您访问的页面不存在或已被删除"
    >
      <template #extra>
        <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
      </template>
    </el-result>
  </template>
  
  <script setup>
  </script>