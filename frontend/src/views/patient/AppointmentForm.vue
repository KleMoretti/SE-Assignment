<template>
  <el-card class="box-card">
    <template #header>
      <div class="flex justify-between items-center">
        <span class="text-xl font-semibold">在线挂号</span>
        <el-button @click="goBack">返回列表</el-button>
      </div>
    </template>
    <el-form :model="form" :rules="rules" ref="formRef" label-width="120px" class="p-4">
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
        <el-date-picker v-model="form.appointment_date" type="date" placeholder="选择日期" format="YYYY-MM-DD" value-format="YYYY-MM-DD"></el-date-picker>
      </el-form-item>
      <el-form-item label="预约时间" prop="appointment_time">
        <el-time-select v-model="form.appointment_time" start="08:30" step="00:30" end="17:30" placeholder="选择时间"></el-time-select>
      </el-form-item>
      <el-form-item label="备注" prop="notes">
        <el-input v-model="form.notes" type="textarea" placeholder="请输入病情描述或其他备注"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submitForm">立即预约</el-button>
        <el-button @click="resetForm">重置</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getDoctorList } from '@/api/doctor'
import { addAppointment } from '@/api/patient'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)

const form = reactive({
  patient_id: userStore.userInfo?.id,
  doctor_id: null,
  department: '',
  appointment_date: '',
  appointment_time: '',
  notes: ''
})

const rules = reactive({
  department: [{ required: true, message: '请选择科室', trigger: 'change' }],
  doctor_id: [{ required: true, message: '请选择医生', trigger: 'change' }],
  appointment_date: [{ required: true, message: '请选择预约日期', trigger: 'change' }],
  appointment_time: [{ required: true, message: '请选择预约时间', trigger: 'change' }]
})

const allDoctors = ref([])
const availableDoctors = ref([])
const departments = ref([])

onMounted(async () => {
  try {
    const res = await getDoctorList()
    allDoctors.value = res.data.items
    // 从医生列表动态生成科室列表
    const deptSet = new Set(res.data.items.map(d => d.department))
    departments.value = Array.from(deptSet)
  } catch (error) {
    ElMessage.error('获取医生列表失败')
  }
})

const handleDepartmentChange = (selectedDept) => {
  form.doctor_id = null // Reset doctor selection
  availableDoctors.value = allDoctors.value.filter(d => d.department === selectedDept)
}

const goBack = () => {
  router.push({ name: 'AppointmentList' })
}

const submitForm = () => {
  formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await addAppointment(form)
        ElMessage.success('预约成功！')
        goBack()
      } catch (error) {
        ElMessage.error('预约失败，请重试')
      }
    } else {
      ElMessage.error('请检查表单是否填写完整')
      return false
    }
  })
}

const resetForm = () => {
  formRef.value.resetFields()
  availableDoctors.value = []
}
</script>

<style scoped>
.box-card {
  margin: 20px;
  min-height: calc(100vh - 100px);
}
</style>

