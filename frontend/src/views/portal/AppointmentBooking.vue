<template>
  <div class="booking-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <el-button :icon="ArrowLeft" @click="goBack" circle></el-button>
          <span class="title">在线预约挂号</span>
          <div class="header-placeholder"></div>
        </div>
      </template>

      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px" class="booking-form">
        <el-form-item label="就诊人" prop="patient_id">
          <el-select v-model="form.patient_id" placeholder="请选择就诊人" size="large">
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
            <el-option
              v-for="p in managedPatients"
              :key="p.id"
              :label="p.name"
              :value="p.id"
            ></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="选择科室" prop="department">
          <el-select v-model="form.department" placeholder="请选择科室" size="large" @change="handleDepartmentChange">
            <template #prefix>
              <el-icon><FolderOpened /></el-icon>
            </template>
            <el-option v-for="dept in departments" :key="dept" :label="dept" :value="dept"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="选择医生" prop="doctor_id">
          <el-select v-model="form.doctor_id" placeholder="请先选择科室" size="large" :disabled="!form.department">
            <template #prefix>
              <el-icon><Avatar /></el-icon>
            </template>
            <el-option v-for="doctor in availableDoctors" :key="doctor.id" :label="doctor.name" :value="doctor.id"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="预约日期" prop="appointment_date">
          <el-date-picker
            v-model="form.appointment_date"
            type="date"
            placeholder="选择日期"
            size="large"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            :disabled-date="disabledDate"
            style="width: 100%"
          ></el-date-picker>
        </el-form-item>

        <el-form-item label="预约时间" prop="appointment_time">
          <el-time-select
            v-model="form.appointment_time"
            size="large"
            start="08:30"
            step="00:30"
            end="17:30"
            placeholder="选择时间"
            style="width: 100%"
          ></el-time-select>
        </el-form-item>

        <el-form-item label="病情描述" prop="notes">
          <el-input
            v-model="form.notes"
            type="textarea"
            :rows="4"
            placeholder="请简单描述您的病情或需要咨询的问题"
            maxlength="200"
            show-word-limit
          ></el-input>
        </el-form-item>

        <el-form-item>
          <div class="form-actions">
            <el-button type="primary" size="large" @click="submitForm" :loading="submitLoading">
              <el-icon class="el-icon--left"><Check /></el-icon>
              立即预约
            </el-button>
            <el-button size="large" @click="resetForm">
              <el-icon class="el-icon--left"><RefreshLeft /></el-icon>
              重置
            </el-button>
          </div>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getDoctorList } from '@/api/doctor'
import { getManagedPatients, createPortalAppointment } from '@/api/patient'
import { ArrowLeft, User, FolderOpened, Avatar, Check, RefreshLeft } from '@element-plus/icons-vue'

const router = useRouter()
const formRef = ref(null)
const submitLoading = ref(false)

// --- Data ---
const form = reactive({
  patient_id: null,
  doctor_id: null,
  department: '',
  appointment_date: '',
  appointment_time: '',
  notes: ''
})

const rules = {
  patient_id: [{ required: true, message: '请选择就诊人', trigger: 'change' }],
  department: [{ required: true, message: '请选择科室', trigger: 'change' }],
  doctor_id: [{ required: true, message: '请选择医生', trigger: 'change' }],
  appointment_date: [{ required: true, message: '请选择预约日期', trigger: 'change' }],
  appointment_time: [{ required: true, message: '请选择预约时间', trigger: 'change' }]
}

const managedPatients = ref([])
const allDoctors = ref([])
const availableDoctors = ref([])
const departments = ref([])

// --- Methods ---
const fetchData = async () => {
  try {
    // 并行请求获取数据
    const patientRes = await getManagedPatients()
    managedPatients.value = patientRes.data || []

    const doctorRes = await getDoctorList()
    allDoctors.value = doctorRes.data.items || []
    const deptSet = new Set(allDoctors.value.map(d => d.department))
    departments.value = Array.from(deptSet)

  } catch (error) {
    ElMessage.error('加载基础数据失败，请稍后重试')
  }
}

onMounted(() => {
  // 连接真实数据库
  fetchData()
})

const handleDepartmentChange = (selectedDept) => {
  form.doctor_id = null
  availableDoctors.value = allDoctors.value.filter(d => d.department === selectedDept)
}

const disabledDate = (time) => {
  return time.getTime() < Date.now() - 8.64e7 // Cannot select days before today
}

const goBack = () => {
  router.push({ name: 'PortalIndex' })
}

const submitForm = () => {
  formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        await createPortalAppointment(form)
        ElMessage.success('预约成功！')
        router.push({ name: 'PortalIndex' })
      } catch (error) {
        console.error('预约失败:', error)
      } finally {
        submitLoading.value = false
      }
    }
  })
}

const resetForm = () => {
  formRef.value.resetFields()
  availableDoctors.value = []
}
</script>

<style scoped>
.booking-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
  padding-bottom: 40px;
  box-sizing: border-box;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.box-card {
  width: 100%;
  max-width: 700px;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  margin-top: 20px;
  animation: slideInUp 0.5s ease-out;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
}

.title {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-placeholder {
  width: 40px;
}

.booking-form {
  padding: 30px 20px 10px;
}

.booking-form :deep(.el-form-item__label) {
  font-weight: 600;
  color: #2c3e50;
}

.booking-form :deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.booking-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.booking-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.25);
}

.booking-form :deep(.el-textarea__inner) {
  border-radius: 8px;
  padding: 12px;
  font-size: 14px;
  line-height: 1.6;
}

.form-actions {
  display: flex;
  gap: 12px;
  padding-top: 10px;
}

.form-actions .el-button {
  border-radius: 8px;
  font-weight: 500;
  padding: 12px 32px;
  transition: all 0.3s ease;
}

.form-actions .el-button--primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.form-actions .el-button--primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

/* 动画 */
@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .box-card {
    margin: 0;
  }

  .booking-form {
    padding: 20px 10px 10px;
  }

  .form-actions {
    flex-direction: column;
  }

  .form-actions .el-button {
    width: 100%;
  }
}
</style>
