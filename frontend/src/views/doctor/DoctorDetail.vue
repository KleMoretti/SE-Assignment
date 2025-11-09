<template>
  <div class="doctor-detail-container">
    <!-- 返回按钮 -->
    <el-button @click="goBack" class="mb-4">
      <el-icon><ArrowLeft /></el-icon>
      返回列表
    </el-button>

    <!-- 加载状态 -->
    <el-skeleton v-if="loading" :rows="8" animated />

    <!-- 医生详情 -->
    <template v-else-if="doctor">
      <!-- 基本信息卡片 -->
      <el-card class="mb-4">
        <template #header>
          <div class="card-header">
            <span class="text-lg font-bold">基本信息</span>
            <el-button type="primary" size="small" @click="handleEdit">
              编辑信息
            </el-button>
          </div>
        </template>

        <el-descriptions :column="3" border>
          <el-descriptions-item label="医生编号">
            {{ doctor.doctor_no }}
          </el-descriptions-item>
          <el-descriptions-item label="姓名">
            {{ doctor.name }}
          </el-descriptions-item>
          <el-descriptions-item label="性别">
            {{ doctor.gender }}
          </el-descriptions-item>
          <el-descriptions-item label="年龄">
            {{ doctor.age }}
          </el-descriptions-item>
          <el-descriptions-item label="电话">
            {{ doctor.phone }}
          </el-descriptions-item>
          <el-descriptions-item label="邮箱">
            {{ doctor.email }}
          </el-descriptions-item>
          <el-descriptions-item label="科室">
            {{ doctor.department }}
          </el-descriptions-item>
          <el-descriptions-item label="职称">
            {{ doctor.title }}
          </el-descriptions-item>
          <el-descriptions-item label="学历">
            {{ doctor.education }}
          </el-descriptions-item>
          <el-descriptions-item label="入职日期">
            {{ doctor.hire_date }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="doctor.status === 'active' ? 'success' : 'info'">
              {{ doctor.status === 'active' ? '在职' : '离职' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="专长" :span="3">
            {{ doctor.specialty || '无' }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 统计信息卡片 -->
      <el-row :gutter="20" class="mb-4">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-icon">
              <el-icon :size="40" color="#409EFF">
                <Calendar />
              </el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-title">总预约数</div>
              <div class="stat-value">{{ doctor.statistics?.total_appointments || 0 }}</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-icon">
              <el-icon :size="40" color="#67C23A">
                <Check />
              </el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-title">已完成预约</div>
              <div class="stat-value">{{ doctor.statistics?.completed_appointments || 0 }}</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-icon">
              <el-icon :size="40" color="#E6A23C">
                <Document />
              </el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-title">病历记录</div>
              <div class="stat-value">{{ doctor.statistics?.total_medical_records || 0 }}</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-icon">
              <el-icon :size="40" color="#F56C6C">
                <Clock />
              </el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-title">排班记录</div>
              <div class="stat-value">{{ doctor.statistics?.total_schedules || 0 }}</div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 快捷操作 -->
      <el-card class="mb-4">
        <template #header>
          <span class="text-lg font-bold">快捷操作</span>
        </template>
        <el-space :size="20">
          <el-button type="primary" @click="handleViewSchedule">
            <el-icon><Calendar /></el-icon>
            查看排班
          </el-button>
          <el-button type="success" @click="handleViewPerformance">
            <el-icon><TrendCharts /></el-icon>
            查看绩效
          </el-button>
          <el-button type="warning" @click="handleAddSchedule">
            <el-icon><Plus /></el-icon>
            添加排班
          </el-button>
          <el-button type="info" @click="handleAddPerformance">
            <el-icon><Plus /></el-icon>
            添加绩效
          </el-button>
        </el-space>
      </el-card>

      <!-- 最近排班 -->
      <el-card class="mb-4" v-if="recentSchedules.length > 0">
        <template #header>
          <div class="card-header">
            <span class="text-lg font-bold">最近排班</span>
            <el-button type="text" @click="handleViewSchedule">查看全部</el-button>
          </div>
        </template>
        <el-table :data="recentSchedules" stripe>
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
          <el-table-column prop="notes" label="备注" show-overflow-tooltip />
        </el-table>
      </el-card>

      <!-- 最近绩效 -->
      <el-card v-if="recentPerformances.length > 0">
        <template #header>
          <div class="card-header">
            <span class="text-lg font-bold">最近绩效</span>
            <el-button type="text" @click="handleViewPerformance">查看全部</el-button>
          </div>
        </template>
        <el-table :data="recentPerformances" stripe>
          <el-table-column prop="year" label="年份" width="100" />
          <el-table-column prop="month" label="月份" width="80">
            <template #default="{ row }">
              {{ row.month }}月
            </template>
          </el-table-column>
          <el-table-column prop="patient_count" label="接诊人数" width="100" />
          <el-table-column prop="satisfaction_score" label="满意度" width="100" />
          <el-table-column prop="punctuality_score" label="准时率" width="100" />
          <el-table-column prop="quality_score" label="质量评分" width="100" />
          <el-table-column prop="total_score" label="综合评分" width="100">
            <template #default="{ row }">
              <el-tag :type="getScoreType(row.total_score)">
                {{ row.total_score ? row.total_score.toFixed(2) : 0 }}分
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="bonus" label="绩效奖金" width="120">
            <template #default="{ row }">
              <span class="bonus-text">¥{{ row.bonus ? row.bonus.toFixed(2) : 0 }}</span>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </template>

    <!-- 错误提示 -->
    <el-empty v-else description="未找到医生信息" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft,
  Calendar,
  Check,
  Document,
  Clock,
  TrendCharts,
  Plus
} from '@element-plus/icons-vue'
import {
  getDoctorDetail,
  getDoctorSchedules,
  getDoctorPerformances
} from '@/api/doctor'

const router = useRouter()
const route = useRoute()

const loading = ref(true)
const doctor = ref(null)
const recentSchedules = ref([])
const recentPerformances = ref([])

// 获取医生详情
const getDoctorInfo = async () => {
  loading.value = true
  
  try {
    const doctorId = route.params.id || route.query.id
    
    if (!doctorId) {
      ElMessage.error('缺少医生ID参数')
      goBack()
      return
    }
    
    // 获取基本信息
    const response = await getDoctorDetail(doctorId)
    
    if (response.success) {
      doctor.value = response.data
      
      // 获取最近排班
      getRecentSchedules(doctorId)
      
      // 获取最近绩效
      getRecentPerformances(doctorId)
    }
  } catch (error) {
    ElMessage.error(error.message || '获取医生详情失败')
  } finally {
    loading.value = false
  }
}

// 获取最近排班
const getRecentSchedules = async (doctorId) => {
  try {
    const today = new Date()
    const response = await getDoctorSchedules(doctorId, {
      start_date: today.toISOString().split('T')[0]
    })
    
    if (response.success) {
      recentSchedules.value = response.data.schedules.slice(0, 5)
    }
  } catch (error) {
    console.error('获取排班数据失败:', error)
  }
}

// 获取最近绩效
const getRecentPerformances = async (doctorId) => {
  try {
    const response = await getDoctorPerformances(doctorId)
    
    if (response.success) {
      recentPerformances.value = response.data.performances.slice(0, 5)
    }
  } catch (error) {
    console.error('获取绩效数据失败:', error)
  }
}

// 返回列表
const goBack = () => {
  router.push('/doctor')
}

// 编辑医生信息
const handleEdit = () => {
  router.push(`/doctor?edit=${doctor.value.id}`)
}

// 查看排班
const handleViewSchedule = () => {
  router.push({
    path: '/doctor/schedule',
    query: { doctor_id: doctor.value.id }
  })
}

// 查看绩效
const handleViewPerformance = () => {
  router.push({
    path: '/doctor/performance',
    query: { doctor_id: doctor.value.id }
  })
}

// 添加排班
const handleAddSchedule = () => {
  router.push({
    path: '/doctor/schedule',
    query: { doctor_id: doctor.value.id, action: 'add' }
  })
}

// 添加绩效
const handleAddPerformance = () => {
  router.push({
    path: '/doctor/performance',
    query: { doctor_id: doctor.value.id, action: 'add' }
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

// 获取评分类型
const getScoreType = (score) => {
  if (!score) return 'info'
  if (score >= 4.5) return 'success'
  if (score >= 3.5) return 'warning'
  return 'danger'
}

// 初始化
onMounted(() => {
  getDoctorInfo()
})
</script>

<style scoped>
.doctor-detail-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
}

.stat-icon {
  margin-right: 15px;
}

.stat-content {
  flex: 1;
}

.stat-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.bonus-text {
  color: #67c23a;
  font-weight: bold;
}

.mb-4 {
  margin-bottom: 20px;
}
</style>

