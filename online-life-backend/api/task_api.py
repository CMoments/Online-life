from flask import Blueprint, request, jsonify
from utils.auth_utils import AuthUtils
from utils.db_utils import get_db_session
from utils.response_utils import success_response, error_response
from utils.task_utils import TaskUtils
from utils.user_utils import UserUtils
from models import Task, GroupTask, GroupTaskUser, BidRecord, User, TaskParticipant
from decimal import Decimal
import traceback
from datetime import datetime
from sqlalchemy import or_, func

task_bp = Blueprint("task", __name__)


@task_bp.route("/group/list", methods=["GET"])
def get_group_tasks():
    """获取团办任务列表"""
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
        db.close()


@task_bp.route("/group/<group_task_id>", methods=["GET"])
def get_group_task_detail(group_task_id):
    """获取团办任务详情（包含多个子任务）"""
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
        db.close()


# @task_bp.route("/group/<group_task_id>/join", methods=["POST"])
# def join_group_task(group_task_id):
#     """参加团办任务"""
#     try:
#         # 验证token
#         token = request.headers.get("Authorization", "").replace("Bearer ", "")
#         payload = AuthUtils.verify_token(token)
#         if not payload:
#             return error_response("认证失败", 401)

#         db = get_db_session()
#         user_id = Decimal(payload["user_id"])
#         group_task_id_decimal = Decimal(group_task_id)

#         # 检查是否已经参加
#         existing = (
#             db.query(GroupTaskUser)
#             .filter(
#                 GroupTaskUser.UserID == user_id,
#                 GroupTaskUser.GroupTaskID == group_task_id_decimal,
#             )
#             .first()
#         )

#         if existing:
#             return error_response("您已经参加了此团办任务", 400)

#         # 参加团办任务
#         result = TaskUtils.join_group_task(db, user_id, group_task_id_decimal)
#         if not result:
#             return error_response("参加团办任务失败", 400)

#         return success_response({}, "成功参加团办任务")

#     except Exception as e:
#         return error_response(f"参加团办任务失败: {str(e)}", 500)
#     finally:
#         db.close()


@task_bp.route("/group/<group_task_id>/leave", methods=["POST"])
def leave_group_task(group_task_id):
    """退出团办任务（从所有相关Task中退出）"""
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        db = get_db_session()
        user_id = Decimal(payload["user_id"])
        group_task_id_decimal = Decimal(group_task_id)

        result = TaskUtils.leave_group_task_completely(
            db, user_id, group_task_id_decimal
        )
        if not result:
            return error_response("退出团办任务失败", 400)

        return success_response(result, "成功退出团办任务")

    except Exception as e:
        return error_response(f"退出团办任务失败: {str(e)}", 500)
    finally:
        db.close()


@task_bp.route("/task/<task_id>/leave", methods=["POST"])
def leave_specific_task(task_id):
    """退出特定的Task（但仍保留在GroupTask中）"""
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        db = get_db_session()
        user_id = Decimal(payload["user_id"])
        task_id_decimal = Decimal(task_id)

        result = TaskUtils.leave_specific_task(db, user_id, task_id_decimal)
        if not result:
            return error_response("退出任务失败", 400)

        return success_response(result, "成功退出任务")

    except Exception as e:
        return error_response(f"退出任务失败: {str(e)}", 500)
    finally:
        db.close()


@task_bp.route("/group/my", methods=["GET"])
def get_my_group_tasks():
    """获取我参加的团办任务"""
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
        db.close()


@task_bp.route("/group/create", methods=["POST"])
def create_group_task():
    """创建团办任务（重新设计）"""
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空", 400)

        # 验证必需字段
        required_fields = ["description", "task_type"]
        for field in required_fields:
            if not data.get(field):
                return error_response(f"缺少必需字段: {field}", 400)

        db = get_db_session()
        user_id = Decimal(payload["user_id"])

        # 创建团办任务
        result = TaskUtils.create_group_task_with_first_task(db, user_id, data)
        if not result:
            return error_response("创建团办任务失败", 400)

        return success_response(result, "团办任务创建成功")

    except Exception as e:
        return error_response(f"创建团办任务失败: {str(e)}", 500)
    finally:
        db.close()


@task_bp.route("/group/available", methods=["GET"])
def get_available_group_tasks():
    """获取可参与的团办任务列表（用户端）"""
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

        available_tasks = TaskUtils.get_available_group_tasks_for_users(
            db, page, per_page, task_type
        )

        return success_response(available_tasks, "获取可参与团办任务列表成功")

    except Exception as e:
        return error_response(f"获取可参与团办任务列表失败: {str(e)}", 500)
    finally:
        db.close()


