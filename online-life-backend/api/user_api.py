from flask import Blueprint, request, jsonify
from utils.auth_utils import AuthUtils
from utils.db_utils import get_db_session
from utils.response_utils import success_response, error_response
from utils.user_utils import UserUtils
from models import User, Admin, Client, Staff, Points, Reputation
from decimal import Decimal

user_bp = Blueprint("user", __name__)


@user_bp.route("/profile", methods=["GET"])
def get_profile():
    """获取用户资料"""
    db = None
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        db = get_db_session()
        user_id = Decimal(payload["user_id"])

        user_info = UserUtils.get_user_info(db, user_id)
        if not user_info:
            return error_response("用户不存在", 404)

        return success_response(user_info, "获取用户资料成功")

    except Exception as e:
        return error_response(f"获取用户资料失败: {str(e)}", 500)
    finally:
        if db is not None:
            db.close()


@user_bp.route("/profile", methods=["PUT"])
def update_profile():
    """更新用户资料"""
    db = None
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        data = request.get_json()
        db = get_db_session()
        user_id = Decimal(payload["user_id"])

        # 更新用户信息
        result = UserUtils.update_user_info(db, user_id, data)
        if not result:
            return error_response("更新失败", 400)

        return success_response({}, "用户资料更新成功")

    except Exception as e:
        return error_response(f"更新用户资料失败: {str(e)}", 500)
    finally:
        if db is not None:
            db.close()


@user_bp.route("/change-password", methods=["POST"])
def change_password():
    """修改密码"""
    db = None
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        data = request.get_json()
        required_fields = ["old_password", "new_password"]

        for field in required_fields:
            if field not in data:
                return error_response(f"缺少必填字段: {field}", 400)

        db = get_db_session()
        user_id = Decimal(payload["user_id"])

        # 验证旧密码
        user = db.query(User).filter(User.UserID == user_id).first()
        if not user or not AuthUtils.verify_password(
            data["old_password"], user.Password
        ):
            return error_response("原密码错误", 400)

        # 更新密码
        new_password_hash = AuthUtils.hash_password(data["new_password"])
        UserUtils.update_password(db, user_id, new_password_hash)

        return success_response({}, "密码修改成功")

    except Exception as e:
        return error_response(f"修改密码失败: {str(e)}", 500)
    finally:
        if db is not None:
            db.close()


@user_bp.route("/reputation", methods=["GET"])
def get_reputation():
    """获取用户信誉"""
    db = None
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        db = get_db_session()
        user_id = Decimal(payload["user_id"])

        reputation_data = UserUtils.get_user_reputation(db, user_id)

        return success_response(reputation_data, "获取信誉信息成功")

    except Exception as e:
        return error_response(f"获取信誉信息失败: {str(e)}", 500)
    finally:
        if db is not None:
            db.close()


@user_bp.route("/reputation", methods=["POST"])
def add_reputation():
    """添加信誉评价"""
    db = None
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        data = request.get_json()
        required_fields = ["target_user_id", "score", "review"]

        for field in required_fields:
            if field not in data:
                return error_response(f"缺少必填字段: {field}", 400)

        db = get_db_session()
        reviewer_id = Decimal(payload["user_id"])
        target_user_id = Decimal(data["target_user_id"])

        # 添加信誉评价
        reputation = Reputation(
            RUserID=reviewer_id,
            UserID=target_user_id,
            Score=str(data["score"]),
            Review=data["review"],
        )

        db.add(reputation)
        db.commit()

        return success_response({}, "信誉评价添加成功")

    except Exception as e:
        return error_response(f"添加信誉评价失败: {str(e)}", 500)
    finally:
        if db is not None:
            db.close()


@user_bp.route("/points", methods=["GET"])
def get_points():
    """获取用户积分"""
    db = None
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        db = get_db_session()
        user_id = Decimal(payload["user_id"])

        points_data = UserUtils.get_user_points(db, user_id)

        return success_response(points_data, "获取积分信息成功")

    except Exception as e:
        return error_response(f"获取积分信息失败: {str(e)}", 500)
    finally:
        if db is not None:
            db.close()


@user_bp.route("/list", methods=["GET"])
def get_user_list():
    """获取用户列表（管理员功能）"""
    db = None
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload or payload["role"] != "admin":
            return error_response("权限不足", 403)

        db = get_db_session()

        # 获取查询参数
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        role = request.args.get("role", "")

        users_data = UserUtils.get_users_list(db, page, per_page, role)

        return success_response(users_data, "获取用户列表成功")

    except Exception as e:
        return error_response(f"获取用户列表失败: {str(e)}", 500)
    finally:
        if db is not None:
            db.close()
