# 用户认证 API 文档

## api文档返回值可能有错，以实际返回内容为准

## 1. 用户注册

- **URL**：`POST /api/auth/register`
- **功能**：注册新用户（支持 `admin`、`client`、`staff` 三种角色）

### 🔸 请求参数（JSON）

|参数名|类型|必填|说明|
|:-:|:-:|:-:|:-:|
|username|string|是|用户名|
|password|string|是|密码（明文）|
|email|string|是|邮箱地址|
|phone|string|是|电话号码|
|address|string|是|地址|
|role|string|是|用户角色：`admin` / `client` / `staff`|
|adlevel|string|否|管理员等级，仅 admin 用|
|salary|string|否|员工薪资，仅 staff 用|

### ✅ 成功响应

```json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "user_id": "123456",
    "username": "test_user",
    "role": "client"
  },
  "timestamp": "2023-10-05T14:30:45.123456"
}
```
### ❌ 失败响应示例

- 缺少字段：

```json
{
  "code": 400,
  "message": "缺少必填字段: username"
}
```

- 用户名或邮箱已存在：

```json
{
  "code": 400,
  "message": "用户名已存在"
}
```

----

## 2. 用户登录

- **URL**：`POST /api/auth/login`
- **功能**：用户登录，验证身份并返回 JWT 令牌

### 🔸 请求参数（JSON）

|参数名|类型|必填|说明|
|:-:|:-:|:-:|:-:|
|username|string|是|用户名|
|password|string|是|密码|

### ✅ 成功响应

```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGci...",
    "user_id": "123456",
    "username": "test_user",
    "role": "client",
    "email": "user@example.com"
  },
  "timestamp": "2023-10-05T14:30:45.123456"
}
```
### ❌ 失败响应

```json
{
  "code": 401,
  "message": "用户名或密码错误"
}
```

----

## 3. 用户登出

- **URL**：`POST /api/auth/logout`
- **功能**：用户登出（当前仅模拟，未加入 token 黑名单）

### 🔸 请求参数

无

### ✅ 成功响应

```json
{
  "code": 200,
  "message": "登出成功",
  "data": {},
  "timestamp": "2023-10-05T14:30:45.123456"
}
```

----

## 4. 验证令牌

- **URL**：`POST /api/auth/verify-token`
- **功能**：验证 JWT 令牌是否有效

### 🔸 请求头

|Header名称|是否必填|说明|
|:-:|:-:|:-:|
|Authorization|是|`Bearer <token>` 格式传递|

### ✅ 成功响应

```json
{
  "code": 200,
  "message": "令牌验证成功",
  "data": {
    "user_id": "123456",
    "role": "admin",
    "exp": 1716787200,
    "iat": 1716783600
  },
  "timestamp": "2023-10-05T14:30:45.123456"
}
```
### ❌ 失败响应

```json
{
  "code": 401,
  "message": "缺少认证令牌"
}
```

或

```json
{
  "code": 401,
  "message": "无效的认证令牌"
}
```

# 订单模块 API 文档

>所有接口均挂载在 `/order` 路由下。请求需携带 `Authorization: Bearer <token>` 头部完成身份验证。

### 流程：用户创建订单->(查询，取消订单)->员工接单->员工完成订单->用户查询可以用于支付的积分->用户支付订单->提醒用户评价订单（信誉积分评价）

----

## 📝 1. 创建订单

- **URL**：`POST /api/order/create`
- **功能**：用户创建订单

### 🔸 请求参数（JSON）

|参数名|类型|是否必填|说明|
|:-:|:-:|:-:|:-:|
|order_type|string|是|订单类型，二选一"immediate", "scheduled"|
|description|string|是|订单描述|
|orderlocation|string|是|订单指定位置（必须是具体地址）|

### ✅ 成功响应

```json
{
    "data": {
        "delivery_fee": 6.75,
        "estimated_time": 45,
        "order_id": "1748491837027703"
    },
    "message": "订单创建成功",
    "success": true,
    "timestamp": "2025-05-29T12:10:38.138043"
}
```

----

## 📋 2. 获取订单列表

- **URL**：`GET /api/order/list`
- **功能**：获取当前用户的订单列表

### 🔸 查询参数

|参数名|类型|是否必填|说明|
|:-:|:-:|:-:|:-:|
|page|int|否|页码，默认 1|
|per_page|int|否|每页数量，默认 10|
|status|string|否|订单状态（可选筛选）|
|order_type|string|否|订单类型（可选筛选）|

