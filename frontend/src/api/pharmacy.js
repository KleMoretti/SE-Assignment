import request from './request'

export function getMedicineList(params) {
  return request({
    url: '/pharmacy/medicines',
    method: 'get',
    params
  })
}

export function getMedicineDetail(id) {
  return request({
    url: `/pharmacy/medicines/${id}`,
    method: 'get'
  })
}

export function createMedicine(data) {
  return request({
    url: '/pharmacy/medicines',
    method: 'post',
    data
  })
}

export function updateMedicine(id, data) {
  return request({
    url: `/pharmacy/medicines/${id}`,
    method: 'put',
    data
  })
}

export function deleteMedicine(id) {
  return request({
    url: `/pharmacy/medicines/${id}`,
    method: 'delete'
  })
}
