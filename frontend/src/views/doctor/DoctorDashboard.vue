<template>
  <div class="doctor-dashboard-container">
    <!-- 欢迎标题 -->
    <div class="welcome-section">
      <h1 class="welcome-title">
        <el-icon class="title-icon"><Odometer /></el-icon>
        医生工作台
      </h1>
      <p class="welcome-subtitle">{{ currentDoctorName }}，欢迎回来！</p>
    </div>

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

    <!-- 服务卡片网格 -->
    <div class="service-grid">
      <div class="service-card" @click="goToMedicationRequest">
        <div class="card-icon medication-icon">
          <el-icon><DocumentCopy /></el-icon>
        </div>
        <h3 class="card-title">开药管理</h3>
        <p class="card-description">管理和审批药品处方申请</p>
        <div class="card-arrow">
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>

      <div class="service-card" @click="goToPatients">
        <div class="card-icon patients-icon">
          <el-icon><User /></el-icon>
        </div>
        <h3 class="card-title">病人信息</h3>
        <p class="card-description">查看和管理病人档案</p>
        <div class="card-arrow">
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>

      <div class="service-card" @click="goToMedicalRecords">
        <div class="card-icon records-icon">
          <el-icon><Notebook /></el-icon>
        </div>
        <h3 class="card-title">病历记录</h3>
        <p class="card-description">查看和编辑病历档案</p>
        <div class="card-arrow">
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>
    </div>

    <!-- 我的病人列表 -->
    <el-card shadow="never" class="patients-table-card">
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { Odometer, DocumentCopy, User, Notebook, ArrowRight } from '@element-plus/icons-vue'
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
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20px;
  padding-bottom: 40px;
  box-sizing: border-box;
}

/* 欢迎区域 */
.welcome-section {
  text-align: center;
  margin-bottom: 50px;
  padding-top: 40px;
  animation: fadeInDown 0.6s ease-out;
}

.welcome-title {
  color: #2c3e50;
  font-size: 36px;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.title-icon {
  font-size: 36px;
  color: #67c23a;
}

.welcome-subtitle {
  color: #606266;
  font-size: 16px;
  margin-top: 10px;
  font-weight: 400;
}

/* 服务卡片网格 */
.service-grid {
  display: flex;
  justify-content: center;
  align-items: stretch;
  gap: 20px;
  max-width: 1200px;
  margin: 0 auto 40px;
  flex-wrap: wrap;
}

.service-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 35px 25px;
  width: 280px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e4e7ed;
  position: relative;
  animation: fadeInUp 0.6s ease-out backwards;
}

.service-card:nth-child(1) {
  animation-delay: 0.1s;
}

.service-card:nth-child(2) {
  animation-delay: 0.2s;
}

.service-card:nth-child(3) {
  animation-delay: 0.3s;
}

.service-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #67c23a;
}

.card-icon {
  width: 70px;
  height: 70px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  margin: 0 auto 20px;
  transition: all 0.3s ease;
}

.medication-icon {
  background: #f0f9ff;
  color: #409eff;
}

.patients-icon {
  background: #fef0f0;
  color: #f56c6c;
}

.records-icon {
  background: #f4f4f5;
  color: #909399;
}

.service-card:hover .card-icon {
  transform: scale(1.05);
}

.card-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 10px 0;
  text-align: center;
}

.card-description {
  font-size: 14px;
  color: #909399;
  margin: 0;
  text-align: center;
  line-height: 1.5;
}

.card-arrow {
  position: absolute;
  bottom: 20px;
  right: 20px;
  font-size: 18px;
  color: #c0c4cc;
  opacity: 0;
  transform: translateX(-5px);
  transition: all 0.3s ease;
}

.service-card:hover .card-arrow {
  opacity: 0.6;
  transform: translateX(0);
  color: #67c23a;
}

/* 病人列表卡片 */
.patients-table-card {
  max-width: 1200px;
  margin: 0 auto;
  animation: fadeInUp 0.6s ease-out 0.4s backwards;
}

.patients-table-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.patients-table-card .card-title {
  text-align: left;
  margin: 0;
  font-size: 18px;
}

/* 动画 */
@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .welcome-title {
    font-size: 28px;
  }

  .title-icon {
    font-size: 28px;
  }

  .welcome-subtitle {
    font-size: 14px;
  }

  .service-grid {
    flex-direction: column;
    align-items: center;
  }

  .service-card {
    width: 100%;
    max-width: 400px;
  }
}
</style>
