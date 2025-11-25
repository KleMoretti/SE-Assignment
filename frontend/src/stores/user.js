/**
 * 用户状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, getCurrentUser } from '@/api/auth'
import router from '@/router'

export const useUserStore = defineStore('user', () => {
  // 状态 - 使用 sessionStorage 实现每个标签页独立登录
  const token = ref(sessionStorage.getItem('token') || '')
  const refreshToken = ref(sessionStorage.getItem('refreshToken') || '')
  const userInfo = ref(null)
  
  // 计算属性
  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => userInfo.value?.role === 'admin')
  const isDoctor = computed(() => userInfo.value?.role === 'doctor')
  
  /**
   * 设置Token
   */
  function setToken(newToken, newRefreshToken) {
    token.value = newToken
    refreshToken.value = newRefreshToken
    
    if (newToken) {
      sessionStorage.setItem('token', newToken)
      if (newRefreshToken) {
        sessionStorage.setItem('refreshToken', newRefreshToken)
      }
    } else {
      sessionStorage.removeItem('token')
      sessionStorage.removeItem('refreshToken')
    }
  }
  
  /**
   * 设置用户信息
   */
  function setUserInfo(info) {
    userInfo.value = info
    if (info) {
      sessionStorage.setItem('userInfo', JSON.stringify(info))
    } else {
      sessionStorage.removeItem('userInfo')
    }
  }
  
  /**
   * 用户登录
   */
  async function handleLogin(loginForm) {
    try {
      const response = await login(loginForm)
      
      if (response.success) {
        const { access_token, refresh_token, user } = response.data
        
        setToken(access_token, refresh_token)
        setUserInfo(user)
        
        return { success: true, message: response.message }
      }
      
      return { success: false, message: response.message || '登录失败' }
    } catch (error) {
      return { success: false, message: error.message || '登录失败' }
    }
  }
  
  /**
   * 用户登出
   */
  function handleLogout() {
    setToken('', '')
    setUserInfo(null)
    router.push('/login')
  }
  
  /**
   * 获取用户信息
   */
  async function getUserInfo() {
    try {
      const response = await getCurrentUser()
      
      if (response.success) {
        setUserInfo(response.data)
        return response.data
      }
      
      return null
    } catch (error) {
      console.error('获取用户信息失败:', error)
      return null
    }
  }
  
  /**
   * 初始化（从sessionStorage恢复）
   */
  function init() {
    const savedUserInfo = sessionStorage.getItem('userInfo')
    if (savedUserInfo) {
      try {
        userInfo.value = JSON.parse(savedUserInfo)
      } catch (e) {
        console.error('解析用户信息失败:', e)
      }
    }
  }
  
  // 初始化
  init()
  
  return {
    // 状态
    token,
    refreshToken,
    userInfo,
    
    // 计算属性
    isLoggedIn,
    isAdmin,
    isDoctor,
    
    // 方法
    setToken,
    setUserInfo,
    handleLogin,
    handleLogout,
    getUserInfo
  }
})
