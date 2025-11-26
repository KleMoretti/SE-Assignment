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

      <el-empty v-if="!loading && managedPatients.length === 0" description="暂无家庭成员" />

      <el-table
        v-else
        :data="managedPatients"
        v-loading="loading"
        stripe
        :header-cell-style="{ background: '#f5f7fa', color: '#2c3e50', fontWeight: '600' }"
        style="width: 100%"
      >
        <el-table-column prop="name" label="姓名" width="180" />
        <el-table-column prop="patient_no" label="病人编号" width="180" />
        <el-table-column prop="gender" label="性别" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.gender === '男' ? 'primary' : 'danger'" size="small">
              {{ row.gender }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="age" label="年龄" width="80" align="center" />
        <el-table-column prop="phone" label="联系电话" />
      </el-table>

    </el-card>

    <!-- 添加成员弹窗 -->
    <el-dialog
      v-model="addDialogVisible"
      title="添加家庭成员"
      width="500px"
      @close="resetForm"
      :close-on-click-modal="false"
      center
    >
      <el-alert
        title="关联说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px;"
      >
        <template #default>
          请输入您家人的系统登录账户信息，验证成功后将自动关联其病人档案
        </template>
      </el-alert>

      <el-form :model="addForm" :rules="addFormRules" ref="addFormRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="addForm.username" placeholder="请输入家人的用户名" size="large">
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="addForm.password"
            type="password"
            placeholder="请输入家人的密码"
            size="large"
            show-password
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button size="large" @click="addDialogVisible = false">取消</el-button>
          <el-button type="primary" size="large" @click="handleAddMember" :loading="addLoading">
            <el-icon class="el-icon--left"><Check /></el-icon>
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
import { ArrowLeft, Plus, User, Lock, Check } from '@element-plus/icons-vue'

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
  // 连接真实数据库
  fetchManagedPatients()
})

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
        // 重新加载列表
        fetchManagedPatients()
      } catch (error) {
        console.error('添加家庭成员失败:', error)
      } finally {
        addLoading.value = false
      }
    }
  })
}
</script>

<style scoped>
.family-management-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
  padding-bottom: 40px;
  box-sizing: border-box;
}

.box-card {
  max-width: 1200px;
  margin: 20px auto;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
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
  color: #000000;
}

.card-header .el-button--primary {
  background: #409EFF;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.card-header .el-button--primary:hover {
  background: #66b1ff;
}

/* 表格样式优化 */
:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table td),
:deep(.el-table th) {
  padding: 16px 0;
}

:deep(.el-table__body tr:hover > td) {
  background-color: #f0f9ff !important;
}

/* 弹窗样式 */
:deep(.el-dialog) {
  border-radius: 16px;
  overflow: hidden;
}

:deep(.el-dialog__header) {
  background: #f5f7fa;
  padding: 20px;
  margin: 0;
}

:deep(.el-dialog__title) {
  color: #000000;
  font-size: 20px;
  font-weight: 600;
}

:deep(.el-dialog__headerbtn .el-dialog__close) {
  color: #000000;
  font-size: 20px;
}

:deep(.el-dialog__body) {
  padding: 30px;
}

:deep(.el-form-item__label) {
  font-weight: 600;
  color: #000000;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 12px rgba(79, 172, 254, 0.15);
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 4px 12px rgba(79, 172, 254, 0.25);
}

.dialog-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.dialog-footer .el-button {
  border-radius: 8px;
  padding: 12px 32px;
  font-weight: 500;
}

.dialog-footer .el-button--primary {
  background: #409EFF;
  border: none;
}

.dialog-footer .el-button--primary:hover {
  background: #66b1ff;
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

  .card-header {
    flex-wrap: wrap;
    gap: 10px;
  }

  .card-header .el-button {
    order: 3;
    width: 100%;
  }

  :deep(.el-table) {
    font-size: 12px;
  }
}
</style>
