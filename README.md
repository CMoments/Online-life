Collecting workspace information# Online Life 网上代办系统部署与使用说明

## 一、项目简介

本项目为“网上代办系统”，包含前端（Vue3 + Element Plus）和后端（Flask + SQLAlchemy + MySQL）。实现了用户注册、登录、订单管理、任务管理、积分、信誉等功能，适合初学者学习全栈开发。

---

## 二、项目结构说明

```
online-life-backend/      # 后端服务目录
    app.py                # Flask应用入口
    config.py             # 配置文件（数据库等）
    models.py             # 数据库ORM模型
    api/                  # 各功能API蓝图
    utils/                # 工具类（如数据库、鉴权、业务逻辑）
    requirements.txt      # Python依赖
online-life-frontend/     # 前端项目目录
    src/                  # 前端源码
        views/            # 页面组件
        api/              # 前端API请求封装
    package.json          # 前端依赖
    vite.config.js        # 构建配置
```

---

## 三、部署与运行步骤

### 1. 环境准备

- Python 3.8+、Node.js 16+、MySQL 5.7/8.0
- 推荐使用虚拟环境（如 venv）
#### Conda 虚拟环境导入
项目目录下有environment.yml文件，记录了项目环境的所有依赖，运行项目：
先加载环境配置文件。
1. **导入环境**
   ```sh
   conda env create -f environment.yml
   ```

2. **激活环境**
   ```sh
   conda activate online
   ```

3. **后续操作**
   - 进入 `online-life-backend` 目录，继续后端部署步骤。


### 2. 后端部署

1. **安装依赖**

   ```sh
   cd online-life-backend
   pip install -r requirements.txt
   ```

2. **配置数据库**

   <!-- - 修改 `config.py`，填写你的 MySQL 账号、密码、数据库名等信息。
   - 初始化数据库（如需建表）：

     ```sh
     python init_db.py
     ``` -->

3. **启动后端服务**

   ```sh
   python app.py
   ```

   默认监听 `http://localhost:5000`。

### 3. 前端部署

1. **安装依赖**

   ```sh
   cd online-life-frontend
   npm install
   ```

2. **启动前端开发服务器**

   ```sh
   npm run dev
   ```

   默认访问 `http://localhost:5173`。

---

## 四、功能与调用关系

### 1. 用户注册与登录

- 前端页面：Register.vue、Login.vue
- 前端API：`src/api/auth.js`
- 后端接口：`/api/auth/register`、`/api/auth/login`（见 api/auth_api.py）

### 2. 订单与任务管理

- 订单相关页面：OrderList.vue、OrderDetail.vue
- 任务相关页面：TaskList.vue、TaskDetail.vue
- 前端API：order.js、`src/api/task.js`
- 后端接口：`/api/order/*`、`/api/task/*`（见 api/order_api.py、api/task_api.py）

### 3. 积分与信誉

- 页面：Points.vue、Reputation.vue
- 前端API：`src/api/points.js`、user.js
- 后端接口：`/api/points/*`、`/api/user/reputation`（见 api/points_api.py、api/user_api.py）

---

## 五、前后端交互原理

1. **鉴权机制**  
   - 用户登录后，后端返回 JWT token，前端保存到 `localStorage`。
   - 前端每次请求自动携带 `Authorization: Bearer <token>`，后端校验。

2. **路由与权限**  
   - 前端路由守卫（index.js）控制未登录用户只能访问登录/注册页。
   - 不同角色（admin/client/staff）有不同的菜单和功能权限。

3. **数据流动**  
   - 前端通过 API 封装（如 order.js）请求后端，后端返回 JSON 数据，前端渲染页面。
   - 典型流程：注册/登录 → 进入主页 → 下单/接单/参加任务 → 完成任务/订单 → 信誉评价/积分奖励。

---

## 六、常见问题

- **数据库连接失败**：检查 `config.py` 数据库配置，确保 MySQL 已启动且有对应数据库。
- **跨域问题**：后端已启用 CORS，若仍有问题请检查前端 `vite.config.js` 的代理设置。
- **依赖安装失败**：确保 Python、Node.js 版本符合要求，使用国内镜像可加速安装。

---

## 七、了解项目

- 推荐先从注册/登录流程入手，理解 token 鉴权与前后端交互。
- 阅读 `api/` 和 `utils/` 目录下的后端业务逻辑，结合前端页面理解数据流。
- 可尝试扩展功能，如增加更多角色、完善订单/任务流程等。

---

