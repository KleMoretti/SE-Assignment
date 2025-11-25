import request from './request'

/**
 * 医生相关API
 */

const formatDateValue = (value) => {
  if (!value) return undefined
  if (typeof value === 'string') {
    return value
  }
  if (value instanceof Date) {
    const year = value.getFullYear()
    const month = String(value.getMonth() + 1).padStart(2, '0')
    const day = String(value.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }
  return value
}

const removeUndefined = (payload) => {
  const cleaned = {}
  Object.keys(payload).forEach((key) => {
    if (payload[key] !== undefined) {
      cleaned[key] = payload[key]
    }
  })
  return cleaned
}

const buildDoctorPayload = (data = {}) => {
  const sanitizedAge = data.age === null || data.age === '' ? undefined : data.age
  const sanitizedEmail = data.email ? data.email : undefined

  const payload = {
    doctor_no: data.doctorNo,
    name: data.name,
    gender: data.gender,
    age: sanitizedAge,
    phone: data.phone,
    email: sanitizedEmail,
    department: data.department,
    title: data.title,
    specialty: data.specialty,
    education: data.education,
    hire_date: formatDateValue(data.hireDate),
    status: data.status
  }

  return removeUndefined(payload)
}

const splitSpecialties = (value) => {
  if (!value || typeof value !== 'string') return []
  return value
    .split(/[,，;；、\s]+/)
    .map((item) => item.trim())
    .filter(Boolean)
}

const calcExperienceYears = (hireDate) => {
  if (!hireDate) return 0
  const start = new Date(hireDate)
  if (Number.isNaN(start.getTime())) return 0

  const today = new Date()
  let years = today.getFullYear() - start.getFullYear()
  const monthDiff = today.getMonth() - start.getMonth()
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < start.getDate())) {
    years -= 1
  }

  return Math.max(years, 0)
}

const normalizeDoctorBase = (doctor = {}) => {
  const specialties = splitSpecialties(doctor.specialty)

  return {
    id: doctor.id,
    doctorNo: doctor.doctor_no,
    name: doctor.name,
    gender: doctor.gender,
    age: doctor.age,
    phone: doctor.phone,
    email: doctor.email,
    department: doctor.department,
    title: doctor.title,
    specialty: doctor.specialty,
    specialties,
    education: doctor.education,
    hireDate: doctor.hire_date,
    status: doctor.status,
    createdAt: doctor.created_at,
    updatedAt: doctor.updated_at
  }
}

const normalizeDoctorListItem = (doctor = {}) => {
  const base = normalizeDoctorBase(doctor)

  return {
    ...base,
    patientCount: doctor.patientCount || doctor.total_patients || 0,
    scheduleCount: doctor.scheduleCount || doctor.total_schedules || 0,
    todayAppointments: doctor.todayAppointments || 0,
    yearsOfExperience: calcExperienceYears(base.hireDate)
  }
}

const normalizeDoctorDetail = (doctorData = {}) => {
  if (!doctorData) return null

  const { statistics = {}, ...rest } = doctorData
  const base = normalizeDoctorBase(rest)

  const totalAppointments = statistics.total_appointments || 0
  const completedAppointments = statistics.completed_appointments || 0
  const totalMedicalRecords = statistics.total_medical_records || 0
  const totalSchedules = statistics.total_schedules || 0

  return {
    ...base,
    patientCount: totalAppointments,
    totalAppointments,
    completedAppointments,
    totalMedicalRecords,
    totalSchedules,
    todayAppointments: rest.todayAppointments || 0,
    yearsOfExperience: calcExperienceYears(base.hireDate),
    statistics: {
      totalAppointments,
      completedAppointments,
      totalMedicalRecords,
      totalSchedules
    }
  }
}

const normalizeSchedule = (schedule = {}) => ({
  id: schedule.id,
  doctorId: schedule.doctor_id,
  doctorName: schedule.doctor_name,
  date: schedule.date,
  type: schedule.shift,
  shift: schedule.shift,
  startTime: schedule.start_time,
  endTime: schedule.end_time,
  maxPatients: schedule.max_patients,
  status: schedule.status,
  notes: schedule.notes,
  createdAt: schedule.created_at,
  bookedCount: schedule.booked_count || schedule.booked_patients || schedule.bookedPatients || 0
})

const normalizePerformanceRecord = (record = {}) => ({
  id: record.id,
  doctorId: record.doctor_id,
  year: record.year,
  month: record.month,
  patientCount: record.patient_count || 0,
  satisfactionScore: record.satisfaction_score || 0,
  punctualityScore: record.punctuality_score || 0,
  qualityScore: record.quality_score || 0,
  totalScore: record.total_score || 0,
  bonus: record.bonus || 0,
  notes: record.notes || '',
  createdAt: record.created_at
})

