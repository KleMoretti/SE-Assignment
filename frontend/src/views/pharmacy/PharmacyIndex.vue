<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const medicines = ref([])
const loading = ref(false)

const fetchData = async () => {
  loading.value = true
  try {
    // 这里应该调用药房API
    // 暂时使用模拟数据
    medicines.value = [
      { id: 1, name: '阿莫西林', stock: 100, unit: '盒', price: 25.5 },
      { id: 2, name: '布洛芬', stock: 50, unit: '瓶', price: 15.8 }
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
  <div class="pharmacy-index">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-800">药房管理</h1>
      <el-button type="primary">新增药品</el-button>
    </div>

    <div class="bg-white rounded-lg shadow-sm">
      <el-table
        v-loading="loading"
        :data="medicines"
        stripe
        border
        class="w-full"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="药品名称" />
        <el-table-column prop="stock" label="库存数量" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="price" label="单价(元)" />
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
.pharmacy-index {
  padding: 20px;
}
</style>
