from flask import Blueprint, request, jsonify
from utils.auth_utils import AuthUtils
from utils.db_utils import get_db_session
from utils.response_utils import success_response, error_response
from utils.order_utils import OrderUtils
from utils.map_utils import MapUtils
from models import Orders, Task, User, Reputation
from decimal import Decimal
from sqlalchemy import and_, desc
import traceback

order_bp = Blueprint("order", __name__)


@order_bp.route("/create", methods=["POST"])
def create_order():
    """创建订单"""
    db = None
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            print("认证失败")
            return error_response("认证失败", 401)

        data = request.get_json()
        required_fields = ["order_type", "description", "orderlocation", "shop_address"]

        for field in required_fields:
            if field not in data or not data[field] or str(data[field]).strip() == "" or str(data[field]).strip() == "23432":
                print(f"字段校验失败: {field} -> {data.get(field)}")
                return error_response(f"缺少或无效的必填字段: {field}", 400)

        # 校验商家地址和收货地址地理编码
        shop_address = data.get('shop_address', '').strip()
        orderlocation = data.get('orderlocation', '').strip()
        shop_coords = MapUtils.geocode(shop_address)
        user_coords = MapUtils.geocode(orderlocation)
        if not shop_coords or not user_coords:
            print(f"地理编码失败: shop_coords={shop_coords}, user_coords={user_coords}")
            return error_response('商家地址或收货地址无法识别，请检查输入', 400)
        # 预计时间校验
        time_estimate = MapUtils.estimate_delivery_time(shop_address=shop_address, delivery_address=orderlocation)
        print('[DEBUG] 预计时间返回:', time_estimate)
        total_seconds = time_estimate.get('total') or time_estimate.get('total_time')
        if not time_estimate or not total_seconds or time_estimate.get('status') not in ('ok', 'calculated'):
            print(f"预计时间校验失败: {time_estimate}")
            return error_response('无法计算预计时间，请检查地址', 400)

        db = get_db_session()
        user_id = Decimal(payload["user_id"])

        # 创建订单
        order_id = OrderUtils.create_order(db, user_id, data, estimated_time=total_seconds)

        # 计算配送费
        order = db.query(Orders).filter(Orders.OrderID == order_id).first()
        if not order:
            return error_response("订单创建失败", 500)

        # 获取预计时间（分钟）
        estimated_time_min = int(order.EstimatedTime) // 60 if order.EstimatedTime else 45  # 默认45分钟
        
        # 计算配送费：预计时间 * 0.15
        delivery_fee = round(estimated_time_min * 0.15, 2)
        
        # 更新订单的配送费
        order.Amount = str(delivery_fee)
        db.commit()

        return success_response(
            {
                "order_id": str(order_id),
                "delivery_fee": delivery_fee,
                "estimated_time": estimated_time_min
            }, 
            "订单创建成功"
        )

    except Exception as e:
        traceback.print_exc()
        return error_response(f"创建订单失败: {str(e)}", 500)
    finally:
        if db:
            db.close()


@order_bp.route("/list", methods=["GET"])
def get_orders():
    """获取订单列表"""
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
        # print(orders_data)

        return success_response(orders_data, "获取订单列表成功")

    except Exception as e:
        traceback.print_exc()
        return error_response(f"获取订单列表失败: {str(e)}", 500)
    finally:
        db.close()


# 高德路径规划api： https://lbs.amap.com/api/webservice/guide/api/newroute
# 计算订单预计时间（先查询起点终点经纬度，然后计算骑行预计时间
# 预计时间=到店时间+配送时间
# 要求在骑手接取订单时向后端发送定位信息，浏览器对骑手进行定位：
# https://lbs.amap.com/api/javascript-api-v2/guide/services/geolocation#t1
# 由于http无法进行定位，采用模拟位置信息
# 可以将高德的api请求代码写入utils.map_utils.py然后导入引用


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

        order_detail = OrderUtils.get_order_detail(
            db, 
            order_id_decimal, 
            user_id,
            is_staff=(payload.get("role") == "staff")
        )
        if not order_detail:
            return error_response("订单不存在或无权访问", 404)

        return success_response(order_detail, "获取订单详情成功")

    except Exception as e:
        return error_response(f"获取订单详情失败: {str(e)}", 500)
    finally:
        db.close()


