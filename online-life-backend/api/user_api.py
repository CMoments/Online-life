from flask import Blueprint, request, jsonify
from utils.auth_utils import AuthUtils
from utils.db_utils import get_db_session
from utils.response_utils import success_response, error_response
from utils.user_utils import UserUtils
from models import User, Admin, Client, Staff, Points, Reputation, Orders
from decimal import Decimal
import traceback
import logging

logger = logging.getLogger(__name__)

user_bp = Blueprint("user", __name__)


@user_bp.route("/profile", methods=["GET"])
def get_profile():
    """获取用户资料"""
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
        db.close()


@user_bp.route("/profile", methods=["PUT"])
def update_profile():
    """更新用户资料"""
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
        db.close()


@user_bp.route("/change-password", methods=["POST"])
def change_password():
    """修改密码"""
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
        db.close()


@user_bp.route("/reputation", methods=["GET"])
def get_reputation():
    """获取用户信誉"""
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
        db.close()


# @user_bp.route("/reputation", methods=["POST"])
# def add_reputation():
#     """添加信誉评价"""
#     try:
#         # 验证token
#         token = request.headers.get("Authorization", "").replace("Bearer ", "")
#         payload = AuthUtils.verify_token(token)
#         if not payload:
#             return error_response("认证失败", 401)

#         data = request.get_json()
#         required_fields = ["target_user_id", "score", "review"]

#         for field in required_fields:
#             if field not in data:
#                 return error_response(f"缺少必填字段: {field}", 400)

#         db = get_db_session()
#         reviewer_id = Decimal(payload["user_id"])
#         target_user_id = Decimal(data["target_user_id"])

#         # 添加信誉评价
#         reputation = Reputation(
#             RUserID=reviewer_id,
#             UserID=target_user_id,
#             Score=str(data["score"]),
#             Review=data["review"],
#         )

#         db.add(reputation)
#         db.commit()

#         return success_response({}, "信誉评价添加成功")

#     except Exception as e:
#         return error_response(f"添加信誉评价失败: {str(e)}", 500)
#     finally:
#         db.close()


@user_bp.route("/order-reputation/<order_id>", methods=["POST"])
def add_order_reputation(order_id):
    """添加订单相关的信誉评价"""
    db = None  # 保证 finally 里 db 总是有定义
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            logger.warning("认证失败")
            return error_response("认证失败", 401)

        data = request.get_json()
        required_fields = ["target_user_id", "score", "review"]

        for field in required_fields:
            if field not in data:
                logger.warning(f"缺少必填字段: {field}")
                return error_response(f"缺少必填字段: {field}", 400)

        db = get_db_session()
        reviewer_id = Decimal(payload["user_id"])
        target_user_id = Decimal(data["target_user_id"])
        order_id_decimal = Decimal(order_id)

        # 获取订单
        order = db.query(Orders).filter(Orders.OrderID == order_id_decimal).first()
        if not order:
            logger.warning(f"订单不存在: {order_id}")
            return error_response("订单不存在", 404)

        # 检查权限
        if order.ClientID != reviewer_id:
            logger.warning(f"无权限评价该订单: reviewer_id={reviewer_id}, order.ClientID={order.ClientID}")
            return error_response("无权限评价该订单", 403)

        # 检查订单状态
        if order.OrderStatus not in ["paid", "completed"]:
            logger.warning(f"该订单状态不允许评价: {order.OrderStatus}")
            return error_response("该订单状态不允许评价", 400)

        # 检查是否已经评价过
        existing = db.query(Reputation).filter(
            Reputation.RUserID == reviewer_id,
            Reputation.UserID == target_user_id,
            Reputation.OrderID == order_id
        ).first()
        logger.warning(f"评价查重 existing={existing}")
        if existing:
            logger.warning(f"已评价过: reviewer_id={reviewer_id}, target_user_id={target_user_id}, order_id={order_id}")
            return error_response("已经评价过该订单", 400)

        logger.info(f"reviewer_id={reviewer_id}, target_user_id={target_user_id}, order.ClientID={order.ClientID}, order.StaffID={order.StaffID}, order.OrderStatus={order.OrderStatus}")

        # 添加订单评价
        result = UserUtils.add_order_reputation(
            db,
            reviewer_id,
            target_user_id,
            order_id_decimal,
            float(data["score"]),
            data["review"],
        )

        if not result:
            logger.warning("UserUtils.add_order_reputation 返回False，可能是订单状态、权限或已评价过")
            return error_response("添加评价失败，请检查订单状态或评价权限", 400)

        return success_response({}, "订单评价添加成功")

    except Exception as e:
        logger.error(f"写入评价记录异常: {str(e)}")
        db.rollback()
        return error_response(f"添加订单评价失败: {str(e)}", 500)
    finally:
        if db:
            db.close()


