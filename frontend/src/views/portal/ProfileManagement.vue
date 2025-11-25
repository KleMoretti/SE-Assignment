<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <el-icon><User /></el-icon>
          <span>个人信息管理</span>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <!-- 用户信息标签 -->
        <el-tab-pane label="账户信息" name="account">
          <el-form
            ref="profileFormRef"
            :model="profileForm"
            :rules="profileRules"
            label-width="120px"
            class="profile-form"
          >
            <el-form-item label="用户名">
              <el-input v-model="profileForm.username" disabled>
                <template #prefix>
                  <el-icon><User /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item label="手机号" prop="phone">
              <el-input v-model="profileForm.phone" placeholder="请输入手机号">
                <template #prefix>
                  <el-icon><Phone /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item label="邮箱" prop="email">
              <el-input v-model="profileForm.email" placeholder="请输入邮箱（选填）">
                <template #prefix>
                  <el-icon><Message /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item label="角色">
              <el-tag :type="getRoleType(profileForm.role)">
                {{ getRoleLabel(profileForm.role) }}
              </el-tag>
            </el-form-item>

            <el-form-item label="注册时间">
              <el-input :value="formatDate(profileForm.created_at)" disabled>
                <template #prefix>
                  <el-icon><Calendar /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item label="最后登录">
              <el-input :value="formatDate(profileForm.last_login)" disabled>
                <template #prefix>
                  <el-icon><Clock /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-divider />

            <el-form-item>
              <el-button type="primary" @click="handleSubmitProfile" :loading="loading">
                <el-icon><Check /></el-icon>
                保存修改
              </el-button>
              <el-button @click="handleResetProfile">
                <el-icon><RefreshLeft /></el-icon>
                重置
              </el-button>
              <el-button @click="showPasswordDialog = true">
                <el-icon><Lock /></el-icon>
                修改密码
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 病人信息标签 -->
        <el-tab-pane label="病人档案" name="patient">
          <el-alert
            v-if="!patientInfo.patient_no"
            title="未找到病人档案"
            type="info"
            description="您还没有病人档案信息"
            :closable="false"
            style="margin-bottom: 20px;"
          />

          <el-form
            v-else
            ref="patientFormRef"
            :model="patientForm"
            :rules="patientRules"
            label-width="120px"
            class="profile-form"
          >
            <el-form-item label="病人编号">
              <el-input v-model="patientInfo.patient_no" disabled>
                <template #prefix>
                  <el-icon><Tickets /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item label="姓名" prop="name">
              <el-input v-model="patientForm.name" placeholder="请输入真实姓名">
                <template #prefix>
                  <el-icon><User /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item label="性别" prop="gender">
              <el-radio-group v-model="patientForm.gender">
                <el-radio label="男">男</el-radio>
                <el-radio label="女">女</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="年龄" prop="age">
              <el-input-number
                v-model="patientForm.age"
                :min="1"
                :max="150"
                placeholder="请输入年龄"
                style="width: 100%"
              />
            </el-form-item>

            <el-form-item label="联系电话">
              <el-input v-model="patientInfo.phone" disabled>
                <template #prefix>
                  <el-icon><Phone /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item label="身份证号" prop="id_card">
              <el-input v-model="patientForm.id_card" placeholder="请输入身份证号" maxlength="18">
                <template #prefix>
                  <el-icon><CreditCard /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item label="居住地址" prop="address">
              <el-input
                v-model="patientForm.address"
                type="textarea"
                :rows="3"
                placeholder="请输入居住地址"
              />
            </el-form-item>

            <el-divider />

            <el-form-item>
              <el-button type="primary" @click="handleSubmitPatient" :loading="patientLoading">
                <el-icon><Check /></el-icon>
                保存病人信息
              </el-button>
              <el-button @click="handleResetPatient">
                <el-icon><RefreshLeft /></el-icon>
                重置
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="showPasswordDialog"
      title="修改密码"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="100px"
      >
        <el-form-item label="旧密码" prop="old_password">
          <el-input
            v-model="passwordForm.old_password"
            type="password"
            placeholder="请输入旧密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="新密码" prop="new_password">
          <el-input
            v-model="passwordForm.new_password"
            type="password"
            placeholder="请输入新密码（至少6位）"
            show-password
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirm_password">
          <el-input
            v-model="passwordForm.confirm_password"
            type="password"
            placeholder="请再次输入新密码"
            show-password
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showPasswordDialog = false">取消</el-button>
        <el-button type="primary" @click="handleChangePassword" :loading="passwordLoading">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  User,
  Message,
  Phone,
  Calendar,
  Clock,
  Check,
  RefreshLeft,
  Lock,
  Tickets,
  CreditCard
} from '@element-plus/icons-vue'
import { getCurrentUser, updateProfile, changePassword, checkPatientInfo, completePatientInfo } from '@/api/auth'
import { formatDate } from '@/utils/format'

// 当前标签
const activeTab = ref('account')

// 表单引用
const profileFormRef = ref(null)
const patientFormRef = ref(null)
const passwordFormRef = ref(null)

// 加载状态
const loading = ref(false)
const patientLoading = ref(false)
const passwordLoading = ref(false)

// 个人信息表单
const profileForm = reactive({
  id: null,
  username: '',
  real_name: '',
  email: '',
  phone: '',
  role: '',
  department: '',
  created_at: '',
  last_login: ''
})

// 病人信息
const patientInfo = reactive({
  patient_no: '',
  phone: '',
  created_at: '',
  updated_at: ''
})

// 病人信息表单
const patientForm = reactive({
  name: '',
  gender: '',
  age: null,
  id_card: '',
  address: ''
})

