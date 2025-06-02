import request from './request';

// 创建订单
export function createOrder(data) {
  return request.post('/api/order/create', data);
}

export function getOrderList(params) {
  return request.get('/api/order/list', { params });
}

// 获取订单详情
export function getOrderDetail(orderId) {
  return request.get(`/api/order/${orderId}`)
}

export function cancelOrder(orderId) {
  return request.post('/api/order/cancel', { order_id: orderId })
}

export function completeOrder(orderId) {
  return request.post(`/api/order/${orderId}/complete`)
}

export function processPayment(orderId, paymentData) {
  return request.post(`/api/order/payment/${orderId}`, paymentData)
}

export function getOrderPointsInfo(orderId) {
  return request.get(`/api/order/payment/${orderId}/points-info`)
}

export function getAvailableOrders(params) {
  return request.get('/api/order/available', { params });
}

// 接受订单
export function acceptOrder(orderId) {
  return request.post(`/api/order/accept/${orderId}`)
}

// 获取我的订单
export function getMyOrders(params) {
  return request.get('/api/order/staff/all', { params })
}

// 评价订单（评论客户或代办服务）
export function reviewOrder(orderId, rating, comment) {
  return request.post('/api/order/review', { order_id: orderId, rating, comment })
}

export function getStaffAllOrders(params) {
  return request({
    url: '/api/order/staff/all',
    method: 'get',
    params
  });
}

// 获取已完成订单
export function getStaffCompletedOrders() {
  return request.get('/api/order/staff/all', { 
    params: { 
      status: 'completed'
    }
  });
}

// 获取已支付订单
export function getStaffPaidOrders() {
  return request.get('/api/order/staff/all', { 
    params: { 
      status: 'paid'
    }
  });
}