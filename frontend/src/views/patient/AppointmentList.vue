<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getAppointmentList } from '@/api/patient'
import { Search, Plus } from '@element-plus/icons-vue'

const router = useRouter()

// Reactive data
const tableData = ref([])
const loading = ref(false)
const total = ref(0)
const queryParams = ref({
  page: 1,
  per_page: 10,
  search: ''
})

// Fetch data
const fetchData = async () => {
  loading.value = true
  try {
    const res = await getAppointmentList(queryParams.value)
    // axios 封装已返回后端 JSON: { success, message, code, data: { items, total, ... } }
    tableData.value = res.data?.items || []
    total.value = res.data?.total || 0
  } catch (error) {
    ElMessage.error('加载挂号列表失败')
  } finally {
    loading.value = false
  }
}

// Search
const handleSearch = () => {
  queryParams.value.page = 1
  fetchData()
}

// Pagination
const handleSizeChange = (newSize) => {
  queryParams.value.per_page = newSize
  fetchData()
}

const handleCurrentChange = (newPage) => {
  queryParams.value.page = newPage
  fetchData()
}

// Lifecycle
onMounted(() => {
  fetchData()
})
</script>

<template>
  <div>
    <!-- Search Area -->
    <div class="mb-4">
      <el-form :inline="true" :model="queryParams">
        <el-form-item label="关键字">
          <el-input
            v-model="queryParams.search"
            placeholder="病人姓名、医生姓名"
            clearable
            style="width: 240px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Plus">新增预约</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- Table Area -->
    <el-table v-loading="loading" :data="tableData" border stripe style="width: 100%">
      <el-table-column prop="appointment_no" label="预约号" width="150" />
      <el-table-column prop="patient_name" label="病人姓名" width="120" />
      <el-table-column prop="doctor_name" label="医生姓名" width="120" />
      <el-table-column prop="appointment_time" label="预约时间" width="180" />
      <el-table-column prop="status" label="状态" width="100" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" size="small">详情</el-button>
          <el-button type="danger" size="small">取消预约</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Pagination -->
    <div class="mt-6 flex justify-end">
      <el-pagination
        v-model:current-page="queryParams.page"
        v-model:page-size="queryParams.per_page"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<style scoped>
.el-form--inline .el-form-item {
  margin-bottom: 0;
}
</style>
