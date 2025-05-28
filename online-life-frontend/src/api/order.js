import request from './request';

export function createOrder(data) {
  return request.post('/api/order/create', data);
}

export function getOrderList(params) {
  return request.get('/api/order/list', { params });
}

export function getOrderDetail(orderId) {
  return request.get(`/api/order/${orderId}`);
}

export function cancelOrder(orderId) {
  return request.post(`/api/order/${orderId}/cancel`);
}

export function completeOrder(orderId) {
  return request.post(`/api/order/${orderId}/complete`);
}

export function processPayment(orderId, data) {
  return request.post(`/api/order/payment/${orderId}`, data);
}

export function getAvailableOrders(params) {
  return request.get('/api/order/available', { params });
}