<template>
  <header class="bg-blue-600 text-white shadow-md">
    <div class="container mx-auto px-4 py-3">
      <div class="flex justify-between items-center">
        <router-link to="/" class="text-xl font-bold hover:text-blue-200">
          医院综合管理系统
        </router-link>
        <nav class="space-x-6">
          <router-link to="/" class="hover:text-blue-200">首页</router-link>
          <router-link to="/patient" class="hover:text-blue-200">病人管理</router-link>
          <router-link to="/doctor" class="hover:text-blue-200">医生管理</router-link>
          <router-link to="/pharmacy" class="hover:text-blue-200">药房管理</router-link>
        </nav>
      </div>
    </div>
  </header>
</template>

<script setup>
// 头部导航组件
</script>

<style scoped>
/* 组件样式 */
</style>
