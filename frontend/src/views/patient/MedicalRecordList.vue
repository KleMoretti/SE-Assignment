<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getMedicalRecordList } from '@/api/patient'
import { Search, Plus, InfoFilled } from '@element-plus/icons-vue'

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
    const res = await getMedicalRecordList(queryParams.value)
    tableData.value = res.data?.items || []
    total.value = res.data?.total || 0
  } catch (error) {
    ElMessage.error('加载病历列表失败')
  } finally {
    loading.value = false
  }
}

// Search
const handleSearch = () => {
  queryParams.value.page = 1
  fetchData()
}

// Go to detail page
const goToDetail = (id) => {
  router.push({ name: 'MedicalRecordDetail', params: { id } })
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
            placeholder="病人姓名、病历号"
            clearable
            style="width: 240px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- Table Area -->
    <el-table v-loading="loading" :data="tableData" border stripe style="width: 100%">
      <el-table-column prop="record_no" label="病历号" width="150" />
      <el-table-column prop="patient_name" label="病人姓名" width="120" />
      <el-table-column prop="doctor_name" label="主治医生" width="120" />
      <el-table-column prop="diagnosis_date" label="就诊日期" width="180" />
      <el-table-column prop="diagnosis" label="诊断结果" min-width="250" show-overflow-tooltip />
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-tooltip content="查看详情" placement="top">
            <el-button type="primary" :icon="InfoFilled" size="small" @click="goToDetail(row.id)" />
          </el-tooltip>
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
