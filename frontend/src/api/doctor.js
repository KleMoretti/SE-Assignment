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
      start_date: startDate,
      end_date: endDate,
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

