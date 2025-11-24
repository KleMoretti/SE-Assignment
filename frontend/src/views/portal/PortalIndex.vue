<template>
  <div class="portal-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>病人服务门户</span>
        </div>
      </template>
      <div class="button-group">
        <el-button type="primary" size="large" @click="goToProfile" class="portal-button">
          <el-icon class="el-icon--left"><User /></el-icon>
          个人信息管理
        </el-button>
        <el-button type="primary" size="large" @click="goToAppointmentBooking" class="portal-button">
          <el-icon class="el-icon--left"><Calendar /></el-icon>
          预约挂号
        </el-button>
        <el-button type="success" size="large" @click="goToFamilyManagement" class="portal-button">
          <el-icon class="el-icon--left"><UserFilled /></el-icon>
          家庭成员管理
        </el-button>
      </div>
    </el-card>

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
import { Calendar, User, UserFilled } from '@element-plus/icons-vue'
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
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 120px); /* Adjust based on header height */
  background-color: #f5f7fa;
  padding: 20px;
}

.box-card {
  width: 100%;
  max-width: 800px;
}

.card-header {
  font-size: 24px;
  font-weight: bold;
  text-align: center;
}

.button-group {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 20px;
  padding: 40px 20px;
}

.portal-button {
  width: 220px;
  height: 80px;
  font-size: 18px;
}

@media (max-width: 768px) {
  .button-group {
    flex-direction: column;
    align-items: center;
  }

  .portal-button {
    width: 100%;
    max-width: 300px;
  }
}
</style>
