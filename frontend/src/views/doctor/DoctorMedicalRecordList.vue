<template>
  <div class="doctor-medical-record-list-container">
    <div class="page-header">
      <el-page-header @back="goBack">
        <template #content>
          <div class="header-content">
            <h1 class="page-title">
              <el-icon class="title-icon"><Document /></el-icon>
              我的病历
            </h1>
            <p class="page-subtitle">仅展示与当前登录医生相关的病历记录</p>
          </div>
        </template>
      </el-page-header>
    </div>

    <el-card class="filter-card" shadow="never">
      <el-form inline>
        <el-form-item label="病人姓名">
          <el-input
            v-model="searchQuery"
            placeholder="输入病人姓名关键字"
            clearable
            style="width: 260px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card" shadow="never">
      <el-table
        v-loading="loading"
        :data="filteredRecords"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column prop="patientName" label="病人姓名" width="140" />
        <el-table-column prop="visitDate" label="就诊日期" width="160">
          <template #default="{ row }">
            {{ formatDate(row.visitDate) }}
          </template>
        </el-table-column>
        <el-table-column prop="diagnosis" label="诊断结果" min-width="260" show-overflow-tooltip />
        <el-table-column label="操作" width="120" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" text @click="viewRecordDetail(row)">
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="table-footer" v-if="total > 0">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>

      <el-empty
        v-if="!loading && filteredRecords.length === 0"
        description="暂无病历记录"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Document } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { getDoctorMedicalRecords } from '@/api/doctor'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const records = ref([])
const searchQuery = ref('')
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const filteredRecords = computed(() => {
  if (!searchQuery.value) {
    return records.value
  }
  const q = searchQuery.value.toLowerCase()
  return records.value.filter((item) =>
    (item.patientName || '').toLowerCase().includes(q)
  )
})

const formatDate = (value) => {
  if (!value) return '—'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return value
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

const fetchRecords = async () => {
  loading.value = true
  try {
    const doctorId = userStore.userInfo?.doctor?.id
    if (!doctorId) {
      ElMessage.warning('未获取到医生信息')
      return
    }

    const res = await getDoctorMedicalRecords(doctorId, {
      page: page.value,
      pageSize: pageSize.value
    })
    records.value = res.data?.items || []
    total.value = res.data?.total || 0
  } catch (error) {
    console.error('加载病历列表失败:', error)
    ElMessage.error('加载病历列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  page.value = 1
  fetchRecords()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  fetchRecords()
}

const handleCurrentChange = (p) => {
  page.value = p
  fetchRecords()
}

const viewRecordDetail = (row) => {
  router.push({
    name: 'MedicalRecordDetail',
    params: { id: row.id }
  })
}

const goBack = () => {
  router.push({ name: 'DoctorDashboard' })
}

onMounted(() => {
  fetchRecords()
})
</script>

<style scoped>
.doctor-medical-record-list-container {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.title-icon {
  font-size: 26px;
  color: #409eff;
}

.page-subtitle {
  font-size: 13px;
  color: #909399;
  margin: 0;
}

.filter-card {
  margin-bottom: 16px;
}

.table-card {
  margin-bottom: 20px;
}

.table-footer {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}
</style>