### ✅ 成功响应

- "assignment_type": 分配方式：bidding竞价, direct直接
- "assignment_status": 分配状态：open开放, assigned已分配, closed已关闭

```json
{
    "data": {
        "orders": [
            {
                "assignment_status": "open",
                "assignment_type": "direct",
                "completion_time": "",
                "creation_time": "2025-05-29 12:10:37",
                "order_id": "1748491837027703",
                "order_location": "四川大学江安校区法学院",
                "order_status": "pending",
                "order_type": "immediate"
            },
            {
                "assignment_status": "closed",
                "assignment_type": "direct",
                "completion_time": "",
                "creation_time": "2025-05-29 11:02:25",
                "order_id": "1748487745413673",
                "order_location": "四川省成都市双流区麦当劳（长城路二段餐厅）",
                "order_status": "cancelled",
                "order_type": "immediate"
            },
            {
                "assignment_status": "open",
                "assignment_type": "direct",
                "completion_time": "",
                "creation_time": "2025-05-29 10:14:48",
                "order_id": "1748484888200098",
                "order_location": "四川大学江安校区南门",
                "order_status": "pending",
                "order_type": "immediate"
            },
            {
                "assignment_status": "closed",
                "assignment_type": "direct",
                "completion_time": "",
                "creation_time": "2025-05-29 10:14:18",
                "order_id": "1748484858449134",
                "order_location": "四川大学江安校区法学院",
                "order_status": "cancelled",
                "order_type": "immediate"
            },
            {
                "assignment_status": "closed",
                "assignment_type": "direct",
                "completion_time": "",
                "creation_time": "2025-05-28 23:05:37",
                "order_id": "1748444737651029",
                "order_location": "四川大学望江校区地铁站",
                "order_status": "cancelled",
                "order_type": "immediate"
            }
        ],
        "pagination": {
            "current_page": 1,
            "per_page": 10,
            "total": 5,
            "total_pages": 1
        }
    },
    "message": "获取订单列表成功",
    "success": true,
    "timestamp": "2025-05-29T12:43:39.948807"
}
```

----

## 📄 3. 获取订单详情

- **URL**：`GET /api/order/<order_id>`
- **功能**：查看某个订单的详细信息

### ✅ 成功响应

```json
{
    "data": {
        "assignment_status": "open",
        "assignment_type": "direct",
        "completion_time": "",
        "creation_time": "2025-05-29 12:10:37",
        "order_id": "1748491837027703",
        "order_location": "四川大学江安校区法学院",
        "order_status": "pending",
        "order_type": "immediate",
        "user_id": "1748434864506324",
        "user_name": "testclient"
    },
    "message": "获取订单详情成功",
    "success": true,
    "timestamp": "2025-05-29T12:44:56.395455"
}
```
### ❌ 错误示例

```json
{
  "code": 404,
  "message": "订单不存在或无权访问"
}
```

----

## ❌ 4. 取消订单

- **URL**：`POST /api/order/<order_id>/cancel`
- **功能**：取消指定订单

### ✅ 成功响应

```json
{
  "code": 200,
  "message": "订单已取消",
  "data": {},
  "timestamp": "2023-10-05T14:30:45.123456"
}
```

----

## ✅ 5. 完成订单

- **URL**：`POST /api/order/<order_id>/complete`
- **功能**：标记订单为已完成

### ✅ 成功响应

```json
{
    "data": {
        "can_review": true,
        "message": "订单已完成",
        "order_id": "1748516532599265",
        "review_target": {
            "role": "staff",
            "user_id": "1748498150567521"
        }
    },
    "message": "订单已完成，您可以对代办人员进行评价",
    "success": true,
    "timestamp": "2025-05-29T19:07:31.215665"
}
```

----
## 💳 6. 查询积分

- **URL**：`GET /api/order/payment/<order_id>/points-info`
- **功能**：用户为查询积分


### ✅ 成功响应

```json
{
    "data": {
        "available_points": 0,
        "can_fully_pay_with_points": false,
        "current_reputation": 0.0,
        "max_deductible_amount": 0.0,
        "max_points_can_use": 0,
        "order_amount": 0.0,
        "order_id": "1748516532599265",
        "points_payment_available": false,
        "reason": "用户信誉度不足（当前: 0.0，要求: ≥80.0），不支持积分支付",
        "required_reputation": 80.0
    },
    "message": "订单积分信息查询成功",
    "success": true,
    "timestamp": "2025-05-29T20:03:12.327367"
}
```

### 错误响应

