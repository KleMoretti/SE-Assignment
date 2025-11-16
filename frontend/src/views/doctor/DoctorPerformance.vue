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
          </div>
        </template>
        <template #extra>
          <el-select v-model="timeRange" @change="loadPerformanceData" style="width: 120px;">
            <el-option label="本周" value="week" />
            <el-option label="本月" value="month" />
            <el-option label="本季度" value="quarter" />
            <el-option label="本年度" value="year" />
          </el-select>
        </template>
      </el-page-header>
    </div>

    <!-- 关键指标卡片 -->
    <el-row :gutter="16" class="kpi-section" v-loading="loading">
      <el-col :span="6">
        <el-card shadow="hover" class="kpi-card kpi-card-blue">
          <div class="kpi-content">
            <div class="kpi-icon">
              <el-icon :size="40"><User /></el-icon>
            </div>
            <div class="kpi-info">
              <p class="kpi-label">接诊患者数</p>
              <p class="kpi-value">{{ performance.totalPatients || 0 }}</p>
              <p class="kpi-change" :class="getChangeClass(performance.patientsChange)">
                <el-icon v-if="performance.patientsChange >= 0"><CaretTop /></el-icon>
                <el-icon v-else><CaretBottom /></el-icon>
                {{ Math.abs(performance.patientsChange || 0) }}% 较上期
              </p>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="kpi-card kpi-card-purple">
          <div class="kpi-content">
            <div class="kpi-icon">
              <el-icon :size="40"><Promotion /></el-icon>
            </div>
            <div class="kpi-info">
              <p class="kpi-label">手术台数</p>
              <p class="kpi-value">{{ performance.totalSurgeries || 0 }}</p>
              <p class="kpi-change" :class="getChangeClass(performance.surgeriesChange)">
                <el-icon v-if="performance.surgeriesChange >= 0"><CaretTop /></el-icon>
                <el-icon v-else><CaretBottom /></el-icon>
                {{ Math.abs(performance.surgeriesChange || 0) }}% 较上期
              </p>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="kpi-card kpi-card-cyan">
          <div class="kpi-content">
            <div class="kpi-icon">
              <el-icon :size="40"><Star /></el-icon>
            </div>
            <div class="kpi-info">
              <p class="kpi-label">患者满意度</p>
              <p class="kpi-value">{{ performance.satisfactionRate || 0 }}%</p>
              <p class="kpi-change" :class="getChangeClass(performance.satisfactionChange)">
                <el-icon v-if="performance.satisfactionChange >= 0"><CaretTop /></el-icon>
                <el-icon v-else><CaretBottom /></el-icon>
                {{ Math.abs(performance.satisfactionChange || 0) }}% 较上期
              </p>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="kpi-card kpi-card-green">
          <div class="kpi-content">
            <div class="kpi-icon">
              <el-icon :size="40"><Money /></el-icon>
            </div>
            <div class="kpi-info">
              <p class="kpi-label">总收入（元）</p>
              <p class="kpi-value">{{ formatCurrency(performance.totalRevenue || 0) }}</p>
              <p class="kpi-change" :class="getChangeClass(performance.revenueChange)">
                <el-icon v-if="performance.revenueChange >= 0"><CaretTop /></el-icon>
                <el-icon v-else><CaretBottom /></el-icon>
                {{ Math.abs(performance.revenueChange || 0) }}% 较上期
              </p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="16" class="charts-section">
      <!-- 接诊趋势图 -->
      <el-col :span="16">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="chart-header">
              <h3 class="chart-title">接诊趋势分析</h3>
              <el-tag type="info" size="small">单位: 人次</el-tag>
            </div>
          </template>
          <div class="chart-body">
            <div class="trend-chart">
              <div class="chart-placeholder" style="height: 300px; display: flex; align-items: center; justify-content: center;">
                <el-empty description="图表数据加载中..." :image-size="100">
                  <template #image>
                    <el-icon :size="60" color="#909399"><TrendCharts /></el-icon>
                  </template>
                </el-empty>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 诊疗类型分布 -->
      <el-col :span="8">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="chart-header">
              <h3 class="chart-title">诊疗类型分布</h3>
            </div>
          </template>
          <div class="chart-body">
            <div class="type-distribution">
              <div
                v-for="item in diagnosisTypes"
                :key="item.name"
                class="type-item"
              >
                <div class="type-info">
                  <span class="type-color" :style="{ backgroundColor: item.color }"></span>
                  <span class="type-name">{{ item.name }}</span>
                </div>
                <div class="type-value">
                  <span class="type-count">{{ item.count }}</span>
                  <el-tag size="small" type="info">{{ item.percentage }}%</el-tag>
                </div>
                <el-progress
                  :percentage="item.percentage"
                  :color="item.color"
                  :show-text="false"
                />
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 工作时长统计 -->
    <el-row :gutter="16" class="work-hours-section">
      <el-col :span="24">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="chart-header">
              <h3 class="chart-title">工作时长统计</h3>
              <el-tag type="info" size="small">单位: 小时</el-tag>
            </div>
          </template>
          <div class="chart-body">
            <div class="work-hours-grid">
              <div class="work-hour-card">
                <div class="hour-icon" style="background: #ecf5ff; color: #409eff;">
                  <el-icon :size="32"><Timer /></el-icon>
                </div>
                <div class="hour-info">
                  <p class="hour-label">门诊时长</p>
                  <p class="hour-value">{{ performance.clinicHours || 0 }}<span class="hour-unit">小时</span></p>
                  <el-progress
                    :percentage="getPercentage(performance.clinicHours, performance.totalHours)"
                    color="#409eff"
                  />
                </div>
              </div>

              <div class="work-hour-card">
                <div class="hour-icon" style="background: #f4f4f5; color: #909399;">
                  <el-icon :size="32"><Operation /></el-icon>
                </div>
                <div class="hour-info">
                  <p class="hour-label">手术时长</p>
                  <p class="hour-value">{{ performance.surgeryHours || 0 }}<span class="hour-unit">小时</span></p>
                  <el-progress
                    :percentage="getPercentage(performance.surgeryHours, performance.totalHours)"
                    color="#909399"
                  />
                </div>
              </div>

              <div class="work-hour-card">
                <div class="hour-icon" style="background: #f0f9ff; color: #67c23a;">
                  <el-icon :size="32"><ChatDotRound /></el-icon>
                </div>
                <div class="hour-info">
                  <p class="hour-label">会诊时长</p>
                  <p class="hour-value">{{ performance.consultationHours || 0 }}<span class="hour-unit">小时</span></p>
                  <el-progress
                    :percentage="getPercentage(performance.consultationHours, performance.totalHours)"
                    color="#67c23a"
                  />
                </div>
              </div>

              <div class="work-hour-card total">
                <div class="hour-icon" style="background: #fef0e6; color: #e6a23c;">
                  <el-icon :size="32"><Odometer /></el-icon>
                </div>
                <div class="hour-info">
                  <p class="hour-label">总工作时长</p>
                  <p class="hour-value total-value">{{ performance.totalHours || 0 }}<span class="hour-unit">小时</span></p>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 详细数据表格 -->
    <el-card shadow="never" class="data-table-card">
      <template #header>
        <div class="table-header">
          <h3 class="section-title">详细绩效数据</h3>
          <el-button type="primary" plain :icon="Download">导出报表</el-button>
        </div>
      </template>
      <el-table :data="performanceDetails" border stripe>
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="patients" label="接诊人数" width="120" align="center" />
        <el-table-column prop="surgeries" label="手术数量" width="120" align="center" />
        <el-table-column prop="prescriptions" label="处方数量" width="120" align="center" />
        <el-table-column prop="satisfaction" label="满意度" width="120" align="center">
          <template #default="{ row }">
            <el-rate v-model="row.satisfaction" disabled show-score text-color="#ff9900" />
          </template>
        </el-table-column>
        <el-table-column prop="revenue" label="收入（元）" align="right">
          <template #default="{ row }">
            <span class="revenue-text">¥{{ formatCurrency(row.revenue) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="备注" prop="notes" show-overflow-tooltip />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  TrendCharts, User, Star, Money, CaretTop, CaretBottom, Timer,
  Promotion, Operation, ChatDotRound, Odometer, Download
} from '@element-plus/icons-vue'
import { getDoctorDetail, getDoctorPerformance } from '@/api/doctor'

// 路由
const router = useRouter()
const route = useRoute()

// 响应式数据
const loading = ref(false)
const doctorInfo = ref(null)
const timeRange = ref('month')

const performance = reactive({
  totalPatients: 0,
  patientsChange: 0,
  totalSurgeries: 0,
  surgeriesChange: 0,
  satisfactionRate: 0,
  satisfactionChange: 0,
  totalRevenue: 0,
  revenueChange: 0,
  clinicHours: 0,
  surgeryHours: 0,
  consultationHours: 0,
  totalHours: 0
})

const diagnosisTypes = ref([
  { name: '门诊', count: 120, percentage: 60, color: '#409eff' },
  { name: '急诊', count: 30, percentage: 15, color: '#f56c6c' },
  { name: '手术', count: 25, percentage: 12.5, color: '#e6a23c' },
  { name: '会诊', count: 25, percentage: 12.5, color: '#67c23a' }
])

const performanceDetails = ref([])

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

const loadPerformanceData = async () => {
  loading.value = true
  try {
    const id = route.params.id || doctorInfo.value?.id
    if (!id) return

    const params = { timeRange: timeRange.value }
    const res = await getDoctorPerformance(id, params)

    Object.assign(performance, res.data)
    performanceDetails.value = res.data.details || []
  } catch (error) {
    ElMessage.error('获取绩效数据失败')
  } finally {
    loading.value = false
  }
}

const formatCurrency = (value) => {
  if (!value) return '0'
  return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

const getPercentage = (value, total) => {
  if (!total || total === 0) return 0
  return Math.round((value / total) * 100)
}

const getChangeClass = (change) => {
  return change >= 0 ? 'positive' : 'negative'
}

const goBack = () => {
  router.back()
}

// 生命周期
onMounted(() => {
  fetchDoctorInfo()
  loadPerformanceData()
})
</script>

<style scoped>
.doctor-performance-container {
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

.kpi-section {
  margin-bottom: 16px;
}

.kpi-card {
  height: 100%;
  border-radius: 12px;
  overflow: hidden;
}

.kpi-card-blue { border-left: 4px solid #409eff; }
.kpi-card-purple { border-left: 4px solid #9c27b0; }
.kpi-card-cyan { border-left: 4px solid #00bcd4; }
.kpi-card-green { border-left: 4px solid #67c23a; }

.kpi-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.kpi-icon {
  width: 80px;
  height: 80px;
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
  font-size: 32px;
  font-weight: 700;
  color: #303133;
  margin: 0 0 8px 0;
}

.kpi-change {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  margin: 0;
}

.kpi-change.positive {
  color: #67c23a;
}

.kpi-change.negative {
  color: #f56c6c;
}

.charts-section {
  margin-bottom: 16px;
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
  padding: 16px 0;
}

.type-distribution {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.type-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
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

.work-hours-section {
  margin-bottom: 16px;
}

.work-hours-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.work-hour-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 24px;
  background-color: #fafafa;
  border-radius: 12px;
  transition: all 0.3s;
}

.work-hour-card:hover {
  background-color: #f0f2f5;
  transform: translateY(-4px);
}

.work-hour-card.total {
  background: linear-gradient(135deg, #fef0e6 0%, #fff7e6 100%);
}

.hour-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hour-info {
  width: 100%;
  text-align: center;
}

.hour-label {
  font-size: 14px;
  color: #909399;
  margin: 0 0 8px 0;
}

.hour-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  margin: 0 0 12px 0;
}

.hour-value.total-value {
  font-size: 36px;
  color: #e6a23c;
}

.hour-unit {
  font-size: 14px;
  font-weight: 400;
  margin-left: 4px;
}

.data-table-card {
  margin-bottom: 24px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
</style>

