import request from './request';

export function getGroupTasks(params) {
  return request.get('/api/task/group/list', { params });
}

export function getGroupTaskDetail(groupTaskId) {
  return request.get(`/api/task/group/${groupTaskId}`);
}

export function joinGroupTask(groupTaskId) {
  return request.post(`/api/task/group/${groupTaskId}/join`);
}

export function leaveGroupTask(groupTaskId) {
  return request.post(`/api/task/group/${groupTaskId}/leave`);
}

export function getMyGroupTasks(params) {
  return request.get('/api/task/group/my', { params });
}

export function bidTask(taskId, data) {
  return request.post(`/api/task/bid/${taskId}`, data);
}

export function getMyBids(params) {
  return request.get('/api/task/bid/my', { params });
}

export function acceptBid(taskId, bidId) {
  return request.post(`/api/task/${taskId}/accept-bid/${bidId}`);
}

export function getStaffAvailableTasks(params) {
  return request.get('/api/task/staff/available', { params });
}

export function bidStaffTask(taskId) {
  return request.post(`/api/task/staff/${taskId}/bid`);
}

export function createGroupTask(data) {
  return request.post('/api/task/group/create', data);
}