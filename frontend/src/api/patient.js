import request from './request'

/**
 * 获取病人列表
 * @param {Object} params 查询参数
 * @returns {Promise}
 */
export function getPatientList(params) {
  return request({
    url: '/patient/patients',
    method: 'get',
    params
  })
}

/**
 * 获取病人详情
 * @param {number} id 病人ID
 * @returns {Promise}
 */
export function getPatientDetail(id) {
  return request({
    url: `/patient/patients/${id}`,
    method: 'get'
  })
}

/**
 * 创建病人
 * @param {Object} data 病人数据
 * @returns {Promise}
 */
export function createPatient(data) {
  return request({
    url: '/patient/patients',
    method: 'post',
    data
  })
}

/**
 * 更新病人
 * @param {number} id 病人ID
 * @param {Object} data 病人数据
 * @returns {Promise}
 */
export function updatePatient(id, data) {
  return request({
    url: `/patient/patients/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除病人
 * @param {number} id 病人ID
 * @returns {Promise}
 */
export function deletePatient(id) {
  return request({
    url: `/patient/patients/${id}`,
    method: 'delete'
  })
}

// 获取挂号预约列表（分页 + 状态过滤）
export function getAppointmentList(params) {
  return request({
    url: '/patient/appointments',
    method: 'get',
    params
  })
}

// 新增挂号预约
export function addAppointment(data) {
  return request({
    url: '/patient/appointments',
    method: 'post',
    data
  })
}

// 获取病历记录列表（分页 + 可按病人过滤）
export function getMedicalRecordList(params) {
  return request({
    url: '/patient/medical-records',
    method: 'get',
    params
  })
}
