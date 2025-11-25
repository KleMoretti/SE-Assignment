<template>
  <div class="doctor-dashboard-container">
    <!-- 完善医生信息弹窗 -->
    <el-dialog
      v-model="showDoctorInfoDialog"
      title="完善医生信息"
      width="600px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false"
    >
      <el-alert
        title="请完善您的医生基本信息后再继续使用系统"
        type="warning"
        :closable="false"
        style="margin-bottom: 20px"
      />
      <el-form
        ref="doctorFormRef"
        :model="doctorForm"
        :rules="doctorRules"
        label-width="100px"
      >
        <el-form-item label="工号" prop="doctorNo">
          <el-input v-model="doctorForm.doctorNo" disabled />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="doctorForm.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="性别" prop="gender">
              <el-radio-group v-model="doctorForm.gender">
                <el-radio label="男">男</el-radio>
                <el-radio label="女">女</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="年龄" prop="age">
              <el-input-number v-model="doctorForm.age" :min="22" :max="70" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="科室" prop="department">
              <el-select v-model="doctorForm.department" placeholder="请选择科室" style="width: 100%">
                <el-option label="内科" value="内科" />
                <el-option label="外科" value="外科" />
                <el-option label="儿科" value="儿科" />
                <el-option label="妇产科" value="妇产科" />
                <el-option label="骨科" value="骨科" />
                <el-option label="眼科" value="眼科" />
                <el-option label="耳鼻喉科" value="耳鼻喉科" />
                <el-option label="口腔科" value="口腔科" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="职称" prop="title">
              <el-select v-model="doctorForm.title" placeholder="请选择职称" style="width: 100%">
                <el-option label="主任医师" value="主任医师" />
                <el-option label="副主任医师" value="副主任医师" />
                <el-option label="主治医师" value="主治医师" />
                <el-option label="住院医师" value="住院医师" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="联系电话" prop="phone">
              <el-input v-model="doctorForm.phone" placeholder="请输入联系电话" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="doctorForm.email" placeholder="请输入邮箱" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="学历" prop="education">
          <el-select v-model="doctorForm.education" placeholder="请选择学历" style="width: 100%">
            <el-option label="本科" value="本科" />
            <el-option label="硕士" value="硕士" />
            <el-option label="博士" value="博士" />
          </el-select>
        </el-form-item>
        <el-form-item label="专长" prop="specialty">
          <el-input
            v-model="doctorForm.specialty"
            type="textarea"
            :rows="3"
            placeholder="请输入专长领域"
          />
        </el-form-item>
        <el-form-item label="入职日期" prop="hireDate">
          <el-date-picker
            v-model="doctorForm.hireDate"
            type="date"
            placeholder="选择入职日期"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button type="primary" :loading="submitting" @click="submitDoctorInfo">
          保存并继续
        </el-button>
      </template>
    </el-dialog>

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
            <el-button size="large" @click="goToPatients">
              病人信息
            </el-button>
            <el-button size="large" @click="goToMedicalRecords">
              病历记录
            </el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="14">
        <el-card shadow="never" class="patients-card">
          <div class="card-header">
            <div class="card-title">我的病人列表</div>
            <el-text type="info" size="small">与我有过预约或就诊记录的病人</el-text>
          </div>
          <el-table
            v-loading="loading"
            :data="tableData"
            border
            stripe
            height="360px"
          >
            <el-table-column prop="patient_no" label="病人编号" width="120" />
            <el-table-column prop="name" label="姓名" min-width="100" />
            <el-table-column prop="gender" label="性别" width="80" align="center" />
            <el-table-column prop="age" label="年龄" width="80" align="center" />
            <el-table-column prop="phone" label="联系电话" min-width="120" />
            <el-table-column prop="appointment_count" label="预约次数" width="100" align="center" />
            <el-table-column prop="medical_record_count" label="就诊次数" width="100" align="center" />
            <el-table-column label="最后就诊" min-width="120">
              <template #default="{ row }">
                {{ row.last_visit_date ? row.last_visit_date.split('T')[0] : '暂无' }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { checkDoctorInfo, completeDoctorInfo } from '@/api/auth'
import { getDoctorPatients } from '@/api/doctor'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const tableData = ref([])
const showDoctorInfoDialog = ref(false)
const submitting = ref(false)
const doctorFormRef = ref(null)

const currentDoctorName = computed(() => userStore.userInfo?.real_name || userStore.userInfo?.username || '')

const doctorForm = reactive({
  doctorNo: '',
  name: '',
  gender: '',
  age: null,
  phone: '',
  email: '',
  department: '',
  title: '',
  specialty: '',
  education: '',
  hireDate: ''
})

const doctorRules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  department: [{ required: true, message: '请选择科室', trigger: 'change' }],
  title: [{ required: true, message: '请选择职称', trigger: 'change' }],
  phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ]
}

