from flask import Blueprint, request, jsonify
from utils.auth_utils import AuthUtils
from utils.db_utils import get_db_session
from utils.response_utils import success_response, error_response
from utils.task_utils import TaskUtils
from models import Task, GroupTask, GroupTaskUser, BidRecord
from decimal import Decimal

task_bp = Blueprint("task", __name__)


@task_bp.route("/group/list", methods=["GET"])
def get_group_tasks():
    """获取团办任务列表"""
    db = None
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        db = get_db_session()

        # 获取查询参数
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        task_type = request.args.get("task_type", "")
        status = request.args.get("status", "active")

        group_tasks = TaskUtils.get_group_tasks(db, page, per_page, task_type, status)

        return success_response(group_tasks, "获取团办任务列表成功")

    except Exception as e:
        return error_response(f"获取团办任务列表失败: {str(e)}", 500)
    finally:
        if db is not None:
            db.close()


@task_bp.route("/group/<group_task_id>", methods=["GET"])
def get_group_task_detail(group_task_id):
    """获取团办任务详情"""
    db = None
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        db = get_db_session()
        group_task_id_decimal = Decimal(group_task_id)

        task_detail = TaskUtils.get_group_task_detail(db, group_task_id_decimal)
        if not task_detail:
            return error_response("团办任务不存在", 404)

        return success_response(task_detail, "获取团办任务详情成功")

    except Exception as e:
        return error_response(f"获取团办任务详情失败: {str(e)}", 500)
    finally:
        if db is not None:
            db.close()


@task_bp.route("/group/<group_task_id>/join", methods=["POST"])
def join_group_task(group_task_id):
    """参加团办任务"""
    db = None
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        db = get_db_session()
        user_id = Decimal(payload["user_id"])
        group_task_id_decimal = Decimal(group_task_id)

        # 检查是否已经参加
        existing = (
            db.query(GroupTaskUser)
            .filter(
                GroupTaskUser.UserID == user_id,
                GroupTaskUser.GroupTaskID == group_task_id_decimal,
            )
            .first()
        )

        if existing:
            return error_response("您已经参加了此团办任务", 400)

        # 参加团办任务
        result = TaskUtils.join_group_task(db, user_id, group_task_id_decimal)
        if not result:
            return error_response("参加团办任务失败", 400)

        return success_response({}, "成功参加团办任务")

    except Exception as e:
        return error_response(f"参加团办任务失败: {str(e)}", 500)
    finally:
        if db is not None:
            db.close()


@task_bp.route("/group/<group_task_id>/leave", methods=["POST"])
def leave_group_task(group_task_id):
    """退出团办任务"""
    db = None
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        db = get_db_session()
        user_id = Decimal(payload["user_id"])
        group_task_id_decimal = Decimal(group_task_id)

        result = TaskUtils.leave_group_task(db, user_id, group_task_id_decimal)
        if not result:
            return error_response("退出团办任务失败", 400)

        return success_response({}, "成功退出团办任务")

    except Exception as e:
        return error_response(f"退出团办任务失败: {str(e)}", 500)
    finally:
        if db is not None:
            db.close()


@task_bp.route("/group/my", methods=["GET"])
def get_my_group_tasks():
    """获取我参加的团办任务"""
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

        my_group_tasks = TaskUtils.get_user_group_tasks(db, user_id, page, per_page)

        return success_response(my_group_tasks, "获取我的团办任务成功")

    except Exception as e:
        return error_response(f"获取我的团办任务失败: {str(e)}", 500)
    finally:
        if db is not None:
            db.close()


@task_bp.route("/bid/<task_id>", methods=["POST"])
def bid_task(task_id):
    """竞标任务"""
    db = None
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload or payload["role"] != "staff":
            return error_response("权限不足", 403)

        data = request.get_json()
        db = get_db_session()
        user_id = Decimal(payload["user_id"])
        task_id_decimal = Decimal(task_id)

        # 检查是否已经竞标
        existing_bid = (
            db.query(BidRecord)
            .filter(BidRecord.UserID == user_id, BidRecord.TaskID == task_id_decimal)
            .first()
        )

        if existing_bid:
            return error_response("您已经对此任务进行了竞标", 400)

        # 创建竞标记录
        result = TaskUtils.create_bid(db, user_id, task_id_decimal, data)
        if not result:
            return error_response("竞标失败", 400)

        return success_response({}, "竞标成功")

    except Exception as e:
        return error_response(f"竞标失败: {str(e)}", 500)
    finally:
        if db is not None:
            db.close()


@task_bp.route("/bid/my", methods=["GET"])
def get_my_bids():
    """获取我的竞标记录"""
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

        my_bids = TaskUtils.get_user_bids(db, user_id, page, per_page, status)

        return success_response(my_bids, "获取竞标记录成功")

    except Exception as e:
        return error_response(f"获取竞标记录失败: {str(e)}", 500)
    finally:
        if db is not None:
            db.close()


@task_bp.route("/<task_id>/accept-bid/<bid_id>", methods=["POST"])
def accept_bid(task_id, bid_id):
    """接受竞标"""
    db = None
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        db = get_db_session()
        user_id = Decimal(payload["user_id"])
        task_id_decimal = Decimal(task_id)
        bid_id_decimal = Decimal(bid_id)

        # 验证任务所有权
        task = db.query(Task).filter(Task.TaskID == task_id_decimal).first()
        if not task:
            return error_response("任务不存在", 404)

        result = TaskUtils.accept_bid(db, task_id_decimal, bid_id_decimal, user_id)
        if not result:
            return error_response("接受竞标失败", 400)

        return success_response({}, "竞标已接受")

    except Exception as e:
        return error_response(f"接受竞标失败: {str(e)}", 500)
    finally:
        if db is not None:
            db.close()
