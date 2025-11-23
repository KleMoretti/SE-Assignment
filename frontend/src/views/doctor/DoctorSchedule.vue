<template>
  <div class="doctor-schedule-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <el-page-header @back="goBack">
        <template #content>
          <div class="header-content">
            <h1 class="page-title">
              <el-icon class="title-icon"><Calendar /></el-icon>
              科室排班总览
            </h1>
            <p class="page-subtitle">
              按科室和日期查看所有医生的排班安排
            </p>
          </div>
        </template>
        <template #extra>
          <el-space wrap>
            <el-select
              v-model="selectedDepartment"
              placeholder="全部科室"
              filterable
              clearable
              style="width: 150px"
              @change="handleDepartmentChange"
            >
              <el-option label="全部科室" value="" />
              <el-option
                v-for="dept in departmentOptions"
                :key="dept.value"
                :label="dept.label"
                :value="dept.value"
              />
            </el-select>
            <el-radio-group v-model="viewMode" size="small" @change="handleViewModeChange">
              <el-radio-button label="week">一周</el-radio-button>
              <el-radio-button label="twoWeeks">两周</el-radio-button>
            </el-radio-group>
          </el-space>
        </template>
      </el-page-header>
    </div>

    <!-- 日期导航与筛选 -->
    <el-card class="filter-card" shadow="never">
      <div class="filter-row">
        <div class="date-navigation">
          <el-button-group>
            <el-button :icon="ArrowLeft" @click="previousPeriod">上一{{viewMode === 'week' ? '周' : '期'}}</el-button>
            <el-button>
              <el-icon><Calendar /></el-icon>
              {{ dateRangeText }}
            </el-button>
            <el-button @click="nextPeriod">
              下一{{viewMode === 'week' ? '周' : '期'}}
              <el-icon><ArrowRight /></el-icon>
            </el-button>
          </el-button-group>
          <el-button type="primary" plain @click="goToday">今天</el-button>
        </div>
        <div class="shift-filter">
          <span class="filter-label">班次筛选：</span>
          <el-checkbox-group v-model="visibleShifts" size="small" @change="fetchScheduleMatrix">
            <el-checkbox label="morning">上午</el-checkbox>
            <el-checkbox label="afternoon">下午</el-checkbox>
            <el-checkbox label="evening">晚上</el-checkbox>
          </el-checkbox-group>
        </div>
      </div>
    </el-card>

    <!-- 统计信息 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="科室医生" :value="stats.totalDoctors">
            <template #prefix>
              <el-icon style="color: #409eff;"><User /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="总排班" :value="stats.totalSchedules">
            <template #prefix>
              <el-icon style="color: #67c23a;"><Calendar /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="可预约" :value="stats.availableSchedules">
            <template #prefix>
              <el-icon style="color: #e6a23c;"><SuccessFilled /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="已约满" :value="stats.fullSchedules">
            <template #prefix>
              <el-icon style="color: #f56c6c;"><Warning /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 排班矩阵 -->
    <el-card class="schedule-matrix-card" shadow="never" v-loading="loading">
      <div class="matrix-container">
        <div class="matrix-scroll" v-if="matrixData.length > 0">
          <table class="schedule-matrix">
            <thead>
              <tr>
                <th class="doctor-column-header">医生</th>
                <th 
                  v-for="dateCol in dateColumns" 
                  :key="dateCol.date"
                  class="date-column-header"
                  :class="{ 'is-today': dateCol.isToday }"
                >
                  <div class="date-header-content">
                    <div class="date-weekday">{{ dateCol.weekday }}</div>
                    <div class="date-text">{{ dateCol.monthDay }}</div>
                    <el-tag v-if="dateCol.isToday" size="small" type="primary" effect="dark">今</el-tag>
                  </div>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in matrixData" :key="row.doctorId" class="doctor-row">
                <td class="doctor-cell">
                  <div class="doctor-info">
                    <div class="doctor-name">{{ row.doctorName }}</div>
                    <div class="doctor-meta">
                      <el-tag size="small" type="info" effect="plain">{{ row.doctorDepartment }}</el-tag>
                      <span class="doctor-title">{{ row.doctorTitle }}</span>
                    </div>
                  </div>
                </td>
                <td 
                  v-for="dateCol in dateColumns" 
                  :key="dateCol.date"
                  class="schedule-cell"
                  :class="{ 'has-schedule': getCellSchedules(row.doctorId, dateCol.date).length > 0 }"
                  @click="handleCellClick(row, dateCol.date)"
                >
                  <div class="cell-content">
                    <div 
                      v-for="schedule in getCellSchedules(row.doctorId, dateCol.date)"
                      :key="schedule.id"
                      class="schedule-badge"
                      :class="`badge-${schedule.shift}`"
                      :title="getScheduleTooltip(schedule)"
                    >
                      <el-tag 
                        :type="getShiftTagType(schedule.shift)" 
                        size="small" 
                        effect="dark"
                        class="shift-tag"
                      >
                        {{ getShiftLabel(schedule.shift) }}
                      </el-tag>
                      <div class="schedule-time">{{ schedule.startTime }}-{{ schedule.endTime }}</div>
                      <div class="schedule-status">
                        <el-icon v-if="schedule.status === 'available'" style="color: #67c23a;"><SuccessFilled /></el-icon>
                        <el-icon v-if="schedule.status === 'full'" style="color: #e6a23c;"><Warning /></el-icon>
                        <el-icon v-if="schedule.status === 'cancelled'" style="color: #909399;"><CircleClose /></el-icon>
                        <span class="patient-count">{{ schedule.bookedCount || 0 }}/{{ schedule.maxPatients }}</span>
                      </div>
                    </div>
                    <div v-if="getCellSchedules(row.doctorId, dateCol.date).length === 0" class="empty-cell">
                      <span class="empty-text">—</span>
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <el-empty 
          v-else 
          description="暂无医生数据" 
          :image-size="120"
        />
      </div>
    </el-card>

    <!-- 排班详情抽屉 -->
    <el-drawer
      v-model="detailDrawerVisible"
      :title="detailDrawerTitle"
      size="500px"
      direction="rtl"
    >
      <div v-if="selectedCellData" class="detail-content">
        <div class="detail-header">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="医生">{{ selectedCellData.doctorName }}</el-descriptions-item>
            <el-descriptions-item label="职称">{{ selectedCellData.doctorTitle }}</el-descriptions-item>
            <el-descriptions-item label="日期">{{ selectedCellData.date }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="schedules-list" v-if="selectedCellData.schedules && selectedCellData.schedules.length > 0">
          <h3 class="list-title">排班明细</h3>
          <el-card 
            v-for="schedule in selectedCellData.schedules" 
            :key="schedule.id"
            class="schedule-detail-card"
            shadow="hover"
          >
            <div class="schedule-detail-header">
              <el-tag :type="getShiftTagType(schedule.shift)" effect="dark">
                {{ getShiftLabel(schedule.shift) }}
              </el-tag>
              <el-tag :type="getStatusTagType(schedule.status)" size="small">
                {{ getStatusLabel(schedule.status) }}
              </el-tag>
            </div>
            <el-descriptions :column="1" size="small" class="schedule-desc">
              <el-descriptions-item label="时间">
                <el-icon><Clock /></el-icon>
                {{ schedule.startTime }} - {{ schedule.endTime }}
              </el-descriptions-item>
              <el-descriptions-item label="预约情况">
                <el-progress 
                  :percentage="getBookingPercentage(schedule)" 
                  :color="getProgressColor(schedule)"
                  :stroke-width="8"
                />
                <span style="margin-left: 8px;">{{ schedule.bookedCount || 0 }}/{{ schedule.maxPatients }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="备注" v-if="schedule.notes">
                {{ schedule.notes }}
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </div>
        <el-empty v-else description="当天无排班" :image-size="100" />
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Calendar, ArrowLeft, ArrowRight, User, Warning, SuccessFilled, CircleClose, Clock
} from '@element-plus/icons-vue'
import { getDepartments, getDepartmentSchedules, getDoctorList } from '@/api/doctor'

// 路由
const router = useRouter()

// 响应式数据
const loading = ref(false)
const selectedDepartment = ref('')
const departmentOptions = ref([])
const viewMode = ref('week') // 'week' | 'twoWeeks'
const currentPeriodStart = ref(new Date())
const visibleShifts = ref(['morning', 'afternoon', 'evening'])

// 排班原始数据
const scheduleList = ref([])
const doctorList = ref([])

// 详情抽屉
const detailDrawerVisible = ref(false)
const selectedCellData = ref(null)

// 统计数据
const stats = reactive({
  totalDoctors: 0,
  totalSchedules: 0,
  availableSchedules: 0,
  fullSchedules: 0
})

// 常量
const SHIFT_LABELS = {
  morning: '上午',
  afternoon: '下午',
  evening: '晚上'
}

const STATUS_LABELS = {
  available: '可预约',
  full: '已约满',
  cancelled: '已取消'
}

// 计算属性
const daysInPeriod = computed(() => {
  return viewMode.value === 'week' ? 7 : 14
})

const dateRangeText = computed(() => {
  const start = new Date(currentPeriodStart.value)
  const end = new Date(start)
  end.setDate(end.getDate() + daysInPeriod.value - 1)
  return `${formatDate(start)} ~ ${formatDate(end)}`
})

const dateColumns = computed(() => {
  const columns = []
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  for (let i = 0; i < daysInPeriod.value; i++) {
    const date = new Date(currentPeriodStart.value)
    date.setDate(date.getDate() + i)
    
    const dateStr = formatDate(date)
    columns.push({
      date: dateStr,
      weekday: ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][date.getDay()],
      monthDay: `${date.getMonth() + 1}/${date.getDate()}`,
      isToday: date.getTime() === today.getTime()
    })
  }
  return columns
})

