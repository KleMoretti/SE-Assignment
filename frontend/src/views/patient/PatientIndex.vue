<template>
  <div class="patient-management-container">
    <el-card class="main-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-button 
              :icon="ArrowLeft" 
              @click="goBack" 
              circle 
              class="back-button"
            />
            <span class="page-title">病人管理</span>
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
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeft, User, Calendar, Document } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const goBack = () => {
  router.push({ name: 'Home' })
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
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
  padding-bottom: 40px;
  box-sizing: border-box;
  animation: fadeIn 0.5s ease-out;
}

.main-card {
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: none;
  overflow: hidden;
  animation: slideUp 0.6s ease-out;
  min-height: calc(100vh - 80px);
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
