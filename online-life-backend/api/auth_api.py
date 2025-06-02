from flask import Blueprint, request, jsonify, current_app
from utils.auth_utils import AuthUtils
from utils.db_utils import get_db_session
from utils.response_utils import success_response, error_response
from models import User, Admin, Client, Staff
import hashlib

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        required_fields = ["username", "password", "email", "phone", "address", "role"]

        # 验证必填字段
        for field in required_fields:
            if field not in data:
                return error_response(f"缺少必填字段: {field}", 400)

        db = get_db_session()

        # 检查用户名是否已存在
        if AuthUtils.check_username_exists(db, data["username"]):
            return error_response("用户名已存在", 400)

        # 检查邮箱是否已存在
        if AuthUtils.check_email_exists(db, data["email"]):
            return error_response("邮箱已存在", 400)

        # 创建用户
        user_id = AuthUtils.generate_user_id()
        hashed_password = AuthUtils.hash_password(data["password"])

        # 根据角色创建不同类型的用户
        if data["role"] == "admin":
            new_user = Admin(
                UserID=user_id,
                Username=data["username"],
                Password=hashed_password,
                Email=data["email"],
                Phone=data["phone"],
                Address=data["address"],
                Role=data["role"],
                JoinDate=AuthUtils.get_current_time(),
                Adlevel=data.get("adlevel", "1"),
            )
        elif data["role"] == "client":
            new_user = Client(
                UserID=user_id,
                Username=data["username"],
                Password=hashed_password,
                Email=data["email"],
                Phone=data["phone"],
                Address=data["address"],
                Role=data["role"],
                ClientID=user_id,
            )
        elif data["role"] == "staff":
            new_user = Staff(
                UserID=user_id,
                Username=data["username"],
                Password=hashed_password,
                Email=data["email"],
                Phone=data["phone"],
                Address=data["address"],
                Role=data["role"],
                StaffID=user_id,
                Salary=data.get("salary", "0"),
            )
        else:
            return error_response("无效的用户角色", 400)

        # 同时创建基础用户记录
        base_user = User(
            UserID=user_id,
            Username=data["username"],
            Password=hashed_password,
            Email=data["email"],
            Phone=data["phone"],
            Address=data["address"],
            Role=data["role"],
        )

        db.add(base_user)
        # db.commit()
        db.flush()

        db.add(new_user)
        db.commit()

        return success_response(
            {
                "user_id": str(user_id),
                "username": data["username"],
                "role": data["role"],
            },
            "注册成功",
        )

    except Exception as e:
        db.rollback()
        return error_response(f"注册失败: {str(e)}", 500)
    finally:
        db.close()


@auth_bp.route("/login", methods=["POST"])
def login():
    """用户登录"""
    try:
        data = request.get_json()

        if "username" not in data or "password" not in data:
            return error_response("用户名和密码不能为空", 400)

        db = get_db_session()

        # 验证用户
        user = AuthUtils.authenticate_user(db, data["username"], data["password"])
        if not user:
            return error_response("用户名或密码错误", 401)

        # 生成JWT令牌
        token = AuthUtils.generate_token(user.UserID, user.Role)

        return success_response(
            {
                "token": token,
                "user_id": str(user.UserID),
                "username": user.Username,
                "role": user.Role,
                "email": user.Email,
            },
            "登录成功",
        )

    except Exception as e:
        return error_response(f"登录失败: {str(e)}", 500)
    finally:
        db.close()


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """用户登出"""
    # 在实际应用中，可以将token加入黑名单
    return success_response({}, "登出成功")


@auth_bp.route("/verify-token", methods=["POST"])
def verify_token():
    """验证JWT令牌"""
    try:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")

        if not token:
            return error_response("缺少认证令牌", 401)

        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("无效的认证令牌", 401)

        return success_response(payload, "令牌验证成功")

    except Exception as e:
        return error_response(f"令牌验证失败: {str(e)}", 500)
