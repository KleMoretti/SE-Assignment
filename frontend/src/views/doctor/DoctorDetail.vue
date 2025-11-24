<template>
  <div class="doctor-detail-container">
    <!-- 加载状态 -->
    <div v-loading="loading" element-loading-text="加载中..." class="loading-wrapper">
      <!-- 返回按钮 -->
      <el-page-header @back="goBack" class="page-header-nav">
        <template #content>
          <span class="page-title">医生详情</span>
        </template>
      </el-page-header>

      <!-- 医生头部信息卡片 -->
      <el-card v-if="doctor" class="doctor-header-card" shadow="never">
        <div class="doctor-header">
          <div class="header-left">
            <el-avatar :size="100" class="doctor-avatar-large">
              {{ doctor.name?.charAt(0) }}
            </el-avatar>

            <div class="header-info">
              <h1 class="doctor-name-large">{{ doctor.name }}</h1>
              <div class="doctor-meta-info">
                <el-tag type="info" size="large">{{ doctor.title }}</el-tag>
                <span class="meta-divider">|</span>
                <span class="department-text">
                  <el-icon><OfficeBuilding /></el-icon>
                  {{ doctor.department }}
                </span>
              </div>
              <div class="doctor-contact">
                <span class="contact-item">
                  <el-icon><User /></el-icon>
                  工号: {{ doctor.doctorNo }}
                </span>
                <span class="contact-item">
                  <el-icon><Phone /></el-icon>
                  {{ doctor.phone }}
                </span>
                <span class="contact-item">
                  <el-icon><Message /></el-icon>
                  {{ doctor.email }}
                </span>
              </div>
              <div class="status-container">
                <el-tag :type="doctor.status === 'active' ? 'success' : 'info'">
                  {{ doctor.status === 'active' ? '在职' : '离职' }}
                </el-tag>
              </div>
            </div>
          </div>

          <div class="header-actions">
            <el-button type="primary" @click="goBack" style="width: 100%;">
              返回列表
            </el-button>
          </div>
        </div>
      </el-card>

      <!-- 详细信息 -->
      <el-card class="detail-card" shadow="never">
            <div class="info-section">
              <h3 class="section-title">联系方式</h3>
              <el-descriptions :column="2" border>
                <el-descriptions-item label="联系电话">
                  <el-icon><Phone /></el-icon>
                  {{ doctor?.phone || '未设置' }}
                </el-descriptions-item>
                <el-descriptions-item label="电子邮箱">
                  <el-icon><Message /></el-icon>
                  {{ doctor?.email || '未设置' }}
                </el-descriptions-item>
              </el-descriptions>
            </div>

            <div class="info-section">
              <h3 class="section-title">专业信息</h3>
              <el-descriptions :column="2" border>
                <el-descriptions-item label="职称">{{ doctor?.title }}</el-descriptions-item>
                <el-descriptions-item label="所属科室">{{ doctor?.department }}</el-descriptions-item>
                <el-descriptions-item label="学历">{{ doctor?.education || '未设置' }}</el-descriptions-item>
              </el-descriptions>
            </div>

            <div class="info-section">
              <h3 class="section-title">专长领域</h3>
              <div v-if="doctor?.specialties && doctor.specialties.length" class="specialties-list">
                <el-tag
                  v-for="(specialty, index) in doctor.specialties"
                  :key="index"
                  size="large"
                  effect="plain"
                  class="specialty-tag"
                >
                  {{ specialty }}
                </el-tag>
              </div>
              <el-empty v-else description="暂无专长信息" :image-size="80" />
            </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  User, Phone, Message, OfficeBuilding
} from '@element-plus/icons-vue'
import { getDoctorDetail } from '@/api/doctor'

// 路由
const router = useRouter()
const route = useRoute()

// 响应式数据
const loading = ref(false)
const doctor = ref(null)

// 方法
const fetchDoctorDetail = async () => {
  loading.value = true
  try {
    const id = route.params.id
    const res = await getDoctorDetail(id)
    doctor.value = res.data
  } catch (error) {
    ElMessage.error('获取医生详情失败')
    goBack()
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/doctor')
}

// 生命周期
onMounted(() => {
  fetchDoctorDetail()
})
</script>

<style scoped>
.doctor-detail-container {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.loading-wrapper {
  min-height: 400px;
}

.page-header-nav {
  margin-bottom: 24px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.doctor-header-card {
  margin-bottom: 16px;
}

.doctor-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-left {
  display: flex;
  gap: 24px;
  flex: 1;
}

.doctor-avatar-large {
  flex-shrink: 0;
  border: 4px solid #f0f2f5;
}

.header-info {
  flex: 1;
}

.doctor-name-large {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 12px 0;
}

.doctor-meta-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.meta-divider {
  color: #dcdfe6;
}

.department-text {
  font-size: 16px;
  color: #606266;
  display: flex;
  align-items: center;
  gap: 4px;
}

.doctor-contact {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  margin-bottom: 12px;
}

.contact-item {
  font-size: 14px;
  color: #606266;
  display: flex;
  align-items: center;
  gap: 4px;
}

.header-actions {
  display: flex;
  gap: 12px;
  flex-direction: column;
}

.stats-section {
  margin-bottom: 16px;
}

.stat-card {
  height: 100%;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin: 0 0 8px 0;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.detail-card {
  margin-bottom: 24px;
}

.info-section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 16px 0;
  padding-bottom: 12px;
  border-bottom: 2px solid #409eff;
}

.specialties-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.specialty-tag {
  font-size: 14px;
}

.bio-text {
  font-size: 14px;
  color: #606266;
  line-height: 1.8;
  margin: 0;
}
</style>

