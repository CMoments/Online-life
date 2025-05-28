<template>
    <el-card>
      <h2>团办任务列表</h2>
      <el-table :data="tasks" style="width: 100%">
        <el-table-column prop="group_task_id" label="团办ID" width="120" />
        <el-table-column prop="task_type" label="类型" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="join_time" label="加入时间" />
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button size="small" @click="viewDetail(scope.row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="page"
        :page-size="perPage"
        :total="total"
        @current-change="fetchTasks"
        layout="prev, pager, next"
        style="margin-top: 20px;"
      />
    </el-card>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue';
  import { getGroupTasks } from '@/api/task';
  import { useRouter } from 'vue-router';
  
  const tasks = ref([]);
  const page = ref(1);
  const perPage = ref(10);
  const total = ref(0);
  const router = useRouter();
  
  const fetchTasks = async () => {
    const res = await getGroupTasks({ page: page.value, per_page: perPage.value });
    if (res.data.code === 0) {
      tasks.value = res.data.data.items || [];
      total.value = res.data.data.total || 0;
    }
  };
  
  const viewDetail = (row) => {
    router.push(`/tasks/${row.group_task_id}`);
  };
  
  onMounted(fetchTasks);
  </script>