<script setup>
import { ref } from 'vue'

const features = ref([
  {
    title: '病人管理',
    description: '完整的病人信息管理，包括添加、编辑、删除和查询病人信息',
    icon: '👥',
    path: '/patient'
  },
  {
    title: '医生管理',
    description: '医生信息管理，包含医生排班、科室管理等功能',
    icon: '👨‍⚕️',
    path: '/doctor'
  },
  {
    title: '药房管理',
    description: '药品库存管理、处方管理、药品出入库等功能',
    icon: '💊',
    path: '/pharmacy'
  }
])
</script>

<template>
  <div class="home">
    <div class="text-center py-12">
      <h1 class="text-4xl font-bold text-gray-800 mb-4">
        欢迎使用医院综合管理系统
      </h1>
      <p class="text-xl text-gray-600 mb-8">
        高效、便捷的医院管理解决方案
      </p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
      <div
        v-for="feature in features"
        :key="feature.title"
        class="card hover:shadow-lg transition-shadow duration-300 cursor-pointer"
        @click="$router.push(feature.path)"
      >
        <div class="text-center">
          <div class="text-6xl mb-4">{{ feature.icon }}</div>
          <h3 class="text-xl font-semibold text-gray-800 mb-2">
            {{ feature.title }}
          </h3>
          <p class="text-gray-600">
            {{ feature.description }}
          </p>
        </div>
      </div>
    </div>

    <div class="text-center py-12">
      <div class="bg-blue-50 rounded-lg p-8 max-w-4xl mx-auto">
        <h2 class="text-2xl font-bold text-gray-800 mb-4">
          系统特性
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 text-left">
          <div class="flex items-start">
            <span class="text-green-500 mr-2">✓</span>
            <span>前后端分离架构，响应式设计</span>
          </div>
          <div class="flex items-start">
            <span class="text-green-500 mr-2">✓</span>
            <span>基于Vue.js 3 + Flask的现代化技术栈</span>
          </div>
          <div class="flex items-start">
            <span class="text-green-500 mr-2">✓</span>
            <span>MySQL数据库，支持数据持久化</span>
          </div>
          <div class="flex items-start">
            <span class="text-green-500 mr-2">✓</span>
            <span>RESTful API设计，易于扩展</span>
          </div>
          <div class="flex items-start">
            <span class="text-green-500 mr-2">✓</span>
            <span>JWT认证，保障数据安全</span>
          </div>
          <div class="flex items-start">
            <span class="text-green-500 mr-2">✓</span>
            <span>模块化设计，便于维护和开发</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home {
  min-height: calc(100vh - 200px);
}
</style>
