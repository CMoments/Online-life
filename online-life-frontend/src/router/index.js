import { createRouter, createWebHistory } from 'vue-router';
import Login from '@/views/Login.vue';
import Register from '@/views/Register.vue';
import Dashboard from '@/views/Dashboard.vue';
import UserProfile from '@/views/UserProfile.vue';
import OrderList from '@/views/OrderList.vue';
import OrderDetail from '@/views/OrderDetail.vue';
import TaskList from '@/views/TaskList.vue';
import TaskDetail from '@/views/TaskDetail.vue';
import Points from '@/views/Points.vue';
import Reputation from '@/views/Reputation.vue';
import UserList from '@/views/UserList.vue';
import NotFound from '@/views/NotFound.vue';

const routes = [
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/', component: Dashboard },
  { path: '/profile', component: UserProfile },
  { path: '/orders', component: OrderList },
  { path: '/orders/:id', component: OrderDetail },
  { path: '/tasks', component: TaskList },
  { path: '/tasks/:id', component: TaskDetail },
  { path: '/points', component: Points },
  { path: '/reputation', component: Reputation },
  { path: '/users', component: UserList },
  { path: '/:pathMatch(.*)*', component: NotFound }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 全局前置守卫：未登录强制跳转到登录页
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');
  console.log('当前用户token:', token, '当前用户role:', role);

  if (to.path !== '/login' && to.path !== '/register' && !token) {
    next('/login');
  } else if ((to.path === '/login' || to.path === '/register') && token) {
    next('/');
  } else {
    next();
  }
});

export default router;