<template>
  <el-card class="box-card">
    <template #header>
      <div class="flex justify-between items-center">
        <span class="text-xl font-semibold">在线挂号</span>
        <el-button @click="goBack">返回列表</el-button>
      </div>
    </template>

    <el-form :model="form" :rules="rules" ref="formRef" label-width="120px" class="p-4">
      <!-- 第一步：选择病人 -->
      <el-divider content-position="left">
        <span class="text-lg font-semibold">第一步：选择病人</span>
      </el-divider>

      <el-form-item label="搜索病人" prop="patientSearch">
        <el-row :gutter="10">
          <el-col :span="18">
            <el-input
              v-model="patientSearchText"
              placeholder="请输入身份证号、病人编号或姓名"
              clearable
              @keyup.enter="searchPatient"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-col>
          <el-col :span="6">
            <el-button type="primary" @click="searchPatient" :loading="searchLoading">搜索</el-button>
          </el-col>
        </el-row>
      </el-form-item>

      <el-form-item label="或直接选择" prop="patient_id">
        <el-select
          v-model="form.patient_id"
          placeholder="请选择病人"
          filterable
          @change="handlePatientChange"
        >
          <el-option
            v-for="patient in patients"
            :key="patient.id"
            :label="`${patient.name} (${patient.patient_no})`"
            :value="patient.id"
          >
            <span>{{ patient.name }}</span>
            <span style="color: var(--el-text-color-secondary); margin-left: 10px;">
              {{ patient.patient_no }}
            </span>
          </el-option>
        </el-select>
      </el-form-item>

      <!-- 病人信息展示 -->
      <el-alert
        v-if="selectedPatient"
        type="info"
        :closable="false"
        class="mb-4"
      >
        <template #title>
          <strong>病人信息</strong>
        </template>
        <div class="grid grid-cols-2 gap-2 text-sm">
          <div><strong>姓名：</strong>{{ selectedPatient.name }}</div>
          <div><strong>编号：</strong>{{ selectedPatient.patient_no }}</div>
          <div><strong>性别：</strong>{{ selectedPatient.gender }}</div>
          <div><strong>年龄：</strong>{{ selectedPatient.age || '未知' }}</div>
          <div><strong>身份证：</strong>{{ selectedPatient.id_card || '无' }}</div>
          <div><strong>电话：</strong>{{ selectedPatient.phone || '无' }}</div>
        </div>
      </el-alert>

      <!-- 第二步：预约信息 -->
      <el-divider content-position="left">
        <span class="text-lg font-semibold">第二步：预约信息</span>
      </el-divider>

      <el-form-item label="选择科室" prop="department">
        <el-select v-model="form.department" placeholder="请选择科室" @change="handleDepartmentChange">
          <el-option v-for="dept in departments" :key="dept" :label="dept" :value="dept"></el-option>
        </el-select>
      </el-form-item>

      <el-form-item label="选择医生" prop="doctor_id">
        <el-select v-model="form.doctor_id" placeholder="请先选择科室" :disabled="!form.department">
          <el-option
            v-for="doctor in availableDoctors"
            :key="doctor.id"
            :label="`${doctor.name} - ${doctor.title || '医生'}`"
            :value="doctor.id"
          >
            <span>{{ doctor.name }}</span>
            <span style="color: var(--el-text-color-secondary); margin-left: 10px;">
              {{ doctor.title || '医生' }}
            </span>
          </el-option>
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
          start="08:00"
          step="00:30"
          end="17:00"
          placeholder="选择时间"
        ></el-time-select>
      </el-form-item>

      <el-form-item label="备注" prop="notes">
        <el-input
          v-model="form.notes"
          type="textarea"
          :rows="3"
          placeholder="请输入病情描述或其他备注"
        ></el-input>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="submitForm" :loading="submitting">立即预约</el-button>
        <el-button @click="resetForm">重置</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { getDoctorList } from '@/api/doctor'
import { addAppointment, getPatientList } from '@/api/patient'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)

const form = reactive({
  patient_id: null,
  doctor_id: null,
  department: '',
  appointment_date: '',
  appointment_time: '',
  notes: ''
})

