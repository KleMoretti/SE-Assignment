<template>
  <div class="doctor-schedule-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <el-page-header @back="goBack">
        <template #content>
          <div class="header-content">
            <h1 class="page-title">
              <el-icon class="title-icon"><Calendar /></el-icon>
              医生排班管理
            </h1>
            <p v-if="doctorInfo" class="doctor-info-text">
              {{ doctorInfo.name }} - {{ doctorInfo.title }} - {{ doctorInfo.department }}
            </p>
          </div>
        </template>
        <template #extra>
          <el-button type="primary" :icon="Plus" @click="showAddScheduleDialog">
            添加排班
          </el-button>
        </template>
      </el-page-header>
    </div>

    <!-- 日期导航卡片 -->
    <el-card class="date-nav-card" shadow="never">
      <div class="date-navigation">
        <el-button-group>
          <el-button :icon="ArrowLeft" @click="previousWeek">上一周</el-button>
          <el-button>
            <el-icon><Calendar /></el-icon>
            {{ dateRangeText }}
          </el-button>
          <el-button @click="nextWeek">
            下一周
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </el-button-group>
        <el-button type="primary" plain @click="goToday">今天</el-button>
      </div>
    </el-card>

    <!-- 排班统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card-small">
          <el-statistic title="本周排班" :value="weekStats.totalSchedules">
            <template #prefix>
              <el-icon style="color: #409eff;"><Calendar /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card-small">
          <el-statistic title="预约人数" :value="weekStats.bookedPatients">
            <template #prefix>
              <el-icon style="color: #67c23a;"><User /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card-small">
          <el-statistic title="工作时长" :value="weekStats.totalHours" suffix="小时">
            <template #prefix>
              <el-icon style="color: #e6a23c;"><Timer /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card-small">
          <el-statistic title="排班率" :value="weekStats.scheduleRate" suffix="%">
            <template #prefix>
              <el-icon style="color: #f56c6c;"><TrendCharts /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 排班日历 -->
    <el-card class="schedule-calendar-card" shadow="never" v-loading="loading">
      <div class="calendar-container">
        <el-table :data="scheduleTableData" border stripe class="schedule-table">
          <el-table-column label="时间" width="100" fixed>
            <template #default="{ row }">
              <div class="time-slot">{{ row.time }}</div>
            </template>
          </el-table-column>

          <el-table-column
            v-for="day in weekDays"
            :key="day.date"
            :label="day.dayName"
            align="center"
          >
            <template #header>
              <div class="day-header" :class="{ 'is-today': day.isToday }">
                <div class="day-name">{{ day.dayName }}</div>
                <div class="day-date">{{ day.dateText }}</div>
                <el-tag v-if="day.isToday" size="small" type="primary">今天</el-tag>
              </div>
            </template>
            <template #default="{ row }">
              <div class="schedule-cell" @click="handleSlotClick(day.date, row.time)">
                <div
                  v-for="schedule in getScheduleForSlot(day.date, row.time)"
                  :key="schedule.id"
                  class="schedule-item"
                >
                  <el-tag
                    :type="getScheduleType(schedule.status)"
                    effect="dark"
                    class="schedule-tag"
                  >
                    {{ schedule.type }}
                  </el-tag>
                  <div class="schedule-time-range">
                    {{ schedule.startTime }} - {{ schedule.endTime }}
                  </div>
                  <div class="schedule-capacity">
                    <el-icon><User /></el-icon>
                    {{ schedule.bookedCount || 0 }}/{{ schedule.maxPatients }}
                  </div>
                  <div class="schedule-actions">
                    <el-button
                      size="small"
                      :icon="Edit"
                      circle
                      @click.stop="editSchedule(schedule)"
                    />
                    <el-button
                      size="small"
                      :icon="Delete"
                      circle
                      type="danger"
                      @click.stop="deleteSchedule(schedule)"
                    />
                  </div>
                </div>
                <el-button
                  v-if="!getScheduleForSlot(day.date, row.time).length"
                  size="small"
                  :icon="Plus"
                  circle
                  class="add-schedule-btn"
                />
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 添加/编辑排班对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingSchedule ? '编辑排班' : '添加排班'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="scheduleFormRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="日期" prop="date">
          <el-date-picker
            v-model="formData.date"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
          />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始时间" prop="startTime">
              <el-time-select
                v-model="formData.startTime"
                start="08:00"
                step="00:30"
                end="22:00"
                placeholder="开始时间"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束时间" prop="endTime">
              <el-time-select
                v-model="formData.endTime"
                start="08:00"
                step="00:30"
                end="22:00"
                placeholder="结束时间"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="排班类型" prop="type">
              <el-select v-model="formData.type" placeholder="请选择类型" style="width: 100%">
                <el-option label="门诊" value="门诊" />
                <el-option label="急诊" value="急诊" />
                <el-option label="手术" value="手术" />
                <el-option label="会诊" value="会诊" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最大人数" prop="maxPatients">
              <el-input-number
                v-model="formData.maxPatients"
                :min="1"
                :max="100"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

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
        <el-button @click="closeDialog">取消</el-button>
        <el-button type="primary" @click="submitSchedule" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Calendar, Plus, ArrowLeft, ArrowRight, Edit, Delete, User, Timer, TrendCharts
} from '@element-plus/icons-vue'
import { getDoctorDetail, getDoctorSchedule, createSchedule, updateSchedule, deleteSchedule as deleteScheduleApi } from '@/api/doctor'

