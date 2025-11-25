<template>
  <el-dialog
    v-model="dialogVisible"
    title="完善个人信息"
    width="500px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :show-close="false"
  >
    <el-alert
      title="请完善您的个人信息"
      type="warning"
      description="首次登录需要完善个人信息，以便更好地为您提供医疗服务。"
      :closable="false"
      style="margin-bottom: 20px;"
    />

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
    >
      <el-form-item label="姓名" prop="name">
        <el-input v-model="form.name" placeholder="请输入真实姓名" />
      </el-form-item>

      <el-form-item label="性别" prop="gender">
        <el-radio-group v-model="form.gender">
          <el-radio label="男">男</el-radio>
          <el-radio label="女">女</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="年龄" prop="age">
        <el-input-number
          v-model="form.age"
          :min="1"
          :max="150"
          placeholder="请输入年龄"
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item label="身份证号" prop="id_card">
        <el-input v-model="form.id_card" placeholder="请输入身份证号" maxlength="18" />
      </el-form-item>

      <el-form-item label="居住地址" prop="address">
        <el-input
          v-model="form.address"
          type="textarea"
          :rows="2"
          placeholder="请输入居住地址"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button type="primary" @click="handleSubmit" :loading="loading" style="width: 100%;">
        {{ loading ? '提交中...' : '提交' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { completePatientInfo } from '@/api/auth'

const dialogVisible = ref(false)
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  name: '',
  gender: '',
  age: null,
  id_card: '',
  address: ''
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

const rules = {
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

const emit = defineEmits(['completed'])

// 显示对话框
const show = (patientData) => {
  if (patientData) {
    Object.assign(form, patientData)
  }
  dialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true

    try {
      const response = await completePatientInfo(form)

      if (response.success) {
        ElMessage.success('个人信息完善成功')
        dialogVisible.value = false
        emit('completed', response.data)
      } else {
        ElMessage.error(response.message || '提交失败')
      }
    } catch (error) {
      ElMessage.error(error.message || '提交失败')
    } finally {
      loading.value = false
    }
  })
}

defineExpose({
  show
})
</script>

<style scoped>
:deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
}

:deep(.el-dialog__title) {
  color: white;
  font-size: 18px;
  font-weight: bold;
}

:deep(.el-dialog__body) {
  padding: 30px 20px;
}
</style>
