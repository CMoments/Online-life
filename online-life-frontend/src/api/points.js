import request from './request';

export function getPointsBalance() {
  return request.get('/api/points/balance');
}

export function addPoints(data) {
  return request.post('/api/points/add', data);
}

export function deductPoints(data) {
  return request.post('/api/points/deduct', data);
}

export function getPointsHistory(params) {
  return request.get('/api/points/history', { params });
}

export function transferPoints(data) {
  return request.post('/api/points/transfer', data);
}

export function getPointsRanking(params) {
  return request.get('/api/points/ranking', { params });
}