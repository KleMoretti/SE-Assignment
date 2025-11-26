<template>
  <div class="patient-management-container">
    <!-- 首页：显示欢迎和功能卡片 -->
    <div v-if="isIndexPage" class="index-page">
      <!-- 返回按钮 -->
      <div class="back-button-container">
        <el-button 
          :icon="ArrowLeft" 
          @click="goBack" 
          circle 
          class="index-back-button"
        />
      </div>
      
      <!-- 欢迎标题 -->
      <div class="welcome-section">
        <h1 class="welcome-title">
          <el-icon class="title-icon"><House /></el-icon>
          病人管理系统
        </h1>
        <p class="welcome-subtitle">统一管理病人信息、预约和病历</p>
      </div>

      <!-- 功能卡片网格 -->
      <div class="service-grid">
        <div class="service-card" @click="navigateTo('PatientList')">
          <div class="card-icon patient-icon">
            <el-icon><User /></el-icon>
          </div>
          <h3 class="card-title">病人信息</h3>
          <p class="card-description">查看和管理病人档案信息</p>
          <div class="card-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>

        <div class="service-card" @click="navigateTo('AppointmentList')">
          <div class="card-icon appointment-icon">
            <el-icon><Calendar /></el-icon>
          </div>
          <h3 class="card-title">挂号预约</h3>
          <p class="card-description">管理病人的预约挂号信息</p>
          <div class="card-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>

        <div class="service-card" @click="navigateTo('MedicalRecordList')">
          <div class="card-icon record-icon">
            <el-icon><Document /></el-icon>
          </div>
          <h3 class="card-title">病历记录</h3>
          <p class="card-description">查看和管理病人病历档案</p>
          <div class="card-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
      </div>
    </div>

    <!-- 子页面：显示卡片布局 -->
    <el-card v-else class="main-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-button 
              :icon="ArrowLeft" 
              @click="goBack" 
              circle 
              class="back-button"
            />
            <span class="page-title">{{ pageTitle }}</span>
          </div>
          <div class="header-right">
            <el-button-group class="nav-buttons">
              <el-button 
                :type="isRouteActive('PatientList') ? 'primary' : 'default'" 
                @click="navigateTo('PatientList')"
                class="nav-btn"
              >
                <el-icon><User /></el-icon>
                病人信息
              </el-button>
              <el-button 
                :type="isRouteActive('AppointmentList') ? 'primary' : 'default'" 
                @click="navigateTo('AppointmentList')"
                class="nav-btn"
              >
                <el-icon><Calendar /></el-icon>
                挂号预约
              </el-button>
              <el-button 
                :type="isRouteActive('MedicalRecordList') ? 'primary' : 'default'" 
                @click="navigateTo('MedicalRecordList')"
                class="nav-btn"
              >
                <el-icon><Document /></el-icon>
                病历记录
              </el-button>
            </el-button-group>
          </div>
        </div>
      </template>
      <div class="content-wrapper">
        <router-view :key="route.fullPath"></router-view>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeft, User, Calendar, Document, House, ArrowRight } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

// 判断是否在首页（没有子路由时显示首页）
const isIndexPage = computed(() => {
  // 如果当前路由是 PatientList、AppointmentList 或 MedicalRecordList，显示子页面
  const childRoutes = ['PatientList', 'AppointmentList', 'MedicalRecordList']
  return !childRoutes.includes(route.name)
})

// 页面标题
const pageTitle = computed(() => {
  const titleMap = {
    'PatientList': '病人信息',
    'AppointmentList': '挂号预约',
    'MedicalRecordList': '病历记录'
  }
  return titleMap[route.name] || '病人管理'
})

const goBack = () => {
  // 如果在子页面，返回病人管理首页
  if (!isIndexPage.value) {
    router.push({ path: '/patient' })
  } else {
    // 如果在首页，返回主页
    router.push({ name: 'Home' })
  }
}

const navigateTo = (routeName) => {
  router.push({ name: routeName })
}

const isRouteActive = (routeName) => {
  return route.name === routeName
}
</script>

<style scoped>
.patient-management-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20px;
  padding-bottom: 40px;
  box-sizing: border-box;
}

/* 首页样式 */
.index-page {
  animation: fadeIn 0.5s ease-out;
}

/* 返回按钮容器 */
.back-button-container {
  padding: 20px 0 0 20px;
  animation: fadeIn 0.5s ease-out;
}

