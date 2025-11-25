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

// 取消预约
export function cancelAppointment(id) {
  return request({
    url: `/patient/appointments/${id}/cancel`,
    method: 'put'
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

/**
 * 获取当前用户可管理的所有病人列表
 * @returns {Promise}
 */
export function getManagedPatients() {
  return request({
    url: '/patient/portal/managed-patients',
    method: 'get'
  })
}

/**
 * 添加家庭成员
 * @param {Object} data 包含 username 和 password
 * @returns {Promise}
 */
export function addManagedPatient(data) {
  return request({
    url: '/patient/portal/family-members/add',
    method: 'post',
    data
  })
}

/**
 * 获取指定病人的预约列表（病人端）
 * @param {number} patientId 病人ID
 * @param {string} status 预约状态（可选）
 * @returns {Promise}
 */
export function getPatientAppointments(patientId, status) {
  return request({
    url: `/patient/portal/patients/${patientId}/appointments`,
    method: 'get',
    params: { status }
  })
}

/**
 * 创建预约（病人端自助挂号）
 * @param {Object} data 预约数据
 * @returns {Promise}
 */
export function createPortalAppointment(data) {
  return request({
    url: '/patient/portal/appointments',
    method: 'post',
    data
  })
}

/**
 * 取消预约（病人端）
 * @param {number} appointmentId 预约ID
 * @returns {Promise}
 */
export function cancelPortalAppointment(appointmentId) {
  return request({
    url: `/patient/portal/appointments/${appointmentId}/cancel`,
    method: 'put'
  })
}

/**
 * 获取指定病人的病历记录列表（病人端）
 * @param {number} patientId 病人ID
 * @returns {Promise}
 */
export function getPatientMedicalRecords(patientId) {
  return request({
    url: `/patient/portal/patients/${patientId}/medical-records`,
    method: 'get'
  })
}
