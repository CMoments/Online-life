import request from './request';

export function getProfile() {
  return request.get('/api/user/profile');
}

export function updateProfile(data) {
  return request.put('/api/user/profile', data);
}

export function changePassword(data) {
  return request.post('/api/user/change-password', data);
}

export function getReputation() {
  return request.get('/api/user/reputation');
}

export function addReputation(data) {
  return request.post('/api/user/reputation', data);
}

export function getUserList(params) {
  return request.get('/api/user/list', { params });
}

// 验证JWT令牌是否有效
export function verifyToken() {
  return request.post('/api/auth/verify-token');
}

export function getPoints() {
  return request.get('/api/user/points');
}

export function addOrderReputation(orderId, data) {
  return request({
    url: `/api/user/order-reputation/${orderId}`,
    method: 'post',
    data
  });
}

export function getOrderReputation(orderId) {
  return request({
    url: `/api/user/order-reputation/${orderId}`,
    method: 'get'
  });
}