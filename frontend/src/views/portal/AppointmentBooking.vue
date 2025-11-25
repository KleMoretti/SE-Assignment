<template>
  <div class="booking-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <el-button :icon="ArrowLeft" @click="goBack" circle></el-button>
          <span class="title">在线预约挂号</span>
          <div></div> <!-- Placeholder for alignment -->
        </div>
      </template>

      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px" class="booking-form">
        <el-form-item label="就诊人" prop="patient_id">
          <el-select v-model="form.patient_id" placeholder="请选择就诊人">
            <el-option
              v-for="p in managedPatients"
              :key="p.id"
              :label="p.name"
              :value="p.id"
            ></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="选择科室" prop="department">
          <el-select v-model="form.department" placeholder="请选择科室" @change="handleDepartmentChange">
            <el-option v-for="dept in departments" :key="dept" :label="dept" :value="dept"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="选择医生" prop="doctor_id">
          <el-select v-model="form.doctor_id" placeholder="请先选择科室" :disabled="!form.department">
            <el-option v-for="doctor in availableDoctors" :key="doctor.id" :label="doctor.name" :value="doctor.id"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="预约日期" prop="appointment_date">
          <el-date-picker
            v-model="form.appointment_date"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            :disabled-date="disabledDate"
          ></el-date-picker>
        </el-form-item>

        <el-form-item label="预约时间" prop="appointment_time">
          <el-time-select
            v-model="form.appointment_time"
            start="08:30"
            step="00:30"
            end="17:30"
            placeholder="选择时间"
          ></el-time-select>
        </el-form-item>

        <el-form-item label="病情描述" prop="notes">
          <el-input v-model="form.notes" type="textarea" placeholder="请简单描述您的病情或需要咨询的问题"></el-input>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitForm" :loading="submitLoading">立即预约</el-button>
          <el-button @click="resetForm">重置</el-button>
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
import { ArrowLeft } from '@element-plus/icons-vue'

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
  display: flex;
  justify-content: center;
  padding: 20px;
  background-color: #f5f7fa;
}
.box-card {
  width: 800px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.title {
  font-size: 20px;
  font-weight: bold;
}
.booking-form {
  padding: 20px 20px 0 0;
}
</style>