@user_bp.route("/order-reputation/<order_id>", methods=["GET"])
def get_order_reputation(order_id):
    """获取订单相关的评价信息"""
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        db = get_db_session()
        order_id_decimal = Decimal(order_id)

        # 获取订单评价
        reputation_data = UserUtils.get_order_reputation(db, order_id_decimal)

        return success_response(reputation_data, "获取订单评价成功")

    except Exception as e:
        return error_response(f"获取订单评价失败: {str(e)}", 500)
    finally:
        db.close()


@user_bp.route("/points", methods=["GET"])
def get_points():
    """获取用户积分"""
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
        db.close()


@user_bp.route("/statistics", methods=["GET"])
def get_user_statistics():
    """获取用户统计信息"""
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        db = get_db_session()
        user_id = Decimal(payload["user_id"])
        print(payload)

        # 获取用户统计信息
        statistics = UserUtils.get_user_statistics(db, user_id)
        if not statistics:
            return error_response("获取用户统计信息失败", 404)

        return success_response(statistics, "获取用户统计信息成功")

    except Exception as e:
        return error_response(f"获取用户统计信息失败: {str(e)}", 500)
    finally:
        db.close()


@user_bp.route("/admin/user-statistics/<user_id>", methods=["GET"])
def admin_get_user_statistics(user_id):
    """管理员获取指定用户的统计信息"""
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload or payload["role"] != "admin":
            return error_response("权限不足", 403)

        db = get_db_session()
        target_user_id = Decimal(user_id)

        # 获取用户统计信息
        statistics = UserUtils.get_user_statistics(db, target_user_id)
        if not statistics:
            return error_response("获取用户统计信息失败", 404)

        return success_response(statistics, "获取用户统计信息成功")

    except Exception as e:
        return error_response(f"获取用户统计信息失败: {str(e)}", 500)
    finally:
        db.close()


@user_bp.route("/admin/list", methods=["GET"])
def get_user_list():
    """获取用户列表（管理员功能）"""
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
        db.close()


@user_bp.route("/admin/update-user", methods=["PUT"])
def admin_update_user():
    """管理员修改用户信息"""
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload or payload["role"] != "admin":
            return error_response("权限不足", 403)

        data = request.get_json()
        if not data or "user_id" not in data:
            return error_response("缺少必填字段: user_id", 400)

        db = get_db_session()
        admin_id = Decimal(payload["user_id"])
        user_id = Decimal(data["user_id"])

        # 移除user_id，剩下的是要更新的数据
        update_data = {k: v for k, v in data.items() if k != "user_id"}
        if not update_data:
            return error_response("没有提供要更新的数据", 400)

        # 更新用户信息
        result = UserUtils.admin_update_user_info(db, admin_id, user_id, update_data)
        if not result:
            return error_response("更新失败，请检查用户ID或权限", 400)

        return success_response({}, "用户信息更新成功")

    except Exception as e:
        return error_response(f"管理员更新用户信息失败: {str(e)}", 500)
    finally:
        db.close()


@user_bp.route("/admin/reset-password", methods=["POST"])
def admin_reset_password():
    """管理员重置用户密码"""
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload or payload["role"] != "admin":
            return error_response("权限不足", 403)

        data = request.get_json()
        required_fields = ["user_id", "new_password"]

        for field in required_fields:
            if field not in data:
                return error_response(f"缺少必填字段: {field}", 400)

        db = get_db_session()
        admin_id = Decimal(payload["user_id"])
        user_id = Decimal(data["user_id"])

        # 生成新密码的哈希值
        new_password_hash = AuthUtils.hash_password(data["new_password"])

        # 重置用户密码
        result = UserUtils.admin_reset_user_password(
            db, admin_id, user_id, new_password_hash
        )
        if not result:
            return error_response("重置密码失败，请检查用户ID或权限", 400)

        return success_response({}, "用户密码重置成功")

    except Exception as e:
        return error_response(f"管理员重置用户密码失败: {str(e)}", 500)
    finally:
        db.close()


@user_bp.route("/list", methods=["GET"])
def list_users():
    """模糊查询用户列表（支持用户名关键字）"""
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        db = get_db_session()
        username = request.args.get("username", "")

        query = db.query(User)
        if username:
            query = query.filter(User.Username.like(f"%{username}%"))
        users = query.limit(20).all()

        result = [
            {
                "user_id": str(u.UserID),
                "username": u.Username,
                "role": u.Role,
            }
            for u in users
        ]
        return success_response(result, "获取用户列表成功")
    except Exception as e:
        return error_response(f"获取用户列表失败: {str(e)}", 500)
    finally:
        db.close()