```json
{
  "code": 500,
  "message": "支付失败"
}
```

----

## 💳 7. 支付订单

- **URL**：`POST /api/order/payment/<order_id>`
- **功能**：用户为订单进行支付

### 🔸 请求参数（JSON）

|参数名|类型|是否必填|说明|
|:-:|:-:|:-:|:-:|
|payment_method|string|是|支付方式|
|amount|number|是|支付金额|

payment_method: ["alipay", "wechat", "bank_card", "points"]

### ✅ 成功响应

```json
{
    "data": {
        "cash_payment": 1.0,
        "order_id": "1748516532599265",
        "paid_at": "2025-05-29 19:58:34",
        "payment_id": "PAY_1748519914",
        "payment_method": "alipay",
        "points_deduction_amount": 0.0,
        "points_earned": 100,
        "points_earned_reason": "现金支付1元获得100积分",
        "points_used": 0,
        "status": "success",
        "total_amount": 1.0
    },
    "message": "支付成功",
    "success": true,
    "timestamp": "2025-05-29T19:58:35.020852"
}
```

### 错误响应

```json
{
  "code": 500,
  "message": "支付失败"
}
```

----

## 📦 8. 获取可接单列表（限 staff）

- **URL**：`GET /api/order/available`

- **功能**：供员工查看尚未被接取的订单任务

### 🔸 查询参数

|参数名|类型|是否必填|说明|
|:-:|:-:|:-:|:-:|
|page|int|否|页码，默认 1|
|per_page|int|否|每页数量，默认 10|
|task_type|string|否|筛选任务类型|

### ✅ 成功响应

```json
{
    "data": {
        "orders": [
            {
                "assignment_type": "direct",
                "client_address": "四川大学江安校区南门",
                "client_name": "testclient",
                "creation_time": "2025-05-29 10:14:48",
                "order_id": "1748484888200098",
                "order_location": "四川大学江安校区南门",
                "order_type": "immediate"
            }
        ],
        "pagination": {
            "current_page": 1,
            "per_page": 10,
            "total": 1,
            "total_pages": 1
        }
    },
    "message": "获取可接单列表成功",
    "success": true,
    "timestamp": "2025-05-29T19:57:10.179930"
}
```
### ❌ 权限不足示例

```json
{
  "code": 403,
  "message": "权限不足"
}
```

----

## 🔐 通用身份认证

- 所有接口均需在请求头中添加以下认证信息：

```makefile
Authorization: Bearer <JWT令牌>
```

# 积分模块 API 文档


>所有接口挂载在 `/points` 路由下。除排行榜外，所有接口需携带 `Authorization: Bearer <token>` 头部用于身份验证。


----

## 📊 1. 获取积分余额

- **URL**：`GET /api/points/balance`
- **功能**：获取当前用户积分余额

### ✅ 成功响应


```json
{
  "code": 200,
  "message": "获取积分余额成功",
  "data": {
    "user_id": "123456789",
    "points_balance": 1000
  },
  "timestamp": "2023-10-05T14:30:45.123456"
}
```

----

## ➕ 2. 增加积分 （前端不用这个，已经写到后端）

- **URL**：`POST /api/points/add`
- **功能**：为当前用户增加积分

### 🔸 请求参数（JSON）

|参数名|类型|是否必填|说明|
|:-:|:-:|:-:|:-:|
|points|int|是|增加的积分|
|reason|string|是|原因说明|


### ✅ 成功响应


```json
{
  "code": 200,
  "message": "积分添加成功",
  "data": {},
  "timestamp": "2023-10-05T14:30:45.123456"
}
```


----

## ➖ 3. 扣除积分 （前端不用这个，已经写到后端）


- **URL**：`POST /api/points/deduct`

- **功能**：扣除当前用户的积分


### 🔸 请求参数（JSON）


|参数名|类型|是否必填|说明|
|:-:|:-:|:-:|:-:|
|points|int|是|扣除的积分|
|reason|string|是|原因说明|


### ❌ 错误示例


```json
{
  "code": 400,
  "message": "积分余额不足"
}
```


----

## 📜 4. 获取积分历史记录（暂时不要）


- **URL**：`GET /api/points/history`

- **功能**：查看当前用户积分变化记录


### 🔸 查询参数


|参数名|类型|是否必填|说明|
|:-:|:-:|:-:|:-:|
|page|int|否|页码（默认1）|
|per_page|int|否|每页数量（默认20）|


### ✅ 成功响应


