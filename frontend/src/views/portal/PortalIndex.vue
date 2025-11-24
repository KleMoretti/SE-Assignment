<template>
  <div class="portal-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>病人服务门户</span>
        </div>
      </template>
      <div class="button-group">
        <el-button type="primary" size="large" @click="goToAppointmentBooking" class="portal-button">
          <el-icon class="el-icon--left"><Calendar /></el-icon>
          预约挂号
        </el-button>
        <el-button type="success" size="large" @click="goToFamilyManagement" class="portal-button">
          <el-icon class="el-icon--left"><User /></el-icon>
          家庭成员管理
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { Calendar, User } from '@element-plus/icons-vue'

const router = useRouter()

const goToAppointmentBooking = () => {
  router.push({ name: 'PortalAppointmentBooking' })
}

const goToFamilyManagement = () => {
  router.push({ name: 'PortalFamilyManagement' })
}
</script>

<style scoped>
.portal-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: calc(100vh - 120px); /* Adjust based on header height */
  background-color: #f5f7fa;
}

.box-card {
  width: 600px;
}

.card-header {
  font-size: 24px;
  font-weight: bold;
  text-align: center;
}

.button-group {
  display: flex;
  justify-content: space-around;
  padding: 40px 20px;
}

.portal-button {
  width: 200px;
  height: 60px;
  font-size: 18px;
}
</style>

