from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from typing import Dict, List, Optional, Any
from models import Task, GroupTask, GroupTaskUser, BidRecord
import logging

logger = logging.getLogger(__name__)


class TaskUtils:
    """任务管理工具类"""

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
            # 构建查询
            query = db.query(GroupTask, Task).join(
                Task, GroupTask.TaskID == Task.TaskID
            )

            # 添加过滤条件
            if task_type:
                query = query.filter(Task.TaskType == task_type)

            # 根据状态过滤（这里可以根据实际业务逻辑调整）
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
                # 获取参与用户数量
                participant_count = (
                    db.query(GroupTaskUser)
                    .filter(GroupTaskUser.GroupTaskID == group_task.GroupTaskID)
                    .count()
                )

                group_tasks.append(
                    {
                        "group_task_id": str(group_task.GroupTaskID),
                        "task_id": str(group_task.TaskID),
                        "task_type": task.TaskType,
                        "description": task.Description,
                        "estimated_time": task.EstimatedTime,
                        "actual_time": task.ActualTime,
                        "current_bidder": task.CurrentBidder,
                        "bid_deadline": task.BidDeadline,
                        "participating_user_id": group_task.ParticipatingUserID,
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
                .join(Task, GroupTask.TaskID == Task.TaskID)
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
                    "join_time": group_task.JoinTime,  # 简化处理，实际可能需要单独存储每个用户的加入时间
                }
                for participant in participants
            ]

            return {
                "group_task_id": str(group_task.GroupTaskID),
                "task_id": str(group_task.TaskID),
                "task_type": task.TaskType,
                "description": task.Description,
                "estimated_time": task.EstimatedTime,
                "actual_time": task.ActualTime,
                "current_bidder": task.CurrentBidder,
                "bid_deadline": task.BidDeadline,
                "participating_user_id": group_task.ParticipatingUserID,
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
    def join_group_task(db: Session, user_id: Decimal, group_task_id: Decimal) -> bool:
        """
        参加团办任务

        Args:
            db: 数据库会话
            user_id: 用户ID
            group_task_id: 团办任务ID

        Returns:
            bool: 操作是否成功
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
                return False

            # 检查任务是否已结束
            if group_task.endTime and group_task.endTime != "":
                logger.warning(f"团办任务 {group_task_id} 已结束")
                return False

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
                return False

            # 创建参与记录
            group_task_user = GroupTaskUser(UserID=user_id, GroupTaskID=group_task_id)

            db.add(group_task_user)

            # 更新团办任务的参与用户信息（如果需要）
            if not group_task.ParticipatingUserID:
                group_task.ParticipatingUserID = str(user_id)
                group_task.JoinTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            db.commit()
            logger.info(f"用户 {user_id} 成功参加团办任务 {group_task_id}")
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"参加团办任务失败: {str(e)}")
            return False

    @staticmethod
    def leave_group_task(db: Session, user_id: Decimal, group_task_id: Decimal) -> bool:
        """
        退出团办任务

        Args:
            db: 数据库会话
            user_id: 用户ID
            group_task_id: 团办任务ID

        Returns:
            bool: 操作是否成功
        """
        try:
            # 查找用户参与记录
            group_task_user = (
                db.query(GroupTaskUser)
                .filter(
                    GroupTaskUser.UserID == user_id,
                    GroupTaskUser.GroupTaskID == group_task_id,
                )
                .first()
            )

            if not group_task_user:
                logger.warning(f"用户 {user_id} 未参加团办任务 {group_task_id}")
                return False

            # 检查任务是否已经开始或完成（根据业务逻辑可能不允许退出）
            group_task = (
                db.query(GroupTask)
                .filter(GroupTask.GroupTaskID == group_task_id)
                .first()
            )

            if group_task and group_task.endTime and group_task.endTime != "":
                logger.warning(f"团办任务 {group_task_id} 已结束，无法退出")
                return False

            # 删除参与记录
            db.delete(group_task_user)

            db.commit()
            logger.info(f"用户 {user_id} 成功退出团办任务 {group_task_id}")
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"退出团办任务失败: {str(e)}")
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
                .join(Task, GroupTask.TaskID == Task.TaskID)
                .filter(GroupTaskUser.UserID == user_id)
                .order_by(desc(GroupTask.GroupTaskID))
            )

            # 计算总数
            total_count = query.count()

            # 分页查询
            offset = (page - 1) * per_page
            results = query.offset(offset).limit(per_page).all()

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
                        "task_id": str(group_task.TaskID),
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
                    # 如果日期格式不正确，记录警告但继续处理
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

            # 创建竞标记录（注意：这里假设BidRecord模型存在相应字段）
            bid_record = BidRecord(
                UserID=user_id,
                TaskID=task_id,
                # 根据实际BidRecord模型添加其他字段
                # BidAmount=bid_data.get("bid_amount"),
                # BidTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                # Message=bid_data.get("message", ""),
                # Status="pending"
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
                # 注意：这里假设BidRecord有Status字段，根据实际模型调整
                # query = query.filter(BidRecord.Status == status)
                pass

            query = query.order_by(desc(BidRecord.TaskID))  # 根据实际主键调整

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
                        "bid_id": str(bid_record.UserID),  # 根据实际BidRecord主键调整
                        "task_id": str(bid_record.TaskID),
                        "task_type": task.TaskType,
                        "description": task.Description,
                        "estimated_time": task.EstimatedTime,
                        "current_bidder": task.CurrentBidder,
                        "bid_deadline": task.BidDeadline,
                        # "bid_amount": bid_record.BidAmount,
                        # "bid_time": bid_record.BidTime,
                        # "message": bid_record.Message,
                        # "status": bid_record.Status,
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
    def accept_bid(
        db: Session, task_id: Decimal, bid_id: Decimal, accepter_user_id: Decimal
    ) -> bool:
        """
        接受竞标

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
                .filter(BidRecord.TaskID == task_id)
                .first()  # 根据实际BidRecord模型调整查询条件
            )

            if not bid_record:
                logger.warning(f"竞标记录不存在: task_id={task_id}, bid_id={bid_id}")
                return False

            # 查找任务记录
            task = db.query(Task).filter(Task.TaskID == task_id).first()
            if not task:
                logger.warning(f"任务 {task_id} 不存在")
                return False

            # 更新任务的当前竞标者
            task.CurrentBidder = str(bid_record.UserID)

            # 更新竞标记录状态（如果BidRecord有状态字段）
            # bid_record.Status = "accepted"
            # bid_record.AcceptTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 拒绝其他竞标（如果需要的话）
            # other_bids = db.query(BidRecord).filter(
            #     BidRecord.TaskID == task_id,
            #     BidRecord.UserID != bid_record.UserID
            # ).all()
            # for other_bid in other_bids:
            #     other_bid.Status = "rejected"

            db.commit()
            logger.info(f"竞标已被接受: task_id={task_id}, winner={bid_record.UserID}")
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"接受竞标失败: {str(e)}")
            return False

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
