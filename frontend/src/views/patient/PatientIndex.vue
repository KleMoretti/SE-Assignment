<template>
  <el-card class="box-card">
    <template #header>
      <div class="flex justify-between items-center">
        <span class="text-xl font-semibold">病人管理</span>
        <div>
          <el-button-group>
            <el-button :type="isRouteActive('PatientList') ? 'primary' : 'default'" @click="navigateTo('PatientList')">病人信息</el-button>
            <el-button :type="isRouteActive('AppointmentList') ? 'primary' : 'default'" @click="navigateTo('AppointmentList')">挂号预约</el-button>
            <el-button :type="isRouteActive('MedicalRecordList') ? 'primary' : 'default'" @click="navigateTo('MedicalRecordList')">病历记录</el-button>
          </el-button-group>
        </div>
      </div>
    </template>
    <!-- The key forces the router-view to re-render when the route changes -->
    <router-view :key="route.fullPath"></router-view>
  </el-card>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const navigateTo = (routeName) => {
  router.push({ name: routeName })
}

const isRouteActive = (routeName) => {
  // This needs to check against the current route's name
  return route.name === routeName
}
</script>

<style scoped>
.box-card {
  margin: 20px;
  /* Ensure the card takes up significant height */
  min-height: calc(100vh - 100px);
}
</style>
