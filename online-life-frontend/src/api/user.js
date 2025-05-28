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