@task_bp.route("/group/<group_task_id>/join", methods=["POST"])
def join_group_task(group_task_id):
    """加入团办任务（自动分配到合适的Task）"""
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        db = get_db_session()
        user_id = Decimal(payload["user_id"])
        print("user_id:", user_id)
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

        # 加入团办任务并自动分配到Task
        result = TaskUtils.join_group_task_with_auto_assignment(
            db, user_id, group_task_id_decimal
        )
        if not result:
            return error_response("加入团办任务失败", 400)

        return success_response(result, "成功加入团办任务")

    except Exception as e:
        return error_response(f"加入团办任务失败: {str(e)}", 500)
    finally:
        db.close()


@task_bp.route("/group/<group_task_id>/participants", methods=["GET"])
def get_group_task_participants(group_task_id):
    """获取团办任务参与者列表"""
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        db = get_db_session()
        group_task_id_decimal = Decimal(group_task_id)

        # 检查团办任务是否存在
        group_task = (
            db.query(GroupTask)
            .filter(GroupTask.GroupTaskID == group_task_id_decimal)
            .first()
        )

        if not group_task:
            return error_response("团办任务不存在", 404)

        # 获取参与者详细信息
        participants_query = (
            db.query(GroupTaskUser, User)
            .join(User, GroupTaskUser.UserID == User.UserID)
            .filter(GroupTaskUser.GroupTaskID == group_task_id_decimal)
            .all()
        )

        participants = []
        for group_task_user, user in participants_query:
            # 获取用户信誉信息
            reputation_info = UserUtils.get_user_reputation(db, user.UserID)

            participants.append(
                {
                    "user_id": str(user.UserID),
                    "username": user.Username,
                    "email": user.Email,
                    "phone": user.Phone,
                    "address": user.Address,
                    "role": user.Role,
                    "reputation_score": (
                        reputation_info.get("average_score", 0)
                        if reputation_info
                        else 0
                    ),
                    "reputation_count": (
                        reputation_info.get("total_reviews", 0)
                        if reputation_info
                        else 0
                    ),
                }
            )

        result = {
            "group_task_id": str(group_task_id),
            "participant_count": len(participants),
            "participants": participants,
            "is_full": len(participants) >= 5,
        }

        return success_response(result, "获取参与者列表成功")

    except Exception as e:
        return error_response(f"获取参与者列表失败: {str(e)}", 500)
    finally:
        db.close()


@task_bp.route("/staff/available", methods=["GET"])
def get_available_tasks_for_staff():
    """获取代办人员可接取的任务列表"""
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        # 验证是否为代办人员
        user_role = payload.get("role")
        if user_role != "staff":
            return error_response("只有代办人员可以查看此列表", 403)

        db = get_db_session()

        # 获取查询参数
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        task_type = request.args.get("task_type", "")

        # 调试输出所有 Task 状态
        all_tasks = db.query(Task).all()
        print(f"[调试] 数据库 Task 总数: {len(all_tasks)}")
        for t in all_tasks:
            print(f"[调试] TaskID={t.TaskID}, Status={t.Status}, CurrentBidder={t.CurrentBidder}, BidDeadline={t.BidDeadline}")

        tasks = TaskUtils.get_full_tasks_for_staff(db, page, per_page, task_type)
        print(f"[调试] 满足 staff 查询条件的任务数: {len(tasks.get('tasks', []))}")
        return success_response(tasks, "获取可接取任务列表成功")

    except Exception as e:
        return error_response(f"获取可接取任务列表失败: {str(e)}", 500)
    finally:
        db.close()


@task_bp.route("/group/<group_task_id>/status", methods=["GET"])
def get_group_task_status(group_task_id):
    """获取团办任务状态信息"""
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        db = get_db_session()
        group_task_id_decimal = Decimal(group_task_id)

        # 获取团办任务基本信息
        group_task = (
            db.query(GroupTask, Task)
            .join(Task, GroupTask.TaskID == Task.TaskID)
            .filter(GroupTask.GroupTaskID == group_task_id_decimal)
            .first()
        )

        if not group_task:
            return error_response("团办任务不存在", 404)

        group_task_obj, task_obj = group_task

        # 获取参与人数
        participant_count = (
            db.query(GroupTaskUser)
            .filter(GroupTaskUser.GroupTaskID == group_task_id_decimal)
            .count()
        )

        # 获取参与用户列表
        participants = (
            db.query(GroupTaskUser, User)
            .join(User, GroupTaskUser.UserID == User.UserID)
            .filter(GroupTaskUser.GroupTaskID == group_task_id_decimal)
            .all()
        )

        participant_list = [
            {
                "user_id": str(participant.UserID),
                "username": user.Username,
            }
            for participant, user in participants
        ]

        # 确定任务状态
        if group_task_obj.endTime and group_task_obj.endTime != "":
            status = "completed"
        elif participant_count >= 5:
            if task_obj.CurrentBidder and task_obj.CurrentBidder != "":
                status = "assigned"
            else:
                status = "waiting_for_staff"
        else:
            status = "recruiting"

        # 如果任务已满5人，获取竞标信息
        bid_info = None
        if participant_count >= 5:
            bid_count = (
                db.query(BidRecord)
                .filter(
                    BidRecord.TaskID == task_obj.TaskID,
                    BidRecord.BidStatus == "pending",
                )
                .count()
            )
            bid_info = {
                "bid_count": bid_count,
                "current_bidder": task_obj.CurrentBidder,
                "bid_deadline": task_obj.BidDeadline,
            }

        result = {
            "group_task_id": str(group_task_obj.GroupTaskID),
            "task_id": str(group_task_obj.TaskID),
            "description": task_obj.Description,
            "task_type": task_obj.TaskType,
            "estimated_time": task_obj.EstimatedTime,
            "task_location": task_obj.TaskLocation,
            "current_participants": participant_count,
            "max_participants": 5,
            "spots_remaining": max(0, 5 - participant_count),
            "status": status,
            "participants": participant_list,
            "bid_info": bid_info,
            "join_time": group_task_obj.JoinTime,
            "end_time": group_task_obj.endTime,
        }

        return success_response(result, "获取团办任务状态成功")

    except Exception as e:
        return error_response(f"获取团办任务状态失败: {str(e)}", 500)
    finally:
        db.close()


