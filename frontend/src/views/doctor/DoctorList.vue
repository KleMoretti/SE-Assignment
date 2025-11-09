<template>
  <div class="doctor-list-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2>医生管理</h2>
      <el-button type="primary" @click="showAddDialog">
        <el-icon><Plus /></el-icon>
        添加医生
      </el-button>
    </div>

    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="搜索">
          <el-input
            v-model="searchForm.search"
            placeholder="姓名/编号/电话/邮箱"
            clearable
            @clear="handleSearch"
          />
        </el-form-item>

        <el-form-item label="科室">
          <el-select
            v-model="searchForm.department"
            placeholder="请选择科室"
            clearable
            @change="handleSearch"
          >
            <el-option
              v-for="dept in departments"
              :key="dept"
              :label="dept"
              :value="dept"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-select
            v-model="searchForm.status"
            placeholder="请选择状态"
            clearable
            @change="handleSearch"
          >
            <el-option label="在职" value="active" />
            <el-option label="离职" value="inactive" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="doctorList"
        stripe
        border
      >
        <el-table-column prop="doctor_no" label="医生编号" width="120" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="gender" label="性别" width="60" />
        <el-table-column prop="age" label="年龄" width="60" />
        <el-table-column prop="phone" label="电话" width="130" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="department" label="科室" width="100" />
        <el-table-column prop="title" label="职称" width="120" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '在职' : '离职' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              link
              @click="handleView(row)"
            >
              查看
            </el-button>
            <el-button
              type="primary"
              size="small"
              link
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              type="success"
              size="small"
              link
              @click="handleViewSchedule(row)"
            >
              排班
            </el-button>
            <el-button
              type="warning"
              size="small"
              link
              @click="handleViewPerformance(row)"
            >
              绩效
            </el-button>
            <el-popconfirm
              title="确定要删除这位医生吗？"
              @confirm="handleDelete(row.id)"
            >
              <template #reference>
                <el-button
                  type="danger"
                  size="small"
                  link
                >
                  删除
                </el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.per_page"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSearch"
        @current-change="handleSearch"
      />
    </el-card>

    <!-- 添加/编辑医生对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="doctorFormRef"
        :model="doctorForm"
        :rules="doctorRules"
        label-width="100px"
      >
        <el-form-item label="医生编号" prop="doctor_no">
          <el-input v-model="doctorForm.doctor_no" placeholder="请输入医生编号" />
        </el-form-item>

        <el-form-item label="姓名" prop="name">
          <el-input v-model="doctorForm.name" placeholder="请输入姓名" />
        </el-form-item>

        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="doctorForm.gender">
            <el-radio label="男">男</el-radio>
            <el-radio label="女">女</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="年龄" prop="age">
          <el-input-number v-model="doctorForm.age" :min="20" :max="100" />
        </el-form-item>

        <el-form-item label="电话" prop="phone">
          <el-input v-model="doctorForm.phone" placeholder="请输入电话" />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="doctorForm.email" placeholder="请输入邮箱" />
        </el-form-item>

        <el-form-item label="科室" prop="department">
          <el-input v-model="doctorForm.department" placeholder="请输入科室" />
        </el-form-item>

        <el-form-item label="职称" prop="title">
          <el-select v-model="doctorForm.title" placeholder="请选择职称">
            <el-option label="主任医师" value="主任医师" />
            <el-option label="副主任医师" value="副主任医师" />
            <el-option label="主治医师" value="主治医师" />
            <el-option label="住院医师" value="住院医师" />
          </el-select>
        </el-form-item>

        <el-form-item label="专长" prop="specialty">
          <el-input v-model="doctorForm.specialty" type="textarea" placeholder="请输入专长" />
        </el-form-item>

        <el-form-item label="学历" prop="education">
          <el-select v-model="doctorForm.education" placeholder="请选择学历">
            <el-option label="博士" value="博士" />
            <el-option label="硕士" value="硕士" />
            <el-option label="本科" value="本科" />
          </el-select>
        </el-form-item>

        <el-form-item label="入职日期" prop="hire_date">
          <el-date-picker
            v-model="doctorForm.hire_date"
            type="date"
            placeholder="选择入职日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>

        <el-form-item v-if="editMode" label="状态" prop="status">
          <el-radio-group v-model="doctorForm.status">
            <el-radio label="active">在职</el-radio>
            <el-radio label="inactive">离职</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saveLoading" @click="handleSave">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="医生详情"
      width="700px"
    >
      <el-descriptions v-if="currentDoctor" :column="2" border>
        <el-descriptions-item label="医生编号">
          {{ currentDoctor.doctor_no }}
        </el-descriptions-item>
        <el-descriptions-item label="姓名">
          {{ currentDoctor.name }}
        </el-descriptions-item>
        <el-descriptions-item label="性别">
          {{ currentDoctor.gender }}
        </el-descriptions-item>
        <el-descriptions-item label="年龄">
          {{ currentDoctor.age }}
        </el-descriptions-item>
        <el-descriptions-item label="电话">
          {{ currentDoctor.phone }}
        </el-descriptions-item>
        <el-descriptions-item label="邮箱">
          {{ currentDoctor.email }}
        </el-descriptions-item>
        <el-descriptions-item label="科室">
          {{ currentDoctor.department }}
        </el-descriptions-item>
        <el-descriptions-item label="职称">
          {{ currentDoctor.title }}
        </el-descriptions-item>
        <el-descriptions-item label="学历">
          {{ currentDoctor.education }}
        </el-descriptions-item>
        <el-descriptions-item label="入职日期">
          {{ currentDoctor.hire_date }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentDoctor.status === 'active' ? 'success' : 'info'">
            {{ currentDoctor.status === 'active' ? '在职' : '离职' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="专长" :span="2">
          {{ currentDoctor.specialty }}
        </el-descriptions-item>

        <!-- 统计信息 -->
        <el-descriptions-item v-if="currentDoctor.statistics" label="预约总数" :span="2">
          {{ currentDoctor.statistics.total_appointments }} 次
          （已完成：{{ currentDoctor.statistics.completed_appointments }} 次）
        </el-descriptions-item>
        <el-descriptions-item v-if="currentDoctor.statistics" label="病历记录">
          {{ currentDoctor.statistics.total_medical_records }} 条
        </el-descriptions-item>
        <el-descriptions-item v-if="currentDoctor.statistics" label="排班记录">
          {{ currentDoctor.statistics.total_schedules }} 条
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import {
  getDoctors,
  getDoctorDetail,
  createDoctor,
  updateDoctor,
  deleteDoctor,
  getDoctorStatistics
} from '@/api/doctor'

const router = useRouter()

// 搜索表单
const searchForm = reactive({
  search: '',
  department: '',
  status: ''
})

// 科室列表
const departments = ref([])

// 医生列表
const doctorList = ref([])
const loading = ref(false)

// 分页
const pagination = reactive({
  page: 1,
  per_page: 10,
  total: 0
})

// 对话框
const dialogVisible = ref(false)
const dialogTitle = ref('添加医生')
const editMode = ref(false)
const saveLoading = ref(false)

// 医生表单
const doctorFormRef = ref(null)
const doctorForm = reactive({
  id: null,
  doctor_no: '',
  name: '',
  gender: '男',
  age: null,
  phone: '',
  email: '',
  department: '',
  title: '',
  specialty: '',
  education: '',
  hire_date: '',
  status: 'active'
})

// 表单验证规则
const doctorRules = {
  doctor_no: [
    { required: true, message: '请输入医生编号', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  gender: [
    { required: true, message: '请选择性别', trigger: 'change' }
  ]
}

// 详情对话框
const detailVisible = ref(false)
const currentDoctor = ref(null)

// 获取医生列表
const getDoctorList = async () => {
  loading.value = true
  
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page,
      ...searchForm
    }
    
    const response = await getDoctors(params)
    
    if (response.success) {
      doctorList.value = response.data.list
      pagination.total = response.data.total
    }
  } catch (error) {
    ElMessage.error(error.message || '获取医生列表失败')
  } finally {
    loading.value = false
  }
}

// 获取统计数据（科室列表）
const getStatistics = async () => {
  try {
    const response = await getDoctorStatistics()
    
    if (response.success) {
      departments.value = response.data.departments || []
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  getDoctorList()
}

// 重置
const handleReset = () => {
  searchForm.search = ''
  searchForm.department = ''
  searchForm.status = ''
  handleSearch()
}

// 显示添加对话框
const showAddDialog = () => {
  editMode.value = false
  dialogTitle.value = '添加医生'
  resetForm()
  dialogVisible.value = true
}

// 查看详情
const handleView = (row) => {
  router.push(`/doctor/detail/${row.id}`)
}

// 编辑
const handleEdit = (row) => {
  editMode.value = true
  dialogTitle.value = '编辑医生'
  
  Object.keys(doctorForm).forEach(key => {
    doctorForm[key] = row[key]
  })
  
  dialogVisible.value = true
}

// 删除
const handleDelete = async (id) => {
  try {
    const response = await deleteDoctor(id)
    
    if (response.success) {
      ElMessage.success('删除成功')
      getDoctorList()
    }
  } catch (error) {
    ElMessage.error(error.message || '删除失败')
  }
}

// 查看排班
const handleViewSchedule = (row) => {
  router.push({
    path: '/doctor/schedule',
    query: { doctor_id: row.id }
  })
}

// 查看绩效
const handleViewPerformance = (row) => {
  router.push({
    path: '/doctor/performance',
    query: { doctor_id: row.id }
  })
}

// 保存
const handleSave = async () => {
  if (!doctorFormRef.value) return
  
  await doctorFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    saveLoading.value = true
    
    try {
      const { id, ...data } = doctorForm
      let response
      
      if (editMode.value) {
        response = await updateDoctor(id, data)
      } else {
        response = await createDoctor(data)
      }
      
      if (response.success) {
        ElMessage.success(editMode.value ? '更新成功' : '创建成功')
        dialogVisible.value = false
        getDoctorList()
      }
    } catch (error) {
      ElMessage.error(error.message || '操作失败')
    } finally {
      saveLoading.value = false
    }
  })
}

// 关闭对话框
const handleDialogClose = () => {
  resetForm()
  doctorFormRef.value?.clearValidate()
}

// 重置表单
const resetForm = () => {
  Object.assign(doctorForm, {
    id: null,
    doctor_no: '',
    name: '',
    gender: '男',
    age: null,
    phone: '',
    email: '',
    department: '',
    title: '',
    specialty: '',
    education: '',
    hire_date: '',
    status: 'active'
  })
}

// 初始化
onMounted(() => {
  getDoctorList()
  getStatistics()
})
</script>

<style scoped>
.doctor-list-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
}

.search-card {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}

.el-pagination {
  margin-top: 20px;
  justify-content: flex-end;
}
</style>
