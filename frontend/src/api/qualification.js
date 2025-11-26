import request from './request'

/**
 * 医生资质管理API
 */

const normalizeQualification = (item = {}) => ({
  id: item.id,
  doctorId: item.doctor_id,
  doctorName: item.doctor_name,
  qualificationType: item.qualification_type,
  certificateNo: item.certificate_no,
  certificateName: item.certificate_name,
  issueDate: item.issue_date,
  expiryDate: item.expiry_date,
  issuingAuthority: item.issuing_authority,
  scopeOfPractice: item.scope_of_practice,
  attachmentUrl: item.attachment_url,
  status: item.status,
  isExpiringSoon: item.is_expiring_soon,
  notes: item.notes,
  createdAt: item.created_at,
  updatedAt: item.updated_at
})

const buildQualificationPayload = (data = {}) => ({
  doctor_id: data.doctorId,
  qualification_type: data.qualificationType,
  certificate_no: data.certificateNo,
  certificate_name: data.certificateName,
  issue_date: data.issueDate,
  expiry_date: data.expiryDate,
  issuing_authority: data.issuingAuthority,
  scope_of_practice: data.scopeOfPractice,
  attachment_url: data.attachmentUrl,
  status: data.status,
  notes: data.notes
})

// 获取资质列表
export function getQualificationList(params = {}) {
  const {
    page = 1,
    pageSize = 10,
    doctorId,
    qualificationType,
    status
  } = params

  return request({
    url: '/doctor/qualifications',
    method: 'get',
    params: {
      page,
      per_page: pageSize,
      doctor_id: doctorId,
      qualification_type: qualificationType,
      status
    }
  }).then((res) => {
    const data = res?.data || {}
    const items = (data.items || data.list || []).map(normalizeQualification)

    return {
      ...res,
      data: {
        ...data,
        items,
        list: items
      }
    }
  })
}

// 获取资质详情
export function getQualificationDetail(id) {
  return request({
    url: `/doctor/qualifications/${id}`,
    method: 'get'
  }).then((res) => ({
    ...res,
    data: normalizeQualification(res?.data)
  }))
}

// 创建资质
export function createQualification(data) {
  return request({
    url: '/doctor/qualifications',
    method: 'post',
    data: buildQualificationPayload(data)
  }).then((res) => ({
    ...res,
    data: normalizeQualification(res?.data)
  }))
}

// 更新资质
export function updateQualification(id, data) {
  return request({
    url: `/doctor/qualifications/${id}`,
    method: 'put',
    data: buildQualificationPayload(data)
  }).then((res) => ({
    ...res,
    data: normalizeQualification(res?.data)
  }))
}

// 删除资质
export function deleteQualification(id) {
  return request({
    url: `/doctor/qualifications/${id}`,
    method: 'delete'
  })
}

// 获取指定医生的资质列表
export function getDoctorQualifications(doctorId) {
  return request({
    url: `/doctor/doctors/${doctorId}/qualifications`,
    method: 'get'
  }).then((res) => {
    const data = res?.data || {}
    const items = (data.qualifications || data.items || data.list || []).map(normalizeQualification)

    return {
      ...res,
      data: {
        ...data,
        doctor: data.doctor,
        qualifications: items,
        items,
        list: items,
        statistics: data.statistics || {}
      }
    }
  })
}
