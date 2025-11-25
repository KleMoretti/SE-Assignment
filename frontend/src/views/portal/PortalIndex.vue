<template>
  <div class="portal-container">
    <!-- 欢迎标题 -->
    <div class="welcome-section">
      <h1 class="welcome-title">
        <el-icon class="title-icon"><House /></el-icon>
        病人服务门户
      </h1>
      <p class="welcome-subtitle">为您提供便捷的医疗服务</p>
    </div>

    <!-- 服务卡片网格 -->
    <div class="service-grid">
      <div class="service-card" @click="goToProfile">
        <div class="card-icon profile-icon">
          <el-icon><User /></el-icon>
        </div>
        <h3 class="card-title">个人信息</h3>
        <p class="card-description">查看和管理您的个人档案</p>
        <div class="card-arrow">
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>

      <div class="service-card" @click="goToAppointmentBooking">
        <div class="card-icon booking-icon">
          <el-icon><Calendar /></el-icon>
        </div>
        <h3 class="card-title">预约挂号</h3>
        <p class="card-description">在线预约医生门诊服务</p>
        <div class="card-arrow">
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>

      <div class="service-card" @click="goToFamilyManagement">
        <div class="card-icon family-icon">
          <el-icon><UserFilled /></el-icon>
        </div>
        <h3 class="card-title">家庭成员</h3>
        <p class="card-description">管理家人的就医档案</p>
        <div class="card-arrow">
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>
    </div>

    <!-- 完善病人信息弹窗 -->
    <CompletePatientInfoDialog
      ref="patientInfoDialogRef"
      @completed="handlePatientInfoCompleted"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Calendar, User, UserFilled, House, ArrowRight } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { checkPatientInfo } from '@/api/auth'
import CompletePatientInfoDialog from '@/components/CompletePatientInfoDialog.vue'

const router = useRouter()
const route = useRoute()
const patientInfoDialogRef = ref(null)

onMounted(async () => {
  // 检查是否需要完善病人信息
  const shouldCheck = route.query.checkPatientInfo === '1'

  if (shouldCheck) {
    // 清除URL参数
    router.replace({ path: route.path, query: {} })

    try {
      const response = await checkPatientInfo()

      if (response.success && response.data) {
        const { has_patient_info, is_complete, patient } = response.data

        // 如果有病人信息但不完整，弹出完善信息对话框
        if (has_patient_info && !is_complete) {
          setTimeout(() => {
            patientInfoDialogRef.value?.show(patient)
          }, 500)
        }
      }
    } catch (error) {
      console.error('检查病人信息失败:', error)
    }
  }
})

const goToProfile = () => {
  router.push({ name: 'PortalProfile' })
}

const goToAppointmentBooking = () => {
  router.push({ name: 'PortalAppointmentBooking' })
}

const goToFamilyManagement = () => {
  router.push({ name: 'PortalFamilyManagement' })
}

const handlePatientInfoCompleted = (patientData) => {
  ElMessage.success('个人信息完善成功！')
  console.log('病人信息已完善:', patientData)
}
</script>

<style scoped>
.portal-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20px;
  padding-bottom: 40px;
  box-sizing: border-box;
}

/* 欢迎区域 */
.welcome-section {
  text-align: center;
  margin-bottom: 50px;
  padding-top: 40px;
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

.profile-icon {
  background: #ecf5ff;
  color: #409eff;
}

.booking-icon {
  background: #fef0f0;
  color: #f56c6c;
}

.family-icon {
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

/* 动画 */
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

/* 响应式设计 */
@media (max-width: 768px) {
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
}
</style>
