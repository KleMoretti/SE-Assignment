<template>
  <div class="qualification-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <el-page-header @back="goBack">
        <template #content>
          <div class="header-content">
            <h1 class="page-title">
              <el-icon class="title-icon"><Medal /></el-icon>
              医生资质管理
            </h1>
            <p class="page-subtitle">管理医生的执业资质和证书信息</p>
          </div>
        </template>
        <template #extra>
          <el-button type="primary" :icon="Plus" @click="handleAdd">
            新增资质
          </el-button>
        </template>
      </el-page-header>
    </div>

    <!-- 筛选区域 -->
    <el-card shadow="never" class="filter-card">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="医生">
          <el-select
            v-model="filterForm.doctorId"
            placeholder="选择医生"
            clearable
            filterable
            style="width: 200px"
          >
            <el-option
              v-for="doctor in doctors"
              :key="doctor.id"
              :label="`${doctor.name} (${doctor.department})`"
              :value="doctor.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="资质类型">
          <el-select
            v-model="filterForm.qualificationType"
            placeholder="选择类型"
            clearable
            style="width: 180px"
          >
            <el-option label="医师执业证" value="medical_license" />
            <el-option label="执业许可证" value="practice_certificate" />
            <el-option label="专科证书" value="specialist_certificate" />
            <el-option label="职称证书" value="title_certificate" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="filterForm.status"
            placeholder="选择状态"
            clearable
            style="width: 150px"
          >
            <el-option label="有效" value="valid" />
            <el-option label="已过期" value="expired" />
            <el-option label="已吊销" value="revoked" />
            <el-option label="待审核" value="pending" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">
            查询
          </el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 资质列表 -->
    <el-card shadow="never" class="table-card">
      <el-table
        v-loading="loading"
        :data="qualificationList"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="doctorName" label="医生姓名" width="120" />
        <el-table-column label="资质类型" width="140">
          <template #default="{ row }">
            <el-tag :type="getQualificationTypeTag(row.qualificationType)">
              {{ getQualificationTypeName(row.qualificationType) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="certificateName" label="证书名称" min-width="180" />
        <el-table-column prop="certificateNo" label="证书编号" width="150" />
        <el-table-column prop="issuingAuthority" label="颁发机构" width="150" />
        <el-table-column label="颁发日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.issueDate) }}
          </template>
        </el-table-column>
        <el-table-column label="过期日期" width="120">
          <template #default="{ row }">
            <span :class="{ 'expiring-soon': row.isExpiringSoon }">
              {{ formatDate(row.expiryDate) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusName(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              link
              :icon="View"
              @click="handleView(row)"
            >
              查看
            </el-button>
            <el-button
              type="primary"
              link
              :icon="Edit"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              link
              :icon="Delete"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <el-form-item label="医生" prop="doctorId">
          <el-select
            v-model="formData.doctorId"
            placeholder="选择医生"
            filterable
            style="width: 100%"
            :disabled="isEdit"
          >
            <el-option
              v-for="doctor in doctors"
              :key="doctor.id"
              :label="`${doctor.name} - ${doctor.department} - ${doctor.title}`"
              :value="doctor.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="资质类型" prop="qualificationType">
          <el-select
            v-model="formData.qualificationType"
            placeholder="选择资质类型"
            style="width: 100%"
          >
            <el-option label="医师执业证" value="medical_license" />
            <el-option label="执业许可证" value="practice_certificate" />
            <el-option label="专科证书" value="specialist_certificate" />
            <el-option label="职称证书" value="title_certificate" />
          </el-select>
        </el-form-item>
        <el-form-item label="证书名称" prop="certificateName">
          <el-input
            v-model="formData.certificateName"
            placeholder="请输入证书名称"
          />
        </el-form-item>
        <el-form-item label="证书编号" prop="certificateNo">
          <el-input
            v-model="formData.certificateNo"
            placeholder="请输入证书编号"
          />
        </el-form-item>
        <el-form-item label="颁发机构" prop="issuingAuthority">
          <el-input
            v-model="formData.issuingAuthority"
            placeholder="请输入颁发机构"
          />
        </el-form-item>
        <el-form-item label="颁发日期" prop="issueDate">
          <el-date-picker
            v-model="formData.issueDate"
            type="date"
            placeholder="选择颁发日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="过期日期" prop="expiryDate">
          <el-date-picker
            v-model="formData.expiryDate"
            type="date"
            placeholder="选择过期日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="执业范围" prop="scopeOfPractice">
          <el-input
            v-model="formData.scopeOfPractice"
            type="textarea"
            :rows="3"
            placeholder="请输入执业范围"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="formData.status">
            <el-radio label="valid">有效</el-radio>
            <el-radio label="expired">已过期</el-radio>
            <el-radio label="revoked">已吊销</el-radio>
            <el-radio label="pending">待审核</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="formData.notes"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="资质详情"
      width="600px"
    >
      <el-descriptions :column="2" border v-if="currentQualification">
        <el-descriptions-item label="医生姓名">
          {{ currentQualification.doctorName }}
        </el-descriptions-item>
        <el-descriptions-item label="资质类型">
          <el-tag :type="getQualificationTypeTag(currentQualification.qualificationType)">
            {{ getQualificationTypeName(currentQualification.qualificationType) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="证书名称" :span="2">
          {{ currentQualification.certificateName }}
        </el-descriptions-item>
        <el-descriptions-item label="证书编号" :span="2">
          {{ currentQualification.certificateNo || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="颁发机构" :span="2">
          {{ currentQualification.issuingAuthority || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="颁发日期">
          {{ formatDate(currentQualification.issueDate) }}
        </el-descriptions-item>
        <el-descriptions-item label="过期日期">
          <span :class="{ 'expiring-soon': currentQualification.isExpiringSoon }">
            {{ formatDate(currentQualification.expiryDate) }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="执业范围" :span="2">
          {{ currentQualification.scopeOfPractice || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentQualification.status)">
            {{ getStatusName(currentQualification.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ formatDateTime(currentQualification.createdAt) }}
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">
          {{ currentQualification.notes || '-' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Medal, Plus, Search, Refresh, View, Edit, Delete
} from '@element-plus/icons-vue'
import {
  getQualificationList,
  createQualification,
  updateQualification,
  deleteQualification
} from '@/api/qualification'
import { getDoctorList } from '@/api/doctor'

const router = useRouter()

// 数据
const loading = ref(false)
const submitting = ref(false)
const qualificationList = ref([])
const doctors = ref([])

const filterForm = reactive({
  doctorId: null,
  qualificationType: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 对话框
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)
const currentQualification = ref(null)
const formRef = ref(null)

const formData = reactive({
  id: null,
  doctorId: null,
  qualificationType: '',
  certificateName: '',
  certificateNo: '',
  issuingAuthority: '',
  issueDate: '',
  expiryDate: '',
  scopeOfPractice: '',
  status: 'valid',
  notes: ''
})

const formRules = {
  doctorId: [{ required: true, message: '请选择医生', trigger: 'change' }],
  qualificationType: [{ required: true, message: '请选择资质类型', trigger: 'change' }],
  certificateName: [{ required: true, message: '请输入证书名称', trigger: 'blur' }]
}

// 方法
const loadQualifications = async () => {
  loading.value = true
  try {
    const res = await getQualificationList({
      page: pagination.page,
      pageSize: pagination.pageSize,
      ...filterForm
    })
    qualificationList.value = res.data.items || []
    pagination.total = res.data.total || 0
  } catch (error) {
    ElMessage.error('获取资质列表失败')
  } finally {
    loading.value = false
  }
}

const loadDoctors = async () => {
  try {
    const res = await getDoctorList({ pageSize: 1000 })
    doctors.value = res.data.items || []
  } catch (error) {
    console.error('获取医生列表失败', error)
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadQualifications()
}

const handleReset = () => {
  filterForm.doctorId = null
  filterForm.qualificationType = ''
  filterForm.status = ''
  pagination.page = 1
  loadQualifications()
}

const handleSizeChange = () => {
  loadQualifications()
}

const handlePageChange = () => {
  loadQualifications()
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增资质'
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑资质'
  Object.assign(formData, {
    id: row.id,
    doctorId: row.doctorId,
    qualificationType: row.qualificationType,
    certificateName: row.certificateName,
    certificateNo: row.certificateNo,
    issuingAuthority: row.issuingAuthority,
    issueDate: row.issueDate,
    expiryDate: row.expiryDate,
    scopeOfPractice: row.scopeOfPractice,
    status: row.status,
    notes: row.notes
  })
  dialogVisible.value = true
}

const handleView = (row) => {
  currentQualification.value = row
  detailDialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除 ${row.doctorName} 的 ${getQualificationTypeName(row.qualificationType)} 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await deleteQualification(row.id)
    ElMessage.success('删除成功')
    loadQualifications()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true
    
    if (isEdit.value) {
      await updateQualification(formData.id, formData)
      ElMessage.success('更新成功')
    } else {
      await createQualification(formData)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    loadQualifications()
  } catch (error) {
    if (error !== false) {
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
    }
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  Object.assign(formData, {
    id: null,
    doctorId: null,
    qualificationType: '',
    certificateName: '',
    certificateNo: '',
    issuingAuthority: '',
    issueDate: '',
    expiryDate: '',
    scopeOfPractice: '',
    status: 'valid',
    notes: ''
  })
  formRef.value?.clearValidate()
}

const goBack = () => {
  router.push('/doctor')
}

// 辅助函数
const getQualificationTypeName = (type) => {
  const map = {
    medical_license: '医师执业证',
    practice_certificate: '执业许可证',
    specialist_certificate: '专科证书',
    title_certificate: '职称证书'
  }
  return map[type] || type
}

const getQualificationTypeTag = (type) => {
  const map = {
    medical_license: 'danger',
    practice_certificate: 'warning',
    specialist_certificate: 'success',
    title_certificate: 'info'
  }
  return map[type] || ''
}

const getStatusName = (status) => {
  const map = {
    valid: '有效',
    expired: '已过期',
    revoked: '已吊销',
    pending: '待审核'
  }
  return map[status] || status
}

const getStatusType = (status) => {
  const map = {
    valid: 'success',
    expired: 'danger',
    revoked: 'info',
    pending: 'warning'
  }
  return map[status] || ''
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return dateStr.split('T')[0]
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  return dateStr.replace('T', ' ').split('.')[0]
}

// 生命周期
onMounted(() => {
  loadDoctors()
  loadQualifications()
})
</script>

<style scoped>
.qualification-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 40px);
}

.page-header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-icon {
  font-size: 28px;
  color: #409eff;
}

.page-subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-form {
  margin-bottom: 0;
}

.table-card {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.expiring-soon {
  color: #f56c6c;
  font-weight: 600;
}
</style>