const normalizePerformanceStatistics = (stats = {}) => ({
  totalPatients: stats.total_patients || 0,
  averageSatisfaction: stats.average_satisfaction || 0,
  averageTotalScore: stats.average_total_score || 0,
  totalBonus: stats.total_bonus || 0
})

const normalizeLeave = (leave = {}) => ({
  id: leave.id,
  doctorId: leave.doctor_id,
  doctorName: leave.doctor_name,
  leaveType: leave.leave_type,
  startDate: leave.start_date,
  endDate: leave.end_date,
  days: leave.days,
  reason: leave.reason,
  status: leave.status,
  approverId: leave.approver_id,
  approvalDate: leave.approval_date,
  approvalNotes: leave.approval_notes,
  substituteDoctorId: leave.substitute_doctor_id,
  substituteDoctorName: leave.substitute_doctor_name,
  createdAt: leave.created_at,
  updatedAt: leave.updated_at
})

const normalizeMedicalRecord = (record = {}) => ({
  id: record.id,
  patientId: record.patient_id,
  patientName: record.patient_name,
  doctorId: record.doctor_id,
  doctorName: record.doctor_name,
  visitDate: record.visit_date,
  diagnosis: record.diagnosis,
  symptoms: record.symptoms,
  treatment: record.treatment,
  prescription: record.prescription,
  notes: record.notes,
  createdAt: record.created_at
})

const buildSchedulePayload = (doctorId, data = {}) => {
  const payload = {
    doctor_id: doctorId,
    date: formatDateValue(data.date),
    shift: data.type || data.shift,
    start_time: data.startTime,
    end_time: data.endTime,
    max_patients: data.maxPatients,
    status: data.status,
    notes: data.notes
  }

  return removeUndefined(payload)
}

const buildLeavePayload = (data = {}) => {
  const trimmedReason = typeof data.reason === 'string' ? data.reason.trim() : data.reason

  const payload = {
    doctor_id: data.doctorId,
    leave_type: data.leaveType,
    start_date: formatDateValue(data.startDate),
    end_date: formatDateValue(data.endDate),
    // 如果原因为空字符串或全是空白，则不传给后端，避免触发最小长度校验
    reason: trimmedReason === '' || trimmedReason === undefined ? undefined : trimmedReason,
    status: data.status,
    substitute_doctor_id: data.substituteDoctorId,
    approval_notes: data.approvalNotes
  }

  return removeUndefined(payload)
}

const normalizeMedicationRequest = (item = {}) => ({
  id: item.id,
  patientId: item.patient_id,
  patientName: item.patient_name,
  doctorId: item.doctor_id,
  doctorName: item.doctor_name,
  medicineId: item.medicine_id,
  medicineName: item.medicine_name,
  dose: item.dose,
  usage: item.usage,
  quantity: item.quantity,
  status: item.status,
  reason: item.reason,
  createdAt: item.created_at,
  approvedAt: item.approved_at,
  dispensedAt: item.dispensed_at,
  updatedAt: item.updated_at
})

const buildMedicationRequestPayload = (data = {}) => {
  const payload = {
    patient_id: data.patientId,
    doctor_id: data.doctorId,
    medicine_id: data.medicineId,
    dose: data.dose,
    usage: data.usage,
    quantity: data.quantity,
    reason: data.reason
  }

  return removeUndefined(payload)
}

// 获取医生列表
export function getDoctorList(params = {}) {
  const {
    page = 1,
    pageSize = 10,
    search,
    department,
    title,
    status,
    minAge,
    maxAge,
    education
  } = params

  return request({
    url: '/doctor/doctors',
    method: 'get',
    params: removeUndefined({
      page,
      per_page: pageSize,
      search,
      department,
      title,
      status,
      min_age: minAge,
      max_age: maxAge,
      education
    })
  }).then((res) => {
    const data = res?.data || {}
    const items = (data.items || []).map(normalizeDoctorListItem)

    return {
      ...res,
      data: {
        ...data,
        items
      }
    }
  })
}

// 获取医生详情
export function getDoctorDetail(id) {
  return request({
    url: `/doctor/doctors/${id}`,
    method: 'get'
  }).then((res) => ({
    ...res,
    data: normalizeDoctorDetail(res?.data)
  }))
}

// 创建医生
export function createDoctor(data) {
  return request({
    url: '/doctor/doctors',
    method: 'post',
    data: buildDoctorPayload(data)
  }).then((res) => ({
    ...res,
    data: normalizeDoctorDetail(res?.data)
  }))
}

