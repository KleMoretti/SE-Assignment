<template>
  <div class="doctor-dashboard-container">
    <el-row :gutter="16">
      <el-col :span="10">
        <el-card shadow="never" class="quick-actions-card">
          <div class="card-header">
            <div class="card-title">医生快捷操作</div>
          </div>
          <div class="quick-actions">
            <el-button type="primary" size="large" @click="goToMedicationRequest">
              医生开药管理
            </el-button>
            <el-button size="large" @click="goToAppointments">
              病人预约管理
            </el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="14">
        <el-card shadow="never" class="appointments-card">
          <div class="card-header">
            <div class="card-title">近期预约概览</div>
          </div>
          <el-table
            v-loading="loading"
            :data="tableData"
            border
            stripe
            height="360px"
          >
            <el-table-column prop="appointment_no" label="预约号" width="120" />
            <el-table-column prop="patient_name" label="病人姓名" min-width="120" />
            <el-table-column prop="department" label="科室" min-width="100" />
            <el-table-column label="预约日期" min-width="120">
              <template #default="{ row }">
                {{ row.appointment_date ? row.appointment_date.split('T')[0] : '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="appointment_time" label="预约时间" width="100" />
            <el-table-column label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getAppointmentList } from '@/api/patient'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const tableData = ref([])

const currentDoctorName = computed(() => userStore.userInfo?.real_name || userStore.userInfo?.username || '')

const getStatusType = (status) => {
  const statusMap = {
    pending: 'warning',
    confirmed: 'primary',
    completed: 'success',
    cancelled: 'info'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    pending: '待确认',
    confirmed: '已确认',
    completed: '已完成',
    cancelled: '已取消'
  }
  return statusMap[status] || status
}

const fetchRecentAppointments = async () => {
  loading.value = true
  try {
    const res = await getAppointmentList({ page: 1, per_page: 20 })
    const items = res.data?.items || []
    if (currentDoctorName.value) {
      tableData.value = items.filter((item) => item.doctor_name === currentDoctorName.value).slice(0, 10)
    } else {
      tableData.value = items.slice(0, 10)
    }
  } catch (error) {
    ElMessage.error('加载预约概览失败')
  } finally {
    loading.value = false
  }
}

const goToMedicationRequest = () => {
  router.push({ name: 'DoctorMedicationRequest' })
}

const goToAppointments = () => {
  router.push({ name: 'AppointmentList' })
}

onMounted(() => {
  fetchRecentAppointments()
})
</script>

<style scoped>
.doctor-dashboard-container {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.quick-actions-card,
.appointments-card {
  height: 100%;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
}

.quick-actions .el-button {
  width: 100%;
  display: block;
  margin: 0;
}
</style>
