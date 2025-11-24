/**
 * 认证相关API
 */
import request from './request'

/**
 * 用户注册
 */
export function register(data) {
  return request({
    url: '/auth/register',
    method: 'post',
    data
  })
}

/**
 * 用户登录
 */
export function login(data) {
  return request({
    url: '/auth/login',
    method: 'post',
    data
  })
}

/**
 * 刷新Token
 */
export function refreshToken() {
  return request({
    url: '/auth/refresh',
    method: 'post'
  })
}

/**
 * 获取当前用户信息
 */
export function getCurrentUser() {
  return request({
    url: '/auth/me',
    method: 'get'
  })
}

/**
 * 更新个人信息
 */
export function updateProfile(data) {
  return request({
    url: '/auth/update-profile',
    method: 'put',
    data
  })
}

/**
 * 修改密码
 */
export function changePassword(data) {
  return request({
    url: '/auth/change-password',
    method: 'post',
    data
  })
}

/**
 * 检查病人信息是否完整
 */
export function checkPatientInfo() {
  return request({
    url: '/auth/check-patient-info',
    method: 'get'
  })
}

/**
 * 完善病人信息
 */
export function completePatientInfo(data) {
  return request({
    url: '/auth/complete-patient-info',
    method: 'post',
    data
  })
}

/**
 * 获取用户列表（管理员）
 */
export function getUsers(params) {
  return request({
    url: '/auth/users',
    method: 'get',
    params
  })
}

/**
 * 更新用户信息（管理员）
 */
export function updateUser(userId, data) {
  return request({
    url: `/auth/users/${userId}`,
    method: 'put',
    data
  })
}

/**
 * 删除用户（管理员）
 */
export function deleteUser(userId) {
  return request({
    url: `/auth/users/${userId}`,
    method: 'delete'
  })
}
