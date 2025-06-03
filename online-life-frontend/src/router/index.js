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
import CreateOrder from '@/views/CreateOrder.vue';
import AvailableOrderList from '@/views/AvailableOrderList.vue'; // Staff可接单列表
import StaffAvailableGroupTask from '@/views/StaffAvailableGroupTask.vue';
import CreateGroupTask from '@/views/CreateGroupTask.vue';
import MyGroupTasks from '@/views/MyGroupTasks.vue';
import MyBidRecords from '@/views/MyBidRecords.vue';
import Developers from '@/views/Developers.vue';


const routes = [
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/', component: Dashboard },
  { path: '/profile', component: UserProfile },
  { path: '/orders', component: OrderList }, // 普通用户订单列表
  { 
    path: '/orders/:orderId', 
    name: 'OrderDetail',
    component: OrderDetail 
  },
  { 
    path: '/payment/:orderId', 
    name: 'OrderPayment',
    component: OrderDetail  // 使用相同的组件，通过路由参数区分
  },
  { path: '/available-orders', component: AvailableOrderList }, // Staff可接单列表
  { path: '/tasks', component: TaskList },
  { path: '/tasks/:id', component: TaskDetail },
  { path: '/points', component: Points },
  { path: '/reputation', component: Reputation },
  { path: '/users', component: UserList },
  { path: '/developers', component: Developers },
  {
    path: '/create-order',
    name: 'CreateOrder',
    component: CreateOrder
  },
  { path: '/staff/group-tasks', component: StaffAvailableGroupTask },
  { path: '/create-group-task', component: CreateGroupTask },
  { path: '/my-group-tasks', component: MyGroupTasks },
  { path: '/my-bid-records', component: MyBidRecords },
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

  // 未登录用户只能访问登录和注册页面
  if (to.path !== '/login' && to.path !== '/register' && !token) {
    next('/login');
    return;
  }

  // 已登录用户不能访问登录和注册页面
  if ((to.path === '/login' || to.path === '/register') && token) {
    next('/');
    return;
  }

  // 权限控制
  const adminOnlyPaths = ['/users', '/developers'];
  if (adminOnlyPaths.includes(to.path) && role !== 'admin') {
    next('/');
    return;
  }

  // 其他情况正常通过
  next();
});

const payOrderHandler = async () => {
  try {
    const res = await payOrder(order_id);
    if (res.data.success) {
      ElMessage.success('支付成功');
      // 刷新订单详情
    } else {
      ElMessage.error(res.data.message || '支付失败');
    }
  } catch (e) {
    ElMessage.error('支付失败');
  }
};

export default router;