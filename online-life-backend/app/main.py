from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, user, order, points, reputation, task, database

app = FastAPI(title="Online Life API")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5000"],  # 允许前端开发服务器的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(order.router)
app.include_router(points.router)
app.include_router(reputation.router)
app.include_router(task.router)
app.include_router(database.router)  # 添加数据库可视化路由

@app.get("/")
async def root():
    return {"message": "Welcome to Online Life API"} 