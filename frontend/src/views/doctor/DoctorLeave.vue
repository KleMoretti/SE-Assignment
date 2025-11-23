<template>
  <div class="doctor-leave-container">
    <div class="page-header">
      <el-page-header @back="goBack">
        <template #content>
          <div class="header-content">
            <h1 class="page-title">
              <el-icon class="title-icon"><Calendar /></el-icon>
              医生请假管理
            </h1>
            <p class="page-subtitle">查看和管理医生的请假记录</p>
          </div>
        </template>
        <template #extra>
          <el-space>
            <el-select
              v-model="filters.doctorId"
              placeholder="选择医生"
              clearable
              filterable
              style="width: 220px"
              :loading="doctorSelectLoading"
              @change="handleFilterChange"
            >
              <el-option
                v-for="item in doctorOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
            <el-select
              v-model="filters.status"
              placeholder="请假状态"
              clearable
              style="width: 160px"
              @change="handleFilterChange"
            >
              <el-option label="待审批" value="pending" />
              <el-option label="已批准" value="approved" />
              <el-option label="已拒绝" value="rejected" />
              <el-option label="已撤销" value="cancelled" />
            </el-select>
            <el-button @click="openScheduleOverview">
              按科室查看排班
            </el-button>
            <el-button type="primary" :icon="Plus" @click="showCreateDialog">
              新建请假
            </el-button>
          </el-space>
        </template>
      </el-page-header>
    </div>

    <el-card class="filter-card" shadow="never">
      <el-row :gutter="16" align="middle">
        <el-col :span="6">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 100%"
            @change="handleFilterChange"
          />
        </el-col>
        <el-col :span="4">
          <el-select
            v-model="filters.leaveType"
            placeholder="请假类型"
            clearable
            style="width: 100%"
            @change="handleFilterChange"
          >
            <el-option label="病假" value="sick" />
            <el-option label="年假" value="annual" />
            <el-option label="事假" value="personal" />
            <el-option label="紧急" value="emergency" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-col>
      </el-row>
    </el-card>

    <el-card shadow="never" class="table-card" v-loading="loading">
      <el-table :data="leaveList" stripe border height="calc(100vh - 360px)">
        <el-table-column prop="doctorName" label="医生" min-width="140" />
        <el-table-column prop="leaveType" label="类型" min-width="90">
          <template #default="{ row }">
            <el-tag size="small">{{ getLeaveTypeLabel(row.leaveType) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="请假日期" min-width="200">
          <template #default="{ row }">
            {{ row.startDate }} 至 {{ row.endDate }}
            <span v-if="row.days">（{{ row.days }} 天）</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" min-width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="substituteDoctorName" label="替班医生" min-width="120" />
        <el-table-column prop="reason" label="原因" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="220" fixed="right" align="center">
          <template #default="{ row }">
            <el-space>
              <el-button size="small" text type="primary" @click="openDetail(row)">
                详情
              </el-button>
              <el-button
                size="small"
                text
                type="success"
                @click="handleApprove(row)"
                :disabled="row.status === 'approved'"
              >
                通过
              </el-button>
              <el-button
                size="small"
                text
                type="danger"
                @click="handleReject(row)"
                :disabled="row.status === 'rejected'"
              >
                拒绝
              </el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="total > 0" class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 新建/编辑请假对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '新建请假申请' : '编辑请假申请'"
      width="520px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="医生" prop="doctorId">
          <el-select
            v-model="formData.doctorId"
            placeholder="请选择医生"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="item in doctorOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="请假类型" prop="leaveType">
          <el-select v-model="formData.leaveType" placeholder="请选择类型" style="width: 100%">
            <el-option label="病假" value="sick" />
            <el-option label="年假" value="annual" />
            <el-option label="事假" value="personal" />
            <el-option label="紧急" value="emergency" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="请假日期" prop="dateRange">
          <el-date-picker
            v-model="formData.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="替班医生" prop="substituteDoctorId">
          <el-select
            v-model="formData.substituteDoctorId"
            placeholder="可选"
            clearable
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="item in doctorOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="原因" prop="reason">
          <el-input
            v-model="formData.reason"
            type="textarea"
            :rows="3"
            maxlength="500"
            show-word-limit
            placeholder="请填写请假原因"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeDialog">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitForm">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 审批备注对话框 -->
    <el-dialog v-model="approveDialogVisible" title="审批请假" width="420px">
      <el-form :model="approveForm" label-width="100px">
        <el-form-item label="审批意见">
          <el-input
            v-model="approveForm.approvalNotes"
            type="textarea"
            :rows="3"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="approveDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="confirmApprove">
          确定
        </el-button>
      </template>
    </el-dialog>

    <el-drawer
      v-model="scheduleOverviewVisible"
      title="科室排班总览"
      size="60%"
    >
      <el-space direction="vertical" style="width: 100%">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-select
              v-model="scheduleOverviewFilters.department"
              placeholder="选择科室"
              clearable
              filterable
              style="width: 100%"
            >
              <el-option
                v-for="item in departmentOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-col>
          <el-col :span="10">
            <el-date-picker
              v-model="scheduleOverviewFilters.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              style="width: 100%"
            />
          </el-col>
          <el-col :span="4">
            <el-select
              v-model="scheduleOverviewFilters.shift"
              placeholder="班次"
              clearable
              style="width: 100%"
            >
              <el-option label="上午" value="morning" />
              <el-option label="下午" value="afternoon" />
              <el-option label="晚上" value="evening" />
            </el-select>
          </el-col>
          <el-col :span="2">
            <el-button type="primary" @click="searchScheduleOverview">
              查询
            </el-button>
          </el-col>
        </el-row>

        <el-table
          :data="scheduleOverviewList"
          stripe
          border
          height="520"
          v-loading="scheduleOverviewLoading"
        >
          <el-table-column prop="date" label="日期" min-width="120" />
          <el-table-column prop="department" label="科室" min-width="140" />
          <el-table-column prop="doctorName" label="医生" min-width="120" />
          <el-table-column prop="shift" label="班次" min-width="90">
            <template #default="{ row }">
              <el-tag size="small">{{ getShiftLabel(row.shift) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="时间" min-width="160">
            <template #default="{ row }">
              <span v-if="row.startTime || row.endTime">{{ row.startTime || '--:--' }} - {{ row.endTime || '--:--' }}</span>
              <span v-else>全天</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" min-width="100" align="center">
            <template #default="{ row }">
              <el-tag size="small" type="success" v-if="row.status === 'available'">可预约</el-tag>
              <el-tag size="small" type="warning" v-else-if="row.status === 'full'">已满</el-tag>
              <el-tag size="small" type="info" v-else>已取消</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-space>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Calendar, Plus
} from '@element-plus/icons-vue'
import {
  getDoctorList,
  getLeaveList,
  createLeave,
  approveLeave,
  rejectLeave,
  getDepartments,
  getDepartmentSchedules
} from '@/api/doctor'

const router = useRouter()

const loading = ref(false)
const dialogVisible = ref(false)
const approveDialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref(null)

const doctorOptions = ref([])
const doctorSelectLoading = ref(false)

const departmentOptions = ref([])

const filters = reactive({
  doctorId: undefined,
  status: undefined,
  leaveType: undefined
})

const dateRange = ref([])

const leaveList = ref([])
const pagination = reactive({
  page: 1,
  pageSize: 10
})
const total = ref(0)

const dialogMode = ref('create')
const currentLeave = ref(null)

const formData = reactive({
  doctorId: undefined,
  leaveType: undefined,
  dateRange: [],
  substituteDoctorId: undefined,
  reason: ''
})

const formRules = {
  doctorId: [{ required: true, message: '请选择医生', trigger: 'change' }],
  leaveType: [{ required: true, message: '请选择请假类型', trigger: 'change' }],
  dateRange: [{ required: true, message: '请选择请假日期', trigger: 'change' }]
}

const approveForm = reactive({
  approvalNotes: ''
})

const scheduleOverviewVisible = ref(false)
const scheduleOverviewLoading = ref(false)
const scheduleOverviewList = ref([])

const scheduleOverviewFilters = reactive({
  department: '',
  dateRange: [],
  shift: ''
})

const fetchDoctorOptions = async () => {
  doctorSelectLoading.value = true
  try {
    const res = await getDoctorList({ page: 1, pageSize: 100, status: 'active' })
    const items = res.data.items || []
    doctorOptions.value = items.map((item) => {
      const parts = [item.name, item.department, item.title].filter(Boolean)
      return {
        value: item.id,
        label: parts.join(' - ')
      }
    })
  } catch (error) {
    console.error('获取医生列表失败', error)
  } finally {
    doctorSelectLoading.value = false
  }
}

const fetchDepartments = async () => {
  try {
    const res = await getDepartments()
    const items = res.data || res
    departmentOptions.value = (items || []).map((item) => ({
      value: item.value || item.code || item,
      label: item.label || item.name || item
    }))
  } catch (error) {
    console.error('获取科室列表失败', error)
  }
}

const buildQueryParams = () => {
  const [start, end] = dateRange.value || []
  return {
    page: pagination.page,
    pageSize: pagination.pageSize,
    doctorId: filters.doctorId,
    status: filters.status,
    leaveType: filters.leaveType,
    startDate: start,
    endDate: end
  }
}

const fetchLeaveList = async () => {
  loading.value = true
  try {
    const params = buildQueryParams()
    const res = await getLeaveList(params)
    leaveList.value = res.data.list || []
    total.value = res.data.total || 0
  } catch (error) {
    ElMessage.error('获取请假列表失败')
  } finally {
    loading.value = false
  }
}

const handleFilterChange = () => {
  pagination.page = 1
  fetchLeaveList()
}

const handleSizeChange = () => {
  pagination.page = 1
  fetchLeaveList()
}

const handlePageChange = () => {
  fetchLeaveList()
}

const showCreateDialog = () => {
  dialogMode.value = 'create'
  currentLeave.value = null
  Object.assign(formData, {
    doctorId: filters.doctorId,
    leaveType: undefined,
    dateRange: [],
    substituteDoctorId: undefined,
    reason: ''
  })
  dialogVisible.value = true
}

const closeDialog = () => {
  dialogVisible.value = false
}

const submitForm = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      const [start, end] = formData.dateRange || []
      await createLeave({
        doctorId: formData.doctorId,
        leaveType: formData.leaveType,
        startDate: start,
        endDate: end,
        reason: formData.reason,
        substituteDoctorId: formData.substituteDoctorId
      })
      ElMessage.success('创建请假申请成功')
      dialogVisible.value = false
      fetchLeaveList()
    } catch (error) {
      ElMessage.error('创建请假申请失败')
    } finally {
      submitting.value = false
    }
  })
}