```json
{
  "code": 200,
  "message": "获取积分历史成功",
  "data": {
    "records": [...],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 100
    }
  },
  "timestamp": "2023-10-05T14:30:45.123456"
}
```


----

## 🔁 5. 积分转账


- **URL**：`POST /api/points/transfer`

- **功能**：将积分转账给其他用户


### 🔸 请求参数（JSON）


|参数名|类型|是否必填|说明|
|:-:|:-:|:-:|:-:|
|target_user_id|string|是|接收用户 ID|
|points|int|是|转账积分数量|
|message|string|否|备注信息|


### ❌ 错误示例


```json
{
  "code": 400,
  "message": "不能向自己转账"
}
```
### ✅ 成功响应


```json
{
  "code": 200,
  "message": "积分转账成功",
  "data": {},
  "timestamp": "2023-10-05T14:30:45.123456"
}
```


----

## 🏆 6. 获取积分排行榜


- **URL**：`GET /api/points/ranking`
- **功能**：获取全站积分排行榜（无需认证）

### 🔸 查询参数

|参数名|类型|是否必填|说明|
|:-:|:-:|:-:|:-:|
|limit|int|否|返回前几名（默认50）|

### ✅ 成功响应

```json
{
  "code": 200,
  "message": "获取积分排行榜成功",
  "data": [
    {
      "rank": 1,
      "username": "张三",
      "points": 1500
    },
    {
      "rank": 2,
      "username": "李四",
      "points": 1200
    },
    {
      "rank": 3,
      "username": "王五",
      "points": 950
    },
    {
      "rank": 4,
      "username": "刘六",
      "points": 0
    }
  ],
  "timestamp": "2023-10-05T14:30:45.123456"
}
```


----

## 🔐 通用身份认证说明


除排行榜接口外，其他接口都需添加如下请求头完成认证：

```makefile
Authorization: Bearer <JWT令牌>
```

# 任务模块 API 文档


>所有接口挂载在 `/task` 路由下，除特别说明外都需携带请求头：
`Authorization: Bearer <JWT令牌>`

### 流程说明：获取团办任务列表展示->创建一个新的团办任务->其他用户可以加入->满5人自动拼团成功（上限不是5，5人成一个小团）->代办人员参与竞标->满5个代办人员竞标则信誉最高的代办人员自动接单->可以在代办人员的接单记录中看到中标

----

## 📌 团办任务接口

----

### 🔍 获取团办任务列表


- **URL**：`GET /api/task/group/list`

- **描述**：分页获取团办任务列表


#### 查询参数


|参数名|类型|是否必填|说明|
|:-:|:-:|:-:|:-:|
|page|int|否|页码（默认1）|
|per_page|int|否|每页数量（默认10）|
|task_type|string|否|任务类型|
|status|string|否|状态（默认active）|


#### 返回示例


```json
{
  "data": {
    "current_page": 1,
    "per_page": 10,
    "tasks": [
      {
        "bid_deadline": "",
        "current_participants": 1,
        "description": "送外卖",
        "estimated_time": "",
        "group_task_id": "1",
        "join_time": "2025-05-29 13:22:48",
        "max_participants": 5,
        "spots_remaining": 4,
        "status": "recruiting",
        "task_id": "1",
        "task_location": "",
        "task_type": "group"
      }
    ],
    "total_pages": 1,
    "total_records": 1
  },
  "message": "获取可参与团办任务列表成功",
  "success": true,
  "timestamp": "2025-05-29T13:35:13.822041"
}

```
- 401 Unauthorized - Token无效
- 500 Internal Server Error - 服务器错误

----

### 📄 获取团办任务详情

- **URL**：`GET /api/task/group/<group_task_id>`
- **描述**：获取指定团办任务的详细信息

#### 返回示例

```json
{
  "data": {
    "actual_time": "",
    "bid_deadline": "",
    "current_bidder": "",
    "description": "送外卖",
    "end_time": "",
    "estimated_time": "",
    "group_task_id": "1",
    "join_time": "2025-05-29 13:22:48",
    "main_participant_id": "1748434864506324",
    "participant_count": 1,
    "participants": [
      {
        "join_time": "2025-05-29 13:22:48",
        "user_id": "1748434864506324"
      }
    ],
    "status": "active",
    "task_id": "1",
    "task_location": "",
    "task_type": "group"
  },
  "message": "获取团办任务详情成功",
  "success": true,
  "timestamp": "2025-05-29T13:26:45.757031"
}
```
- 401 Unauthorized - Token无效
- 404 Not Found - 任务不存在
- 500 Internal Server Error - 服务器错误

