<template>
  <div class="doctor-list-container">
    <!-- 页面标题和操作栏 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <el-icon class="title-icon"><User /></el-icon>
          医生管理
        </h1>
        <p class="page-subtitle">管理医院医生信息、排班和绩效</p>
      </div>
      <div class="action-buttons">
        <el-button type="primary" @click="showAddDialog" :icon="Plus">
          添加医生
        </el-button>
        <el-button @click="goToSchedule" :icon="Calendar">
          排班管理
        </el-button>
        <el-button @click="goToPerformance" :icon="TrendCharts">
          绩效管理
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选区域 -->
    <el-card class="filter-card" shadow="never">
      <div class="filter-section">
        <el-input
          v-model="searchQuery"
          placeholder="搜索医生姓名、工号..."
          :prefix-icon="Search"
          clearable
          @input="handleSearch"
          class="search-input"
        />

        <div class="filter-group">
          <el-select v-model="filterDepartment" placeholder="全部科室" clearable @change="handleFilter">
            <el-option
              v-for="dept in departments"
              :key="dept.id"
              :label="dept.name"
              :value="dept.id"
            />
          </el-select>

          <el-select v-model="filterTitle" placeholder="全部职称" clearable @change="handleFilter">
            <el-option
              v-for="title in titles"
              :key="title"
              :label="title"
              :value="title"
            />
          </el-select>

          <el-select v-model="filterStatus" placeholder="全部状态" clearable @change="handleFilter">
            <el-option label="在职" value="active" />
            <el-option label="离职" value="inactive" />
          </el-select>
        </div>
      </div>
    </el-card>

    <!-- 医生列表卡片 -->
    <div v-loading="loading" element-loading-text="加载中...">
      <el-empty v-if="!loading && doctorList.length === 0" description="暂无医生数据">
        <el-button type="primary" @click="showAddDialog">添加医生</el-button>
      </el-empty>

      <div v-else class="doctor-grid">
        <el-card
          v-for="doctor in doctorList"
          :key="doctor.id"
          class="doctor-card"
          shadow="hover"
          @click="viewDoctorDetail(doctor.id)"
        >
          <div class="doctor-card-content">
            <div class="doctor-header-section">
              <el-avatar :size="60" class="doctor-avatar">
                <template v-if="doctor.avatar">
                  <img :src="doctor.avatar" :alt="doctor.name" />
                </template>
                <template v-else>
                  {{ doctor.name.charAt(0) }}
                </template>
              </el-avatar>

              <div class="doctor-basic-info">
                <h3 class="doctor-name">{{ doctor.name }}</h3>
                <div class="doctor-meta">
                  <el-tag size="small" type="info">{{ doctor.title }}</el-tag>
                  <span class="doctor-department">{{ doctor.department }}</span>
                </div>
              </div>

              <el-tag
                :type="doctor.status === 'active' ? 'success' : 'info'"
                size="small"
                class="status-tag"
              >
                {{ doctor.status === 'active' ? '在职' : '离职' }}
              </el-tag>
            </div>

            <el-divider class="card-divider" />

            <div class="doctor-stats-section">
              <div class="stat-item">
                <el-icon class="stat-icon"><User /></el-icon>
                <div class="stat-content">
                  <span class="stat-value">{{ doctor.patientCount || 0 }}</span>
                  <span class="stat-label">患者数</span>
                </div>
              </div>
              <div class="stat-item">
                <el-icon class="stat-icon"><Star /></el-icon>
                <div class="stat-content">
                  <span class="stat-value">{{ doctor.rating || 'N/A' }}</span>
                  <span class="stat-label">评分</span>
                </div>
              </div>
              <div class="stat-item">
                <el-icon class="stat-icon"><Calendar /></el-icon>
                <div class="stat-content">
                  <span class="stat-value">{{ doctor.scheduleCount || 0 }}</span>
                  <span class="stat-label">排班数</span>
                </div>
              </div>
            </div>

            <div v-if="doctor.specialties && doctor.specialties.length" class="doctor-specialties">
              <el-tag
                v-for="specialty in doctor.specialties.slice(0, 3)"
                :key="specialty"
                size="small"
                effect="plain"
                class="specialty-tag"
              >
                {{ specialty }}
              </el-tag>
              <el-tag v-if="doctor.specialties.length > 3" size="small" effect="plain">
                +{{ doctor.specialties.length - 3 }}
              </el-tag>
            </div>

            <div class="doctor-actions" @click.stop>
              <el-button-group>
                <el-tooltip content="查看排班" placement="top">
                  <el-button size="small" :icon="Calendar" @click="viewSchedule(doctor.id)" />
                </el-tooltip>
                <el-tooltip content="查看绩效" placement="top">
                  <el-button size="small" :icon="TrendCharts" @click="viewPerformance(doctor.id)" />
                </el-tooltip>
                <el-tooltip content="编辑信息" placement="top">
                  <el-button size="small" :icon="Edit" @click="editDoctor(doctor)" />
                </el-tooltip>
                <el-tooltip content="删除医生" placement="top">
                  <el-button size="small" :icon="Delete" type="danger" @click="deleteDoctor(doctor.id)" />
                </el-tooltip>
              </el-button-group>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="total > 0" class="pagination-container">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>

    <!-- 添加/编辑医生对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingDoctor ? '编辑医生' : '添加医生'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="doctorFormRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="formData.name" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="工号" prop="doctorNo">
              <el-input v-model="formData.doctorNo" placeholder="请输入工号" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="性别" prop="gender">
              <el-radio-group v-model="formData.gender">
                <el-radio label="男">男</el-radio>
                <el-radio label="女">女</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="年龄" prop="age">
              <el-input-number v-model="formData.age" :min="20" :max="100" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="科室" prop="department">
              <el-select v-model="formData.department" placeholder="请选择科室" style="width: 100%">
                <el-option
                  v-for="dept in departments"
                  :key="dept.id"
                  :label="dept.name"
                  :value="dept.name"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="职称" prop="title">
              <el-select v-model="formData.title" placeholder="请选择职称" style="width: 100%">
                <el-option v-for="title in titles" :key="title" :label="title" :value="title" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="联系电话" prop="phone">
              <el-input v-model="formData.phone" placeholder="请输入联系电话" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="formData.email" placeholder="请输入邮箱" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="学历" prop="education">
          <el-select v-model="formData.education" placeholder="请选择学历" style="width: 100%">
            <el-option label="本科" value="本科" />
            <el-option label="硕士" value="硕士" />
            <el-option label="博士" value="博士" />
          </el-select>
        </el-form-item>

        <el-form-item label="专长" prop="specialty">
          <el-input
            v-model="formData.specialty"
            type="textarea"
            :rows="3"
            placeholder="请输入专长领域"
          />
        </el-form-item>

        <el-form-item label="入职日期" prop="hireDate">
          <el-date-picker
            v-model="formData.hireDate"
            type="date"
            placeholder="选择入职日期"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="formData.status">
            <el-radio label="active">在职</el-radio>
            <el-radio label="inactive">离职</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="closeDialog">取消</el-button>
        <el-button type="primary" @click="submitDoctor" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Calendar, TrendCharts, Search, User, Star, Edit, Delete
} from '@element-plus/icons-vue'
import { getDoctorList, createDoctor, updateDoctor, deleteDoctor as deleteDoctorApi, getDepartments } from '@/api/doctor'

