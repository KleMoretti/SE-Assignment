import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

// 创建axios实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 从sessionStorage获取token并添加到请求头
    const token = sessionStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // 如果是刷新token的请求，使用refresh_token
    if (config.url === '/auth/refresh') {
      const refreshToken = sessionStorage.getItem('refreshToken')
      if (refreshToken) {
        config.headers.Authorization = `Bearer ${refreshToken}`
      }
    }
    
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    const { data } = response

    // 统一处理响应
    if (data.success === false) {
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(new Error(data.message))
    }

    return data
  },
  (error) => {
    // 统一错误处理
    if (error.response) {
      const { status, data, config } = error.response

      switch (status) {
        case 401:
          // 只在token过期时显示提示并跳转
          if (config && config.url !== '/auth/login') {
            ElMessage.error('登录已过期，请重新登录')
            // 清除token并跳转到登录页
            sessionStorage.removeItem('token')
            sessionStorage.removeItem('refreshToken')
            sessionStorage.removeItem('userInfo')
            router.push('/login')
          }
          break
        // 其他错误由业务代码自行处理，避免重复提示
      }
    } else if (error.request) {
      ElMessage.error('网络错误，请检查网络连接')
    }

    return Promise.reject(error)
  }
)

export default request