@order_bp.route("/estimate-time", methods=["POST"])
def estimate_order_time():
    """估算订单预计时间"""
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        data = request.get_json()
        if "orderlocation" not in data:
            return error_response("缺少必填字段: orderlocation", 400)

        # 获取数据库连接
        db = get_db_session()

        try:
            # 计算预计时间
            time_estimate = MapUtils.calculate_order_estimated_time(
                db, data["orderlocation"], payload["user_id"]
            )
            return success_response(time_estimate, "获取预计时间成功")
        finally:
            db.close()

    except Exception as e:
        return error_response(f"估算订单时间失败: {str(e)}", 500)


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
        db.close()


@order_bp.route("/<order_id>/complete", methods=["POST"])
def complete_order(order_id):
    """完成订单（staff操作，将assigned订单变为completed）"""
    try:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload or payload["role"] != "staff":
            return error_response("权限不足", 403)
        staff_id = Decimal(payload["user_id"])
        db = get_db_session()
        order_id_decimal = Decimal(order_id)
        result = OrderUtils.complete_order(db, order_id_decimal, staff_id)
        if not result:
            return error_response("完成订单失败", 400)
        return success_response({}, "订单已完成")
    except Exception as e:
        return error_response(f"完成订单失败: {str(e)}", 500)
    finally:
        if "db" in locals():
            db.close()


@order_bp.route("/payment/<order_id>/points-info", methods=["GET"])
def get_order_points_info(order_id):
    """查询订单的积分支付信息"""
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        db = get_db_session()
        user_id = Decimal(payload["user_id"])
        order_id_decimal = Decimal(order_id)

        # 获取订单积分信息
        points_info = OrderUtils.get_order_points_info(db, order_id_decimal, user_id)
        return success_response(points_info, "订单积分信息查询成功")

    except Exception as e:
        return error_response(f"查询失败: {str(e)}", 500)
    finally:
        db.close()


from contextlib import contextmanager

@order_bp.route("/payment/<order_id>", methods=["POST"])
def process_payment(order_id):
    """处理支付"""
    db = None
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        data = request.get_json()
        required_fields = ["payment_method", "amount"]

        for field in required_fields:
            if field not in data or not data[field] or str(data[field]).strip() == "" or str(data[field]).strip() == "23432":
                return error_response(f"缺少或无效的必填字段: {field}", 400)

        user_id = Decimal(payload["user_id"])
        order_id_decimal = Decimal(order_id)

        # 获取数据库连接
        db = get_db_session()

        # 处理支付逻辑
        payment_result = OrderUtils.process_payment(db, order_id_decimal, user_id, data)

        return success_response(payment_result, "支付成功")

    except Exception as e:
        traceback.print_exc()
        return error_response(f"支付失败: {str(e)}", 500)
    finally:
        if db:
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

        # 从token中获取user_id作为staff_id（修正点）
        staff_id = Decimal(payload["user_id"])  # 使用user_id作为staff_id
        db = get_db_session()

        # 获取查询参数
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        task_type = request.args.get("task_type", None)

        result = OrderUtils.get_available_orders(
            db, page, per_page, task_type
        )

        return success_response(result, "获取可接单列表成功")

    except Exception as e:
        return error_response(f"获取可接单列表失败: {str(e)}", 500)
    finally:
        if "db" in locals():
            db.close()


@order_bp.route("/completed", methods=["GET"])
def get_completed_orders():
    """获取已完成订单列表（代办人员使用）"""
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload or payload["role"] != "staff":
            return error_response("权限不足", 403)

        db = get_db_session()
        staff_id = Decimal(payload["user_id"])

        # 获取查询参数
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))

        # 使用工具类方法获取已完成订单
        orders_data = OrderUtils.get_staff_orders(
            db, staff_id, page, per_page, status="completed"
        )

        return success_response(orders_data, "获取已完成订单列表成功")

    except Exception as e:
        return error_response(f"获取已完成订单列表失败: {str(e)}", 500)
    finally:
        db.close()