const openDetail = (row) => {
  currentLeave.value = row
  // 目前只弹出基础信息，后续可扩展为侧滑详情
  ElMessage.info(`请假：${row.doctorName} ${row.startDate} - ${row.endDate}`)
}

const handleApprove = (row) => {
  currentLeave.value = row
  approveForm.approvalNotes = ''
  approveDialogVisible.value = true
}

const confirmApprove = async () => {
  if (!currentLeave.value) return
  submitting.value = true
  try {
    await approveLeave(currentLeave.value.id, {
      approvalNotes: approveForm.approvalNotes
    })
    ElMessage.success('审批通过成功')
    approveDialogVisible.value = false
    fetchLeaveList()
  } catch (error) {
    ElMessage.error('审批通过失败')
  } finally {
    submitting.value = false
  }
}

const handleReject = async (row) => {
  try {
    await rejectLeave(row.id, { approvalNotes: '不符合请假要求' })
    ElMessage.success('已拒绝该请假申请')
    fetchLeaveList()
  } catch (error) {
    ElMessage.error('拒绝失败')
  }
}

const getLeaveTypeLabel = (type) => {
  const map = {
    sick: '病假',
    annual: '年假',
    personal: '事假',
    emergency: '紧急',
    other: '其他'
  }
  return map[type] || type || '-'
}

