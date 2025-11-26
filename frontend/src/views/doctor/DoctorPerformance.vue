<template>
  <div class="doctor-performance-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <el-page-header @back="goBack">
        <template #content>
          <div class="header-content">
            <h1 class="page-title">
              <el-icon class="title-icon"><TrendCharts /></el-icon>
              医生绩效分析
            </h1>
            <p v-if="doctorInfo" class="doctor-info-text">
              {{ doctorInfo.name }} - {{ doctorInfo.title }} - {{ doctorInfo.department }}
            </p>
            <p v-else class="doctor-info-text">
              所有医生绩效一览
            </p>
          </div>
        </template>
        <template #extra>
          <el-space>
            <el-select v-model="timeRange" @change="loadPerformanceData" style="width: 120px;">
              <el-option label="本月" value="month" />
              <el-option label="本年度" value="year" />
            </el-select>
            <el-button @click="exportPerformanceReport" :icon="Download">
              导出报表
            </el-button>
          </el-space>
        </template>
      </el-page-header>
    </div>

    <!-- 关键指标卡片 -->
    <el-row :gutter="16" class="kpi-section" v-loading="loading">
      <el-col :span="8">
        <el-card shadow="hover" class="kpi-card kpi-card-blue">
          <div class="kpi-content">
            <div class="kpi-icon">
              <el-icon :size="40"><User /></el-icon>
            </div>
            <div class="kpi-info">
              <p class="kpi-label">接诊患者数</p>
              <p class="kpi-value">{{ computedKPI.totalPatients }}</p>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="hover" class="kpi-card kpi-card-cyan">
          <div class="kpi-content">
            <div class="kpi-icon">
              <el-icon :size="40"><Star /></el-icon>
            </div>
            <div class="kpi-info">
              <p class="kpi-label">患者满意度</p>
              <p class="kpi-value">{{ computedKPI.satisfactionRate }}%</p>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="hover" class="kpi-card kpi-card-green">
          <div class="kpi-content">
            <div class="kpi-icon">
              <el-icon :size="40"><Money /></el-icon>
            </div>
            <div class="kpi-info">
              <p class="kpi-label">总收入（元）</p>
              <p class="kpi-value">{{ formatCurrency(computedKPI.totalRevenue) }}</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 趋势图表和详细数据 -->
    <el-row :gutter="16" class="data-section">
      <!-- 左侧：接诊趋势分析 -->
      <el-col :span="14">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="chart-header">
              <h3 class="chart-title">接诊趋势分析</h3>
              <el-tag type="info" size="small">单位: 人次</el-tag>
            </div>
          </template>
          <div class="chart-body">
            <div v-if="chartPoints.length" class="trend-chart-wrapper">
              <div class="chart-grid">
                <div class="y-axis">
                  <span v-for="tick in yAxisTicks" :key="tick">{{ tick }}</span>
                </div>
                <div class="chart-content">
                  <svg viewBox="0 0 700 250" class="trend-svg">
                    <!-- 网格线 -->
                    <line x1="0" y1="20" x2="700" y2="20" stroke="#e4e7ed" stroke-width="1" />
                    <line x1="0" y1="70" x2="700" y2="70" stroke="#e4e7ed" stroke-width="1" />
                    <line x1="0" y1="120" x2="700" y2="120" stroke="#e4e7ed" stroke-width="1" />
                    <line x1="0" y1="170" x2="700" y2="170" stroke="#e4e7ed" stroke-width="1" />
                    <line x1="0" y1="220" x2="700" y2="220" stroke="#e4e7ed" stroke-width="1" />
                    <!-- 折线 -->
                    <polyline
                      :points="chartPolylinePoints"
                      fill="none"
                      stroke="#409eff"
                      stroke-width="3"
                      class="data-line"
                    />
                    <!-- 数据点 -->
                    <circle
                      v-for="(pt, index) in chartSvgPoints"
                      :key="index"
                      :cx="pt.x"
                      :cy="pt.y"
                      r="5"
                      fill="#409eff"
                      class="data-point"
                    />
                  </svg>
                  <div class="x-axis">
                    <span v-for="item in chartPoints" :key="item.label">
                      {{ item.label }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
            <el-empty v-else description="暂无绩效数据" :image-size="80" />
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：详细数据表格 -->
      <el-col :span="10">
        <el-card shadow="never" class="data-table-card">
          <template #header>
            <div class="table-header">
              <h3 class="section-title">{{ timeRange === 'year' ? '年度绩效数据' : '详细绩效数据' }}</h3>
              <el-button type="primary" plain :icon="Download" size="small" @click="exportTableData">导出</el-button>
            </div>
          </template>
          <el-table :data="displayDetails" stripe style="width: 100%;" :row-style="{ height: '48px' }" :cell-style="{ padding: '12px 8px' }">
            <el-table-column prop="date" :label="timeRange === 'year' ? '月份' : '日期'" width="80" align="center">
              <template #default="{ row }">
                <span>{{ formatDateLabel(row.date) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="patients" label="接诊" width="80" align="center" />
            <el-table-column prop="satisfaction" label="满意度" min-width="120" align="center">
              <template #default="{ row }">
                <el-rate v-model="row.satisfaction" disabled text-color="#ff9900" size="small" />
              </template>
            </el-table-column>
            <el-table-column prop="revenue" label="收入" width="90" align="center">
              <template #default="{ row }">
                <span class="revenue-text">¥{{ (row.revenue / 1000).toFixed(1) }}k</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  TrendCharts, User, Star, Money, Download, Search
} from '@element-plus/icons-vue'
import { getDoctorDetail, getDoctorPerformance } from '@/api/doctor'

// 路由
const router = useRouter()
const route = useRoute()

// 响应式数据
const loading = ref(false)
const doctorInfo = ref(null)
const timeRange = ref('year')  // 默认显示年度视图
const tableSearch = ref('')

const performance = reactive({
  totalPatients: 0,
  satisfactionRate: 0,
  totalRevenue: 0
})

const performanceDetails = ref([])

// 折线图数据：基于数据库真实数据生成
const chartPoints = computed(() => {
  const items = performanceDetails.value || []
  
  if (timeRange.value === 'year') {
    // 年度视图：生成完整的12个月数据
    const monthlyData = Array.from({ length: 12 }, (_, i) => {
      const monthNum = String(i + 1).padStart(2, '0')
      return { label: monthNum, value: 0 }
    })
    
    // 用真实数据填充
    items.forEach((item) => {
      const monthStr = item.date.slice(-2)  // 取月份部分 '01', '02'...
      const monthIndex = parseInt(monthStr, 10) - 1
      if (monthIndex >= 0 && monthIndex < 12) {
        monthlyData[monthIndex] = {
          label: monthStr,
          value: item.patients || 0
        }
      }
    })
    
    return monthlyData
  }
  
  // 月度视图：使用当月数据（如果有），否则返回空数组
  return items.map((item) => ({
    label: item.date.slice(-2), // 月份或日期
    value: item.patients || 0
  }))
})

const chartSvgPoints = computed(() => {
  const points = chartPoints.value
  if (!points.length) return []

  const maxValue = Math.max(...points.map((p) => p.value || 0)) || 1
  const viewWidth = 700
  const viewHeight = 250
  const left = 40
  const right = 40
  const top = 20
  const bottom = 30
  const innerWidth = viewWidth - left - right
  const innerHeight = viewHeight - top - bottom

  return points.map((p, index) => {
    const count = points.length
    const x = count === 1
      ? left + innerWidth / 2
      : left + (innerWidth * index) / (count - 1)
    const ratio = (p.value || 0) / maxValue
    const y = top + (1 - ratio) * innerHeight
    return { ...p, x, y }
  })
})

const chartPolylinePoints = computed(() =>
  chartSvgPoints.value.map((p) => `${Math.round(p.x)},${Math.round(p.y)}`).join(' ')
)

// Y轴刻度
const yAxisTicks = computed(() => {
  const points = chartPoints.value
  if (!points.length) return []
  const maxValue = Math.max(...points.map((p) => p.value || 0)) || 100
  const step = Math.ceil(maxValue / 4)
  return [maxValue, step * 3, step * 2, step, 0]
})

// KPI统计：优先使用API返回的统计数据，无数据时作为备用
const computedKPI = computed(() => {
  // 如果API有返回统计数据，优先使用
  if (performance.totalPatients > 0 || performance.satisfactionRate > 0 || performance.totalRevenue > 0) {
    return {
      totalPatients: performance.totalPatients,
      satisfactionRate: Math.round(performance.satisfactionRate),
      totalRevenue: performance.totalRevenue
    }
  }
  
  // 否则根据详细数据计算（作为备用）
  const details = displayDetails.value
  if (!details || details.length === 0) {
    return {
      totalPatients: 0,
      satisfactionRate: 0,
      totalRevenue: 0
    }
  }

  const totalPatients = details.reduce((sum, item) => sum + (item.patients || 0), 0)
  const totalRevenue = details.reduce((sum, item) => sum + (item.revenue || 0), 0)
  const avgSatisfaction = details.reduce((sum, item) => sum + (item.satisfaction || 0), 0) / details.length
  
  return {
    totalPatients,
    satisfactionRate: Math.round(avgSatisfaction * 20), // 5分制转100分制
    totalRevenue
  }
})

// 表格显示数据：直接使用数据库数据
const displayDetails = computed(() => {
  return performanceDetails.value || []
})

// 方法
const fetchDoctorInfo = async () => {
  try {
    const id = route.params.id
    if (id) {
      const res = await getDoctorDetail(id)
      doctorInfo.value = res.data
    } else {
      // 没有特定医生ID，显示所有医生绩效
      doctorInfo.value = null
    }
  } catch (error) {
    console.error('获取医生信息失败', error)
  }
}

const loadPerformanceData = async () => {
  loading.value = true
  try {
    const id = route.params.id || doctorInfo.value?.id
    if (!id) {
      // 没有特定医生ID时，清空数据
      performanceDetails.value = []
      performance.totalPatients = 0
      performance.satisfactionRate = 0
      performance.totalRevenue = 0
      loading.value = false
      return
    }

    const now = new Date()
    const year = now.getFullYear()
    const month = now.getMonth() + 1

    const params = { year }
    if (timeRange.value === 'month') {
      params.month = month
    }

    const res = await getDoctorPerformance(id, params)

    const stats = res.data.statistics || {}
    const items = res.data.items || res.data.performances || []

    // 使用API返回的统计数据
    performance.totalPatients = stats.totalPatients || 0
    performance.satisfactionRate = stats.averageSatisfaction || 0
    performance.totalRevenue = stats.totalBonus || 0

    performanceDetails.value = items.map((item) => {
      const month = String(item.month || 1).padStart(2, '0')
      // 满意度评分：将0-100分转换为0-5星 (除以20)
      const satisfactionScore = item.satisfactionScore || item.satisfaction_score || 0
      const satisfaction = Math.max(0, Math.min(5, satisfactionScore / 20))
      return {
        date: `${item.year}-${month}`,
        patients: item.patientCount || item.patient_count || 0,
        satisfaction,
        revenue: item.bonus || 0,
        notes: item.notes || ''
      }
    })
  } catch (error) {
    ElMessage.error('获取绩效数据失败')
    performanceDetails.value = []
    performance.totalPatients = 0
    performance.satisfactionRate = 0
    performance.totalRevenue = 0
  } finally {
    loading.value = false
  }
}

const formatCurrency = (value) => {
  if (!value) return '0'
  return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

const formatDateLabel = (dateStr) => {
  if (timeRange.value === 'year') {
    // 年度视图：显示 '1月', '2月', ..., '12月'
    const monthNum = parseInt(dateStr.slice(-2), 10)  // 取最后两位并转为数字
    return `${monthNum}月`
  }
  // 月度视图：显示原始标签
  return dateStr
}

const goBack = () => {
  router.push('/doctor')
}

const exportPerformanceReport = () => {
  ElMessage.success('正在生成报表...')
  // 导出逻辑
}

const exportTableData = () => {
  const csv = convertPerformanceToCSV(performanceDetails.value)
  downloadCSV(csv, `performance_${timeRange.value}.csv`)
  ElMessage.success('导出成功')
}

const convertPerformanceToCSV = (data) => {
  if (!data || data.length === 0) return ''
  
  const headers = ['日期', '接诊人数', '满意度', '收入']
  const rows = data.map(d => [
    d.date,
    d.patients,
    d.satisfaction,
    d.revenue
  ])
  
  return [headers, ...rows].map(row => row.join(',')).join('\n')
}

const downloadCSV = (csv, filename) => {
  const blob = new Blob([`\uFEFF${csv}`], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = filename
  link.click()
  URL.revokeObjectURL(link.href)
}

// 生命周期
onMounted(() => {
  fetchDoctorInfo()
  loadPerformanceData()
})
</script>

<style scoped>
.doctor-performance-container {
  padding: 16px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 32px);
}

.page-header {
  margin-bottom: 16px;
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

.kpi-section {
  margin-bottom: 12px;
}

.kpi-card {
  height: 100%;
  border-radius: 8px;
  overflow: hidden;
}

.kpi-card-blue { border-left: 4px solid #409eff; }
.kpi-card-purple { border-left: 4px solid #9c27b0; }
.kpi-card-cyan { border-left: 4px solid #00bcd4; }
.kpi-card-green { border-left: 4px solid #67c23a; }

.kpi-content {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
}

.kpi-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.kpi-card-blue .kpi-icon { background: #ecf5ff; color: #409eff; }
.kpi-card-purple .kpi-icon { background: #f3e5f5; color: #9c27b0; }
.kpi-card-cyan .kpi-icon { background: #e0f7fa; color: #00bcd4; }
.kpi-card-green .kpi-icon { background: #f0f9ff; color: #67c23a; }

.kpi-info {
  flex: 1;
}

.kpi-label {
  font-size: 14px;
  color: #909399;
  margin: 0 0 8px 0;
}

.kpi-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  margin: 0;
}

.data-section {
  margin-bottom: 0;
}

.chart-card {
  height: 100%;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.chart-body {
  padding: 8px 0 0 0;
  overflow: visible;
}

.type-distribution {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 8px;
}

.type-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.type-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.type-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.type-name {
  font-size: 14px;
  color: #606266;
  flex: 1;
}

.type-value {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.type-count {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.data-table-card {
  height: 100%;
}

.data-table-card :deep(.el-card__body) {
  padding: 16px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.revenue-text {
  font-weight: 600;
  color: #67c23a;
}

/* 趋势图样式 */
.trend-chart-wrapper {
  padding: 12px;
}

.chart-grid {
  display: flex;
  gap: 12px;
  align-items: stretch;
}

.y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-width: 40px;
  padding-right: 8px;
  height: 270px;
}

.y-axis span {
  font-size: 12px;
  color: #909399;
  text-align: right;
  line-height: 1;
  transform: translateY(-6px);
}

.chart-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.trend-svg {
  width: 100%;
  height: 250px;
  margin-bottom: 12px;
  overflow: visible;
}

.x-axis {
  display: flex;
  justify-content: space-around;
  padding: 0 30px;
}

.x-axis span {
  font-size: 12px;
  color: #606266;
  font-weight: 500;
}

.data-line {
  stroke-dasharray: 2000;
  stroke-dashoffset: 2000;
  animation: drawLine 2s ease-out forwards;
}

.data-point {
  opacity: 0;
  animation: fadeIn 0.4s ease-out forwards;
  animation-delay: 2s;
}

.data-label {
  opacity: 0;
  animation: fadeIn 0.4s ease-out forwards;
  animation-delay: 2.2s;
}

@keyframes drawLine {
  to {
    stroke-dashoffset: 0;
  }
}

@keyframes fadeIn {
  to {
    opacity: 1;
  }
}

/* 排名样式 */
</style>