// 路由
const router = useRouter()
const route = useRoute()

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const editingSchedule = ref(null)
const scheduleFormRef = ref(null)

const doctorInfo = ref(null)
const currentWeekStart = ref(new Date())
const scheduleList = ref([])

const weekStats = reactive({
  totalSchedules: 0,
  bookedPatients: 0,
  totalHours: 0,
  scheduleRate: 0
})

const formData = reactive({
  date: '',
  startTime: '',
  endTime: '',
  type: '',
  maxPatients: 10,
  notes: ''
})

const formRules = {
  date: [{ required: true, message: '请选择日期', trigger: 'change' }],
  startTime: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  endTime: [{ required: true, message: '请选择结束时间', trigger: 'change' }],
  type: [{ required: true, message: '请选择排班类型', trigger: 'change' }],
  maxPatients: [{ required: true, message: '请输入最大人数', trigger: 'blur' }]
}

// 时间段
const timeSlots = [
  '08:00', '09:00', '10:00', '11:00', '12:00',
  '13:00', '14:00', '15:00', '16:00', '17:00',
  '18:00', '19:00', '20:00'
]

// 计算属性
const dateRangeText = computed(() => {
  const start = new Date(currentWeekStart.value)
  const end = new Date(start)
  end.setDate(end.getDate() + 6)
  return `${formatDate(start)} - ${formatDate(end)}`
})

const weekDays = computed(() => {
  const days = []
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  for (let i = 0; i < 7; i++) {
    const date = new Date(currentWeekStart.value)
    date.setDate(date.getDate() + i)

    days.push({
      date: formatDate(date),
      dayName: ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][date.getDay()],
      dateText: `${date.getMonth() + 1}/${date.getDate()}`,
      isToday: date.getTime() === today.getTime()
    })
  }
  return days
})

const scheduleTableData = computed(() => {
  return timeSlots.map(time => ({ time }))
})

// 方法
const fetchDoctorInfo = async () => {
  try {
    const id = route.params.id
    if (id) {
      const res = await getDoctorDetail(id)
      doctorInfo.value = res.data
    }
  } catch (error) {
    console.error('获取医生信息失败', error)
  }
}

const fetchScheduleList = async () => {
  loading.value = true
  try {
    const id = route.params.id || doctorInfo.value?.id
    if (!id) return

    const params = {
      startDate: weekDays.value[0].date,
      endDate: weekDays.value[6].date
    }
    const res = await getDoctorSchedule(id, params)
    scheduleList.value = res.data.items || []
    calculateWeekStats()
  } catch (error) {
    ElMessage.error('获取排班数据失败')
  } finally {
    loading.value = false
  }
}

const calculateWeekStats = () => {
  weekStats.totalSchedules = scheduleList.value.length
  weekStats.bookedPatients = scheduleList.value.reduce((sum, s) => sum + (s.bookedCount || 0), 0)
  weekStats.totalHours = scheduleList.value.reduce((sum, s) => {
    const start = new Date(`2000-01-01 ${s.startTime}`)
    const end = new Date(`2000-01-01 ${s.endTime}`)
    return sum + (end - start) / (1000 * 60 * 60)
  }, 0)
  weekStats.scheduleRate = weekStats.totalSchedules > 0 ? Math.round((weekStats.bookedPatients / (weekStats.totalSchedules * 10)) * 100) : 0
}

const getScheduleForSlot = (date, time) => {
  return scheduleList.value.filter(schedule => {
    if (schedule.date !== date) return false
    const scheduleHour = parseInt(schedule.startTime.split(':')[0])
    const slotHour = parseInt(time.split(':')[0])
    return scheduleHour === slotHour
  })
}

