<template>
  <div class="doctor-patient-list-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <el-page-header @back="goBack">
        <template #content>
          <div class="header-content">
            <h1 class="page-title">
              <el-icon class="title-icon"><User /></el-icon>
              我的病人
            </h1>
            <p class="page-subtitle">
              与我有过预约或就诊记录的病人列表
            </p>
          </div>
        </template>
      </el-page-header>
    </div>

    <!-- 筛选搜索 -->
    <el-card class="filter-card" shadow="never">
      <el-form inline>
        <el-form-item label="搜索">
          <el-input
            v-model="searchQuery"
            placeholder="病人编号、姓名、电话"
            clearable
            style="width: 300px"
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          >
            <template #append>
              <el-button :icon="Search" @click="handleSearch" />
            </template>
          </el-input>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 病人列表 -->
    <el-card class="table-card" shadow="never">
      <el-table
        v-loading="loading"
        :data="filteredPatients"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column prop="patient_no" label="病人编号" width="120" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="gender" label="性别" width="80" align="center" />
        <el-table-column prop="age" label="年龄" width="80" align="center" />
        <el-table-column prop="phone" label="联系电话" min-width="120" />
        <el-table-column prop="appointment_count" label="预约次数" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="primary" size="small">{{ row.appointment_count }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="medical_record_count" label="就诊次数" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="success" size="small">{{ row.medical_record_count }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="最后就诊" width="120">
          <template #default="{ row }">
            {{ row.last_visit_date ? row.last_visit_date.split('T')[0] : '暂无' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              text
              @click="viewPatientDetail(row)"
            >
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && filteredPatients.length === 0" description="暂无病人数据" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Search } from '@element-plus/icons-vue'
import { getDoctorPatients } from '@/api/doctor'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const patients = ref([])
const searchQuery = ref('')

// 筛选后的病人列表
const filteredPatients = computed(() => {
  if (!searchQuery.value) {
    return patients.value
  }
  
  const query = searchQuery.value.toLowerCase()
  return patients.value.filter(patient => {
    return (
      patient.patient_no?.toLowerCase().includes(query) ||
      patient.name?.toLowerCase().includes(query) ||
      patient.phone?.includes(query)
    )
  })
})

// 获取病人列表
const fetchPatients = async () => {
  loading.value = true
  try {
    const doctorId = userStore.userInfo?.doctor?.id
    if (!doctorId) {
      ElMessage.warning('未获取到医生信息')
      return
    }
    
    const res = await getDoctorPatients(doctorId)
    patients.value = res.data?.patients || []
  } catch (error) {
    console.error('加载病人列表失败:', error)
    ElMessage.error('加载病人列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  // 搜索由计算属性自动处理
}

// 查看病人详情
const viewPatientDetail = (patient) => {
  router.push({
    name: 'PatientDetail',
    params: { id: patient.id }
  })
}

// 返回
const goBack = () => {
  router.push({ name: 'DoctorDashboard' })
}

onMounted(() => {
  fetchPatients()
})
</script>

<style scoped>
.doctor-patient-list-container {
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
</style>