----

### 🔍 获取可参与的团办任务列表

- **URL**：`GET /api/task/group/available`
- **描述**：分页获取用户可参与的团办任务列表

#### 查询参数

|参数名|类型|是否必填|说明|
|:-:|:-:|:-:|:-:|
|page|int|否|页码（默认1）|
|per_page|int|否|每页数量（默认10）|
|task_type|string|否|任务类型|


#### 返回示例


```json
{
  "data": {
    "current_page": 1,
    "per_page": 10,
    "tasks": [
      {
        "bid_deadline": "",
        "current_participants": 1,
        "description": "送外卖",
        "estimated_time": "",
        "group_task_id": "1",
        "join_time": "2025-05-29 13:22:48",
        "max_participants": 5,
        "spots_remaining": 4,
        "status": "recruiting",
        "task_id": "1",
        "task_location": "",
        "task_type": "group"
      }
    ],
    "total_pages": 1,
    "total_records": 1
  },
  "message": "获取可参与团办任务列表成功",
  "success": true,
  "timestamp": "2025-05-29T13:35:13.822041"
}

```
- 401 Unauthorized - Token无效
- 500 Internal Server Error - 服务器错误

----

### ➕ 创建团办任务

- **URL**：`POST /api/task/group/create`
- **描述**：用户报名参与团办任务

### 🔸 请求参数（JSON）

|参数名|类型|是否必填|说明|
|:-:|:-:|:-:|:-:|
|description|string|是|任务描述|
|task_type|int|是|任务类型（默认为group）|
|task_location|string|否|需要代办人员去的位置|

#### 返回示例

```json
{
  "data": {
    "bid_deadline": "",
    "creator_id": "1748434864506324",
    "current_participants": 1,
    "description": "送外卖",
    "estimated_time": "",
    "first_task_id": "1",
    "group_task_id": "1",
    "join_time": "2025-05-29 13:22:48",
    "max_participants": 5,
    "status": "recruiting",
    "task_location": "",
    "task_type": "group"
  },
  "message": "团办 任务创建成功",
  "success": true,
  "timestamp": "2025-05-29T13:22:48.694523"
}
```
- 400 Bad Request - 已经参加/任务已结束
- 401 Unauthorized - Token无效
- 500 Internal Server Error - 服务器错误

----

### ➕ 参加团办任务


- **URL**：`POST /api/task/group/<group_task_id>/join`
- **描述**：用户报名参与团办任务


#### 返回示例


```json
{
  "data": {
    "assigned_task_id": "1",
    "current_participants": 2,
    "group_task_id": "1",
    "max_participants": 5,
    "task_description": "送外卖",
    "task_status": "recruiting"
  },
  "message": "成功加入团办任务",
  "success": true,
  "timestamp": "2025-05-29T13:37:26.894154"
}

{
  "error_code": null,
  "message": "您已经参加了此团办任务",
  "success": false,
  "timestamp": "2025-05-29T13:46:29.282717"
}
```
- 400 Bad Request - 已经参加/任务已结束
- 401 Unauthorized - Token无效
- 500 Internal Server Error - 服务器错误

----

### ➖ 退出团办任务


- **URL**：`POST /api/task/group/<group_task_id>/leave`

- **描述**：用户退出团办任务

#### 请求参数

无

#### 返回示例

```json
{
  "data": {
    "group_task_id": "1",
    "left_tasks": ["1"],
    "status": "success"
  },
  "message": "成功退出团办任务",
  "success": true,
  "timestamp": "2025-05-29T13:38:33.033688"
}
```
- 400 Bad Request - 未参加/任务已结束
- 401 Unauthorized - Token无效
- 500 Internal Server Error - 服务器错误

----

### 👤 获取我参加的团办任务


- **URL**：`GET /api/task/group/my`

- **描述**：获取当前用户参与的团办任务


#### 查询参数


|参数名|类型|是否必填|说明|
|:-:|:-:|:-:|:-:|
|page|int|否|页码（默认1）|
|per_page|int|否|每页数（默认10）|


#### 返回示例


```json
{
  "data": {
    "current_page": 1,
    "per_page": 10,
    "tasks": [
      {
        "actual_time": "",
        "bid_deadline": "",
        "current_bidder": "",
        "description": "送外卖",
        "end_time": "",
        "estimated_time": "",
        "group_task_id": "1",
        "join_time": "2025-05-29 13:22:48",
        "participant_count": 1,
        "status": "active",
        "task_id": "1",
        "task_type": "group"
      }
    ],
    "total_pages": 1,
    "total_records": 1
  },
  "message": "获取我的团办任务成功",
  "success": true,
  "timestamp": "2025-05-29T13:25:07.447139"
}
```

