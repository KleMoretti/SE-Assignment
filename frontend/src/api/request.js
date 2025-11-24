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
    // 从localStorage获取token并添加到请求头
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // 如果是刷新token的请求，使用refresh_token
    if (config.url === '/auth/refresh') {
      const refreshToken = localStorage.getItem('refreshToken')
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
        case 400:
          ElMessage.error(data?.message || '请求参数错误')
          break
        case 401:
          // 区分登录失败与token过期
          if (config && config.url === '/auth/login') {
            // 登录接口返回401，通常是用户名或密码错误
            ElMessage.error(data?.message || '用户名或密码错误')
          } else {
            ElMessage.error('登录已过期，请重新登录')
            // 清除token并跳转到登录页
            localStorage.removeItem('token')
            localStorage.removeItem('refreshToken')
            localStorage.removeItem('userInfo')
            router.push('/login')
          }
          break
        case 403:
          ElMessage.error(data?.message || '权限不足')
          break
        case 404:
          ElMessage.error(data?.message || '请求资源不存在')
          break
        case 500:
          ElMessage.error(data?.message || '服务器错误')
          break
        default:
          ElMessage.error(data?.message || '请求失败')
      }
    } else if (error.request) {
      ElMessage.error('网络错误，请检查网络连接')
    } else {
      ElMessage.error(error.message || '请求配置错误')
    }

    return Promise.reject(error)
  }
)

export default request
