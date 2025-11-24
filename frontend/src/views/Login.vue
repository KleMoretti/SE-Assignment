<template>
  <div class="login-container" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center;">
    <div class="login-box" style="background: white; padding: 40px; border-radius: 12px; max-width: 420px; width: 100%;">
      <div class="login-header" style="text-align: center; margin-bottom: 30px;">
        <h2 style="margin: 0 0 10px 0; font-size: 24px; color: #333;">🏥 医院综合管理系统</h2>
        <p style="margin: 0; font-size: 14px; color: #999;">Hospital Management System</p>
      </div>

      <el-tabs v-model="activeTab" class="login-tabs">
        <!-- 登录表单 -->
        <el-tab-pane label="登录" name="login">
          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            class="login-form"
          >
            <el-form-item prop="username">
              <el-input
                v-model="loginForm.username"
                placeholder="请输入用户名"
                prefix-icon="User"
                size="large"
                clearable
              />
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                prefix-icon="Lock"
                size="large"
                show-password
                @keyup.enter="handleLogin"
              />
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="loading"
                class="login-button"
                @click="handleLogin"
              >
                {{ loading ? '登录中...' : '登录' }}
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 注册表单 -->
        <el-tab-pane label="注册" name="register">
          <el-form
            ref="registerFormRef"
            :model="registerForm"
            :rules="registerRules"
            class="login-form"
          >
            <el-form-item prop="username">
              <el-input
                v-model="registerForm.username"
                placeholder="请输入用户名"
                prefix-icon="User"
                size="large"
                clearable
              />
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="请输入密码（至少6位）"
                prefix-icon="Lock"
                size="large"
                show-password
              />
            </el-form-item>

            <el-form-item prop="confirmPassword">
              <el-input
                v-model="registerForm.confirmPassword"
                type="password"
                placeholder="请确认密码"
                prefix-icon="Lock"
                size="large"
                show-password
              />
            </el-form-item>

            <el-form-item prop="role">
              <el-select
                v-model="registerForm.role"
                placeholder="请选择角色"
                size="large"
                style="width: 100%"
              >
                <el-option label="普通用户" value="user" />
                <el-option label="医生" value="doctor" />
                <el-option label="管理员" value="admin" />
              </el-select>
            </el-form-item>

            <!-- 管理员和医生需要输入口令 -->
            <el-form-item v-if="registerForm.role === 'admin' || registerForm.role === 'doctor'" prop="accessCode">
              <el-input
                v-model="registerForm.accessCode"
                type="password"
                placeholder="请输入注册口令"
                prefix-icon="Key"
                size="large"
                show-password
              >
                <template #append>
                  <el-tooltip content="管理员和医生注册需要特殊口令" placement="top">
                    <el-icon><QuestionFilled /></el-icon>
                  </el-tooltip>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item prop="phone">
              <el-input
                v-model="registerForm.phone"
                placeholder="请输入手机号"
                prefix-icon="Phone"
                size="large"
                clearable
              />
            </el-form-item>

            <el-form-item prop="real_name">
              <el-input
                v-model="registerForm.real_name"
                placeholder="请输入真实姓名（选填）"
                prefix-icon="User"
                size="large"
                clearable
              />
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="loading"
                class="login-button"
                @click="handleRegister"
              >
                {{ loading ? '注册中...' : '注册' }}
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <div class="login-footer">
        <p>© 2025 Hospital Management System v2.1</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { QuestionFilled } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { register } from '@/api/auth'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 注册口令
const ACCESS_CODE = 'hospitalmanager121121'

onMounted(() => {
  console.log('Login page mounted successfully!')
})

// 标签页
const activeTab = ref('login')

// 加载状态
const loading = ref(false)

// 登录表单
const loginFormRef = ref(null)
const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ]
}

// 注册表单
const registerFormRef = ref(null)
const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  role: 'user',
  accessCode: '',
  phone: '',
  real_name: ''
})

// 监听角色变化，清空口令
watch(() => registerForm.role, (newRole) => {
  if (newRole === 'user') {
    registerForm.accessCode = ''
  }
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const validateAccessCode = (rule, value, callback) => {
  const role = registerForm.role
  if ((role === 'admin' || role === 'doctor') && !value) {
    callback(new Error('管理员和医生注册需要输入口令'))
  } else if ((role === 'admin' || role === 'doctor') && value !== ACCESS_CODE) {
    callback(new Error('口令错误，请联系系统管理员'))
  } else {
    callback()
  }
}

const validatePhone = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入手机号'))
  } else if (!/^1[3-9]\d{9}$/.test(value)) {
    callback(new Error('请输入正确的手机号格式'))
  } else {
    callback()
  }
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3-20个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  accessCode: [
    { validator: validateAccessCode, trigger: 'blur' }
  ],
  phone: [
    { required: true, validator: validatePhone, trigger: 'blur' }
  ]
}

// 登录处理
const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    loading.value = true
    
    try {
      const result = await userStore.handleLogin(loginForm)
      
      if (result.success) {
        ElMessage.success(result.message || '登录成功')
        
        // 根据用户角色跳转
        const userRole = userStore.userInfo?.role
        let redirectPath = '/'

        if (userRole === 'user') {
          // 普通用户跳转到门户
          redirectPath = '/portal'
        } else if (userRole === 'admin' || userRole === 'doctor') {
          // 管理员和医生跳转到管理系统首页
          redirectPath = route.query.redirect || '/'
        }

        // 使用 push 跳转，并传递需要检查病人信息的标志
        router.push({
          path: redirectPath,
          query: { checkPatientInfo: userRole === 'user' ? '1' : '0' }
        })
      } else {
        ElMessage.error(result.message || '登录失败')
      }
    } catch (error) {
      ElMessage.error(error.message || '登录失败')
    } finally {
      loading.value = false
    }
  })
}

// 注册处理
const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  await registerFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    loading.value = true
    
    try {
      // 移除确认密码和口令字段
      const { confirmPassword, accessCode, ...data } = registerForm
      const response = await register(data)
      
      if (response.success) {
        ElMessage.success('注册成功，请登录')
        
        // 切换到登录标签
        activeTab.value = 'login'
        
        // 填充用户名到登录表单
        loginForm.username = registerForm.username
        
        // 清空注册表单
        registerFormRef.value.resetFields()
      }
    } catch (error) {
      ElMessage.error(error.message || '注册失败')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
  width: 100%;
  max-width: 420px;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  margin: 0 0 10px 0;
  font-size: 24px;
  color: #333;
}

.login-header p {
  margin: 0;
  font-size: 14px;
  color: #999;
}

.login-tabs {
  margin-bottom: 20px;
}

.login-form {
  padding: 20px 0;
}

.login-button {
  width: 100%;
  font-size: 16px;
  height: 44px;
}

.login-footer {
  text-align: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.login-footer p {
  margin: 0;
  font-size: 12px;
  color: #999;
}

:deep(.el-tabs__nav-wrap::after) {
  display: none;
}
</style>
