<template>
  <div class="doctor-medication-request-container">
    <div class="page-header">
      <el-page-header @back="goBack">
        <template #content>
          <div class="header-content">
            <h1 class="page-title">
              医生开药申请
            </h1>
            <p class="page-subtitle">选择病人和药品，提交用药申请。系统会自动生成病历记录，申请说明将作为病历描述</p>
          </div>
        </template>
      </el-page-header>
    </div>

    <el-card class="form-card" shadow="never">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="开药医生" prop="doctorId">
              <template v-if="userStore.isAdmin">
                <el-select
                  v-model="form.doctorId"
                  filterable
                  clearable
                  placeholder="请选择医生"
                  :loading="doctorLoading"
                  style="width: 100%"
                  @change="handleDoctorChange"
                >
                  <el-option
                    v-for="item in doctorOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                  />
                </el-select>
              </template>
              <template v-else-if="userStore.isDoctor">
                <el-input
                  :model-value="currentDoctorDisplay"
                  disabled
                />
              </template>
              <template v-else>
                <el-input
                  model-value="仅管理员和医生可以提交用药申请"
                  disabled
                />
              </template>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="就诊病人" prop="patientId">
              <el-select
                v-model="form.patientId"
                filterable
                remote
                clearable
                placeholder="输入姓名或编号搜索病人"
                :remote-method="remoteSearchPatients"
                :loading="patientLoading"
                style="width: 100%"
              >
                <el-option
                  v-for="item in patientOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="选择药品" prop="medicineId">
              <el-select
                v-model="form.medicineId"
                filterable
                clearable
                placeholder="选择药品"
                style="width: 100%"
                @change="handleMedicineChange"
              >
                <el-option
                  v-for="item in medicineOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                >
                  <div class="option-row">
                    <span class="option-name">{{ item.label }}</span>
                    <span class="option-meta">库存：{{ item.stock }} {{ item.unit }}</span>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="数量" prop="quantity">
              <el-input-number v-model="form.quantity" :min="1" :max="9999" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="剂量说明" prop="dose">
              <el-input v-model="form.dose" placeholder="如：500mg/次" />
            </el-form-item>
          </el-col>
          <el-col :span="16">
            <el-form-item label="用法用量" prop="usage">
              <el-input
                v-model="form.usage"
                type="textarea"
                :rows="2"
                placeholder="如：口服，每日3次，每次1片"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="24">
            <el-form-item label="申请说明" prop="reason">
              <el-input
                v-model="form.reason"
                type="textarea"
                :rows="3"
                placeholder="请填写诊断要点或开药原因。此内容将作为病历的症状描述，并用于药房审核"
              />
              <el-text type="info" size="small" style="margin-top: 4px; display: block;">
                💡 提示：提交用药申请时，系统将自动为该病人创建病历记录
              </el-text>
            </el-form-item>
          </el-col>
        </el-row>

        <div class="form-actions">
          <el-button @click="resetForm">重置</el-button>
          <el-button type="primary" :loading="submitting" @click="submitForm">提交用药申请</el-button>
        </div>
      </el-form>
    </el-card>

    <el-card class="list-card" shadow="never">
      <div class="list-header">
        <div class="list-title">我的用药申请</div>
        <el-select
          v-model="filters.status"
          placeholder="按状态筛选"
          clearable
          style="width: 160px"
          @change="handleFilterChange"
        >
          <el-option label="待审核" value="PENDING" />
          <el-option label="已通过" value="APPROVED" />
          <el-option label="已拒绝" value="REJECTED" />
        </el-select>
      </div>

      <el-table
        v-loading="listLoading"
        :data="requestList"
        border
        stripe
        height="360px"
      >
        <el-table-column prop="createdAt" label="申请时间" width="180" />
        <el-table-column prop="patientName" label="病人" width="140" />
        <el-table-column prop="medicineName" label="药品" min-width="160" />
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reason" label="说明" show-overflow-tooltip />
      </el-table>

      <div v-if="total > 0" class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handlePageSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { getPatientList } from '@/api/patient'
import { getMedicineList } from '@/api/pharmacy'
import { getMedicationRequestList, createMedicationRequest, getDoctorList } from '@/api/doctor'

const userStore = useUserStore()

const formRef = ref(null)
const submitting = ref(false)

const form = reactive({
  doctorId: undefined,
  patientId: undefined,
  medicineId: undefined,
  quantity: 1,
  dose: '',
  usage: '',
  reason: ''
})

const rules = {
  doctorId: [{ required: true, message: '请选择开药医生', trigger: 'change' }],
  patientId: [{ required: true, message: '请选择病人', trigger: 'change' }],
  medicineId: [{ required: true, message: '请选择药品', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'change' }]
}

const doctorOptions = ref([])
const doctorLoading = ref(false)

const patientOptions = ref([])
const patientLoading = ref(false)

const medicineOptions = ref([])
const medicineMap = ref({})
const medicineLoading = ref(false)

const listLoading = ref(false)
const requestList = ref([])
const pagination = reactive({
  page: 1,
  pageSize: 10
})
const total = ref(0)

const filters = reactive({
  status: ''
})

const currentDoctorId = computed(() => {
  if (userStore.isDoctor) {
    return userStore.userInfo?.doctor?.id || null
  }
  if (userStore.isAdmin) {
    return form.doctorId
  }
  return null
})

const currentDoctorDisplay = computed(() => {
  const user = userStore.userInfo
  if (!user) return ''
  const name = user.real_name || user.username || ''
  // 从 doctor 对象获取真正的工号
  const doctor = user.doctor
  let doctorNo = doctor?.doctor_no || doctor?.doctorNo || ''
  // 如果工号等于姓名或为空，不显示工号
  if (!doctorNo || doctorNo === name) {
    return name
  }
  return `${name}（${doctorNo}）`
})

