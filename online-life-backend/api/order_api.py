from flask import Blueprint, request, jsonify
from utils.auth_utils import AuthUtils
from utils.db_utils import get_db_session
from utils.response_utils import success_response, error_response
from utils.order_utils import OrderUtils
from models import Orders, Task
from decimal import Decimal

order_bp = Blueprint("order", __name__)


@order_bp.route("/create", methods=["POST"])
def create_order():
    """创建订单"""
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        data = request.get_json()
        required_fields = ["order_type", "task_type", "description"]

        for field in required_fields:
            if field not in data:
                return error_response(f"缺少必填字段: {field}", 400)

        db = get_db_session()
        user_id = Decimal(payload["user_id"])

        # 创建订单和任务
        order_id = OrderUtils.create_order(db, user_id, data)

        return success_response({"order_id": str(order_id)}, "订单创建成功")

    except Exception as e:
        return error_response(f"创建订单失败: {str(e)}", 500)
    finally:
        if 'db' in locals():
            db.close()


@order_bp.route("/list", methods=["GET"])
def get_orders():
    """获取订单列表"""
    db = None
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        db = get_db_session()
        user_id = Decimal(payload["user_id"])

        # 获取查询参数
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        status = request.args.get("status", "")
        order_type = request.args.get("order_type", "")

        orders_data = OrderUtils.get_user_orders(
            db, user_id, page, per_page, status, order_type
        )

        return success_response(orders_data, "获取订单列表成功")

    except Exception as e:
        return error_response(f"获取订单列表失败: {str(e)}", 500)
    finally:
        if db is not None:
            db.close()


@order_bp.route("/<order_id>", methods=["GET"])
def get_order_detail(order_id):
    """获取订单详情"""
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        db = get_db_session()
        user_id = Decimal(payload["user_id"])
        order_id_decimal = Decimal(order_id)

        order_detail = OrderUtils.get_order_detail(db, order_id_decimal, user_id)
        if not order_detail:
            return error_response("订单不存在或无权访问", 404)

        return success_response(order_detail, "获取订单详情成功")

    except Exception as e:
        return error_response(f"获取订单详情失败: {str(e)}", 500)
    finally:
        if 'db' in locals():
            db.close()


@order_bp.route("/<order_id>/cancel", methods=["POST"])
def cancel_order(order_id):
    """取消订单"""
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        db = get_db_session()
        user_id = Decimal(payload["user_id"])
        order_id_decimal = Decimal(order_id)

        result = OrderUtils.cancel_order(db, order_id_decimal, user_id)
        if not result:
            return error_response("取消订单失败", 400)

        return success_response({}, "订单已取消")

    except Exception as e:
        return error_response(f"取消订单失败: {str(e)}", 500)
    finally:
        if 'db' in locals():
            db.close()


@order_bp.route("/<order_id>/complete", methods=["POST"])
def complete_order(order_id):
    """完成订单"""
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        db = get_db_session()
        user_id = Decimal(payload["user_id"])
        order_id_decimal = Decimal(order_id)

        result = OrderUtils.complete_order(db, order_id_decimal, user_id)
        if not result:
            return error_response("完成订单失败", 400)

        return success_response({}, "订单已完成")

    except Exception as e:
        return error_response(f"完成订单失败: {str(e)}", 500)
    finally:
        if 'db' in locals():
            db.close()


@order_bp.route("/payment/<order_id>", methods=["POST"])
def process_payment(order_id):
    """处理支付"""
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        data = request.get_json()
        required_fields = ["payment_method", "amount"]

        for field in required_fields:
            if field not in data:
                return error_response(f"缺少必填字段: {field}", 400)

        db = get_db_session()
        user_id = Decimal(payload["user_id"])
        order_id_decimal = Decimal(order_id)

        # 处理支付逻辑
        payment_result = OrderUtils.process_payment(db, order_id_decimal, user_id, data)

        return success_response(payment_result, "支付成功")

    except Exception as e:
        return error_response(f"支付失败: {str(e)}", 500)
    finally:
        if 'db' in locals():
            db.close()


@order_bp.route("/available", methods=["GET"])
def get_available_orders():
    """获取可接单列表（代办人员使用）"""
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload or payload["role"] != "staff":
            return error_response("权限不足", 403)

        db = get_db_session()

        # 获取查询参数
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        task_type = request.args.get("task_type", "")

        orders_data = OrderUtils.get_available_orders(db, page, per_page, task_type)

        return success_response(orders_data, "获取可接单列表成功")

    except Exception as e:
        return error_response(f"获取可接单列表失败: {str(e)}", 500)
    finally:
        if 'db' in locals():
            db.close()