const getScheduleType = (status) => {
  const typeMap = {
    available: 'success',
    full: 'warning',
    cancelled: 'info'
  }
  return typeMap[status] || 'info'
}

const formatDate = (date) => {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

const previousWeek = () => {
  const date = new Date(currentWeekStart.value)
  date.setDate(date.getDate() - 7)
  currentWeekStart.value = date
  fetchScheduleList()
}

const nextWeek = () => {
  const date = new Date(currentWeekStart.value)
  date.setDate(date.getDate() + 7)
  currentWeekStart.value = date
  fetchScheduleList()
}

const goToday = () => {
  const today = new Date()
  today.setDate(today.getDate() - today.getDay())
  currentWeekStart.value = today
  fetchScheduleList()
}

const handleSlotClick = (date, time) => {
  const schedules = getScheduleForSlot(date, time)
  if (schedules.length === 0) {
    showAddScheduleDialog()
    formData.date = date
    formData.startTime = time
  }
}

const showAddScheduleDialog = () => {
  editingSchedule.value = null
  resetFormData()
  dialogVisible.value = true
}

const editSchedule = (schedule) => {
  editingSchedule.value = schedule
  Object.assign(formData, {
    date: schedule.date,
    startTime: schedule.startTime,
    endTime: schedule.endTime,
    type: schedule.type,
    maxPatients: schedule.maxPatients,
    notes: schedule.notes
  })
  dialogVisible.value = true
}

const submitSchedule = async () => {
  if (!scheduleFormRef.value) return

  await scheduleFormRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      const doctorId = route.params.id || doctorInfo.value?.id
      if (editingSchedule.value) {
        await updateSchedule(doctorId, editingSchedule.value.id, formData)
        ElMessage.success('更新排班成功')
      } else {
        await createSchedule(doctorId, formData)
        ElMessage.success('添加排班成功')
      }
      closeDialog()
      fetchScheduleList()
    } catch (error) {
      ElMessage.error(editingSchedule.value ? '更新排班失败' : '添加排班失败')
    } finally {
      submitting.value = false
    }
  })
}

const deleteSchedule = async (schedule) => {
  try {
    await ElMessageBox.confirm('确定要删除该排班吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const doctorId = route.params.id || doctorInfo.value?.id
    await deleteScheduleApi(doctorId, schedule.id)
    ElMessage.success('删除排班成功')
    fetchScheduleList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除排班失败')
    }
  }
}

const closeDialog = () => {
  dialogVisible.value = false
  resetFormData()
}

const resetFormData = () => {
  Object.assign(formData, {
    date: '',
    startTime: '',
    endTime: '',
    type: '',
    maxPatients: 10,
    notes: ''
  })
  if (scheduleFormRef.value) {
    scheduleFormRef.value.clearValidate()
  }
}

const goBack = () => {
  router.back()
}

// 生命周期
onMounted(() => {
  goToday()
  fetchDoctorInfo()
  fetchScheduleList()
})
</script>

<style scoped>
.doctor-schedule-container {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 24px;
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

.doctor-info-text {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.date-nav-card {
  margin-bottom: 16px;
}

.date-navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stats-row {
  margin-bottom: 16px;
}

.stat-card-small {
  height: 100%;
}

.schedule-calendar-card {
  margin-bottom: 24px;
}

.calendar-container {
  overflow-x: auto;
}

.schedule-table {
  width: 100%;
  min-width: 1200px;
}

.time-slot {
  font-weight: 600;
  color: #606266;
  text-align: center;
}

.day-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 8px;
}

.day-header.is-today {
  background-color: #ecf5ff;
  border-radius: 8px;
}

.day-name {
  font-weight: 600;
  color: #303133;
}

.day-date {
  font-size: 12px;
  color: #909399;
}

.schedule-cell {
  min-height: 80px;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.3s;
}

.schedule-cell:hover {
  background-color: #f5f7fa;
}

.schedule-item {
  width: 100%;
  padding: 12px;
  background-color: #ecf5ff;
  border-radius: 8px;
  border: 1px solid #d9ecff;
  transition: all 0.3s;
}

.schedule-item:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.schedule-tag {
  margin-bottom: 8px;
}

.schedule-time-range {
  font-size: 12px;
  color: #606266;
  margin-bottom: 4px;
}

.schedule-capacity {
  font-size: 12px;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 8px;
}

.schedule-actions {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.add-schedule-btn {
  opacity: 0.3;
  transition: opacity 0.3s;
}

.schedule-cell:hover .add-schedule-btn {
  opacity: 1;
}
</style>

