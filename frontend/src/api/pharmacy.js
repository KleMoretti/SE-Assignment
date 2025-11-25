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

export function getMedicationRequestList(params) {
  return request({
    url: '/pharmacy/medication-requests',
    method: 'get',
    params
  })
}

export function approveMedicationRequest(id) {
  return request({
    url: `/pharmacy/medication-requests/${id}/approve`,
    method: 'post'
  })
}

export function rejectMedicationRequest(id, data) {
  return request({
    url: `/pharmacy/medication-requests/${id}/reject`,
    method: 'post',
    data
  })
}

export function getPurchaseOrderList(params) {
  return request({
    url: '/pharmacy/purchase-orders',
    method: 'get',
    params
  })
}

export function createPurchaseOrder(data) {
  return request({
    url: '/pharmacy/purchase-orders',
    method: 'post',
    data
  })
}

export function getPurchaseOrderDetail(id) {
  return request({
    url: `/pharmacy/purchase-orders/${id}`,
    method: 'get'
  })
}

export function receivePurchaseOrder(id, data) {
  return request({
    url: `/pharmacy/purchase-orders/${id}/receive`,
    method: 'post',
    data
  })
}
