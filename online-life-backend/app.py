from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
from models import Base
import logging
logging.basicConfig(level=logging.DEBUG)

# 导入API蓝图
from api.auth_api import auth_bp
from api.user_api import user_bp
from api.order_api import order_bp
from api.task_api import task_bp
from api.points_api import points_bp

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "your-secret-key-here"

    # 启用CORS
    CORS(app)

    # 数据库配置
    DATABASE_URL = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    engine = create_engine(DATABASE_URL, echo=True)

    # 创建数据库会话
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # 将数据库会话添加到应用配置
    app.config["DB_SESSION"] = SessionLocal
    app.config["DB_ENGINE"] = engine

    # 注册蓝图
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/user")
    app.register_blueprint(order_bp, url_prefix="/api/order")
    app.register_blueprint(task_bp, url_prefix="/api/task")
    app.register_blueprint(points_bp, url_prefix="/api/points")

    @app.route("/")
    def index():
        return {"message": "网上代办系统API服务正在运行", "version": "1.0"}

    @app.route("/health")
    def health_check():
        return {"status": "healthy", "message": "服务运行正常"}

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