@order_bp.route("/in-progress", methods=["GET"])
def get_in_progress_orders():
    """获取进行中订单列表（代办人员使用）"""
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload or payload["role"] != "staff":
            return error_response("权限不足", 403)

        db = get_db_session()
        staff_id = Decimal(payload["user_id"])

        # 获取查询参数
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))

        # 使用工具类方法获取进行中订单
        orders_data = OrderUtils.get_staff_orders(
            db, staff_id, page, per_page, status="in_progress"
        )

        return success_response(orders_data, "获取进行中订单列表成功")

    except Exception as e:
        return error_response(f"获取进行中订单列表失败: {str(e)}", 500)
    finally:
        db.close()


@order_bp.route("/assigned", methods=["GET"])
def get_assigned_orders():
    """获取已分配订单列表（代办人员使用）"""
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload or payload["role"] != "staff":
            return error_response("权限不足", 403)

        db = get_db_session()
        staff_id = Decimal(payload["user_id"])

        # 获取查询参数
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))

        # 使用工具类方法获取已分配订单
        orders_data = OrderUtils.get_staff_orders(
            db, staff_id, page, per_page, status="assigned"
        )

        return success_response(orders_data, "获取已分配订单列表成功")

    except Exception as e:
        return error_response(f"获取已分配订单列表失败: {str(e)}", 500)
    finally:
        db.close()


@order_bp.route("/staff/all", methods=["GET"])
def get_staff_all_orders():
    """获取代办人员所有订单列表"""
    try:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload or payload["role"] != "staff":
            return error_response("权限不足", 403)
        staff_id = Decimal(payload["user_id"])
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        status = request.args.get("status", "")
        order_type = request.args.get("order_type", "")
        
        print(f"[DEBUG] 获取staff订单列表: staff_id={staff_id}, status={status}")
        
        db = get_db_session()
        result = OrderUtils.get_staff_orders(db, staff_id, page, per_page, status, order_type)
        print(f"[DEBUG] 查询结果: {result}")
        
        return success_response(result, "获取我的订单成功")
    except Exception as e:
        print(f"[ERROR] 获取staff订单失败: {str(e)}")
        return error_response(f"获取我的订单失败: {str(e)}", 500)
    finally:
        if "db" in locals():
            db.close()


@order_bp.route("/available-map", methods=["GET"])
def get_available_orders_map():
    """获取可接单列表（地图模式，带经纬度）"""
    try:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload or payload["role"] != "staff":
            return error_response("权限不足", 403)
        staff_id = Decimal(payload["user_id"])
        db = get_db_session()
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        task_type = request.args.get("task_type", None)
        result = OrderUtils.get_available_orders_map(db, page, per_page, task_type, staff_id)
        return success_response(result, "获取可接单地图列表成功")
    except Exception as e:
        return error_response(f"获取可接单地图列表失败: {str(e)}", 500)
    finally:
        if "db" in locals():
            db.close()


@order_bp.route("/accept/<order_id>", methods=["POST"])
def accept_order(order_id):
    """代办人员接单"""
    try:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload or payload["role"] != "staff":
            return error_response("权限不足", 403)
        staff_id = Decimal(payload["user_id"])
        db = get_db_session()
        order_id_decimal = Decimal(order_id)
        result = OrderUtils.accept_order(db, order_id_decimal, staff_id)
        return success_response(result, "接单成功")
    except Exception as e:
        return error_response(f"接单失败: {str(e)}", 500)
    finally:
        if "db" in locals():
            db.close()


@order_bp.route("/staff/assigned", methods=["GET"])
def get_staff_assigned_orders():
    """获取代办人员已分配的订单列表"""
    try:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload or payload["role"] != "staff":
            return error_response("权限不足", 403)
        staff_id = Decimal(payload["user_id"])
        db = get_db_session()
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        order_type = request.args.get("order_type", "")
        orders_data = OrderUtils.get_staff_orders(db, staff_id, page, per_page, status="assigned", order_type=order_type)
        return success_response(orders_data, "获取已分配订单列表成功")
    except Exception as e:
        return error_response(f"获取已分配订单失败: {str(e)}", 500)
    finally:
        if "db" in locals():
            db.close()
