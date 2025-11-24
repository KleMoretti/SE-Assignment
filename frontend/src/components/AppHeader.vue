<template>
  <header class="bg-blue-600 text-white shadow-md">
    <div class="container mx-auto px-4 py-3">
      <div class="flex justify-between items-center">
        <router-link to="/" class="text-xl font-bold hover:text-blue-200">
          医院综合管理系统
        </router-link>
        <nav class="flex items-center space-x-6">
          <router-link to="/" class="hover:text-blue-200">首页</router-link>
          <router-link :to="{ name: 'PatientList' }" class="hover:text-blue-200">病人管理</router-link>

          <!-- 医生管理下拉菜单 -->
          <el-dropdown @command="handleCommand">
            <span class="el-dropdown-link hover:text-blue-200 cursor-pointer">
              医生管理
              <el-icon class="el-icon--right">
                <arrow-down />
              </el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="/doctor">医生列表</el-dropdown-item>
                <el-dropdown-item command="/doctor/schedule">排班管理</el-dropdown-item>
                <el-dropdown-item command="/doctor/performance">绩效管理</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          
          <router-link to="/pharmacy" class="hover:text-blue-200">药房管理</router-link>
        </nav>
      </div>
    </div>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ArrowDown } from '@element-plus/icons-vue'

const router = useRouter()

// 处理下拉菜单命令
const handleCommand = (command) => {
  router.push(command)
}
</script>

<style scoped>
/* 组件样式 */
</style>