// 路由
const router = useRouter()

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const editingDoctor = ref(null)
const doctorFormRef = ref(null)

const searchQuery = ref('')
const filterDepartment = ref('')
const filterTitle = ref('')
const filterStatus = ref('')

const doctorList = ref([])
const departments = ref([])
const titles = ref(['主任医师', '副主任医师', '主治医师', '住院医师'])

const pagination = reactive({
  page: 1,
  pageSize: 10
})
const total = ref(0)

const formData = reactive({
  name: '',
  doctorNo: '',
  gender: '男',
  age: null,
  phone: '',
  email: '',
  department: '',
  title: '',
  specialty: '',
  education: '',
  hireDate: '',
  status: 'active'
})

const formRules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  doctorNo: [{ required: true, message: '请输入工号', trigger: 'blur' }],
  department: [{ required: true, message: '请选择科室', trigger: 'change' }],
  title: [{ required: true, message: '请选择职称', trigger: 'change' }],
  phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

// 方法
const fetchDoctorList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      pageSize: pagination.pageSize,
      search: searchQuery.value,
      department: filterDepartment.value,
      title: filterTitle.value,
      status: filterStatus.value
    }
    const res = await getDoctorList(params)
    doctorList.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (error) {
    ElMessage.error('获取医生列表失败')
  } finally {
    loading.value = false
  }
}

