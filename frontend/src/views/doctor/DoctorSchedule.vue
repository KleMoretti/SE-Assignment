<template>
  <div class="doctor-schedule-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2>医生排班管理</h2>
      <el-button type="primary" @click="showAddDialog">
        <el-icon><Plus /></el-icon>
        添加排班
      </el-button>
    </div>

    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="医生">
          <el-select
            v-model="searchForm.doctor_id"
            placeholder="请选择医生"
            clearable
            filterable
            @change="handleSearch"
          >
            <el-option
              v-for="doctor in doctors"
              :key="doctor.id"
              :label="`${doctor.name} - ${doctor.department}`"
              :value="doctor.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="日期">
          <el-date-picker
            v-model="searchForm.date"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            clearable
            @change="handleSearch"
          />
        </el-form-item>

        <el-form-item label="班次">
          <el-select
            v-model="searchForm.shift"
            placeholder="请选择班次"
            clearable
            @change="handleSearch"
          >
            <el-option label="上午班" value="morning" />
            <el-option label="下午班" value="afternoon" />
            <el-option label="夜班" value="evening" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-select
            v-model="searchForm.status"
            placeholder="请选择状态"
            clearable
            @change="handleSearch"
          >
            <el-option label="可预约" value="available" />
            <el-option label="已满" value="full" />
            <el-option label="已取消" value="cancelled" />
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
        :data="scheduleList"
        stripe
        border
      >
        <el-table-column prop="doctor_name" label="医生姓名" width="120" />
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="shift" label="班次" width="100">
          <template #default="{ row }">
            <el-tag :type="getShiftType(row.shift)">
              {{ getShiftText(row.shift) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="开始时间" width="100" />
        <el-table-column prop="end_time" label="结束时间" width="100" />
        <el-table-column prop="max_patients" label="最大接诊数" width="110" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="备注" min-width="150" show-overflow-tooltip />

        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              link
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-popconfirm
              title="确定要删除这条排班记录吗？"
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

    <!-- 添加/编辑排班对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="scheduleFormRef"
        :model="scheduleForm"
        :rules="scheduleRules"
        label-width="110px"
      >
        <el-form-item label="医生" prop="doctor_id">
          <el-select
            v-model="scheduleForm.doctor_id"
            placeholder="请选择医生"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="doctor in doctors"
              :key="doctor.id"
              :label="`${doctor.name} - ${doctor.department} - ${doctor.title}`"
              :value="doctor.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="日期" prop="date">
          <el-date-picker
            v-model="scheduleForm.date"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="班次" prop="shift">
          <el-radio-group v-model="scheduleForm.shift">
            <el-radio label="morning">上午班</el-radio>
            <el-radio label="afternoon">下午班</el-radio>
            <el-radio label="evening">夜班</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="开始时间" prop="start_time">
          <el-time-picker
            v-model="scheduleForm.start_time"
            placeholder="选择开始时间"
            format="HH:mm"
            value-format="HH:mm"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="结束时间" prop="end_time">
          <el-time-picker
            v-model="scheduleForm.end_time"
            placeholder="选择结束时间"
            format="HH:mm"
            value-format="HH:mm"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="最大接诊数" prop="max_patients">
          <el-input-number
            v-model="scheduleForm.max_patients"
            :min="1"
            :max="100"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item v-if="editMode" label="状态" prop="status">
          <el-radio-group v-model="scheduleForm.status">
            <el-radio label="available">可预约</el-radio>
            <el-radio label="full">已满</el-radio>
            <el-radio label="cancelled">已取消</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="scheduleForm.notes"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saveLoading" @click="handleSave">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import {
  getSchedules,
  createSchedule,
  updateSchedule,
  deleteSchedule,
  getDoctors
} from '@/api/doctor'

const route = useRoute()

// 搜索表单
const searchForm = reactive({
  doctor_id: null,
  date: '',
  shift: '',
  status: ''
})

// 医生列表
const doctors = ref([])

// 排班列表
const scheduleList = ref([])
const loading = ref(false)

// 分页
const pagination = reactive({
  page: 1,
  per_page: 10,
  total: 0
})

// 对话框
const dialogVisible = ref(false)
const dialogTitle = ref('添加排班')
const editMode = ref(false)
const saveLoading = ref(false)

// 排班表单
const scheduleFormRef = ref(null)
const scheduleForm = reactive({
  id: null,
  doctor_id: null,
  date: '',
  shift: 'morning',
  start_time: '',
  end_time: '',
  max_patients: 20,
  status: 'available',
  notes: ''
})

// 表单验证规则
const scheduleRules = {
  doctor_id: [
    { required: true, message: '请选择医生', trigger: 'change' }
  ],
  date: [
    { required: true, message: '请选择日期', trigger: 'change' }
  ],
  shift: [
    { required: true, message: '请选择班次', trigger: 'change' }
  ]
}

// 获取排班列表
const getScheduleList = async () => {
  loading.value = true
  
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page,
      ...searchForm
    }
    
    const response = await getSchedules(params)
    
    if (response.success) {
      scheduleList.value = response.data.list
      pagination.total = response.data.total
    }
  } catch (error) {
    ElMessage.error(error.message || '获取排班列表失败')
  } finally {
    loading.value = false
  }
}

