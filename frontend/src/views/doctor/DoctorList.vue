<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const tableData = ref([])
const loading = ref(false)

const fetchData = async () => {
  loading.value = true
  try {
    // 这里应该调用医生API
    // 暂时使用模拟数据
    tableData.value = [
      { id: 1, name: '张医生', department: '内科', title: '主任医师', phone: '13800138001' },
      { id: 2, name: '李医生', department: '外科', title: '副主任医师', phone: '13800138002' }
    ]
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="doctor-list">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-800">医生管理</h1>
      <el-button type="primary">新增医生</el-button>
    </div>

    <div class="bg-white rounded-lg shadow-sm">
      <el-table
        v-loading="loading"
        :data="tableData"
        stripe
        border
        class="w-full"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="department" label="科室" />
        <el-table-column prop="title" label="职称" />
        <el-table-column prop="phone" label="手机号" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small">详情</el-button>
            <el-button type="warning" size="small">编辑</el-button>
            <el-button type="danger" size="small">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<style scoped>
.doctor-list {
  padding: 20px;
}
</style>
