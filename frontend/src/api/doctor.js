import request from './request'

/**
 * 医生相关API
 */

// 获取医生列表
export function getDoctorList(params) {
  return request({
    url: '/doctor/doctors',
    method: 'get',
    params
  })
}

// 获取医生详情
export function getDoctorDetail(id) {
  return request({
    url: `/doctor/doctors/${id}`,
    method: 'get'
  })
}

// 创建医生
export function createDoctor(data) {
  return request({
    url: '/doctor/doctors',
    method: 'post',
    data
  })
}

// 更新医生信息
export function updateDoctor(id, data) {
  return request({
    url: `/doctor/doctors/${id}`,
    method: 'put',
    data
  })
}

// 删除医生
export function deleteDoctor(id) {
  return request({
    url: `/doctor/doctors/${id}`,
    method: 'delete'
  })
}

// 获取医生排班
export function getDoctorSchedule(doctorId, params) {
  return request({
    url: `/doctor/doctors/${doctorId}/schedule`,
    method: 'get',
    params
  })
}

// 创建排班
export function createSchedule(doctorId, data) {
  return request({
    url: `/doctor/doctors/${doctorId}/schedule`,
    method: 'post',
    data
  })
}

// 更新排班
export function updateSchedule(doctorId, scheduleId, data) {
  return request({
    url: `/doctor/doctors/${doctorId}/schedule/${scheduleId}`,
    method: 'put',
    data
  })
}

// 删除排班
export function deleteSchedule(doctorId, scheduleId) {
  return request({
    url: `/doctor/doctors/${doctorId}/schedule/${scheduleId}`,
    method: 'delete'
  })
}

// 获取医生绩效
export function getDoctorPerformance(doctorId, params) {
  return request({
    url: `/doctor/doctors/${doctorId}/performance`,
    method: 'get',
    params
  })
}

// 获取科室列表
export function getDepartments() {
  return request({
    url: '/doctor/departments',
    method: 'get'
  })
}

// 获取职称列表
export function getTitles() {
  return request({
    url: '/doctor/titles',
    method: 'get'
  })
}