// 获取医生列表
const getDoctorList = async () => {
  try {
    const response = await getDoctors({ per_page: 1000, status: 'active' })
    
    if (response.success) {
      doctors.value = response.data.list
    }
  } catch (error) {
    console.error('获取医生列表失败:', error)
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  getScheduleList()
}

// 重置
const handleReset = () => {
  searchForm.doctor_id = null
  searchForm.date = ''
  searchForm.shift = ''
  searchForm.status = ''
  handleSearch()
}

// 显示添加对话框
const showAddDialog = () => {
  editMode.value = false
  dialogTitle.value = '添加排班'
  resetForm()
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  editMode.value = true
  dialogTitle.value = '编辑排班'
  
  Object.keys(scheduleForm).forEach(key => {
    scheduleForm[key] = row[key]
  })
  
  dialogVisible.value = true
}

// 删除
const handleDelete = async (id) => {
  try {
    const response = await deleteSchedule(id)
    
    if (response.success) {
      ElMessage.success('删除成功')
      getScheduleList()
    }
  } catch (error) {
    ElMessage.error(error.message || '删除失败')
  }
}

// 保存
const handleSave = async () => {
  if (!scheduleFormRef.value) return
  
  await scheduleFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    saveLoading.value = true
    
    try {
      const { id, ...data } = scheduleForm
      let response
      
      if (editMode.value) {
        response = await updateSchedule(id, data)
      } else {
        response = await createSchedule(data)
      }
      
      if (response.success) {
        ElMessage.success(editMode.value ? '更新成功' : '创建成功')
        dialogVisible.value = false
        getScheduleList()
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
  scheduleFormRef.value?.clearValidate()
}

// 重置表单
const resetForm = () => {
  Object.assign(scheduleForm, {
    id: null,
    doctor_id: null,
    date: '',
    shift: 'morning',
    start_time: '',
    end_time: '',
    max_patients: 20,
    status: 'available',
    notes: ''
  })
}

// 获取班次类型
const getShiftType = (shift) => {
  const typeMap = {
    morning: 'success',
    afternoon: 'warning',
    evening: 'danger'
  }
  return typeMap[shift] || ''
}

// 获取班次文本
const getShiftText = (shift) => {
  const textMap = {
    morning: '上午班',
    afternoon: '下午班',
    evening: '夜班'
  }
  return textMap[shift] || shift
}

// 获取状态类型
const getStatusType = (status) => {
  const typeMap = {
    available: 'success',
    full: 'warning',
    cancelled: 'info'
  }
  return typeMap[status] || ''
}

// 获取状态文本
const getStatusText = (status) => {
  const textMap = {
    available: '可预约',
    full: '已满',
    cancelled: '已取消'
  }
  return textMap[status] || status
}

// 初始化
onMounted(() => {
  getDoctorList()
  
  // 从 URL 查询参数中获取 doctor_id
  const route = useRoute()
  if (route.query.doctor_id) {
    searchForm.doctor_id = parseInt(route.query.doctor_id)
  }
  
  getScheduleList()
})
</script>

<style scoped>
.doctor-schedule-container {
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