@task_bp.route("/staff/<task_id>/bid", methods=["POST"])
def bid_for_task(task_id):
    """代办人员竞标任务"""
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        # 验证是否为代办人员
        user_role = payload.get("role")
        if user_role != "staff":
            return error_response("只有代办人员可以竞标", 403)

        db = get_db_session()
        user_id = Decimal(payload["user_id"])
        task_id_decimal = Decimal(task_id)

        # 竞标任务，详细失败原因判断
        task = (
            db.query(Task)
            .filter(
                Task.TaskID == task_id_decimal,
                Task.Status == "full",
                or_(Task.CurrentBidder.is_(None), Task.CurrentBidder == ""),
            )
            .first()
        )
        if not task:
            return error_response("任务不存在或不可竞标", 400)

        # 检查竞标截止时间
        if task.BidDeadline:
            deadline = datetime.strptime(task.BidDeadline, "%Y-%m-%d %H:%M:%S")
            if datetime.now() > deadline:
                return error_response("竞标已截止", 400)

        # 检查是否已经竞标
        existing_bid = (
            db.query(BidRecord)
            .filter(BidRecord.UserID == user_id, BidRecord.TaskID == task_id_decimal)
            .first()
        )
        if existing_bid:
            return error_response("你已对该任务竞标过", 400)

        # 生成新的BidID
        max_bid_id = db.query(func.max(BidRecord.BidID)).scalar() or 0
        new_bid_id = max_bid_id + 1

        # 创建竞标记录
        bid_record = BidRecord(
            UserID=user_id,
            TaskID=task_id_decimal,
            BidID=new_bid_id,
            BidTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            BidStatus="pending",
        )
        db.add(bid_record)
        db.commit()

        # 检查是否已有5个竞标，如果是则自动分配给信誉最高的
        bid_count = (
            db.query(BidRecord)
            .filter(BidRecord.TaskID == task_id_decimal, BidRecord.BidStatus == "pending")
            .count()
        )
        if bid_count >= 5:
            TaskUtils._auto_assign_task_to_best_bidder(db, task_id_decimal)

        return success_response({
            "bid_id": str(new_bid_id),
            "task_id": str(task_id_decimal),
            "bid_time": bid_record.BidTime,
            "current_bid_count": bid_count,
            "status": "pending",
        }, "竞标成功")

    except Exception as e:
        db.rollback()
        return error_response(f"竞标失败: {str(e)}", 500)
    finally:
        db.close()


@task_bp.route("/bid/my", methods=["GET"])
def get_my_bids():
    """获取我的竞标记录"""
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
        db.close()


@task_bp.route("/task/<task_id>/participants", methods=["GET"])
def get_task_participants(task_id):
    """获取任务参与者列表"""
    try:
        # 验证token
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = AuthUtils.verify_token(token)
        if not payload:
            return error_response("认证失败", 401)

        db = get_db_session()
        task_id_decimal = Decimal(task_id)

        participants = TaskUtils.get_task_participants(db, task_id_decimal)
        if participants is None:
            return error_response("任务不存在", 404)

        return success_response(participants, "获取任务参与者成功")

    except Exception as e:
        return error_response(f"获取任务参与者失败: {str(e)}", 500)
    finally:
        db.close()


@task_bp.route("/<task_id>/accept-bid/<bid_id>", methods=["POST"])
def accept_bid(task_id, bid_id):
    """接受竞标（管理员手动接受）"""
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

        result = TaskUtils.accept_bid_manually(
            db, task_id_decimal, bid_id_decimal, user_id
        )
        if not result:
            return error_response("接受竞标失败", 400)

        return success_response({}, "竞标已接受")

    except Exception as e:
        return error_response(f"接受竞标失败: {str(e)}", 500)
    finally:
        db.close()
