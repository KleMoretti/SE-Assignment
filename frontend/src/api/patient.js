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
