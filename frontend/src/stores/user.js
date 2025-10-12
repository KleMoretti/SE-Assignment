import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  // 状态
  const isLoggedIn = ref(false)
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || '')

  // 计算属性
  const userName = computed(() => user.value?.name || '未登录')
  const isAdmin = computed(() => user.value?.role === 'admin')

  // 方法
  function login(userData, authToken) {
    user.value = userData
    token.value = authToken
    isLoggedIn.value = true
    localStorage.setItem('token', authToken)
  }

  function logout() {
    user.value = null
    token.value = ''
    isLoggedIn.value = false
    localStorage.removeItem('token')
  }

  function updateUser(userData) {
    user.value = { ...user.value, ...userData }
  }

  return {
    // 状态
    isLoggedIn,
    user,
    token,
    // 计算属性
    userName,
    isAdmin,
    // 方法
    login,
    logout,
    updateUser
  }
})
