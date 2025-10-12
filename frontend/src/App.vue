<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div id="app">
    <header class="bg-blue-600 text-white p-4">
      <nav class="container mx-auto flex justify-between items-center">
        <RouterLink to="/" class="text-xl font-bold">
          医院综合管理系统
        </RouterLink>
        <ul class="flex space-x-4">
          <li>
            <RouterLink to="/patient" class="hover:underline">病人管理</RouterLink>
          </li>
          <li>
            <RouterLink to="/doctor" class="hover:underline">医生管理</RouterLink>
          </li>
          <li>
            <RouterLink to="/pharmacy" class="hover:underline">药房管理</RouterLink>
          </li>
        </ul>
      </nav>
    </header>

    <main class="container mx-auto p-4">
      <RouterView />
    </main>
  </div>
</template>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>