const rules = reactive({
  patient_id: [{ required: true, message: '请选择病人', trigger: 'change' }],
  department: [{ required: true, message: '请选择科室', trigger: 'change' }],
  doctor_id: [{ required: true, message: '请选择医生', trigger: 'change' }],
  appointment_date: [{ required: true, message: '请选择预约日期', trigger: 'change' }],
  appointment_time: [{ required: true, message: '请选择预约时间', trigger: 'change' }]
})

const patients = ref([])
const patientSearchText = ref('')
const searchLoading = ref(false)
const selectedPatient = ref(null)
const allDoctors = ref([])
const availableDoctors = ref([])
const departments = ref([])
const submitting = ref(false)

// 禁用今天之前的日期
const disabledDate = (time) => {
  return time.getTime() < Date.now() - 24 * 60 * 60 * 1000
}

onMounted(async () => {
  await loadPatients()
  await loadDoctors()
})

// 加载病人列表
const loadPatients = async () => {
  try {
    const res = await getPatientList({ per_page: 1000 })
    patients.value = res.data.items || []
  } catch (error) {
    console.error('获取病人列表失败:', error)
    ElMessage.error('获取病人列表失败')
  }
}

// 加载医生列表
const loadDoctors = async () => {
  try {
    const res = await getDoctorList({ status: 'active', per_page: 1000 })
    allDoctors.value = res.data.items || []
    // 从医生列表动态生成科室列表
    const deptSet = new Set(res.data.items.map(d => d.department))
    departments.value = Array.from(deptSet).sort()
  } catch (error) {
    console.error('获取医生列表失败:', error)
    ElMessage.error('获取医生列表失败')
  }
}

// 搜索病人
const searchPatient = () => {
  if (!patientSearchText.value.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }

  searchLoading.value = true
  const searchText = patientSearchText.value.trim().toLowerCase()

  setTimeout(() => {
    const found = patients.value.find(p =>
      (p.name && p.name.toLowerCase().includes(searchText)) ||
      (p.patient_no && p.patient_no.toLowerCase().includes(searchText)) ||
      (p.id_card && p.id_card.toLowerCase().includes(searchText))
    )

    if (found) {
      form.patient_id = found.id
      selectedPatient.value = found
      ElMessage.success(`找到病人：${found.name}`)
    } else {
      ElMessage.warning('未找到匹配的病人，请检查输入是否正确')
    }

    searchLoading.value = false
  }, 300)
}

// 病人选择改变
const handlePatientChange = (patientId) => {
  const patient = patients.value.find(p => p.id === patientId)
  selectedPatient.value = patient || null
}

// 科室选择改变
const handleDepartmentChange = (selectedDept) => {
  form.doctor_id = null // 重置医生选择
  availableDoctors.value = allDoctors.value.filter(d => d.department === selectedDept)

  if (availableDoctors.value.length === 0) {
    ElMessage.warning('该科室暂无可预约医生')
  }
}

const goBack = () => {
  router.push({ name: 'AppointmentList' })
}

const submitForm = () => {
  formRef.value.validate(async (valid) => {
    if (valid) {
      if (!form.patient_id) {
        ElMessage.error('请先选择病人')
        return
      }

      submitting.value = true
      try {
        await addAppointment(form)
        ElMessage.success('预约成功！')
        goBack()
      } catch (error) {
        console.error('预约失败:', error)
        const errorMsg = error.response?.data?.message || error.message || '预约失败，请重试'
        ElMessage.error(errorMsg)
      } finally {
        submitting.value = false
      }
    } else {
      ElMessage.error('请检查表单是否填写完整')
      return false
    }
  })
}

const resetForm = () => {
  formRef.value.resetFields()
  selectedPatient.value = null
  availableDoctors.value = []
  patientSearchText.value = ''
}
</script>

<style scoped>
.box-card {
  margin: 20px;
  min-height: calc(100vh - 100px);
}

:deep(.el-alert__content) {
  width: 100%;
}

.grid {
  display: grid;
}

.grid-cols-2 {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.gap-2 {
  gap: 0.5rem;
}
</style>