----

### 👤 获取团办任务参与者列表

- **URL**：`GET /api/task/group/<group_task_id>/participants`
- **描述**：获取指定团办任务参与者列表

#### 查询参数

|参数名|类型|是否必填|说明|
|:-:|:-:|:-:|:-:|
|page|int|否|页码（默认1）|
|per_page|int|否|每页数（默认10）|


#### 返回示例


```json
{
  "data": {
    "group_task_id": "1",
    "is_full": false,
    "participant_count": 2,
    "participants": [
      {
        "address": "四川省成都市四川大学江安校区7舍",
        "email": "123@example.com",
        "phone": "18935139705",
        "reputation_count": 0,
        "reputation_score": 0.0,
        "role": "client",
        "user_id": "1748397795518788",
        "username": "client1"
      },
      {
        "address": "四川大学江安校区南门",
        "email": "client@example.com",
        "phone": "9876543210",
        "reputation_count": 0,
        "reputation_score": 0.0,
        "role": "client",
        "user_id": "1748434864506324",
        "username": "testclient"
      }
    ]
  },
  "message": "获取参与者列表成功",
  "success": true,
  "timestamp": "2025-05-29T13:50:57.746156"
}
```

----

## 🧾 竞标任务接口

### 📤 获取可参与竞标的任务（满5人且未竞标成功）

- **URL**：`GET /api/task/staff/available`
- **描述**：员工对某任务进行竞标（仅限 `staff` 角色）

#### 返回示例

```json
{
  "data": {
    "current_page": 1,
    "per_page": 10,
    "tasks": [
      {
        "bid_count": 0,
        "bid_deadline": "2025-06-05 14:18:43",
        "description": "送外卖",
        "estimated_time": "",
        "group_task_id": "1",
        "participants_count": 5,
        "status": "available_for_bidding",
        "task_id": "1",
        "task_location": "",
        "task_type": "group"
      }
    ],
    "total_pages": 1,
    "total_records": 1
  },
  "message": "获取可接取任务列表成功",
  "success": true,
  "timestamp": "2025-05-29T14:22:03.774536"
}
```
- 400 Bad Request - 已竞标过该任务
- 403 Forbidden - 非staff角色
- 404 Not Found - 任务不存在
- 500 Internal Server Error - 服务器错误

----

### 📤 提交竞标


- **URL**：`POST /api/task/staff/<task_id>/bid`
- **描述**：员工对某任务进行竞标（仅限 `staff` 角色）


#### 请求体（JSON）

无

#### 返回示例

```json
{
  "data": {
    "bid_id": "1",
    "bid_time": "2025-05-29 14:26:07",
    "current_bid_count": 1,
    "status": "pending",
    "task_id": "1"
  },
  "message": "竞标成功",
  "success": true,
  "timestamp": "2025-05-29T14:26:07.557235"
}
```
- 400 Bad Request - 已竞标过该任务
- 403 Forbidden - 非staff角色
- 404 Not Found - 任务不存在
- 500 Internal Server Error - 服务器错误

----

### 📑 获取我的竞标记录


- **URL**：`GET /api/task/bid/my`

- **描述**：获取当前用户的竞标记录


#### 查询参数


|参数名|类型|是否必填|说明|
|:-:|:-:|:-:|:-:|
|page|int|否|页码（默认1）|
|per_page|int|否|每页数量（默认10）|
|status|string|否|竞标状态筛选|


#### 返回示例


```json
{
  "data": {
    "bids": [
      {
        "bid_deadline": "2025-06-05 14:18:43",
        "bid_id": "1",
        "bid_status": "accepted",
        "bid_time": "2025-05-29 14:26:07",
        "current_bidder": "1748498150567521",
        "description": "送外卖",
        "estimated_time": "",
        "is_current_bidder": true,
        "task_id": "1",
        "task_type": "group"
      }
    ],
    "current_page": 1,
    "per_page": 10,
    "total_pages": 1,
    "total_records": 1
  },
  "message": "获取竞标记录成功",
  "success": true,
  "timestamp": "2025-05-29T14:42:29.251415"
}
```


----

### ✅ 接受竞标（没有用）


- **URL**：`POST /api/task/<task_id>/accept-bid/<bid_id>`