// 更新医生信息
export function updateDoctor(id, data) {
  return request({
    url: `/doctor/doctors/${id}`,
    method: 'put',
    data: buildDoctorPayload(data)
  }).then((res) => ({
    ...res,
    data: normalizeDoctorDetail(res?.data)
  }))
}

// 删除医生
export function deleteDoctor(id) {
  return request({
    url: `/doctor/doctors/${id}`,
    method: 'delete'
  })
}

// 获取医生排班
export function getDoctorSchedule(doctorId, params = {}) {
  const { startDate, endDate, status, type } = params

  return request({
    url: `/doctor/doctors/${doctorId}/schedules`,
    method: 'get',
    params: removeUndefined({
      start_date: formatDateValue(startDate),
      end_date: formatDateValue(endDate),
      status,
      shift: type
    })
  }).then((res) => {
    const data = res?.data || {}
    const schedules = (data.schedules || data.list || []).map(normalizeSchedule)
    const doctor = data.doctor ? normalizeDoctorBase(data.doctor) : null

    return {
      ...res,
      data: {
        ...data,
        doctor,
        schedules,
        items: schedules,
        list: schedules,
        total: data.total ?? schedules.length
      }
    }
  })
}

// 创建排班
export function createSchedule(doctorId, data) {
  return request({
    url: '/doctor/schedules',
    method: 'post',
    data: buildSchedulePayload(doctorId, data)
  }).then((res) => ({
    ...res,
    data: normalizeSchedule(res?.data)
  }))
}

// 更新排班
export function updateSchedule(doctorId, scheduleId, data) {
  const payload = buildSchedulePayload(doctorId, data)
  if (!doctorId) {
    delete payload.doctor_id
  }

  return request({
    url: `/doctor/schedules/${scheduleId}`,
    method: 'put',
    data: payload
  }).then((res) => ({
    ...res,
    data: normalizeSchedule(res?.data)
  }))
}

// 删除排班
export function deleteSchedule(doctorId, scheduleId) {
  return request({
    url: `/doctor/schedules/${scheduleId}`,
    method: 'delete'
  })
}

// 按科室和日期范围获取排班总览
export function getDepartmentSchedules(params = {}) {
  const {
    department,
    startDate,
    endDate,
    shift,
    status = 'available'
  } = params

  return request({
    url: '/doctor/schedules/overview',
    method: 'get',
    params: removeUndefined({
      department,
      start_date: formatDateValue(startDate),
      end_date: formatDateValue(endDate),
      shift,
      status
    })
  }).then((res) => {
    const data = res?.data || {}
    const rawList = data.list || data.items || []
    const list = rawList.map((item) => {
      const schedule = normalizeSchedule(item)
      return {
        ...schedule,
        department: item.department || item.doctor_department || item.department_name
      }
    })

    return {
      ...res,
      data: {
        ...data,
        list,
        items: list,
        total: data.total ?? list.length
      }
    }
  })
}

// 获取请假列表
export function getLeaveList(params = {}) {
  const {
    page = 1,
    pageSize = 10,
    doctorId,
    status,
    leaveType,
    startDate,
    endDate
  } = params

  return request({
    url: '/doctor/leaves',
    method: 'get',
    params: removeUndefined({
      page,
      per_page: pageSize,
      doctor_id: doctorId,
      status,
      leave_type: leaveType,
      start_date: formatDateValue(startDate),
      end_date: formatDateValue(endDate)
    })
  }).then((res) => {
    const data = res?.data || {}
    const list = (data.list || data.items || []).map(normalizeLeave)

    return {
      ...res,
      data: {
        ...data,
        list,
        items: list
      }
    }
  })
}

// 获取指定医生的请假记录
export function getDoctorLeaves(doctorId, params = {}) {
  const { status, startDate, endDate } = params

  return request({
    url: `/doctor/doctors/${doctorId}/leaves`,
    method: 'get',
    params: removeUndefined({
      status,
      start_date: formatDateValue(startDate),
      end_date: formatDateValue(endDate)
    })
  }).then((res) => {
    const data = res?.data || {}
    const leaves = (data.leaves || data.list || data.items || []).map(normalizeLeave)
    const doctor = data.doctor ? normalizeDoctorBase(data.doctor) : null

    return {
      ...res,
      data: {
        ...data,
        doctor,
        leaves,
        list: leaves,
        items: leaves,
        total: data.total ?? leaves.length
      }
    }
  })
}

// 创建请假申请
export function createLeave(data) {
  return request({
    url: '/doctor/leaves',
    method: 'post',
    data: buildLeavePayload(data)
  }).then((res) => ({
    ...res,
    data: normalizeLeave(res?.data)
  }))
}