// 原始数据备份
let originalProfileData = {}
let originalPatientData = {}

// 修改密码对话框
const showPasswordDialog = ref(false)

// 修改密码表单
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

// 身份证号验证
const validateIdCard = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入身份证号'))
  } else if (!/^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$/.test(value)) {
    callback(new Error('请输入正确的身份证号'))
  } else {
    callback()
  }
}

// 表单验证规则
const profileRules = {
  email: [
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ]
}

// 病人信息验证规则
const patientRules = {
  name: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '姓名长度在2-20个字符', trigger: 'blur' }
  ],
  gender: [
    { required: true, message: '请选择性别', trigger: 'change' }
  ],
  age: [
    { required: true, message: '请输入年龄', trigger: 'blur' },
    { type: 'number', min: 1, max: 150, message: '年龄必须在1-150之间', trigger: 'blur' }
  ],
  id_card: [
    { required: true, validator: validateIdCard, trigger: 'blur' }
  ],
  address: [
    { required: true, message: '请输入居住地址', trigger: 'blur' }
  ]
}

// 密码表单验证规则
const passwordRules = {
  old_password: [
    { required: true, message: '请输入旧密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 获取角色标签
const getRoleLabel = (role) => {
  const roleMap = {
    admin: '管理员',
    doctor: '医生',
    nurse: '护士',
    user: '普通用户'
  }
  return roleMap[role] || role
}

// 获取角色类型
const getRoleType = (role) => {
  const typeMap = {
    admin: 'danger',
    doctor: 'success',
    nurse: 'warning',
    user: 'info'
  }
  return typeMap[role] || 'info'
}

// 加载用户信息
const loadUserInfo = async () => {
  try {
    loading.value = true
    const response = await getCurrentUser()

    if (response.success) {
      const userData = response.data
      Object.keys(profileForm).forEach(key => {
        if (userData[key] !== undefined) {
          profileForm[key] = userData[key]
        }
      })
      originalProfileData = { ...userData }
    } else {
      ElMessage.error(response.message || '获取用户信息失败')
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
    ElMessage.error('加载用户信息失败')
  } finally {
    loading.value = false
  }
}

// 加载病人信息
const loadPatientInfo = async () => {
  try {
    const response = await checkPatientInfo()

    if (response.success && response.data && response.data.patient) {
      const patient = response.data.patient

      // 更新病人基础信息
      patientInfo.patient_no = patient.patient_no || ''
      patientInfo.phone = patient.phone || ''
      patientInfo.created_at = patient.created_at || ''
      patientInfo.updated_at = patient.updated_at || ''

      // 更新可编辑的表单数据
      patientForm.name = patient.name || ''
      patientForm.gender = patient.gender || ''
      patientForm.age = patient.age || null
      patientForm.id_card = patient.id_card || ''
      patientForm.address = patient.address || ''

      originalPatientData = { ...patient }
    }
  } catch (error) {
    console.error('加载病人信息失败:', error)
  }
}

// 提交个人信息
const handleSubmitProfile = async () => {
  try {
    await profileFormRef.value.validate()
    loading.value = true

    const updateData = {
      real_name: profileForm.real_name,
      email: profileForm.email,
      phone: profileForm.phone
    }

    const response = await updateProfile(updateData)

    if (response.success) {
      ElMessage.success('个人信息更新成功')
      await loadUserInfo()
    } else {
      ElMessage.error(response.message || '更新失败')
    }
  } catch (error) {
    console.error('更新个人信息失败:', error)
    ElMessage.error('更新失败')
  } finally {
    loading.value = false
  }
}

// 提交病人信息
const handleSubmitPatient = async () => {
  try {
    await patientFormRef.value.validate()
    patientLoading.value = true

    const response = await completePatientInfo(patientForm)

    if (response.success) {
      ElMessage.success('病人信息更新成功')
      await loadPatientInfo()
    } else {
      ElMessage.error(response.message || '更新失败')
    }
  } catch (error) {
    console.error('更新病人信息失败:', error)
    ElMessage.error('更新失败')
  } finally {
    patientLoading.value = false
  }
}

// 重置个人信息
const handleResetProfile = () => {
  Object.keys(profileForm).forEach(key => {
    if (originalProfileData[key] !== undefined) {
      profileForm[key] = originalProfileData[key]
    }
  })
  profileFormRef.value?.clearValidate()
}

// 重置病人信息
const handleResetPatient = () => {
  patientForm.name = originalPatientData.name || ''
  patientForm.gender = originalPatientData.gender || ''
  patientForm.age = originalPatientData.age || null
  patientForm.id_card = originalPatientData.id_card || ''
  patientForm.address = originalPatientData.address || ''
  patientFormRef.value?.clearValidate()
}

// 修改密码
const handleChangePassword = async () => {
  try {
    await passwordFormRef.value.validate()
    passwordLoading.value = true

    const response = await changePassword({
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password
    })

    if (response.success) {
      ElMessage.success('密码修改成功')
      showPasswordDialog.value = false
      passwordForm.old_password = ''
      passwordForm.new_password = ''
      passwordForm.confirm_password = ''
    } else {
      ElMessage.error(response.message || '密码修改失败')
    }
  } catch (error) {
    console.error('修改密码失败:', error)
    ElMessage.error('修改密码失败')
  } finally {
    passwordLoading.value = false
  }
}

// 页面加载时获取数据
onMounted(() => {
  loadUserInfo()
  loadPatientInfo()
})
</script>

<style scoped>
.profile-container {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.profile-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: bold;
}

.profile-form {
  padding: 20px 0;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}
</style>