- **描述**：任务发起者接受指定的竞标


#### 返回示例


```json
{
  "success": true,
  "message": "竞标已接受",
  "data": {},
  "timestamp": "2023-10-05T14:30:45.123456"
}
```

- 400 Bad Request - 无效操作
- 401 Unauthorized - 未授权
- 404 Not Found - 任务/竞标不存在
- 500 Internal Server Error - 服务器错误

----

## 🔐 认证说明


大部分接口需要有效 JWT token，并通过如下请求头传递：

```makefile
Authorization: Bearer <token>
```
仅 `/task/group/list` 和 `/task/group/<id>` 接口暂未支持匿名访问。


# 用户模块 API 接口文档


所有接口均挂载于 `/user` 路由前缀下。除特别说明外，均需携带身份认证令牌：

```makefile
Authorization: Bearer <token>
```


----

## 📘 1. 获取用户资料


- **接口**：`GET /api/user/profile`

- **功能**：获取当前登录用户的详细资料


### 请求头


|参数名|类型|必填|描述|
|:-:|:-:|:-:|:-:|
|Authorization|string|✅|Bearer Token 授权|


### 返回示例


```json
{
  "success": true,
  "message": "获取用户资料成功",
  "data": {
    "user_id": "123456789",
    "username": "张三",
    "email": "test@example.com",
    "phone": "13800138000",
    "address": "北京市朝阳区",
    "role": "client",
    "client_type": None,
    "registration_date": None
  },
  "timestamp": "2023-10-05T14:30:45.123456"
}
```
- 401 Unauthorized - Token无效
- 404 Not Found - 用户不存在
- 500 Internal Server Error - 服务器错误

----

## ✏️ 2. 更新用户资料


- **接口**：`PUT /api/user/profile`

- **功能**：修改当前用户的个人信息


### 请求体示例



```json
{
  "username": "新用户名",
  "email": "new_email@example.com",
  "phone": "13800138001",
  "address": "上海市浦东新区"
}
```
### 返回示例


```json
{
  "success": true,
  "message": "用户资料更新成功",
  "data": {},
  "timestamp": "2023-10-05T14:30:45.123456"
}
```
- 400 Bad Request - 更新失败
- 401 Unauthorized - Token无效
- 500 Internal Server Error - 服务器错误

----

## 🔐 3. 修改密码


- **接口**：`POST /api/user/change-password`

- **功能**：用户修改登录密码


### 请求体字段


|参数名|类型|是否必填|描述|
|:-:|:-:|:-:|:-:|
|old_password|string|✅|原始密码|
|new_password|string|✅|新密码|


### 请求体示例


```json
{
  "old_password": "123456",
  "new_password": "newpass789"
}
```
### 返回示例


```json
{
  "success": true,
  "message": "密码修改成功",
  "data": {},
  "timestamp": "2023-10-05T14:30:45.123456"
}
```
- 400 Bad Request - 原密码错误
- 401 Unauthorized - Token无效
- 500 Internal Server Error - 服务器错误

----

## 🌟 4. 获取信誉信息


- **接口**：`GET /api/user/reputation`

- **功能**：获取当前用户的信誉评分与评价记录


### 返回示例


```json
{
  "success": true,
  "message": "获取信誉信息成功",
  "data": {
    "average_score": 4.6,
    "total_reviews": 5,
    "score_distribution": {
      "5": 3,
      "4": 2
    },
    "recent_reviews": [
      {
        "score": 5.0,
        "review": "很棒的合作！",
        "reviewer": "李四",
        "reviewer_id": "2"
      }
    ]
  },
  "timestamp": "2023-10-05T14:30:45.123456"
}
```


----

## 📝 5. 添加订单相关的信誉评价


- **接口**：`POST /api/user/order-reputation/<order_id>`

- **功能**：对他人用户添加信誉评价

**满分100**

### 请求体字段


|参数名|类型|是否必填|描述|
|:-:|:-:|:-:|:-:|
|target_user_id|string|✅|被评价用户ID|
|score|float|✅|评分（如 80）|
|review|string|✅|评价内容|


### 示例请求体


```json
{
  "target_user_id": "2",
  "score": "4.8",
  "review": "合作顺利，按时完成任务"
}
```
### 返回示例


```json
{
  "success": true,
  "message": "信誉评价添加成功",
  "data": {},
  "timestamp": "2023-10-05T14:30:45.123456"
}
```
- 400 Bad Request - 重复评价/不能评价自己
- 401 Unauthorized - Token无效
- 500 Internal Server Error - 服务器错误

