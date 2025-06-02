import hashlib
import jwt
import time
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import secrets
from models import User


class AuthUtils:
    SECRET_KEY = "your-jwt-secret-key-here"  # 在生产环境中应该使用环境变量

    @staticmethod
    def hash_password(password: str) -> str:
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """验证密码"""
        return hashlib.sha256(password.encode()).hexdigest() == hashed_password

    @staticmethod
    def generate_user_id() -> Decimal:
        """生成用户ID"""
        timestamp = int(time.time() * 1000)  # 毫秒级时间戳
        random_part = secrets.randbelow(1000)  # 3位随机数
        return Decimal(timestamp * 1000 + random_part)

    @staticmethod
    def generate_token(user_id: Decimal, role: str) -> str:
        """生成JWT令牌"""
        now = datetime.now(timezone.utc)  # 使用带时区的 UTC 时间
        payload = {
            "user_id": str(user_id),
            "role": role,
            "exp": now + timedelta(days=7),
            "iat": now,
        }
        return jwt.encode(payload, AuthUtils.SECRET_KEY, algorithm="HS256")

    @staticmethod
    def verify_token(token: str) -> dict:
        """验证JWT令牌"""
        try:
            payload = jwt.decode(token, AuthUtils.SECRET_KEY, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def check_username_exists(db, username: str) -> bool:
        """检查用户名是否存在"""
        user = db.query(User).filter(User.Username == username).first()
        return user is not None

    @staticmethod
    def check_email_exists(db, email: str) -> bool:
        """检查邮箱是否存在"""
        user = db.query(User).filter(User.Email == email).first()
        return user is not None

    @staticmethod
    def authenticate_user(db, username: str, password: str):
        """验证用户登录"""
        user = db.query(User).filter(User.Username == username).first()
        if user and AuthUtils.verify_password(password, user.Password):
            return user
        return None

    @staticmethod
    def get_current_time() -> str:
        """获取当前时间字符串"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def require_role(allowed_roles: list):
        """装饰器：验证用户角色权限"""

        def decorator(func):
            def wrapper(*args, **kwargs):
                from flask import request

                token = request.headers.get("Authorization", "").replace("Bearer ", "")
                payload = AuthUtils.verify_token(token)

                if not payload:
                    from utils.response_utils import error_response

                    return error_response("认证失败", 401)

                if payload["role"] not in allowed_roles:
                    from utils.response_utils import error_response

                    return error_response("权限不足", 403)

                return func(*args, **kwargs)

            return wrapper

        return decorator
