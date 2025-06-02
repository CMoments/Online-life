import axios from 'axios';

const request = axios.create({
  baseURL: 'http://localhost:5000', // 后端地址
  timeout: 5000,
});

request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

export default request;