const loadDoctorOptions = async () => {
  if (!userStore.isAdmin) return
  doctorLoading.value = true
  try {
    const res = await getDoctorList({ status: 'active', pageSize: 200 })
    const items = res.data?.items || []
    doctorOptions.value = items.map((item) => {
      // 工号处理：如果工号等于姓名或为空，显示"未设置"
      let doctorNo = item.doctorNo || item.doctor_no || ''
      if (!doctorNo || doctorNo === item.name) {
        doctorNo = '未设置'
      }
      return {
        value: item.id,
        label: `${item.name}（${doctorNo}）`
      }
    })
  } catch (error) {
    ElMessage.error('加载医生列表失败')
  } finally {
    doctorLoading.value = false
  }
}

const loadMedicines = async () => {
  medicineLoading.value = true
  try {
    const res = await getMedicineList({ page: 1, per_page: 100 })
    const items = res.data?.items || []
    const map = {}
    medicineOptions.value = items
      .filter((item) => item.status === 'active')
      .map((item) => {
        const stock = item.inventory?.quantity ?? 0
        const option = {
          value: item.id,
          label: `${item.name}（${item.specification || ''}）`,
          stock,
          unit: item.unit || ''
        }
        map[item.id] = item
        return option
      })
    medicineMap.value = map
  } catch (error) {
    ElMessage.error('加载药品列表失败')
  } finally {
    medicineLoading.value = false
  }
}

const remoteSearchPatients = async (query) => {
  if (!query) {
    patientOptions.value = []
    return
  }
  patientLoading.value = true
  try {
    const res = await getPatientList({ page: 1, per_page: 20, search: query })
    const items = res.data?.items || res.data?.list || []
    patientOptions.value = items.map((item) => ({
      value: item.id,
      label: `${item.name}（${item.patient_no}）`
    }))
  } catch (error) {
    ElMessage.error('搜索病人失败')
  } finally {
    patientLoading.value = false
  }
}

const handleMedicineChange = () => {
  const medicine = medicineMap.value[form.medicineId]
  if (medicine && !form.usage) {
    form.usage = medicine.usage || ''
  }
}

const fetchRequestList = async () => {
  if (!currentDoctorId.value) return
  listLoading.value = true
  try {
    const res = await getMedicationRequestList({
      page: pagination.page,
      pageSize: pagination.pageSize,
      doctorId: currentDoctorId.value,
      status: filters.status || undefined
    })
    requestList.value = res.data.list || []
    total.value = res.data.total || 0
  } catch (error) {
    ElMessage.error('加载用药申请列表失败')
  } finally {
    listLoading.value = false
  }
}

const handleDoctorChange = () => {
  pagination.page = 1
  fetchRequestList()
}

const handleFilterChange = () => {
  pagination.page = 1
  fetchRequestList()
}

const handlePageSizeChange = () => {
  pagination.page = 1
  fetchRequestList()
}

const handlePageChange = () => {
  fetchRequestList()
}

const resetForm = () => {
  form.patientId = undefined
  form.medicineId = undefined
  form.quantity = 1
  form.dose = ''
  form.usage = ''
  form.reason = ''
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

const submitForm = async () => {
  if (!formRef.value) return
  if (!currentDoctorId.value) {
    if (userStore.isAdmin) {
      ElMessage.error('请选择开药医生后再提交用药申请')
    } else {
      ElMessage.error('当前登录用户不是医生，无法提交用药申请')
    }
    return
  }

  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      const res = await createMedicationRequest({
        doctorId: currentDoctorId.value,
        patientId: form.patientId,
        medicineId: form.medicineId,
        quantity: form.quantity,
        dose: form.dose,
        usage: form.usage,
        reason: form.reason
      })
      ElMessage.success('用药申请已提交，已自动生成病历记录')
      resetForm()
      fetchRequestList()
    } catch (error) {
      ElMessage.error('提交用药申请失败')
    } finally {
      submitting.value = false
    }
  })
}

const statusLabel = (status) => {
  const map = {
    PENDING: '待审核',
    APPROVED: '已通过',
    REJECTED: '已拒绝',
    DISPENSED: '已发药',
    CANCELLED: '已取消'
  }
  return map[status] || status || '-'
}

const statusTagType = (status) => {
  const map = {
    PENDING: 'warning',
    APPROVED: 'success',
    REJECTED: 'danger',
    DISPENSED: 'success',
    CANCELLED: 'info'
  }
  return map[status] || 'info'
}

const goBack = () => {
  window.history.back()
}

onMounted(async () => {
  if (userStore.isDoctor && currentDoctorId.value) {
    form.doctorId = currentDoctorId.value
  }
  if (userStore.isAdmin) {
    await loadDoctorOptions()
  }
  await loadMedicines()
  await fetchRequestList()
})
</script>

<style scoped>
.doctor-medication-request-container {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 16px;
}

.header-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.page-title {
  font-size: 22px;
  font-weight: 600;
  color: #303133;
}

.page-subtitle {
  font-size: 13px;
  color: #909399;
}

.form-card {
  margin-bottom: 16px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 8px;
}

.list-card {
  margin-top: 8px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.list-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.pagination-container {
  display: flex;
  justify-content: center;
  padding-top: 16px;
}

.option-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.option-name {
  font-size: 14px;
}

.option-meta {
  font-size: 12px;
  color: #909399;
}
</style>
