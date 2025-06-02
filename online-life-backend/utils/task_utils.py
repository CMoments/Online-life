import threading
import time
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func, and_, or_
from sqlalchemy import DECIMAL
from typing import Dict, List, Optional, Any
from models import (
    Task,
    GroupTask,
    GroupTaskUser,
    BidRecord,
    User,
    TaskParticipant,
    Reputation,
    Orders,
)
import logging
from utils.user_utils import UserUtils
import traceback

logger = logging.getLogger(__name__)


class TaskUtils:
    """任务管理工具类"""

    # 存储定时器的字典，key为task_id，value为timer对象
    _assignment_timers = {}

    @staticmethod
    def get_group_tasks(
        db: Session,
        page: int = 1,
        per_page: int = 10,
        task_type: str = "",
        status: str = "active",
    ) -> Dict[str, Any]:
        """
        获取团办任务列表

        Args:
            db: 数据库会话
            page: 页码
            per_page: 每页记录数
            task_type: 任务类型过滤
            status: 状态过滤

        Returns:
            Dict: 包含任务列表和分页信息的字典
        """
        try:
            # 构建查询 - 通过Task表的GroupTaskID字段关联
            query = db.query(GroupTask, Task).join(
                Task, GroupTask.GroupTaskID == Task.GroupTaskID
            )

            # 添加过滤条件
            if task_type:
                query = query.filter(Task.TaskType == task_type)

            # 根据状态过滤
            if status == "active":
                # 假设活跃任务是还未结束的任务
                query = query.filter(
                    or_(GroupTask.endTime.is_(None), GroupTask.endTime == "")
                )
            elif status == "completed":
                query = query.filter(
                    and_(GroupTask.endTime.isnot(None), GroupTask.endTime != "")
                )

            # 计算总数
            total_count = query.count()

            # 分页查询
            offset = (page - 1) * per_page
            results = query.offset(offset).limit(per_page).all()

            # 处理结果
            group_tasks = []
            for group_task, task in results:
                # 获取参与用户数量和用户列表
                participants = (
                    db.query(GroupTaskUser)
                    .filter(GroupTaskUser.GroupTaskID == group_task.GroupTaskID)
                    .all()
                )

                participant_count = len(participants)
                # 获取第一个参与用户作为主要参与用户（或者可以根据业务逻辑调整）
                main_participant_id = participants[0].UserID if participants else None

                group_tasks.append(
                    {
                        "group_task_id": str(group_task.GroupTaskID),
                        "task_id": str(task.TaskID),
                        "task_type": task.TaskType,
                        "description": task.Description,
                        "estimated_time": task.EstimatedTime,
                        "actual_time": task.ActualTime,
                        "current_bidder": task.CurrentBidder,
                        "bid_deadline": task.BidDeadline,
                        "task_location": task.TaskLocation,
                        "main_participant_id": (
                            str(main_participant_id) if main_participant_id else ""
                        ),
                        "join_time": group_task.JoinTime,
                        "end_time": group_task.endTime,
                        "participant_count": participant_count,
                        "status": (
                            "completed"
                            if group_task.endTime and group_task.endTime != ""
                            else "active"
                        ),
                    }
                )

            total_pages = (total_count + per_page - 1) // per_page

            return {
                "tasks": group_tasks,
                "current_page": page,
                "per_page": per_page,
                "total_records": total_count,
                "total_pages": total_pages,
            }

        except Exception as e:
            logger.error(f"获取团办任务列表失败: {str(e)}")
            return {
                "tasks": [],
                "current_page": page,
                "per_page": per_page,
                "total_records": 0,
                "total_pages": 0,
            }

    @staticmethod
    def get_group_task_detail(
        db: Session, group_task_id: Decimal
    ) -> Optional[Dict[str, Any]]:
        """
        获取团办任务详情

        Args:
            db: 数据库会话
            group_task_id: 团办任务ID

        Returns:
            Optional[Dict]: 任务详情，如果不存在则返回None
        """
        try:
            # 查询团办任务和关联的任务信息
            result = (
                db.query(GroupTask, Task)
                .join(Task, GroupTask.GroupTaskID == Task.GroupTaskID)
                .filter(GroupTask.GroupTaskID == group_task_id)
                .first()
            )

            if not result:
                return None

            group_task, task = result

            # 获取参与用户列表
            participants = (
                db.query(GroupTaskUser)
                .filter(GroupTaskUser.GroupTaskID == group_task_id)
                .all()
            )

            participant_list = [
                {
                    "user_id": str(participant.UserID),
                    "join_time": group_task.JoinTime,  # 所有用户使用相同的加入时间，或者可以扩展模型单独存储
                }
                for participant in participants
            ]

            # 获取主要参与用户（第一个参与用户）
            main_participant_id = participants[0].UserID if participants else None

            return {
                "group_task_id": str(group_task.GroupTaskID),
                "task_id": str(task.TaskID),
                "task_type": task.TaskType,
                "description": task.Description,
                "estimated_time": task.EstimatedTime,
                "actual_time": task.ActualTime,
                "current_bidder": task.CurrentBidder,
                "bid_deadline": task.BidDeadline,
                "task_location": task.TaskLocation,
                "main_participant_id": (
                    str(main_participant_id) if main_participant_id else ""
                ),
                "join_time": group_task.JoinTime,
                "end_time": group_task.endTime,
                "participants": participant_list,
                "participant_count": len(participant_list),
                "status": (
                    "completed"
                    if group_task.endTime and group_task.endTime != ""
                    else "active"
                ),
            }

        except Exception as e:
            logger.error(f"获取团办任务详情失败: {str(e)}")
            return None

    @staticmethod
    def join_group_task_with_auto_assignment(
        db: Session, user_id: Decimal, group_task_id: Decimal
    ) -> Optional[Dict[str, Any]]:
        """
        加入团办任务并自动分配到合适的Task

        Args:
            db: 数据库会话
            user_id: 用户ID
            group_task_id: 团办任务ID

        Returns:
            Optional[Dict]: 分配结果，失败返回None
        """
        try:
            # 检查团办任务是否存在
            group_task = (
                db.query(GroupTask)
                .filter(GroupTask.GroupTaskID == group_task_id)
                .first()
            )
            if not group_task:
                logger.warning(f"团办任务 {group_task_id} 不存在")
                return None

            # 检查任务是否已结束
            if group_task.endTime and group_task.endTime != "":
                logger.warning(f"团办任务 {group_task_id} 已结束")
                return None

            # 检查用户是否已经参加
            existing = (
                db.query(GroupTaskUser)
                .filter(
                    GroupTaskUser.UserID == user_id,
                    GroupTaskUser.GroupTaskID == group_task_id,
                )
                .first()
            )

            if existing:
                logger.warning(f"用户 {user_id} 已经参加团办任务 {group_task_id}")
                return None

            # 查找该GroupTask下有空位的Task
            available_task = TaskUtils._find_available_task(db, group_task_id)

            # 如果没有可用Task，创建新Task
            if not available_task:
                available_task = TaskUtils._create_new_task_for_group(db, group_task_id)
                if not available_task:
                    return None

            # 添加用户到GroupTaskUser
            group_task_user = GroupTaskUser(
                UserID=user_id, TaskID=available_task.TaskID, GroupTaskID=group_task_id
            )
            db.add(group_task_user)

            # 添加用户到TaskParticipant
            existing = (
                db.query(TaskParticipant)
                .filter_by(UserID=user_id, TaskID=available_task.TaskID)
                .first()
            )

            if existing:
                existing.Status = "active"
                existing.JoinTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logger.info("用户已存在，更新状态为 active")
            else:
                task_participant = TaskParticipant(
                    UserID=user_id,
                    TaskID=available_task.TaskID,
                    JoinTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    Status="active",
                )
                db.add(task_participant)

            db.commit()

            # 检查Task是否满员，满员则自动开放给代办人员
            new_participant_count = (
                db.query(TaskParticipant)
                .filter(
                    TaskParticipant.TaskID == available_task.TaskID,
                    TaskParticipant.Status == "active",
                )
                .count()
            )
            if new_participant_count >= available_task.MaxParticipants:
                available_task.Status = "full"
                # 设置竞标截止时间（如7天后）
                available_task.BidDeadline = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
                db.commit()

            logger.info(
                f"用户 {user_id} 成功加入团办任务 {group_task_id}，分配到Task {available_task.TaskID}"
            )

            return {
                "group_task_id": str(group_task_id),
                "assigned_task_id": str(available_task.TaskID),
                "task_description": available_task.Description,
                "current_participants": new_participant_count,
                "max_participants": available_task.MaxParticipants,
                "task_status": available_task.Status,
            }

        except Exception as e:
            db.rollback()
            traceback.print_exc()
            logger.error(f"加入团办任务失败: {str(e)}")
            return None

    @staticmethod
    def _create_new_task_for_group(
        db: Session, group_task_id: Decimal
    ) -> Optional[Task]:
        """
        为GroupTask创建新的子Task
        """
        try:
            # 获取GroupTask的基本信息
            group_task = (
                db.query(GroupTask)
                .filter(GroupTask.GroupTaskID == group_task_id)
                .first()
            )
            if not group_task:
                return None

            # 获取第一个Task作为模板
            template_task = (
                db.query(Task).filter(Task.GroupTaskID == group_task_id).first()
            )
            if not template_task:
                return None

            # 生成新的TaskID
            max_task_id = db.query(func.max(Task.TaskID)).scalar() or 0
            new_task_id = max_task_id + 1

            # 创建新Task
            new_task = Task(
                TaskID=new_task_id,
                TaskType=template_task.TaskType,
                Description=template_task.Description,
                EstimatedTime=template_task.EstimatedTime,
                ActualTime="",
                CurrentBidder="",
                BidDeadline=template_task.BidDeadline,
                GroupTaskID=group_task_id,
                TaskLocation=template_task.TaskLocation,
                MaxParticipants=5,
                Status="recruiting",
            )

            db.add(new_task)
            db.flush()

            logger.info(f"为团办任务 {group_task_id} 创建新的子任务 {new_task_id}")
            return new_task

        except Exception as e:
            logger.error(f"创建新子任务失败: {str(e)}")
            return None

    @staticmethod
    def _make_task_available_for_staff(db: Session, task_id: Decimal) -> bool:
        """
        将满员的Task开放给代办人员竞标
        """
        try:
            task = db.query(Task).filter(Task.TaskID == task_id).first()
            if not task:
                return False

            # 设置竞标截止时间（7天后）
            bid_deadline = (datetime.now() + timedelta(days=7)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            task.BidDeadline = bid_deadline
            task.Status = "full"

            logger.info(f"任务 {task_id} 已满员，开放给代办人员竞标")
            return True

        except Exception as e:
            logger.error(f"开放任务给代办人员失败: {str(e)}")
            return False

    @staticmethod
    def create_group_task_with_first_task(
        db: Session, creator_id: Decimal, task_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        创建团办任务并创建第一个子任务

        Args:
            db: 数据库会话
            creator_id: 创建者用户ID
            task_data: 任务数据

        Returns:
            Optional[Dict]: 创建的任务信息，失败返回None
        """
        try:
            # 生成新的GroupTaskID
            max_group_task_id = db.query(func.max(GroupTask.GroupTaskID)).scalar() or 0
            new_group_task_id = max_group_task_id + 1

            # 生成新的TaskID
            max_task_id = db.query(func.max(Task.TaskID)).scalar() or 0
            new_task_id = max_task_id + 1

            # 创建GroupTask记录
            group_task = GroupTask(
                GroupTaskID=new_group_task_id,
                JoinTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                endTime="",
            )

            # 创建第一个Task记录
            task = Task(
                TaskID=new_task_id,
                TaskType=task_data.get("task_type", "group"),
                Description=task_data.get("description", ""),
                EstimatedTime=task_data.get("estimated_time", ""),
                ActualTime="",
                CurrentBidder="",
                BidDeadline=task_data.get("bid_deadline", ""),
                GroupTaskID=new_group_task_id,
                TaskLocation=task_data.get("task_location", ""),
                MaxParticipants=5,
                Status="recruiting",
            )

            # 创建创建者的GroupTask参与记录
            group_task_user = GroupTaskUser(
                UserID=creator_id, TaskID=new_task_id, GroupTaskID=new_group_task_id
            )

            # 创建创建者的Task参与记录
            task_participant = TaskParticipant(
                UserID=creator_id,
                TaskID=new_task_id,
                JoinTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                Status="active",
            )

            db.add(group_task)
            db.flush()
            db.add(task)
            db.flush()
            db.add(group_task_user)
            db.add(task_participant)
            db.commit()

            # 自动补全：如果参与人数已满，设为 full
            participants = db.query(GroupTaskUser).filter(GroupTaskUser.GroupTaskID == new_group_task_id).count()
            if participants >= 5:
                task.Status = "full"
                db.commit()

            logger.info(
                f"用户 {creator_id} 成功创建团办任务 {new_group_task_id}，第一个子任务 {new_task_id}"
            )

            return {
                "group_task_id": str(new_group_task_id),
                "first_task_id": str(new_task_id),
                "task_type": task.TaskType,
                "description": task.Description,
                "estimated_time": task.EstimatedTime,
                "task_location": task.TaskLocation,
                "bid_deadline": task.BidDeadline,
                "creator_id": str(creator_id),
                "join_time": group_task.JoinTime,
                "current_participants": 1,
                "max_participants": 5,
                "status": "recruiting",
            }

        except Exception as e:
            db.rollback()
            logger.error(f"创建团办任务失败: {str(e)}")
            return None

    @staticmethod
    def leave_group_task_completely(
        db: Session, user_id: Decimal, group_task_id: Decimal
    ) -> Optional[Dict[str, Any]]:
        """
        完全退出团办任务（从所有相关Task中退出）

        Args:
            db: 数据库会话
            user_id: 用户ID
            group_task_id: 团办任务ID

        Returns:
            Optional[Dict]: 退出结果，失败返回None
        """
        try:
            # 查找用户在该GroupTask中的所有参与记录
            user_participations = (
                db.query(GroupTaskUser)
                .filter(
                    GroupTaskUser.UserID == user_id,
                    GroupTaskUser.GroupTaskID == group_task_id,
                )
                .all()
            )

            if not user_participations:
                logger.warning(f"用户 {user_id} 未参加团办任务 {group_task_id}")
                return None

            left_tasks = []

            for participation in user_participations:
                task_id = participation.TaskID

                # 更新TaskParticipant状态
                task_participant = (
                    db.query(TaskParticipant)
                    .filter(
                        TaskParticipant.UserID == user_id,
                        TaskParticipant.TaskID == task_id,
                    )
                    .first()
                )

                if task_participant:
                    task_participant.Status = "left"
                    left_tasks.append(str(task_id))

                # 删除GroupTaskUser记录
                db.delete(participation)

                # 检查Task是否需要重新开放招募
                TaskUtils._check_and_reopen_task_recruitment(db, task_id)

            db.commit()

            logger.info(
                f"用户 {user_id} 成功退出团办任务 {group_task_id}，退出的Task: {left_tasks}"
            )

            return {
                "group_task_id": str(group_task_id),
                "left_tasks": left_tasks,
                "status": "success",
            }

        except Exception as e:
            db.rollback()
            logger.error(f"退出团办任务失败: {str(e)}")
            return None

    @staticmethod
    def leave_specific_task(
        db: Session, user_id: Decimal, task_id: Decimal
    ) -> Optional[Dict[str, Any]]:
        """
        退出特定的Task（但仍保留在GroupTask中）

        Args:
            db: 数据库会话
            user_id: 用户ID
            task_id: 任务ID

        Returns:
            Optional[Dict]: 退出结果，失败返回None
        """
        try:
            # 查找Task参与记录
            task_participant = (
                db.query(TaskParticipant)
                .filter(
                    TaskParticipant.UserID == user_id,
                    TaskParticipant.TaskID == task_id,
                    TaskParticipant.Status == "active",
                )
                .first()
            )

            if not task_participant:
                logger.warning(f"用户 {user_id} 未参加任务 {task_id}")
                return None

            # 获取Task信息
            task = db.query(Task).filter(Task.TaskID == task_id).first()
            if not task:
                return None

            group_task_id = task.GroupTaskID

            # 更新TaskParticipant状态
            task_participant.Status = "left"

            # 更新GroupTaskUser记录（指向其他Task或删除）
            group_task_user = (
                db.query(GroupTaskUser)
                .filter(
                    GroupTaskUser.UserID == user_id,
                    GroupTaskUser.TaskID == task_id,
                    GroupTaskUser.GroupTaskID == group_task_id,
                )
                .first()
            )

            if group_task_user:
                # 尝试重新分配到其他Task
                available_task = TaskUtils._find_available_task(
                    db, group_task_id, exclude_task_id=task_id
                )

                if available_task:
                    # 重新分配到其他Task
                    group_task_user.TaskID = available_task.TaskID

                    # 创建新的TaskParticipant记录
                    new_task_participant = TaskParticipant(
                        UserID=user_id,
                        TaskID=available_task.TaskID,
                        JoinTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        Status="active",
                    )
                    db.add(new_task_participant)

                    reassigned_task_id = available_task.TaskID
                else:
                    # 没有其他可用Task，创建新Task
                    new_task = TaskUtils._create_new_task_for_group(db, group_task_id)
                    if new_task:
                        group_task_user.TaskID = new_task.TaskID

                        new_task_participant = TaskParticipant(
                            UserID=user_id,
                            TaskID=new_task.TaskID,
                            JoinTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            Status="active",
                        )
                        db.add(new_task_participant)

                        reassigned_task_id = new_task.TaskID
                    else:
                        # 创建失败，完全退出GroupTask
                        db.delete(group_task_user)
                        reassigned_task_id = None

            # 检查原Task是否需要重新开放招募
            TaskUtils._check_and_reopen_task_recruitment(db, task_id)

            db.commit()

            logger.info(f"用户 {user_id} 成功退出任务 {task_id}")

            return {
                "left_task_id": str(task_id),
                "reassigned_task_id": (
                    str(reassigned_task_id) if reassigned_task_id else None
                ),
                "group_task_id": str(group_task_id),
                "status": "success",
            }

        except Exception as e:
            db.rollback()
            logger.error(f"退出任务失败: {str(e)}")
            return None

    @staticmethod
    def _find_available_task(
        db: Session, group_task_id: Decimal, exclude_task_id: Decimal = None
    ) -> Optional[Task]:
        """
        查找GroupTask下有空位的Task
        """
        try:
            query = db.query(Task).filter(
                Task.GroupTaskID == group_task_id, Task.Status == "recruiting"
            )

            if exclude_task_id:
                query = query.filter(Task.TaskID != exclude_task_id)

            tasks = query.all()

            for task in tasks:
                current_participants = (
                    db.query(TaskParticipant)
                    .filter(
                        TaskParticipant.TaskID == task.TaskID,
                        TaskParticipant.Status == "active",
                    )
                    .count()
                )

                if current_participants < task.MaxParticipants:
                    return task

            return None

        except Exception as e:
            logger.error(f"查找可用Task失败: {str(e)}")
            return None

    @staticmethod
    def _create_new_task_for_group(
        db: Session, group_task_id: Decimal
    ) -> Optional[Task]:
        """
        为GroupTask创建新的子Task
        """
        try:
            # 获取第一个Task作为模板
            template_task = (
                db.query(Task).filter(Task.GroupTaskID == group_task_id).first()
            )

            if not template_task:
                return None

            # 生成新的TaskID
            max_task_id = db.query(func.max(Task.TaskID)).scalar() or 0
            new_task_id = max_task_id + 1

            # 创建新Task
            new_task = Task(
                TaskID=new_task_id,
                TaskType=template_task.TaskType,
                Description=template_task.Description,
                EstimatedTime=template_task.EstimatedTime,
                ActualTime="",
                CurrentBidder="",
                BidDeadline=template_task.BidDeadline,
                GroupTaskID=group_task_id,
                TaskLocation=template_task.TaskLocation,
                MaxParticipants=5,
                Status="recruiting",
            )

            db.add(new_task)
            db.flush()

            logger.info(f"为团办任务 {group_task_id} 创建新的子任务 {new_task_id}")
            return new_task

        except Exception as e:
            logger.error(f"创建新子任务失败: {str(e)}")
            return None

    @staticmethod
    def _make_task_available_for_staff(db: Session, task_id: Decimal) -> bool:
        """
        将满员的Task开放给代办人员竞标
        """
        try:
            task = db.query(Task).filter(Task.TaskID == task_id).first()
            if not task:
                return False

            # 设置竞标截止时间（7天后）
            bid_deadline = (datetime.now() + timedelta(days=7)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            task.BidDeadline = bid_deadline
            task.Status = "full"

            logger.info(f"任务 {task_id} 已满员，开放给代办人员竞标")
            return True

        except Exception as e:
            logger.error(f"开放任务给代办人员失败: {str(e)}")
            return False

    @staticmethod
    def _check_and_reopen_task_recruitment(db: Session, task_id: Decimal) -> bool:
        """
        检查Task是否需要重新开放招募
        """
        try:
            task = db.query(Task).filter(Task.TaskID == task_id).first()
            if not task:
                return False

            # 统计当前活跃参与者
            current_participants = (
                db.query(TaskParticipant)
                .filter(
                    TaskParticipant.TaskID == task_id,
                    TaskParticipant.Status == "active",
                )
                .count()
            )

            # 如果人数不足且Task状态为full，重新开放招募
            if current_participants < task.MaxParticipants and task.Status == "full":
                task.Status = "recruiting"
                task.CurrentBidder = ""

                # 取消所有pending的竞标
                pending_bids = (
                    db.query(BidRecord)
                    .filter(
                        BidRecord.TaskID == task_id, BidRecord.BidStatus == "pending"
                    )
                    .all()
                )

                for bid in pending_bids:
                    bid.BidStatus = "cancelled"

                logger.info(
                    f"任务 {task_id} 重新开放招募，当前人数: {current_participants}"
                )
                return True

            return False

        except Exception as e:
            logger.error(f"检查任务招募状态失败: {str(e)}")
            return False

    @staticmethod
    def get_user_group_tasks(
        db: Session, user_id: Decimal, page: int = 1, per_page: int = 10
    ) -> Dict[str, Any]:
        """
        获取用户参加的团办任务

        Args:
            db: 数据库会话
            user_id: 用户ID
            page: 页码
            per_page: 每页记录数

        Returns:
            Dict: 包含任务列表和分页信息的字典
        """
        try:
            # 构建查询
            query = (
                db.query(GroupTask, Task, GroupTaskUser)
                .join(GroupTaskUser, GroupTask.GroupTaskID == GroupTaskUser.GroupTaskID)
                .join(Task, GroupTask.GroupTaskID == Task.GroupTaskID)
                .filter(GroupTaskUser.UserID == user_id)
                .order_by(desc(GroupTask.GroupTaskID))
            )
            print(type(user_id))

            # 计算总数
            total_count = query.count()

            # 分页查询
            offset = (page - 1) * per_page
            results = query.offset(offset).limit(per_page).all()
            print(results)

            # 处理结果
            my_group_tasks = []
            for group_task, task, group_task_user in results:
                # 获取参与用户数量
                participant_count = (
                    db.query(GroupTaskUser)
                    .filter(GroupTaskUser.GroupTaskID == group_task.GroupTaskID)
                    .count()
                )

                my_group_tasks.append(
                    {
                        "group_task_id": str(group_task.GroupTaskID),
                        "task_id": str(task.TaskID),
                        "task_type": task.TaskType,
                        "description": task.Description,
                        "estimated_time": task.EstimatedTime,
                        "actual_time": task.ActualTime,
                        "current_bidder": task.CurrentBidder,
                        "bid_deadline": task.BidDeadline,
                        "join_time": group_task.JoinTime,
                        "end_time": group_task.endTime,
                        "participant_count": participant_count,
                        "status": (
                            "completed"
                            if group_task.endTime and group_task.endTime != ""
                            else "active"
                        ),
                    }
                )

            total_pages = (total_count + per_page - 1) // per_page

            return {
                "tasks": my_group_tasks,
                "current_page": page,
                "per_page": per_page,
                "total_records": total_count,
                "total_pages": total_pages,
            }

        except Exception as e:
            traceback.print_exc()
            logger.error(f"获取用户团办任务失败: {str(e)}")
            return {
                "tasks": [],
                "current_page": page,
                "per_page": per_page,
                "total_records": 0,
                "total_pages": 0,
            }

    @staticmethod
    def create_bid(
        db: Session, user_id: Decimal, task_id: Decimal, bid_data: Dict[str, Any]
    ) -> bool:
        """
        创建竞标记录

        Args:
            db: 数据库会话
            user_id: 用户ID
            task_id: 任务ID
            bid_data: 竞标数据

        Returns:
            bool: 操作是否成功
        """
        try:
            # 检查任务是否存在
            task = db.query(Task).filter(Task.TaskID == task_id).first()
            if not task:
                logger.warning(f"任务 {task_id} 不存在")
                return False

            # 检查竞标截止时间（如果有的话）
            if task.BidDeadline:
                try:
                    deadline = datetime.strptime(task.BidDeadline, "%Y-%m-%d %H:%M:%S")
                    if datetime.now() > deadline:
                        logger.warning(f"任务 {task_id} 竞标已截止")
                        return False
                except ValueError:
                    logger.warning(
                        f"任务 {task_id} 竞标截止时间格式不正确: {task.BidDeadline}"
                    )

            # 检查是否已经竞标
            existing_bid = (
                db.query(BidRecord)
                .filter(BidRecord.UserID == user_id, BidRecord.TaskID == task_id)
                .first()
            )

            if existing_bid:
                logger.warning(f"用户 {user_id} 已经对任务 {task_id} 进行了竞标")
                return False

            # 生成BidID
            max_bid_id = db.query(func.max(BidRecord.BidID)).scalar() or 0
            new_bid_id = max_bid_id + 1

            # 创建竞标记录
            bid_record = BidRecord(
                UserID=user_id,
                TaskID=task_id,
                BidID=new_bid_id,
                # BidAmount=bid_data.get("bid_amount", "0"),
                BidTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                BidStatus="pending",
            )

            db.add(bid_record)
            db.commit()

            logger.info(f"用户 {user_id} 成功竞标任务 {task_id}")
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"创建竞标记录失败: {str(e)}")
            return False

    @staticmethod
    def auto_assign_task_if_needed(db: Session, task_id: Decimal) -> bool:
        """
        检查是否需要自动分配任务（当有前5位竞标者时，选择信誉最高的一位）

        Args:
            db: 数据库会话
            task_id: 任务ID

        Returns:
            bool: 是否进行了自动分配
        """
        try:
            # 获取任务的所有待处理竞标记录，按时间排序
            pending_bids = (
                db.query(BidRecord)
                .filter(BidRecord.TaskID == task_id, BidRecord.BidStatus == "pending")
                .order_by(asc(BidRecord.BidTime))  # 按竞标时间升序
                .limit(5)  # 只取前5位
                .all()
            )

            # 如果竞标者不足5位，不进行自动分配
            if len(pending_bids) < 5:
                logger.info(
                    f"任务 {task_id} 竞标者不足5位，当前有 {len(pending_bids)} 位"
                )
                return False

            # 获取前5位竞标者的信誉信息
            bidder_ids = [bid.UserID for bid in pending_bids]

            # 修改：使用UserUtils获取每个竞标者的信誉分数
            bidders_with_reputation = []
            for bidder_id in bidder_ids:
                reputation_info = UserUtils.get_user_reputation(db, bidder_id)
                user = db.query(User).filter(User.UserID == bidder_id).first()
                if user and reputation_info:
                    bidders_with_reputation.append(
                        {
                            "user": user,
                            "user_id": bidder_id,
                            "reputation_score": reputation_info["average_score"],
                        }
                    )

            # 按信誉分数降序排序
            bidders_with_reputation.sort(
                key=lambda x: x["reputation_score"], reverse=True
            )

            if not bidders_with_reputation:
                logger.warning(f"任务 {task_id} 无法获取竞标者信誉信息")
                return False

            # 选择信誉最高的用户
            highest_reputation_bidder = bidders_with_reputation[0]
            winner_user_id = highest_reputation_bidder["user_id"]

            # 找到获胜者的竞标记录
            winner_bid = next(
                (bid for bid in pending_bids if bid.UserID == winner_user_id), None
            )

            if not winner_bid:
                logger.error(f"任务 {task_id} 无法找到获胜者的竞标记录")
                return False

            # 自动接受该竞标
            result = TaskUtils.accept_bid_internal(
                db, task_id, winner_bid.BidID, winner_user_id
            )

            if result:
                logger.info(
                    f"自动分配任务 {task_id} 给用户 {winner_user_id}，"
                    f"信誉分数: {highest_reputation_bidder['reputation_score']}"
                )
                return True
            else:
                logger.error(f"自动分配任务 {task_id} 失败")
                return False

        except Exception as e:
            logger.error(f"自动分配任务失败: {str(e)}")
            return False

    @staticmethod
    def _auto_assign_task_to_best_bidder(db: Session, task_id: Decimal) -> bool:
        """
        自动将任务分配给前5个竞标中信誉最高的代办人员，并同步写入Task和Orders分配字段
        """
        try:
            # 获取前5个竞标记录
            bids = (
                db.query(BidRecord)
                .filter(BidRecord.TaskID == task_id, BidRecord.BidStatus == "pending")
                .order_by(BidRecord.BidTime)
                .limit(5)
                .all()
            )
            if len(bids) < 5:
                return False
            # 获取竞标者的信誉分数
            best_bidder = None
            highest_reputation = -1
            for bid in bids:
                avg_score = (
                    db.query(func.avg(func.cast(Reputation.Score, DECIMAL)))
                    .filter(Reputation.UserID == bid.UserID)
                    .scalar()
                    or 0
                )
                if avg_score > highest_reputation:
                    highest_reputation = avg_score
                    best_bidder = bid
            if not best_bidder:
                return False
            # 更新任务状态
            task = db.query(Task).filter(Task.TaskID == task_id).first()
            if task:
                task.CurrentBidder = str(best_bidder.UserID)
                task.Status = "assigned"
                # 同步写入 Orders（如有）
                order = db.query(Orders).filter(Orders.OrderID == task_id).first()
                if order:
                    order.StaffID = best_bidder.UserID
                    order.OrderStatus = "assigned"
            # 更新竞标状态
            best_bidder.BidStatus = "accepted"
            for bid in bids:
                if bid.BidID != best_bidder.BidID:
                    bid.BidStatus = "rejected"
            db.commit()
            logger.info(
                f"任务 {task_id} 已自动分配给代办人员 {best_bidder.UserID}（信誉分数: {highest_reputation}）"
            )
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"自动分配任务失败: {str(e)}")
            return False

    @staticmethod
    def accept_bid_internal(
        db: Session, task_id: Decimal, bid_id: Decimal, winner_user_id: Decimal
    ) -> bool:
        """
        内部方法：接受竞标（用于自动分配），并同步写入Task和Orders分配字段
        """
        try:
            # 查找任务记录
            task = db.query(Task).filter(Task.TaskID == task_id).first()
            if not task:
                logger.warning(f"任务 {task_id} 不存在")
                return False
            # 更新任务的当前竞标者
            task.CurrentBidder = str(winner_user_id)
            task.Status = "assigned"
            # 同步写入 Orders（如有）
            order = db.query(Orders).filter(Orders.OrderID == task_id).first()
            if order:
                order.StaffID = winner_user_id
                order.OrderStatus = "assigned"
            # 更新获胜的竞标记录状态
            winner_bid = (
                db.query(BidRecord)
                .filter(
                    BidRecord.TaskID == task_id,
                    BidRecord.BidID == bid_id,
                    BidRecord.UserID == winner_user_id,
                )
                .first()
            )
            if winner_bid:
                winner_bid.BidStatus = "accepted"
            # 拒绝其他竞标
            other_bids = (
                db.query(BidRecord)
                .filter(
                    BidRecord.TaskID == task_id,
                    BidRecord.UserID != winner_user_id,
                    BidRecord.BidStatus == "pending",
                )
                .all()
            )
            for other_bid in other_bids:
                other_bid.BidStatus = "rejected"
            db.commit()
            logger.info(f"竞标已被接受: task_id={task_id}, winner={winner_user_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"接受竞标失败: {str(e)}")
            return False

    @staticmethod
    def accept_bid_manually(
        db: Session, task_id: Decimal, bid_id: Decimal, accepter_user_id: Decimal
    ) -> bool:
        """
        手动接受竞标（管理员操作）

        Args:
            db: 数据库会话
            task_id: 任务ID
            bid_id: 竞标ID
            accepter_user_id: 接受竞标的用户ID

        Returns:
            bool: 操作是否成功
        """
        try:
            # 查找竞标记录
            bid_record = (
                db.query(BidRecord)
                .filter(BidRecord.TaskID == task_id, BidRecord.BidID == bid_id)
                .first()
            )

            if not bid_record:
                logger.warning(f"竞标记录不存在: task_id={task_id}, bid_id={bid_id}")
                return False

            return TaskUtils.accept_bid_internal(db, task_id, bid_id, bid_record.UserID)

        except Exception as e:
            logger.error(f"手动接受竞标失败: {str(e)}")
            return False

    @staticmethod
    def get_user_bids(
        db: Session,
        user_id: Decimal,
        page: int = 1,
        per_page: int = 10,
        status: str = "",
    ) -> Dict[str, Any]:
        """
        获取用户的竞标记录

        Args:
            db: 数据库会话
            user_id: 用户ID
            page: 页码
            per_page: 每页记录数
            status: 状态过滤

        Returns:
            Dict: 包含竞标记录和分页信息的字典
        """
        try:
            # 构建查询
            query = (
                db.query(BidRecord, Task)
                .join(Task, BidRecord.TaskID == Task.TaskID)
                .filter(BidRecord.UserID == user_id)
            )

            # 添加状态过滤
            if status:
                query = query.filter(BidRecord.BidStatus == status)

            query = query.order_by(desc(BidRecord.BidTime))

            # 计算总数
            total_count = query.count()

            # 分页查询
            offset = (page - 1) * per_page
            results = query.offset(offset).limit(per_page).all()

            # 处理结果
            my_bids = []
            for bid_record, task in results:
                my_bids.append(
                    {
                        "bid_id": str(bid_record.BidID),
                        "task_id": str(bid_record.TaskID),
                        "task_type": task.TaskType,
                        "description": task.Description,
                        "estimated_time": task.EstimatedTime,
                        "current_bidder": task.CurrentBidder,
                        "bid_deadline": task.BidDeadline,
                        # "bid_amount": bid_record.BidAmount,
                        "bid_time": bid_record.BidTime,
                        "bid_status": bid_record.BidStatus,
                        "is_current_bidder": task.CurrentBidder == str(user_id),
                    }
                )

            total_pages = (total_count + per_page - 1) // per_page

            return {
                "bids": my_bids,
                "current_page": page,
                "per_page": per_page,
                "total_records": total_count,
                "total_pages": total_pages,
            }

        except Exception as e:
            logger.error(f"获取用户竞标记录失败: {str(e)}")
            return {
                "bids": [],
                "current_page": page,
                "per_page": per_page,
                "total_records": 0,
                "total_pages": 0,
            }

    @staticmethod
    def get_task_bids_summary(db: Session, task_id: Decimal) -> Dict[str, Any]:
        """
        获取任务的竞标摘要信息

        Args:
            db: 数据库会话
            task_id: 任务ID

        Returns:
            Dict: 竞标摘要信息
        """
        try:
            # 获取该任务的所有竞标记录
            bids = (
                db.query(BidRecord, User)
                .join(User, BidRecord.UserID == User.UserID)
                .filter(BidRecord.TaskID == task_id)
                .order_by(asc(BidRecord.BidTime))
                .all()
            )

            total_bids = len(bids)
            pending_bids = len([bid for bid, _ in bids if bid.BidStatus == "pending"])

            # 获取前5位竞标者信息
            top_5_bids = bids[:5]
            top_5_info = []

            for bid_record, credit_score in top_5_bids:
                top_5_info.append(
                    {
                        "user_id": str(bid_record.UserID),
                        "bid_time": bid_record.BidTime,
                        # "bid_amount": bid_record.BidAmount,
                        "credit_score": float(credit_score),
                        "status": bid_record.BidStatus,
                    }
                )

            return {
                "task_id": str(task_id),
                "total_bids": total_bids,
                "pending_bids": pending_bids,
                "top_5_bids": top_5_info,
                "auto_assign_ready": pending_bids >= 5,
            }

        except Exception as e:
            logger.error(f"获取任务竞标摘要失败: {str(e)}")
            return {
                "task_id": str(task_id),
                "total_bids": 0,
                "pending_bids": 0,
                "top_5_bids": [],
                "auto_assign_ready": False,
            }

    @staticmethod
    def complete_group_task(
        db: Session, group_task_id: Decimal, user_id: Decimal
    ) -> bool:
        """
        完成团办任务

        Args:
            db: 数据库会话
            group_task_id: 团办任务ID
            user_id: 操作用户ID

        Returns:
            bool: 操作是否成功
        """
        try:
            # 查找团办任务
            group_task = (
                db.query(GroupTask)
                .filter(GroupTask.GroupTaskID == group_task_id)
                .first()
            )

            if not group_task:
                logger.warning(f"团办任务 {group_task_id} 不存在")
                return False

            # 检查用户是否有权限完成任务（例如是否是参与者或管理员）
            participant = (
                db.query(GroupTaskUser)
                .filter(
                    GroupTaskUser.GroupTaskID == group_task_id,
                    GroupTaskUser.UserID == user_id,
                )
                .first()
            )

            if not participant:
                logger.warning(f"用户 {user_id} 不是团办任务 {group_task_id} 的参与者")
                return False

            # 标记任务完成
            group_task.endTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 更新相关任务的实际时间
            task = db.query(Task).filter(Task.TaskID == group_task.TaskID).first()
            if task and (not task.ActualTime or task.ActualTime == ""):
                task.ActualTime = group_task.endTime

            db.commit()
            logger.info(f"团办任务 {group_task_id} 已完成")
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"完成团办任务失败: {str(e)}")
            return False

    @staticmethod
    def get_task_statistics(db: Session) -> Dict[str, Any]:
        """
        获取任务统计信息

        Args:
            db: 数据库会话

        Returns:
            Dict: 统计信息
        """
        try:
            # 总任务数
            total_tasks = db.query(Task).count()

            # 团办任务数
            total_group_tasks = db.query(GroupTask).count()

            # 活跃团办任务数
            active_group_tasks = (
                db.query(GroupTask)
                .filter(or_(GroupTask.endTime.is_(None), GroupTask.endTime == ""))
                .count()
            )

            # 已完成团办任务数
            completed_group_tasks = (
                db.query(GroupTask)
                .filter(and_(GroupTask.endTime.isnot(None), GroupTask.endTime != ""))
                .count()
            )

            # 总竞标数
            total_bids = db.query(BidRecord).count()

            # 按任务类型统计
            task_type_stats = (
                db.query(Task.TaskType, func.count(Task.TaskID))
                .group_by(Task.TaskType)
                .all()
            )

            return {
                "total_tasks": total_tasks,
                "total_group_tasks": total_group_tasks,
                "active_group_tasks": active_group_tasks,
                "completed_group_tasks": completed_group_tasks,
                "total_bids": total_bids,
                "task_type_distribution": [
                    {"task_type": task_type, "count": count}
                    for task_type, count in task_type_stats
                ],
            }

        except Exception as e:
            logger.error(f"获取任务统计失败: {str(e)}")
            return {
                "total_tasks": 0,
                "total_group_tasks": 0,
                "active_group_tasks": 0,
                "completed_group_tasks": 0,
                "total_bids": 0,
                "task_type_distribution": [],
            }

    @staticmethod
    def create_group_task(
        db: Session, creator_id: Decimal, task_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        创建团办任务

        Args:
            db: 数据库会话
            creator_id: 创建者用户ID
            task_data: 任务数据

        Returns:
            Optional[Dict]: 创建的任务信息，失败返回None
        """
        try:
            # 生成新的TaskID
            max_task_id = db.query(func.max(Task.TaskID)).scalar() or 0
            new_task_id = max_task_id + 1

            # 生成新的GroupTaskID
            max_group_task_id = db.query(func.max(GroupTask.GroupTaskID)).scalar() or 0
            new_group_task_id = max_group_task_id + 1

            # 创建GroupTask记录
            group_task = GroupTask(
                GroupTaskID=new_group_task_id,
                JoinTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                endTime="",
            )

            # 创建Task记录
            task = Task(
                TaskID=new_task_id,
                TaskType=task_data.get("task_type", "group"),
                Description=task_data.get("description", ""),
                EstimatedTime=task_data.get("estimated_time", ""),
                ActualTime="",
                CurrentBidder="",
                BidDeadline=task_data.get("bid_deadline", ""),
                GroupTaskID=new_group_task_id,
                TaskLocation=task_data.get("task_location", ""),
            )

            # 创建创建者的参与记录
            group_task_user = GroupTaskUser(UserID=creator_id, TaskID=new_task_id)

            db.add(group_task)
            db.flush()
            db.add(task)
            db.flush()
            db.add(group_task_user)
            db.commit()

            # 自动补全：如果参与人数已满，设为 full
            participants = db.query(GroupTaskUser).filter(GroupTaskUser.GroupTaskID == new_group_task_id).count()
            if participants >= 5:
                task.Status = "full"
                db.commit()

            logger.info(f"用户 {creator_id} 成功创建团办任务 {new_group_task_id}")

            return {
                "group_task_id": str(new_group_task_id),
                "task_id": str(new_task_id),
                "task_type": task.TaskType,
                "description": task.Description,
                "estimated_time": task.EstimatedTime,
                "task_location": task.TaskLocation,
                "bid_deadline": task.BidDeadline,
                "creator_id": str(creator_id),
                "join_time": group_task.JoinTime,
                "participant_count": 1,
                "status": "recruiting",  # 招募中
            }

        except Exception as e:
            db.rollback()
            logger.error(f"创建团办任务失败: {str(e)}")
            return None

    @staticmethod
    def check_and_create_task_for_staff(db: Session, group_task_id: Decimal) -> bool:
        """
        检查团办任务是否达到5人，如果达到则创建可供代办人员接取的任务

        Args:
            db: 数据库会话
            group_task_id: 团办任务ID

        Returns:
            bool: 是否成功创建了代办任务
        """
        try:
            # 统计参与人数
            participant_count = (
                db.query(GroupTaskUser)
                .filter(GroupTaskUser.GroupTaskID == group_task_id)
                .count()
            )

            if participant_count < 5:
                logger.info(
                    f"团办任务 {group_task_id} 参与人数不足5人，当前 {participant_count} 人"
                )
                return False

            # 检查是否已经创建了代办任务（避重复创建）
            group_task = (
                db.query(GroupTask)
                .filter(GroupTask.GroupTaskID == group_task_id)
                .first()
            )
            if not group_task:
                return False

            # 获取关联的原始任务
            original_task = (
                db.query(Task).filter(Task.TaskID == group_task.TaskID).first()
            )
            if not original_task:
                return False

            # 检查是否已有代办人员竞标记录（说明已经开放给代办人员）
            existing_bids = (
                db.query(BidRecord)
                .filter(BidRecord.TaskID == original_task.TaskID)
                .count()
            )
            if existing_bids > 0:
                logger.info(f"团办任务 {group_task_id} 已经开放给代办人员")
                return False

            # 更新任务状态，开放给代办人员竞标
            # 设置竞标截止时间（比如7天后）
            bid_deadline = (datetime.now() + timedelta(days=7)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            original_task.BidDeadline = bid_deadline

            # 标记团办任务为"已满员，等待代办"状态
            # 这里可以通过添加一个状态字段或者通过其他方式标记

            db.commit()

            logger.info(f"团办任务 {group_task_id} 已达到5人，开放给代办人员竞标")
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"检查并创建代办任务失败: {str(e)}")
            return False

    @staticmethod
    def get_available_group_tasks_for_users(
        db: Session, page: int = 1, per_page: int = 10, task_type: str = ""
    ) -> Dict[str, Any]:
        """
        获取用户可参与的团办任务列表（人数未满5人的）

        Args:
            db: 数据库会话
            page: 页码
            per_page: 每页记录数
            task_type: 任务类型过滤

        Returns:
            Dict: 包含任务列表和分页信息的字典
        """
        try:
            # 构建子查询：查找参与人数 < 5 的 GroupTaskID
            subquery = (
                db.query(
                    GroupTaskUser.GroupTaskID,
                    func.count(GroupTaskUser.UserID).label("participant_count"),
                )
                .group_by(GroupTaskUser.GroupTaskID)
                .having(func.count(GroupTaskUser.UserID) < 5)
                .subquery()
            )

            # 主查询：从 Task 和 GroupTask 联查，并筛选人数 < 5，且 endTime 未结束的任务
            query = (
                db.query(GroupTask, Task)
                .join(Task, Task.GroupTaskID == GroupTask.GroupTaskID)
                .join(subquery, GroupTask.GroupTaskID == subquery.c.GroupTaskID)
                .filter(or_(GroupTask.endTime.is_(None), GroupTask.endTime == ""))
            )

            # 添加任务类型过滤
            if task_type:
                query = query.filter(Task.TaskType == task_type)

            # 计算总数
            total_count = query.count()

            # 分页查询
            offset = (page - 1) * per_page
            results = query.offset(offset).limit(per_page).all()

            # 处理结果
            available_tasks = []
            for group_task, task in results:
                # 获取当前参与人数
                participant_count = (
                    db.query(GroupTaskUser)
                    .filter(GroupTaskUser.GroupTaskID == group_task.GroupTaskID)
                    .count()
                )

                available_tasks.append(
                    {
                        "group_task_id": str(group_task.GroupTaskID),
                        "task_id": str(task.TaskID),
                        "task_type": task.TaskType,
                        "description": task.Description,
                        "estimated_time": task.EstimatedTime,
                        "task_location": task.TaskLocation,
                        "bid_deadline": task.BidDeadline,
                        "join_time": group_task.JoinTime,
                        "current_participants": participant_count,
                        "max_participants": 5,
                        "spots_remaining": 5 - participant_count,
                        "status": "recruiting",
                    }
                )

            total_pages = (total_count + per_page - 1) // per_page

            return {
                "tasks": available_tasks,
                "current_page": page,
                "per_page": per_page,
                "total_records": total_count,
                "total_pages": total_pages,
            }

        except Exception as e:
            traceback.print_exc()
            logger.error(f"获取可参与团办任务列表失败: {str(e)}")
            return {
                "tasks": [],
                "current_page": page,
                "per_page": per_page,
                "total_records": 0,
                "total_pages": 0,
            }

    @staticmethod
    def get_full_tasks_for_staff(
        db: Session, page: int = 1, per_page: int = 10, task_type: str = ""
    ) -> Dict[str, Any]:
        """
        获取代办人员可接取的任务列表（满员未被接取的Task + 已分配但未完成的Task）
        """
        try:
            # 原有可竞标任务
            query = db.query(Task).filter(
                Task.Status == "full",
                or_(Task.CurrentBidder.is_(None), Task.CurrentBidder == ""),
            )
            # 新增：已分配但未完成的任务
            assigned_query = db.query(Task).filter(Task.Status == "assigned")
            if task_type:
                query = query.filter(Task.TaskType == task_type)
                assigned_query = assigned_query.filter(Task.TaskType == task_type)
            total_count = query.count() + assigned_query.count()
            offset = (page - 1) * per_page
            results = query.offset(offset).limit(per_page).all()
            assigned_results = assigned_query.offset(max(0, offset - len(results))).limit(per_page - len(results)).all() if per_page > len(results) else []
            staff_tasks = []
            for task in results:
                bid_count = (
                    db.query(BidRecord)
                    .filter(
                        BidRecord.TaskID == task.TaskID,
                        BidRecord.BidStatus == "pending",
                    )
                    .count()
                )
                participants = TaskUtils.get_task_participants(db, task.TaskID)
                staff_tasks.append(
                    {
                        "type": "group_task",
                        "task_id": str(task.TaskID),
                        "group_task_id": str(task.GroupTaskID),
                        "task_type": task.TaskType,
                        "description": task.Description,
                        "estimated_time": task.EstimatedTime,
                        "task_location": task.TaskLocation,
                        "bid_deadline": task.BidDeadline,
                        "participants_count": (
                            len(participants["participants"]) if participants else 0
                        ),
                        "bid_count": bid_count,
                        "status": "available_for_bidding",
                    }
                )
            for task in assigned_results:
                participants = TaskUtils.get_task_participants(db, task.TaskID)
                staff_tasks.append(
                    {
                        "type": "group_task",
                        "task_id": str(task.TaskID),
                        "group_task_id": str(task.GroupTaskID),
                        "task_type": task.TaskType,
                        "description": task.Description,
                        "estimated_time": task.EstimatedTime,
                        "task_location": task.TaskLocation,
                        "bid_deadline": task.BidDeadline,
                        "participants_count": (
                            len(participants["participants"]) if participants else 0
                        ),
                        "bid_count": 0,
                        "status": "assigned",
                    }
                )
            total_pages = (total_count + per_page - 1) // per_page
            return {
                "tasks": staff_tasks,
                "current_page": page,
                "per_page": per_page,
                "total_records": total_count,
                "total_pages": total_pages,
            }
        except Exception as e:
            logger.error(f"获取代办任务列表失败: {str(e)}")
            return {
                "tasks": [],
                "current_page": page,
                "per_page": per_page,
                "total_records": 0,
                "total_pages": 0,
            }

    @staticmethod
    def bid_for_task(
        db: Session, staff_id: Decimal, task_id: Decimal  # , bid_amount: str
    ) -> Optional[Dict[str, Any]]:
        """
        代办人员竞标任务
        """
        try:
            # 检查任务是否存在且可竞标
            task = (
                db.query(Task)
                .filter(
                    Task.TaskID == task_id,
                    Task.Status == "full",
                    or_(Task.CurrentBidder.is_(None), Task.CurrentBidder == ""),
                )
                .first()
            )

            if not task:
                logger.warning(f"任务 {task_id} 不存在或不可竞标")
                return None

            # 检查竞标截止时间
            if task.BidDeadline:
                deadline = datetime.strptime(task.BidDeadline, "%Y-%m-%d %H:%M:%S")
                if datetime.now() > deadline:
                    logger.warning(f"任务 {task_id} 竞标已截止")
                    return None

            # 检查是否已经竞标
            existing_bid = (
                db.query(BidRecord)
                .filter(BidRecord.UserID == staff_id, BidRecord.TaskID == task_id)
                .first()
            )

            if existing_bid:
                logger.warning(f"代办人员 {staff_id} 已经竞标任务 {task_id}")
                return None

            # 生成新的BidID
            max_bid_id = db.query(func.max(BidRecord.BidID)).scalar() or 0
            new_bid_id = max_bid_id + 1

            # 创建竞标记录
            bid_record = BidRecord(
                UserID=staff_id,
                TaskID=task_id,
                BidID=new_bid_id,
                BidTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                BidStatus="pending",
                # BidAmount=bid_amount,
            )

            db.add(bid_record)
            db.commit()

            # 检查是否已有5个竞标，如果是则自动分配给信誉最高的
            bid_count = (
                db.query(BidRecord)
                .filter(BidRecord.TaskID == task_id, BidRecord.BidStatus == "pending")
                .count()
            )

            if bid_count >= 5:
                TaskUtils._auto_assign_task_to_best_bidder(db, task_id)

            logger.info(f"代办人员 {staff_id} 成功竞标任务 {task_id}")

            return {
                "bid_id": str(new_bid_id),
                "task_id": str(task_id),
                "bid_time": bid_record.BidTime,
                # "bid_amount": bid_amount,
                "current_bid_count": bid_count,
                "status": "pending",
            }

        except Exception as e:
            db.rollback()
            logger.error(f"竞标失败: {str(e)}")
            return None

    @staticmethod
    def get_task_participants(
        db: Session, task_id: Decimal
    ) -> Optional[Dict[str, Any]]:
        """
        获取任务参与者列表
        """
        try:
            task = db.query(Task).filter(Task.TaskID == task_id).first()
            if not task:
                return None

            participants = (
                db.query(TaskParticipant, User)
                .join(User, TaskParticipant.UserID == User.UserID)
                .filter(
                    TaskParticipant.TaskID == task_id,
                    TaskParticipant.Status == "active",
                )
                .all()
            )

            participant_list = []
            for participant, user in participants:
                participant_list.append(
                    {
                        "user_id": str(participant.UserID),
                        "username": user.Username,
                        "join_time": participant.JoinTime,
                        "status": participant.Status,
                    }
                )

            return {
                "task_id": str(task_id),
                "task_description": task.Description,
                "participants": participant_list,
                "participant_count": len(participant_list),
                "max_participants": task.MaxParticipants,
                "task_status": task.Status,
            }

        except Exception as e:
            logger.error(f"获取任务参与者失败: {str(e)}")
            return None

    # # 重写join_group_task方法，添加自动检查逻辑
    # @staticmethod
    # def join_group_task(db: Session, user_id: Decimal, group_task_id: Decimal) -> bool:
    #     """
    #     参加团办任务（更新版本，包含自动检查5人逻辑）

    #     Args:
    #         db: 数据库会话
    #         user_id: 用户ID
    #         group_task_id: 团办任务ID

    #     Returns:
    #         bool: 操作是否成功
    #     """
    #     try:
    #         # 检查团办任务是否存在
    #         group_task = (
    #             db.query(GroupTask)
    #             .filter(GroupTask.GroupTaskID == group_task_id)
    #             .first()
    #         )

    #         if not group_task:
    #             logger.warning(f"团办任务 {group_task_id} 不存在")
    #             return False

    #         # 检查任务是否已结束
    #         if group_task.endTime and group_task.endTime != "":
    #             logger.warning(f"团办任务 {group_task_id} 已结束")
    #             return False

    #         # 检查用户是否已经参加
    #         existing = (
    #             db.query(GroupTaskUser)
    #             .filter(
    #                 GroupTaskUser.UserID == user_id,
    #                 GroupTaskUser.GroupTaskID == group_task_id,
    #             )
    #             .first()
    #         )

    #         if existing:
    #             logger.warning(f"用户 {user_id} 已经参加团办任务 {group_task_id}")
    #             return False

    #         # 检查是否已满5人
    #         current_count = (
    #             db.query(GroupTaskUser)
    #             .filter(GroupTaskUser.GroupTaskID == group_task_id)
    #             .count()
    #         )

    #         if current_count >= 5:
    #             logger.warning(f"团办任务 {group_task_id} 已满员")
    #             return False

    #         # 创建参与记录
    #         group_task_user = GroupTaskUser(UserID=user_id, GroupTaskID=group_task_id)
    #         db.add(group_task_user)

    #         db.commit()

    #         # 检查是否达到5人，如果是则开放给代办人员
    #         new_count = current_count + 1
    #         if new_count == 5:
    #             TaskUtils.check_and_create_task_for_staff(db, group_task_id)

    #         logger.info(
    #             f"用户 {user_id} 成功参加团办任务 {group_task_id}，当前人数: {new_count}"
    #         )
    #         return True

    #     except Exception as e:
    #         db.rollback()
    #         logger.error(f"参加团办任务失败: {str(e)}")
    #         return False
