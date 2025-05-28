from flask import Blueprint, request, jsonify
from utils.auth_utils import AuthUtils
from utils.db_utils import get_db_session
from utils.response_utils import success_response, error_response
from utils.points_utils import PointsUtils
from models import Points
from decimal import Decimal

points_bp = Blueprint("points", __name__)


@points_bp.route("/balance", methods=["GET"])
def get_points_balance():
    """获取积分余额"""
    db = None
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        db = get_db_session()
        user_id = Decimal(payload["user_id"])

        balance = PointsUtils.get_user_points_balance(db, user_id)

        return success_response(
            {"user_id": str(user_id), "points_balance": balance}, "获取积分余额成功"
        )

    except Exception as e:
        return error_response(f"获取积分余额失败: {str(e)}", 500)
    finally:
        if db is not None:
            db.close()


@points_bp.route("/add", methods=["POST"])
def add_points():
    """增加积分"""
    db = None
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        data = request.get_json()
        if "points" not in data or "reason" not in data:
            return error_response("缺少必填字段", 400)

        db = get_db_session()
        user_id = Decimal(payload["user_id"])
        points_to_add = int(data["points"])
        reason = data["reason"]

        if points_to_add <= 0:
            return error_response("积分数量必须大于0", 400)

        result = PointsUtils.add_points(db, user_id, points_to_add, reason)
        if not result:
            return error_response("积分添加失败", 400)

        return success_response({}, "积分添加成功")

    except Exception as e:
        return error_response(f"积分添加失败: {str(e)}", 500)
    finally:
        if db is not None:
            db.close()


@points_bp.route("/deduct", methods=["POST"])
def deduct_points():
    """扣除积分"""
    db = None
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        data = request.get_json()
        if "points" not in data or "reason" not in data:
            return error_response("缺少必填字段", 400)

        db = get_db_session()
        user_id = Decimal(payload["user_id"])
        points_to_deduct = int(data["points"])
        reason = data["reason"]

        if points_to_deduct <= 0:
            return error_response("积分数量必须大于0", 400)

        # 检查积分余额
        current_balance = PointsUtils.get_user_points_balance(db, user_id)
        if current_balance < points_to_deduct:
            return error_response("积分余额不足", 400)

        result = PointsUtils.deduct_points(db, user_id, points_to_deduct, reason)
        if not result:
            return error_response("积分扣除失败", 400)

        return success_response({}, "积分扣除成功")

    except Exception as e:
        return error_response(f"积分扣除失败: {str(e)}", 500)
    finally:
        if db is not None:
            db.close()


@points_bp.route("/history", methods=["GET"])
def get_points_history():
    """获取积分历史记录"""
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
        per_page = int(request.args.get("per_page", 20))

        history = PointsUtils.get_points_history(db, user_id, page, per_page)

        return success_response(history, "获取积分历史成功")

    except Exception as e:
        return error_response(f"获取积分历史失败: {str(e)}", 500)
    finally:
        if db is not None:
            db.close()


@points_bp.route("/transfer", methods=["POST"])
def transfer_points():
    """积分转账"""
    db = None
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        data = request.get_json()
        required_fields = ["target_user_id", "points", "message"]

        for field in required_fields:
            if field not in data:
                return error_response(f"缺少必填字段: {field}", 400)

        db = get_db_session()
        from_user_id = Decimal(payload["user_id"])
        to_user_id = Decimal(data["target_user_id"])
        points_amount = int(data["points"])
        message = data["message"]

        if points_amount <= 0:
            return error_response("转账积分必须大于0", 400)

        if from_user_id == to_user_id:
            return error_response("不能向自己转账", 400)

        # 检查积分余额
        current_balance = PointsUtils.get_user_points_balance(db, from_user_id)
        if current_balance < points_amount:
            return error_response("积分余额不足", 400)

        result = PointsUtils.transfer_points(
            db, from_user_id, to_user_id, points_amount, message
        )
        if not result:
            return error_response("积分转账失败", 400)

        return success_response({}, "积分转账成功")

    except Exception as e:
        return error_response(f"积分转账失败: {str(e)}", 500)
    finally:
        if db is not None:
            db.close()


@points_bp.route("/ranking", methods=["GET"])
def get_points_ranking():
    """获取积分排行榜"""
    db = None
    try:
        db = get_db_session()

        # 获取查询参数
        limit = int(request.args.get("limit", 50))

        ranking = PointsUtils.get_points_ranking(db, limit)

        return success_response(ranking, "获取积分排行榜成功")

    except Exception as e:
        return error_response(f"获取积分排行榜失败: {str(e)}", 500)
    finally:
        if db is not None:
            db.close()