const fetchDoctorPatients = async () => {
  loading.value = true
  try {
    const doctorId = userStore.userInfo?.doctor?.id
    if (!doctorId) {
      console.warn('未获取到医生ID')
      tableData.value = []
      return
    }
    
    const res = await getDoctorPatients(doctorId)
    tableData.value = res.data?.patients || []
  } catch (error) {
    console.error('加载病人列表失败:', error)
    ElMessage.error('加载病人列表失败')
  } finally {
    loading.value = false
  }
}

const goToMedicationRequest = () => {
  router.push({ name: 'DoctorMedicationRequest' })
}

const goToPatients = () => {
  router.push({ name: 'DoctorPatientList' })
}

const goToMedicalRecords = () => {
  router.push({ name: 'DoctorMedicalRecordList' })
}

const checkDoctorInfoStatus = async () => {
  try {
    const res = await checkDoctorInfo()
    if (res.success && !res.data.is_complete) {
      // 信息不完整，弹出表单
      showDoctorInfoDialog.value = true
      // 预填充已有信息
      if (res.data.doctor) {
        const doctor = res.data.doctor
        // 工号从 doctor 记录中获取（注册时填的）
        doctorForm.doctorNo = doctor.doctor_no || doctor.doctorNo || ''
        doctorForm.name = doctor.name || userStore.userInfo?.real_name || ''
        doctorForm.gender = doctor.gender || ''
        doctorForm.age = doctor.age || null
        doctorForm.phone = doctor.phone || userStore.userInfo?.phone || ''
        doctorForm.email = doctor.email || ''
        doctorForm.department = doctor.department || ''
        doctorForm.title = doctor.title || ''
        doctorForm.specialty = doctor.specialty || ''
        doctorForm.education = doctor.education || ''
        doctorForm.hireDate = doctor.hire_date || ''
      } else {
        // 如果没有 doctor 记录，说明注册时没有正确创建
        // 工号留空，让用户知道有问题
        doctorForm.doctorNo = '（注册异常，请联系管理员）'
        doctorForm.name = userStore.userInfo?.real_name || ''
        doctorForm.phone = userStore.userInfo?.phone || ''
      }
    }
  } catch (error) {
    console.error('检查医生信息失败:', error)
  }
}

const submitDoctorInfo = async () => {
  if (!doctorFormRef.value) return

  await doctorFormRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      const data = {
        name: doctorForm.name,
        gender: doctorForm.gender || undefined,
        age: doctorForm.age || undefined,
        phone: doctorForm.phone || undefined,
        email: doctorForm.email || undefined,
        department: doctorForm.department || undefined,
        title: doctorForm.title || undefined,
        specialty: doctorForm.specialty || undefined,
        education: doctorForm.education || undefined,
        hire_date: doctorForm.hireDate ? (doctorForm.hireDate instanceof Date ? doctorForm.hireDate.toISOString().split('T')[0] : doctorForm.hireDate) : undefined
      }

      await completeDoctorInfo(data)
      ElMessage.success('医生信息保存成功')
      showDoctorInfoDialog.value = false

      // 刷新用户信息（等待1秒确保后端数据更新完成）
      setTimeout(async () => {
        try {
          await userStore.getUserInfo()
        } catch (error) {
          console.error('刷新用户信息失败:', error)
        }
      }, 1000)
    } catch (error) {
      ElMessage.error('保存医生信息失败')
    } finally {
      submitting.value = false
    }
  })
}

onMounted(async () => {
  // 先检查医生信息是否完整
  if (userStore.isDoctor) {
    await checkDoctorInfoStatus()
  }
  // 加载医生关联的病人列表
  fetchDoctorPatients()
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
.patients-card {
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
