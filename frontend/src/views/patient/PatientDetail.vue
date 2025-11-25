<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPatientDetail, getPatientAppointments, getPatientMedicalRecords, cancelPortalAppointment } from '@/api/patient'
// 引入图标
import { User, ArrowLeft, Document, Delete } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const patientId = computed(() => route.params.id)
const patient = ref(null)
const loading = ref(false)
const activeTab = ref('info')

// 病历记录
const medicalRecords = ref([])
const recordsLoading = ref(false)

// 预约记录
const appointments = ref([])
const appointmentsLoading = ref(false)
const appointmentStatusMap = {
  'pending': { text: '待确认', type: 'warning' },
  'confirmed': { text: '已确认', type: 'primary' },
  'completed': { text: '已完成', type: 'success' },
  'cancelled': { text: '已取消', type: 'info' }
}

// 加载病人数据
const loadPatientData = async () => {
  loading.value = true
  try {
    const res = await getPatientDetail(patientId.value)
    if (res.success) {
      patient.value = res.data
    } else {
      ElMessage.error(res.message || '加载病人数据失败')
    }
  } catch (error) {
    ElMessage.error('请求失败，请检查网络')
  } finally {
    loading.value = false
  }
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 加载病历记录
const loadMedicalRecords = async () => {
  recordsLoading.value = true
  try {
    const res = await getPatientMedicalRecords(patientId.value)
    if (res.success) {
      medicalRecords.value = res.data || []
    } else {
      ElMessage.error(res.message || '加载病历记录失败')
    }
  } catch (error) {
    console.error('加载病历记录失败:', error)
    ElMessage.error('加载病历记录失败')
  } finally {
    recordsLoading.value = false
  }
}

// 加载预约记录
const loadAppointments = async () => {
  appointmentsLoading.value = true
  try {
    const res = await getPatientAppointments(patientId.value)
    if (res.success) {
      appointments.value = res.data || []
    } else {
      ElMessage.error(res.message || '加载预约记录失败')
    }
  } catch (error) {
    console.error('加载预约记录失败:', error)
    ElMessage.error('加载预约记录失败')
  } finally {
    appointmentsLoading.value = false
  }
}

// 取消预约
const handleCancelAppointment = async (appointment) => {
  try {
    await ElMessageBox.confirm(
      `确定要取消与 ${appointment.doctor_name} 医生的预约吗？`,
      '取消预约',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await cancelPortalAppointment(appointment.id)
    ElMessage.success('预约已取消')
    loadAppointments() // 重新加载列表
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消预约失败:', error)
      ElMessage.error('取消预约失败')
    }
  }
}

// 监听标签切换，按需加载数据
watch(activeTab, (newTab) => {
  if (newTab === 'records' && medicalRecords.value.length === 0) {
    loadMedicalRecords()
  } else if (newTab === 'appointments' && appointments.value.length === 0) {
    loadAppointments()
  }
})

// 生命周期
onMounted(() => {
  loadPatientData()
})
</script>

<template>
  <el-card class="box-card" v-loading="loading">
    <!-- 头部 -->
    <template #header>
      <div class="flex justify-between items-center">
        <span class="text-xl font-semibold flex items-center">
          <el-icon class="mr-2"><User /></el-icon>
          <span>病人详情: {{ patient?.name }}</span>
        </span>
        <div>
          <el-button :icon="ArrowLeft" @click="goBack">返回</el-button>
        </div>
      </div>
    </template>

    <div v-if="patient">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="基本信息" name="info">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="病人编号">{{ patient.patient_no }}</el-descriptions-item>
            <el-descriptions-item label="姓名">{{ patient.name }}</el-descriptions-item>
            <el-descriptions-item label="性别">{{ patient.gender }}</el-descriptions-item>
            <el-descriptions-item label="年龄">{{ patient.age }}</el-descriptions-item>
            <el-descriptions-item label="身份证号">{{ patient.id_card }}</el-descriptions-item>
            <el-descriptions-item label="联系电话">{{ patient.phone }}</el-descriptions-item>
            <el-descriptions-item label="住址" :span="2">{{ patient.address }}</el-descriptions-item>
            <el-descriptions-item label="紧急联系人">{{ patient.emergency_contact }}</el-descriptions-item>
            <el-descriptions-item label="紧急联系电话">{{ patient.emergency_phone }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ patient.created_at }}</el-descriptions-item>
            <el-descriptions-item label="更新时间">{{ patient.updated_at }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>

        <el-tab-pane label="病历记录" name="records">
          <div v-loading="recordsLoading">
            <el-empty v-if="medicalRecords.length === 0" description="暂无病历记录" />
            <el-timeline v-else>
              <el-timeline-item
                v-for="record in medicalRecords"
                :key="record.id"
                :timestamp="record.visit_date"
                placement="top"
              >
                <el-card>
                  <template #header>
                    <div class="flex justify-between items-center">
                      <span class="font-semibold">
                        <el-icon class="mr-1"><Document /></el-icon>
                        就诊医生：{{ record.doctor_name }}
                      </span>
                      <el-tag type="info" size="small">{{ record.visit_date }}</el-tag>
                    </div>
                  </template>
                  <el-descriptions :column="1" border>
                    <el-descriptions-item label="症状描述">
                      {{ record.symptoms || '无' }}
                    </el-descriptions-item>
                    <el-descriptions-item label="诊断结果">
                      {{ record.diagnosis || '无' }}
                    </el-descriptions-item>
                    <el-descriptions-item label="治疗方案">
                      {{ record.treatment || '无' }}
                    </el-descriptions-item>
                    <el-descriptions-item label="处方">
                      {{ record.prescription || '无' }}
                    </el-descriptions-item>
                    <el-descriptions-item label="备注" v-if="record.notes">
                      {{ record.notes }}
                    </el-descriptions-item>
                  </el-descriptions>
                </el-card>
              </el-timeline-item>
            </el-timeline>
          </div>
        </el-tab-pane>

        <el-tab-pane label="预约记录" name="appointments">
          <div v-loading="appointmentsLoading">
            <el-empty v-if="appointments.length === 0" description="暂无预约记录" />
            <el-table v-else :data="appointments" stripe style="width: 100%">
              <el-table-column prop="appointment_no" label="预约编号" width="150" />
              <el-table-column prop="doctor_name" label="医生" width="120" />
              <el-table-column prop="department" label="科室" width="120" />
              <el-table-column prop="appointment_date" label="预约日期" width="120" />
              <el-table-column prop="appointment_time" label="预约时间" width="100" />
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="appointmentStatusMap[row.status]?.type || 'info'">
                    {{ appointmentStatusMap[row.status]?.text || row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="notes" label="备注" show-overflow-tooltip />
              <el-table-column label="操作" width="120" fixed="right">
                <template #default="{ row }">
                  <el-button
                    v-if="row.status === 'pending' || row.status === 'confirmed'"
                    type="danger"
                    size="small"
                    :icon="Delete"
                    @click="handleCancelAppointment(row)"
                  >
                    取消
                  </el-button>
                  <span v-else class="text-gray-400">-</span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
    <div v-else class="text-center text-gray-500 p-8">
      未能加载病人信息。
    </div>
  </el-card>
</template>

<style scoped>
.el-descriptions {
  margin-top: 20px;
}

.el-timeline {
  padding: 20px 0;
}

.el-timeline-item :deep(.el-card) {
  margin-bottom: 0;
}

.el-timeline-item :deep(.el-card__header) {
  padding: 12px 20px;
  background-color: #f5f7fa;
}

.el-timeline-item :deep(.el-card__body) {
  padding: 15px 20px;
}

.el-table {
  margin-top: 10px;
}

.flex {
  display: flex;
}

.justify-between {
  justify-content: space-between;
}

.items-center {
  align-items: center;
}

.font-semibold {
  font-weight: 600;
}

.mr-1 {
  margin-right: 4px;
}

.text-gray-400 {
  color: #9ca3af;
}
</style>