const fetchDepartments = async () => {
  try {
    const res = await getDepartments()
    departments.value = res.data || []
  } catch (error) {
    console.error('获取科室列表失败', error)
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchDoctorList()
}

const handleFilter = () => {
  pagination.page = 1
  fetchDoctorList()
}

const handleSizeChange = () => {
  pagination.page = 1
  fetchDoctorList()
}

const handlePageChange = () => {
  fetchDoctorList()
}

const showAddDialog = () => {
  editingDoctor.value = null
  resetFormData()
  dialogVisible.value = true
}

const editDoctor = (doctor) => {
  editingDoctor.value = doctor
  Object.assign(formData, {
    name: doctor.name,
    doctorNo: doctor.doctorNo,
    gender: doctor.gender,
    age: doctor.age,
    phone: doctor.phone,
    email: doctor.email,
    department: doctor.department,
    title: doctor.title,
    specialty: doctor.specialty,
    education: doctor.education,
    hireDate: doctor.hireDate,
    status: doctor.status
  })
  dialogVisible.value = true
}

const submitDoctor = async () => {
  if (!doctorFormRef.value) return

  await doctorFormRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      if (editingDoctor.value) {
        await updateDoctor(editingDoctor.value.id, formData)
        ElMessage.success('更新医生信息成功')
      } else {
        await createDoctor(formData)
        ElMessage.success('添加医生成功')
      }
      closeDialog()
      fetchDoctorList()
    } catch (error) {
      ElMessage.error(editingDoctor.value ? '更新医生信息失败' : '添加医生失败')
    } finally {
      submitting.value = false
    }
  })
}

const deleteDoctor = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除该医生吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteDoctorApi(id)
    ElMessage.success('删除医生成功')
    fetchDoctorList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除医生失败')
    }
  }
}

const closeDialog = () => {
  dialogVisible.value = false
  resetFormData()
}

const resetFormData = () => {
  Object.assign(formData, {
    name: '',
    doctorNo: '',
    gender: '男',
    age: null,
    phone: '',
    email: '',
    department: '',
    title: '',
    specialty: '',
    education: '',
    hireDate: '',
    status: 'active'
  })
  if (doctorFormRef.value) {
    doctorFormRef.value.clearValidate()
  }
}

const viewDoctorDetail = (id) => {
  router.push(`/doctor/detail/${id}`)
}

const viewSchedule = (id) => {
  router.push(`/doctor/schedule/${id}`)
}

const viewPerformance = (id) => {
  router.push(`/doctor/performance/${id}`)
}

const goToSchedule = () => {
  router.push('/doctor/schedule')
}

const goToPerformance = () => {
  router.push('/doctor/performance')
}

// 生命周期
onMounted(() => {
  fetchDoctorList()
  fetchDepartments()
})
</script>

<style scoped>
.doctor-list-container {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-content {
  flex: 1;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
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

.action-buttons {
  display: flex;
  gap: 12px;
}

.filter-card {
  margin-bottom: 24px;
}

.filter-section {
  display: flex;
  gap: 16px;
  align-items: center;
}

.search-input {
  flex: 1;
  max-width: 400px;
}

.filter-group {
  display: flex;
  gap: 12px;
}

.doctor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.doctor-card {
  cursor: pointer;
  transition: all 0.3s ease;
}

.doctor-card:hover {
  transform: translateY(-4px);
}

.doctor-card-content {
  padding: 4px;
}

.doctor-header-section {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  position: relative;
}

.doctor-avatar {
  flex-shrink: 0;
}

.doctor-basic-info {
  flex: 1;
  min-width: 0;
}

.doctor-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.doctor-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.doctor-department {
  font-size: 14px;
  color: #606266;
}

.status-tag {
  position: absolute;
  top: 0;
  right: 0;
}

.card-divider {
  margin: 16px 0;
}

.doctor-stats-section {
  display: flex;
  justify-content: space-around;
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.stat-icon {
  font-size: 24px;
  color: #409eff;
}

.stat-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

.doctor-specialties {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.specialty-tag {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.doctor-actions {
  display: flex;
  justify-content: center;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}

.pagination-container {
  display: flex;
  justify-content: center;
  padding: 24px 0;
}
</style>