const getStatusLabel = (status) => {
  const map = {
    pending: '待审批',
    approved: '已批准',
    rejected: '已拒绝',
    cancelled: '已撤销'
  }
  return map[status] || status || '-'
}

const getStatusTagType = (status) => {
  const map = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
    cancelled: 'info'
  }
  return map[status] || 'info'
}

const goBack = () => {
  router.push('/doctor')
}

const openScheduleOverview = () => {
  scheduleOverviewVisible.value = true
}

const getShiftLabel = (shift) => {
  const map = {
    morning: '上午',
    afternoon: '下午',
    evening: '晚上'
  }
  return map[shift] || shift || '-'
}

const searchScheduleOverview = async () => {
  const [start, end] = scheduleOverviewFilters.dateRange || []
  if (!scheduleOverviewFilters.department || !start || !end) {
    ElMessage.warning('请选择科室和日期范围')
    return
  }

  scheduleOverviewLoading.value = true
  try {
    const res = await getDepartmentSchedules({
      department: scheduleOverviewFilters.department,
      startDate: start,
      endDate: end,
      shift: scheduleOverviewFilters.shift,
      status: 'available'
    })
    scheduleOverviewList.value = res.data.list || []
  } catch (error) {
    ElMessage.error('获取排班总览失败')
  } finally {
    scheduleOverviewLoading.value = false
  }
}

onMounted(async () => {
  await fetchDoctorOptions()
  await fetchDepartments()
  await fetchLeaveList()
})
</script>

<style scoped>
.doctor-leave-container {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 16px;
}

.header-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.page-title {
  font-size: 22px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-icon {
  font-size: 24px;
  color: #409eff;
}

.page-subtitle {
  font-size: 13px;
  color: #909399;
}

.filter-card {
  margin-bottom: 16px;
}

.table-card {
  margin-bottom: 24px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  padding-top: 16px;
}
</style>