const matrixData = computed(() => {
  if (doctorList.value.length === 0) {
    return []
  }

  return doctorList.value.map(doctor => ({
    doctorId: doctor.id,
    doctorName: doctor.name,
    doctorTitle: doctor.title || '医师',
    doctorDepartment: doctor.department || '未分配',
    schedules: scheduleList.value.filter(s => s.doctorId === doctor.id)
  }))
})

const detailDrawerTitle = computed(() => {
  if (!selectedCellData.value) return '排班详情'
  return `${selectedCellData.value.doctorName} - ${selectedCellData.value.date}`
})

// 工具方法
const formatDate = (date) => {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

const getShiftLabel = (shift) => SHIFT_LABELS[shift] || shift
const getStatusLabel = (status) => STATUS_LABELS[status] || status

const getShiftTagType = (shift) => {
  const typeMap = { morning: 'success', afternoon: 'warning', evening: 'info' }
  return typeMap[shift] || ''
}

const getStatusTagType = (status) => {
  const typeMap = { available: 'success', full: 'warning', cancelled: 'info' }
  return typeMap[status] || ''
}

const getBookingPercentage = (schedule) => {
  if (!schedule.maxPatients) return 0
  return Math.round(((schedule.bookedCount || 0) / schedule.maxPatients) * 100)
}

const getProgressColor = (schedule) => {
  const percentage = getBookingPercentage(schedule)
  if (percentage >= 90) return '#f56c6c'
  if (percentage >= 70) return '#e6a23c'
  return '#67c23a'
}

const getScheduleTooltip = (schedule) => {
  return `${getShiftLabel(schedule.shift)} ${schedule.startTime}-${schedule.endTime} (${schedule.bookedCount || 0}/${schedule.maxPatients})`
}

// 数据获取
const fetchDepartments = async () => {
  try {
    const res = await getDepartments()
    const items = res.data || res || []
    departmentOptions.value = items.map(item => {
      // 后端返回的可能是 { id: '内科', name: '内科' } 或直接是字符串
      const deptName = item.name || item.id || item
      return {
        value: deptName,  // 使用科室名称作为 value
        label: deptName
      }
    })
  } catch (error) {
    console.error('获取科室列表失败', error)
  }
}

const fetchDepartmentDoctors = async () => {
  try {
    const params = {
      status: 'active',
      page: 1,
      pageSize: 200  // 增加每页数量以支持显示所有医生
    }
    
    // 如果选择了科室，添加科室筛选
    if (selectedDepartment.value) {
      params.department = selectedDepartment.value
      console.log('查询科室医生:', selectedDepartment.value)
    } else {
      console.log('查询所有医生')
    }
    
    const res = await getDoctorList(params)
    doctorList.value = res.data.items || []
    stats.totalDoctors = doctorList.value.length
    
    console.log('获取到医生:', doctorList.value.length, '人')
    if (doctorList.value.length > 0) {
      console.log('医生列表:', doctorList.value.map(d => ({ id: d.id, name: d.name, dept: d.department })))
    }
  } catch (error) {
    console.error('获取医生列表失败:', error)
    doctorList.value = []
    stats.totalDoctors = 0
  }
}

const fetchScheduleMatrix = async () => {
  loading.value = true
  try {
    const params = {
      startDate: dateColumns.value[0]?.date,
      endDate: dateColumns.value[dateColumns.value.length - 1]?.date
      // 不限制 status，获取所有状态的排班
    }
    
    // 如果选择了科室，添加科室筛选
    if (selectedDepartment.value) {
      params.department = selectedDepartment.value
    }

    console.log('查询排班参数:', params)
    const res = await getDepartmentSchedules(params)
    const allSchedules = res.data.list || res.data.items || []
    
    console.log('后端返回排班数据:', allSchedules.length, '条')
    if (allSchedules.length > 0) {
      console.log('第一条排班示例:', allSchedules[0])
    }
    
    // 按班次筛选
    scheduleList.value = allSchedules.filter(s => 
      visibleShifts.value.includes(s.shift)
    )
    
    console.log('筛选后排班数据:', scheduleList.value.length, '条')
    console.log('当前医生列表:', doctorList.value.length, '人')
    
    updateStats()
  } catch (error) {
    console.error('获取排班数据失败:', error)
    ElMessage.error('获取排班数据失败')
    scheduleList.value = []
  } finally {
    loading.value = false
  }
}

const updateStats = () => {
  stats.totalSchedules = scheduleList.value.length
  stats.availableSchedules = scheduleList.value.filter(s => s.status === 'available').length
  stats.fullSchedules = scheduleList.value.filter(s => s.status === 'full').length
}

// 矩阵单元格数据获取
const getCellSchedules = (doctorId, date) => {
  const matches = scheduleList.value.filter(s => {
    // 后端返回的是驼峰命名 doctorId，不是 doctor_id
    const doctorMatch = s.doctorId === doctorId
    const dateMatch = s.date === date
    
    return doctorMatch && dateMatch
  })
  
  return matches
}

// 日期导航
const previousPeriod = () => {
  const date = new Date(currentPeriodStart.value)
  date.setDate(date.getDate() - daysInPeriod.value)
  currentPeriodStart.value = date
  fetchScheduleMatrix()
}

const nextPeriod = () => {
  const date = new Date(currentPeriodStart.value)
  date.setDate(date.getDate() + daysInPeriod.value)
  currentPeriodStart.value = date
  fetchScheduleMatrix()
}

const goToday = () => {
  const today = new Date()
  const dayOfWeek = today.getDay()
  const offset = dayOfWeek === 0 ? -6 : 1 - dayOfWeek  // 周一作为一周开始
  today.setDate(today.getDate() + offset)
  today.setHours(0, 0, 0, 0)
  currentPeriodStart.value = today
  fetchScheduleMatrix()
}

// 交互处理
const handleCellClick = (row, date) => {
  const schedules = getCellSchedules(row.doctorId, date)
  selectedCellData.value = {
    doctorId: row.doctorId,
    doctorName: row.doctorName,
    doctorTitle: row.doctorTitle,
    date,
    schedules
  }
  detailDrawerVisible.value = true
}

const handleDepartmentChange = async () => {
  console.log('科室切换:', selectedDepartment.value)
  
  // 先清空现有数据
  doctorList.value = []
  scheduleList.value = []
  
  // 先获取医生列表
  await fetchDepartmentDoctors()
  
  // 再获取排班数据
  await fetchScheduleMatrix()
  
  console.log('切换完成 - 医生:', doctorList.value.length, '排班:', scheduleList.value.length)
}

const handleViewModeChange = () => {
  goToday()
}

const goBack = () => {
  router.push('/doctor')
}

// 生命周期
onMounted(async () => {
  await fetchDepartments()
  // 初始化时获取所有医生
  await fetchDepartmentDoctors()
  goToday()
})
</script>

<style scoped>
.doctor-schedule-container {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

/* 页面头部 */
.page-header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.title-icon {
  font-size: 26px;
  color: #409eff;
}

.page-subtitle {
  font-size: 13px;
  color: #909399;
  margin: 0;
}

/* 筛选与导航 */
.filter-card {
  margin-bottom: 16px;
}

.filter-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.date-navigation {
  display: flex;
  align-items: center;
  gap: 12px;
}

.shift-filter {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 14px;
  color: #606266;
  white-space: nowrap;
}

/* 统计卡片 */
.stats-row {
  margin-bottom: 16px;
}

.stat-card {
  height: 100%;
}

/* 排班矩阵 */
.schedule-matrix-card {
  margin-bottom: 20px;
}

.matrix-container {
  overflow-x: auto;
  overflow-y: hidden;
}

.matrix-scroll {
  min-width: 100%;
  overflow-x: auto;
}

.schedule-matrix {
  width: 100%;
  border-collapse: collapse;
  background: white;
  min-width: 1000px;
}

/* 表头样式 */
.schedule-matrix thead {
  position: sticky;
  top: 0;
  z-index: 10;
  background: white;
}

.doctor-column-header {
  min-width: 120px;
  padding: 16px 12px;
  text-align: left;
  font-weight: 600;
  font-size: 14px;
  color: #303133;
  background: linear-gradient(135deg, #ecf5ff 0%, #f0f9ff 100%);
  border: 1px solid #ebeef5;
  position: sticky;
  left: 0;
  z-index: 11;
}

.date-column-header {
  min-width: 140px;
  padding: 12px 8px;
  text-align: center;
  font-weight: 500;
  background: #fafafa;
  border: 1px solid #ebeef5;
}

.date-column-header.is-today {
  background: linear-gradient(135deg, #ecf5ff 0%, #f0f9ff 100%);
  border-color: #409eff;
}

.date-header-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.date-weekday {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
}

.date-text {
  font-size: 12px;
  color: #909399;
}

/* 表格行 */
.doctor-row {
  transition: background-color 0.2s;
}

.doctor-row:hover {
  background-color: #fafafa;
}

/* 医生列 */
.doctor-cell {
  padding: 12px;
  border: 1px solid #ebeef5;
  background: white;
  position: sticky;
  left: 0;
  z-index: 5;
}

.doctor-row:hover .doctor-cell {
  background-color: #fafafa;
}

.doctor-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.doctor-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.doctor-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.doctor-title {
  font-size: 12px;
  color: #909399;
}

/* 排班单元格 */
.schedule-cell {
  padding: 8px;
  border: 1px solid #ebeef5;
  min-height: 80px;
  vertical-align: top;
  cursor: pointer;
  transition: all 0.2s;
  background: white;
}

.schedule-cell:hover {
  background-color: #f5f7fa;
}

.schedule-cell.has-schedule {
  background-color: #fafcff;
}

.schedule-cell.has-schedule:hover {
  background-color: #ecf5ff;
}

.cell-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-height: 60px;
}

/* 排班徽章 */
.schedule-badge {
  padding: 8px;
  border-radius: 6px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e6f7ff 100%);
  border-left: 3px solid #409eff;
  transition: all 0.2s;
}

.schedule-badge:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
}

.schedule-badge.badge-morning {
  border-left-color: #67c23a;
  background: linear-gradient(135deg, #f0f9ff 0%, #e6f7ff 100%);
}

.schedule-badge.badge-afternoon {
  border-left-color: #e6a23c;
  background: linear-gradient(135deg, #fdf6ec 0%, #fef0e0 100%);
}

.schedule-badge.badge-evening {
  border-left-color: #909399;
  background: linear-gradient(135deg, #f4f4f5 0%, #e9e9eb 100%);
}

.shift-tag {
  font-size: 11px;
  margin-bottom: 4px;
}

.schedule-time {
  font-size: 11px;
  color: #606266;
  margin-bottom: 4px;
  font-weight: 500;
}

.schedule-status {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #909399;
}

.patient-count {
  margin-left: auto;
}

/* 空单元格 */
.empty-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60px;
  color: #c0c4cc;
}

.empty-text {
  font-size: 16px;
  color: #dcdfe6;
}

/* 详情抽屉 */
.detail-content {
  padding: 0;
}

.detail-header {
  margin-bottom: 20px;
}

.schedules-list {
  margin-top: 20px;
}

.list-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid #f0f0f0;
}

.schedule-detail-card {
  margin-bottom: 12px;
}

.schedule-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.schedule-desc {
  margin-top: 8px;
}

/* 响应式 */
@media (max-width: 1200px) {
  .schedule-matrix {
    min-width: 1400px;
  }
  
  .date-column-header {
    min-width: 120px;
  }
}
</style>

