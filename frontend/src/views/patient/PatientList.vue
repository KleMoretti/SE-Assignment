<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPatientList, deletePatient } from '@/api/patient'

// 响应式数据
const tableData = ref([])
const loading = ref(false)
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const searchKeyword = ref('')

// 获取数据
const fetchData = async () => {
  loading.value = true
  try {
    const res = await getPatientList({
      page: page.value,
      per_page: pageSize.value,
      search: searchKeyword.value
    })
    if (res.success) {
      tableData.value = res.data.items
      total.value = res.data.total
    }
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  page.value = 1
  fetchData()
}

// 分页
const handlePageChange = (newPage) => {
  page.value = newPage
  fetchData()
}

// 删除
const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除吗？', '提示', {
      type: 'warning'
    })
    await deletePatient(id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 生命周期
onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="patient-list">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-800">病人管理</h1>
      <el-button type="primary" @click="$router.push('/patient/add')">
        新增病人
      </el-button>
    </div>

    <!-- 搜索栏 -->
    <div class="bg-white p-4 rounded-lg shadow-sm mb-4">
      <div class="flex gap-4">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索病人姓名"
          clearable
          class="w-64"
          @keyup.enter="handleSearch"
        />
        <el-button type="primary" @click="handleSearch">搜索</el-button>
      </div>
    </div>

    <!-- 表格 -->
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
        <el-table-column prop="gender" label="性别" width="80" />
        <el-table-column prop="age" label="年龄" width="80" />
        <el-table-column prop="phone" label="手机号" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="$router.push(`/patient/${row.id}`)"
            >
              详情
            </el-button>
            <el-button
              type="warning"
              size="small"
              @click="$router.push(`/patient/edit/${row.id}`)"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(row.id)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="p-4 flex justify-end">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="handlePageChange"
          @size-change="fetchData"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.patient-list {
  padding: 20px;
}
</style>