----

## 📝 5. 获取订单相关的评价信息（没写）


- **接口**：`GET /api/user/order-reputation/<order_id>`

- **功能**：获取订单相关的评价信息

满分100

### 返回示例


```json
{

}
```


----

## 🪙 6. 获取用户积分（不用这里的，在points中）


- **接口**：`GET /api/user/points`
- **功能**：获取当前登录用户的积分信息

**points_history不用考虑**

### 返回示例


```json
{
  "success": true,
  "message": "获取积分信息成功",
  "data": {
    "total_points": 120,
    "available_points": 120, // 就是总积分
    "used_points": 20,
    "points_history": [  // 不用考虑
      {
        "points": 20,
        "type": "任务奖励",
        "description": "完成任务A",
        "date": "2023-05-01T10:00:00"
      }
    ]
  },
  "timestamp": "2023-10-05T14:30:45.123456"
}
```


----

## 获取用户统计信息

- **接口**：`GET /api/user/statistics`
- **功能**：查询当前用户详情

### 返回示例

```json
{
  "data": {
    "points": {
      "total_points": 0
    },
    "reputation": {
      "average_score": 0.0,
      "total_reviews": 0
    },
    "user_info": {
      "role": "client",
      "user_id": "1748434864506324",
      "username": "testclient"
    }
  },
  "message": "获取用户统计信息成功",
  "success": true,
  "timestamp": "2025-05-28T21:12:09.915509"
}
```

- 403 Forbidden - 非管理员访问
- 401 Unauthorized - Token无效
- 500 Internal Server Error - 服务器错误

---

## 🧑‍💼 7. 获取用户列表（管理员专用）


- **接口**：`GET /api/user/admin/list`

- **功能**：分页查询用户列表，仅限管理员使用


### 查询参数

示例 `/user/admin/list?page=1&per_page=10&role=client`

|参数名|类型|是否必填|描述|
|:-:|:-:|:-:|:-:|
|page|int|否|页码（默认 1）|
|per_page|int|否|每页数量（默认 10）|
|role|string|否|用户角色筛选（可选）|

### 返回示例

```json
{
  "data": {
    "pagination": {
      "current_page": 1,
      "has_next": true,
      "has_prev": false,
      "per_page": 10,
      "total": 13,
      "total_pages": 2
    },
    "users": [
      {
        "address": "四川省成都市四川大学江安区7舍",
        "email": "2319317070@qq.com",
        "phone": "18935139706",
        "reputation_score": 0.0,
        "review_count": 0,
        "role": "client",
        "user_id": "1748395817847071",
        "username": "client"
      },
	  ......
      {
        "address": "四川省成都市电子科技大学（清水河校区）",
        "email": "staff2@example.com",
        "phone": "242424242",
        "reputation_score": 0.0,
        "review_count": 0,
        "role": "staff",
        "user_id": "1748500567543179",
        "username": "staff2"
      }
    ]
  },
  "message": "获取用户列表成功",
  "success": true,
  "timestamp": "2025-05-29T21:27:43.923195"
}
```

- 403 Forbidden - 非管理员访问
- 401 Unauthorized - Token无效
- 500 Internal Server Error - 服务器错误

---

## 🧑‍💼 8. 管理员修改用户信息（管理员专用）

- **接口**：`PUT /api/user/admin/update-user`

### 查询参数

|参数名|类型|是否必填|描述|
|:-:|:-:|:-:|:-:|
|user_id|int|是|用户id|
|username|string|否||
|email|string|否||
|phone|string|否||
|address|string|否||

### 返回示例

```json
{
  "success": True,
  "message": "用户信息更新成功",
  "data": {},
  "timestamp": "2023-10-05T14:30:45.123456"
}
```

- 403 Forbidden - 非管理员访问
- 401 Unauthorized - Token无效
- 500 Internal Server Error - 服务器错误

---

## 🧑‍💼 8. 管理员修改用户密码（管理员专用）


- **接口**：`POST /api/user/admin/reset-password`

### 查询参数

|参数名|类型|是否必填|描述|
|:-:|:-:|:-:|:-:|
|user_id|int|是|用户id|
|new_password|string|是|新密码|

### 返回示例


```json
{
  "success": True,
  "message": "用户密码重置成功",
  "data": {},
  "timestamp": "2023-10-05T14:30:45.123456"
}
```

- 403 Forbidden - 非管理员访问
- 401 Unauthorized - Token无效
- 500 Internal Server Error - 服务器错误