// 更新请假申请
export function updateLeave(id, data) {
  return request({
    url: `/doctor/leaves/${id}`,
    method: 'put',
    data: buildLeavePayload(data)
  }).then((res) => ({
    ...res,
    data: normalizeLeave(res?.data)
  }))
}

// 删除请假记录
export function deleteLeave(id) {
  return request({
    url: `/doctor/leaves/${id}`,
    method: 'delete'
  })
}

// 审批通过请假
export function approveLeave(id, data = {}) {
  const payload = removeUndefined({
    approver_id: data.approverId,
    approval_notes: data.approvalNotes
  })

  return request({
    url: `/doctor/leaves/${id}/approve`,
    method: 'put',
    data: payload
  }).then((res) => ({
    ...res,
    data: normalizeLeave(res?.data)
  }))
}

// 审批拒绝请假
export function rejectLeave(id, data = {}) {
  const payload = removeUndefined({
    approver_id: data.approverId,
    approval_notes: data.approvalNotes
  })

  return request({
    url: `/doctor/leaves/${id}/reject`,
    method: 'put',
    data: payload
  }).then((res) => ({
    ...res,
    data: normalizeLeave(res?.data)
  }))
}

// 获取用药申请列表（按条件分页）
export function getMedicationRequestList(params = {}) {
  const {
    page = 1,
    pageSize = 10,
    doctorId,
    patientId,
    status
  } = params

  return request({
    url: '/doctor/medication-requests',
    method: 'get',
    params: removeUndefined({
      page,
      per_page: pageSize,
      doctor_id: doctorId,
      patient_id: patientId,
      status
    })
  }).then((res) => {
    const data = res?.data || {}
    const list = (data.items || data.list || []).map(normalizeMedicationRequest)

    return {
      ...res,
      data: {
        ...data,
        list,
        items: list,
        total: data.total ?? list.length
      }
    }
  })
}

// 获取指定医生的用药申请列表
export function getDoctorMedicationRequests(doctorId, params = {}) {
  const { status, patientId } = params

  return request({
    url: `/doctor/doctors/${doctorId}/medication-requests`,
    method: 'get',
    params: removeUndefined({
      status,
      patient_id: patientId
    })
  }).then((res) => {
    const data = res?.data || {}
    const list = (data.requests || data.list || data.items || []).map(normalizeMedicationRequest)
    const doctor = data.doctor ? normalizeDoctorBase(data.doctor) : null

    return {
      ...res,
      data: {
        ...data,
        doctor,
        list,
        items: list,
        total: data.total ?? list.length
      }
    }
  })
}

// 创建用药申请
export function createMedicationRequest(data) {
  return request({
    url: '/doctor/medication-requests',
    method: 'post',
    data: buildMedicationRequestPayload(data)
  }).then((res) => ({
    ...res,
    data: normalizeMedicationRequest(res?.data)
  }))
}

// 获取医生绩效
export function getDoctorPerformance(doctorId, params = {}) {
  const { year, month } = params

  return request({
    url: `/doctor/doctors/${doctorId}/performances`,
    method: 'get',
    params: removeUndefined({ year, month })
  }).then((res) => {
    const data = res?.data || {}
    const performances = (data.performances || data.list || []).map(normalizePerformanceRecord)
    const statistics = normalizePerformanceStatistics(data.statistics || {})
    const doctor = data.doctor ? normalizeDoctorBase(data.doctor) : null

    return {
      ...res,
      data: {
        ...data,
        doctor,
        performances,
        statistics,
        items: performances,
        list: performances,
        total: data.total ?? performances.length
      }
    }
  })
}

// 获取指定医生的病历列表
export function getDoctorMedicalRecords(doctorId, params = {}) {
  const {
    page = 1,
    pageSize = 10,
    patientId
  } = params

  return request({
    url: `/doctor/doctors/${doctorId}/medical-records`,
    method: 'get',
    params: removeUndefined({
      page,
      per_page: pageSize,
      patient_id: patientId
    })
  }).then((res) => {
    const data = res?.data || {}
    const items = (data.items || data.records || []).map(normalizeMedicalRecord)

    return {
      ...res,
      data: {
        ...data,
        items,
        records: items,
        total: data.total ?? items.length
      }
    }
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

// 获取医生关联的病人列表（基于预约和病历）
export function getDoctorPatients(doctorId) {
  return request({
    url: `/doctor/doctors/${doctorId}/patients`,
    method: 'get'
  }).then((res) => {
    const data = res?.data || {}
    return {
      ...res,
      data: {
        doctor: data.doctor || null,
        patients: data.patients || [],
        total: data.total || 0
      }
    }
  })
}

