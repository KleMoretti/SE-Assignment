<template>
  <div class="family-management-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <el-button :icon="ArrowLeft" @click="goBack" circle></el-button>
          <span class="title">家庭成员管理</span>
          <el-button type="primary" @click="openAddDialog">
            <el-icon class="el-icon--left"><Plus /></el-icon>
            添加成员
          </el-button>
        </div>
      </template>

      <el-table :data="managedPatients" v-loading="loading" border stripe>
        <el-table-column prop="name" label="姓名" width="180" />
        <el-table-column prop="patient_no" label="病人编号" width="180" />
        <el-table-column prop="gender" label="性别" />
        <el-table-column prop="age" label="年龄" />
        <el-table-column prop="phone" label="联系电话" />
      </el-table>

    </el-card>

    <!-- 添加成员弹窗 -->
    <el-dialog v-model="addDialogVisible" title="添加家庭成员" width="500px" @close="resetForm">
      <p class="dialog-tip">请输入您家人的系统登录账户信息以完成关联。</p>
      <el-form :model="addForm" :rules="addFormRules" ref="addFormRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="addForm.username" placeholder="请输入家人的用户名"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="addForm.password" type="password" placeholder="请输入家人的密码" show-password></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleAddMember" :loading="addLoading">
            确认添加
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getManagedPatients, addManagedPatient } from '@/api/patient'
import { ArrowLeft, Plus } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)
const managedPatients = ref([])

const addDialogVisible = ref(false)
const addLoading = ref(false)
const addFormRef = ref(null)
const addForm = reactive({
  username: '',
  password: ''
})
const addFormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const fetchManagedPatients = async () => {
  loading.value = true
  try {
    const res = await getManagedPatients()
    managedPatients.value = res.data || []
  } catch (error) {
    ElMessage.error('获取家庭成员列表失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // For now, we use mock data as login is not implemented
  // In a real scenario, you would call fetchManagedPatients()
  // fetchManagedPatients()

  // --- Mock Data ---
  managedPatients.value = [
    { id: 1, name: '张三 (我)', patient_no: 'P00000001', gender: '男', age: 30, phone: '13800138000' },
    { id: 2, name: '张小美 (女儿)', patient_no: 'P00000002', gender: '女', age: 5, phone: '13800138001' }
  ]
});

const goBack = () => {
  router.push({ name: 'PortalIndex' })
}

const openAddDialog = () => {
  addDialogVisible.value = true
}

const resetForm = () => {
  if (addFormRef.value) {
    addFormRef.value.resetFields()
  }
}

const handleAddMember = () => {
  if (!addFormRef.value) return
  addFormRef.value.validate(async (valid) => {
    if (valid) {
      addLoading.value = true
      try {
        const res = await addManagedPatient(addForm)
        managedPatients.value.push(res.data)
        ElMessage.success('家庭成员添加成功！')
        addDialogVisible.value = false
      } catch (error) {
        // Error message is already handled by the request interceptor
        // ElMessage.error(error.message || '添加失败，请检查用户名和密码')
      } finally {
        addLoading.value = false
      }
    }
  })
}
</script>

<style scoped>
.family-management-container {
  padding: 20px;
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
.dialog-tip {
  margin-bottom: 20px;
  color: #909399;
  font-size: 14px;
}
</style>