.index-back-button {
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.index-back-button:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

/* 欢迎区域 */
.welcome-section {
  text-align: center;
  margin-bottom: 50px;
  padding-top: 20px;
  animation: fadeInDown 0.6s ease-out;
}

.welcome-title {
  color: #2c3e50;
  font-size: 36px;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.title-icon {
  font-size: 36px;
  color: #409eff;
}

.welcome-subtitle {
  color: #606266;
  font-size: 16px;
  margin-top: 10px;
  font-weight: 400;
}

/* 服务卡片网格 */
.service-grid {
  display: flex;
  justify-content: center;
  align-items: stretch;
  gap: 20px;
  max-width: 1200px;
  margin: 0 auto;
  flex-wrap: wrap;
}

.service-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 35px 25px;
  width: 280px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e4e7ed;
  position: relative;
  animation: fadeInUp 0.6s ease-out backwards;
}

.service-card:nth-child(1) {
  animation-delay: 0.1s;
}

.service-card:nth-child(2) {
  animation-delay: 0.2s;
}

.service-card:nth-child(3) {
  animation-delay: 0.3s;
}

.service-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #409eff;
}

.card-icon {
  width: 70px;
  height: 70px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  margin: 0 auto 20px;
  transition: all 0.3s ease;
}

.patient-icon {
  background: #ecf5ff;
  color: #409eff;
}

.appointment-icon {
  background: #fef0f0;
  color: #f56c6c;
}

.record-icon {
  background: #f0f9ff;
  color: #67c23a;
}

.service-card:hover .card-icon {
  transform: scale(1.05);
}

.card-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 10px 0;
  text-align: center;
}

.card-description {
  font-size: 14px;
  color: #909399;
  margin: 0;
  text-align: center;
  line-height: 1.5;
}

.card-arrow {
  position: absolute;
  bottom: 20px;
  right: 20px;
  font-size: 18px;
  color: #c0c4cc;
  opacity: 0;
  transform: translateX(-5px);
  transition: all 0.3s ease;
}

.service-card:hover .card-arrow {
  opacity: 0.6;
  transform: translateX(0);
  color: #409eff;
}

/* 子页面卡片样式 */
.main-card {
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: none;
  overflow: hidden;
  animation: slideUp 0.6s ease-out;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-button {
  transition: all 0.3s ease;
}

.back-button:hover {
  transform: scale(1.05);
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
  letter-spacing: 0.5px;
}

.header-right {
  display: flex;
  align-items: center;
}

.nav-buttons {
  display: flex;
  gap: 0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.nav-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  font-weight: 500;
  transition: all 0.3s ease;
  border-radius: 0 !important;
}

.nav-btn:hover {
  transform: translateY(-2px);
}

:deep(.el-button-group .el-button:first-child) {
  border-radius: 8px 0 0 8px !important;
}

:deep(.el-button-group .el-button:last-child) {
  border-radius: 0 8px 8px 0 !important;
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  border: none;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
}

:deep(.el-button--primary:hover) {
  background: linear-gradient(135deg, #66b1ff 0%, #409eff 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
}

.content-wrapper {
  padding: 20px 0;
  animation: fadeIn 0.8s ease-out 0.2s backwards;
}

:deep(.el-card__header) {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border-bottom: 2px solid #e4e7ed;
  padding: 24px;
}

:deep(.el-card__body) {
  padding: 24px;
}

/* 动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .patient-management-container {
    padding: 10px;
  }

  /* 首页响应式 */
  .welcome-title {
    font-size: 28px;
  }

  .title-icon {
    font-size: 28px;
  }

  .welcome-subtitle {
    font-size: 14px;
  }

  .service-grid {
    flex-direction: column;
    align-items: center;
  }

  .service-card {
    width: 100%;
    max-width: 400px;
  }

  /* 子页面响应式 */
  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-left {
    width: 100%;
  }

  .header-right {
    width: 100%;
  }

  .nav-buttons {
    width: 100%;
    flex-direction: column;
  }

  .nav-btn {
    width: 100%;
    justify-content: center;
    border-radius: 8px !important;
  }

  :deep(.el-button-group .el-button) {
    border-radius: 8px !important;
    margin-bottom: 8px;
  }

  .page-title {
    font-size: 20px;
  }
}
</style>
