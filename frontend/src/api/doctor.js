/**
 * 医生管理相关API
 */
import request from './request'

// ============= 医生信息管理 =============

/**
 * 获取医生列表
 */
export function getDoctors(params) {
  return request({
    url: '/doctor/doctors',
    method: 'get',
    params
  })
}

/**
 * 获取医生详情
 */
export function getDoctorDetail(doctorId) {
  return request({
    url: `/doctor/doctors/${doctorId}`,
    method: 'get'
  })
}

/**
 * 创建医生
 */
export function createDoctor(data) {
  return request({
    url: '/doctor/doctors',
    method: 'post',
    data
  })
}

/**
 * 更新医生信息
 */
export function updateDoctor(doctorId, data) {
  return request({
    url: `/doctor/doctors/${doctorId}`,
    method: 'put',
    data
  })
}

/**
 * 删除医生
 */
export function deleteDoctor(doctorId) {
  return request({
    url: `/doctor/doctors/${doctorId}`,
    method: 'delete'
  })
}

/**
 * 获取医生统计数据
 */
export function getDoctorStatistics() {
  return request({
    url: '/doctor/doctors/statistics',
    method: 'get'
  })
}

// ============= 医生排班管理 =============

/**
 * 获取排班列表
 */
export function getSchedules(params) {
  return request({
    url: '/doctor/schedules',
    method: 'get',
    params
  })
}

/**
 * 获取排班详情
 */
export function getScheduleDetail(scheduleId) {
  return request({
    url: `/doctor/schedules/${scheduleId}`,
    method: 'get'
  })
}

/**
 * 创建排班
 */
export function createSchedule(data) {
  return request({
    url: '/doctor/schedules',
    method: 'post',
    data
  })
}

/**
 * 更新排班
 */
export function updateSchedule(scheduleId, data) {
  return request({
    url: `/doctor/schedules/${scheduleId}`,
    method: 'put',
    data
  })
}

/**
 * 删除排班
 */
export function deleteSchedule(scheduleId) {
  return request({
    url: `/doctor/schedules/${scheduleId}`,
    method: 'delete'
  })
}

/**
 * 获取医生的排班列表
 */
export function getDoctorSchedules(doctorId, params) {
  return request({
    url: `/doctor/doctors/${doctorId}/schedules`,
    method: 'get',
    params
  })
}

// ============= 医生绩效管理 =============

/**
 * 获取绩效列表
 */
export function getPerformances(params) {
  return request({
    url: '/doctor/performances',
    method: 'get',
    params
  })
}

/**
 * 获取绩效详情
 */
export function getPerformanceDetail(performanceId) {
  return request({
    url: `/doctor/performances/${performanceId}`,
    method: 'get'
  })
}

/**
 * 创建绩效评估
 */
export function createPerformance(data) {
  return request({
    url: '/doctor/performances',
    method: 'post',
    data
  })
}

/**
 * 更新绩效评估
 */
export function updatePerformance(performanceId, data) {
  return request({
    url: `/doctor/performances/${performanceId}`,
    method: 'put',
    data
  })
}

/**
 * 删除绩效评估
 */
export function deletePerformance(performanceId) {
  return request({
    url: `/doctor/performances/${performanceId}`,
    method: 'delete'
  })
}

/**
 * 获取医生的绩效记录
 */
export function getDoctorPerformances(doctorId, params) {
  return request({
    url: `/doctor/doctors/${doctorId}/performances`,
    method: 'get',
    params
  })
}

/**
 * 获取绩效统计数据
 */
export function getPerformanceStatistics(params) {
  return request({
    url: '/doctor/performances/statistics',
    method: 'get',
    params
  })
}

