"""
订单管理工具模块
提供订单创建、查询、更新、取消、支付等功能
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
import json

from models import Orders, Task, User, Points, BidRecord


class OrderUtils:
    """订单管理工具类"""

    @staticmethod
    def generate_order_id() -> Decimal:
        """生成唯一订单ID"""
        # 使用时间戳生成唯一ID
        timestamp = int(datetime.now().timestamp() * 1000000)  # 微秒时间戳
        return Decimal(str(timestamp))

    @staticmethod
    def generate_task_id() -> Decimal:
        """生成唯一任务ID"""
        # 使用时间戳生成唯一ID，加上前缀以区分
        timestamp = int(datetime.now().timestamp() * 1000000)
        return Decimal(str(2000000000000000000 + timestamp))

    @staticmethod
    def create_order(
        db: Session, user_id: Decimal, order_data: Dict[str, Any]
    ) -> Decimal:
        """
        创建订单和关联任务
        Args:
            db: 数据库会话
            user_id: 用户ID
            order_data: 订单数据
        Returns:
            订单ID
        """
        try:
            # 生成ID
            order_id = OrderUtils.generate_order_id()
            task_id = OrderUtils.generate_task_id()

            # 验证订单类型
            order_type = order_data.get("order_type", "immediate")
            if order_type not in ["immediate", "scheduled"]:
                raise ValueError("无效的订单类型")

            # 计算竞价截止时间
            bid_deadline = order_data.get("bid_deadline")
            if not bid_deadline:
                if order_type == "immediate":
                    # 即时订单：2小时后截止
                    bid_deadline = (datetime.now() + timedelta(hours=2)).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                else:
                    # 预约订单：预约时间前1小时截止
                    scheduled_time = order_data.get("scheduled_time")
                    if scheduled_time:
                        scheduled_dt = datetime.strptime(
                            scheduled_time, "%Y-%m-%d %H:%M:%S"
                        )
                        bid_deadline = (scheduled_dt - timedelta(hours=1)).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    else:
                        bid_deadline = (datetime.now() + timedelta(hours=24)).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )

            # 创建任务记录
            task = Task(
                TaskID=task_id,
                TaskType=order_data.get("task_type", "other"),
                Description=order_data.get("description", ""),
                EstimatedTime=order_data.get("estimated_time", "1小时"),
                ActualTime="",
                CurrentBidder="",
                BidDeadline=bid_deadline,
            )
            db.add(task)

            # 创建订单记录
            order = Orders(
                OUserID=order_id,
                UserID=user_id,
                OrderType=order_type,
                OrderStatus="pending",  # 待接单
                CreationTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                CompletionTime="",
                AssignmentType=order_data.get(
                    "assignment_type", "bidding"
                ),  # 分配方式：bidding竞价, direct直接
                AssignmentStatus="open",  # 分配状态：open开放, assigned已分配, closed已关闭
            )
            db.add(order)

            db.commit()
            return order_id

        except Exception as e:
            db.rollback()
            raise Exception(f"创建订单失败: {str(e)}")

    @staticmethod
    def get_user_orders(
        db: Session,
        user_id: Decimal,
        page: int = 1,
        per_page: int = 10,
        status: str = "",
        order_type: str = "",
    ) -> Dict[str, Any]:
        """
        获取用户订单列表
        Args:
            db: 数据库会话
            user_id: 用户ID
            page: 页码
            per_page: 每页数量
            status: 订单状态筛选
            order_type: 订单类型筛选
        """
        try:
            # 构建查询
            query = db.query(Orders).filter(Orders.UserID == user_id)

            # 添加筛选条件
            if status:
                query = query.filter(Orders.OrderStatus == status)
            if order_type:
                query = query.filter(Orders.OrderType == order_type)

            # 总数统计
            total = query.count()

            # 分页查询
            orders = (
                query.order_by(desc(Orders.CreationTime))
                .offset((page - 1) * per_page)
                .limit(per_page)
                .all()
            )

            # 构建返回数据
            orders_list = []
            for order in orders:
                # 获取关联的任务信息（通过时间匹配或其他逻辑）
                task = (
                    db.query(Task)
                    .filter(Task.BidDeadline >= order.CreationTime)
                    .order_by(Task.TaskID.desc())
                    .first()
                )

                order_data = {
                    "order_id": str(order.OUserID),
                    "order_type": order.OrderType,
                    "order_status": order.OrderStatus,
                    "creation_time": order.CreationTime,
                    "completion_time": order.CompletionTime,
                    "assignment_type": order.AssignmentType,
                    "assignment_status": order.AssignmentStatus,
                    "task_info": {
                        "task_id": str(task.TaskID) if task else "",
                        "task_type": task.TaskType if task else "",
                        "description": task.Description if task else "",
                        "estimated_time": task.EstimatedTime if task else "",
                        "current_bidder": task.CurrentBidder if task else "",
                        "bid_deadline": task.BidDeadline if task else "",
                    },
                }
                orders_list.append(order_data)

            return {
                "orders": orders_list,
                "pagination": {
                    "current_page": page,
                    "per_page": per_page,
                    "total": total,
                    "total_pages": (total + per_page - 1) // per_page,
                },
            }

        except Exception as e:
            raise Exception(f"获取订单列表失败: {str(e)}")

    @staticmethod
    def get_order_detail(
        db: Session, order_id: Decimal, user_id: Decimal
    ) -> Optional[Dict[str, Any]]:
        """
        获取订单详情
        Args:
            db: 数据库会话
            order_id: 订单ID
            user_id: 用户ID（用于权限验证）
        """
        try:
            # 查询订单
            order = db.query(Orders).filter(Orders.OUserID == order_id).first()
            if not order:
                return None

            # 权限验证：只能查看自己的订单，或者是接单的代办人员
            if order.UserID != user_id:
                # 检查是否是接单的代办人员
                task = (
                    db.query(Task)
                    .filter(Task.BidDeadline >= order.CreationTime)
                    .order_by(Task.TaskID.desc())
                    .first()
                )

                if not task or str(user_id) not in task.CurrentBidder:
                    return None

            # 获取关联任务信息
            task = (
                db.query(Task)
                .filter(Task.BidDeadline >= order.CreationTime)
                .order_by(Task.TaskID.desc())
                .first()
            )

            # 获取用户信息
            user = db.query(User).filter(User.UserID == order.UserID).first()

            # 获取竞价记录
            bid_records = []
            if task:
                bids = (
                    db.query(BidRecord, User)
                    .join(User, BidRecord.UserID == User.UserID)
                    .filter(BidRecord.TaskID == task.TaskID)
                    .all()
                )

                for bid, bidder in bids:
                    bid_records.append(
                        {
                            "bidder_id": str(bid.UserID),
                            "bidder_name": bidder.Username,
                            "bid_time": bid.BidTime,
                            "bid_status": bid.BidStatus,
                        }
                    )

            order_detail = {
                "order_id": str(order.OUserID),
                "user_id": str(order.UserID),
                "user_name": user.Username if user else "",
                "order_type": order.OrderType,
                "order_status": order.OrderStatus,
                "creation_time": order.CreationTime,
                "completion_time": order.CompletionTime,
                "assignment_type": order.AssignmentType,
                "assignment_status": order.AssignmentStatus,
                "task_info": {
                    "task_id": str(task.TaskID) if task else "",
                    "task_type": task.TaskType if task else "",
                    "description": task.Description if task else "",
                    "estimated_time": task.EstimatedTime if task else "",
                    "actual_time": task.ActualTime if task else "",
                    "current_bidder": task.CurrentBidder if task else "",
                    "bid_deadline": task.BidDeadline if task else "",
                },
                "bid_records": bid_records,
            }

            return order_detail

        except Exception as e:
            raise Exception(f"获取订单详情失败: {str(e)}")

    @staticmethod
    def cancel_order(db: Session, order_id: Decimal, user_id: Decimal) -> bool:
        """
        取消订单
        Args:
            db: 数据库会话
            order_id: 订单ID
            user_id: 用户ID
        """
        try:
            # 查询订单
            order = db.query(Orders).filter(Orders.OUserID == order_id).first()
            if not order:
                return False

            # 权限验证
            if order.UserID != user_id:
                return False

            # 状态验证
            if order.OrderStatus not in ["pending", "assigned"]:
                return False  # 只有待接单和已分配的订单可以取消

            # 更新订单状态
            order.OrderStatus = "cancelled"
            order.AssignmentStatus = "closed"

            # 如果已分配给代办人员，需要释放分配
            if order.AssignmentStatus == "assigned":
                # 查找相关任务并清空当前竞价者
                task = (
                    db.query(Task)
                    .filter(Task.BidDeadline >= order.CreationTime)
                    .order_by(Task.TaskID.desc())
                    .first()
                )

                if task:
                    task.CurrentBidder = ""

            db.commit()
            return True

        except Exception as e:
            db.rollback()
            raise Exception(f"取消订单失败: {str(e)}")

    @staticmethod
    def complete_order(db: Session, order_id: Decimal, user_id: Decimal) -> bool:
        """
        完成订单
        Args:
            db: 数据库会话
            order_id: 订单ID
            user_id: 用户ID（可以是客户或代办人员）
        """
        try:
            # 查询订单
            order = db.query(Orders).filter(Orders.OUserID == order_id).first()
            if not order:
                return False

            # 权限验证：订单所有者或接单的代办人员
            has_permission = order.UserID == user_id

            if not has_permission:
                # 检查是否是接单的代办人员
                task = (
                    db.query(Task)
                    .filter(Task.BidDeadline >= order.CreationTime)
                    .order_by(Task.TaskID.desc())
                    .first()
                )

                if task and str(user_id) in task.CurrentBidder:
                    has_permission = True

            if not has_permission:
                return False

            # 状态验证
            if order.OrderStatus != "in_progress":
                return False  # 只有进行中的订单可以完成

            # 更新订单状态
            order.OrderStatus = "completed"
            order.CompletionTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            order.AssignmentStatus = "closed"

            # 更新任务实际完成时间
            task = (
                db.query(Task)
                .filter(Task.BidDeadline >= order.CreationTime)
                .order_by(Task.TaskID.desc())
                .first()
            )

            if task:
                task.ActualTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 奖励积分给代办人员
            if task and task.CurrentBidder:
                try:
                    staff_id = Decimal(
                        task.CurrentBidder.split(",")[0]
                    )  # 取第一个竞价者
                    points_record = (
                        db.query(Points).filter(Points.UserID == staff_id).first()
                    )
                    if points_record:
                        current_points = int(points_record.Points)
                        points_record.Points = str(
                            current_points + 50
                        )  # 完成任务奖励50积分
                    else:
                        new_points = Points(UserID=staff_id, Points="50")
                        db.add(new_points)
                except:
                    pass  # 积分奖励失败不影响订单完成

            db.commit()
            return True

        except Exception as e:
            db.rollback()
            raise Exception(f"完成订单失败: {str(e)}")

    @staticmethod
    def process_payment(
        db: Session, order_id: Decimal, user_id: Decimal, payment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        处理支付
        Args:
            db: 数据库会话
            order_id: 订单ID
            user_id: 用户ID
            payment_data: 支付数据
        """
        try:
            # 查询订单
            order = db.query(Orders).filter(Orders.OUserID == order_id).first()
            if not order:
                raise Exception("订单不存在")

            # 权限验证
            if order.UserID != user_id:
                raise Exception("无权限操作此订单")

            # 状态验证
            if order.OrderStatus not in ["assigned", "in_progress"]:
                raise Exception("订单状态不允许支付")

            # 验证支付金额
            amount = float(payment_data.get("amount", 0))
            if amount <= 0:
                raise Exception("支付金额无效")

            payment_method = payment_data.get("payment_method", "")
            if payment_method not in ["alipay", "wechat", "bank_card", "points"]:
                raise Exception("不支持的支付方式")

            # 模拟支付处理
            if payment_method == "points":
                # 积分支付
                points_record = (
                    db.query(Points).filter(Points.UserID == user_id).first()
                )
                if not points_record:
                    raise Exception("积分记录不存在")

                current_points = int(points_record.Points)
                required_points = int(amount)  # 1元=1积分

                if current_points < required_points:
                    raise Exception("积分不足")

                # 扣除积分
                points_record.Points = str(current_points - required_points)

            # 更新订单状态
            if order.OrderStatus == "assigned":
                order.OrderStatus = "in_progress"  # 支付后进入进行中状态

            db.commit()

            return {
                "payment_id": f"PAY_{int(datetime.now().timestamp())}",
                "order_id": str(order_id),
                "amount": amount,
                "payment_method": payment_method,
                "status": "success",
                "paid_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

        except Exception as e:
            db.rollback()
            raise Exception(f"支付处理失败: {str(e)}")

    @staticmethod
    def get_available_orders(
        db: Session, page: int = 1, per_page: int = 10, task_type: str = ""
    ) -> Dict[str, Any]:
        """
        获取可接单列表（代办人员使用）
        Args:
            db: 数据库会话
            page: 页码
            per_page: 每页数量
            task_type: 任务类型筛选
        """
        try:
            # 构建查询 - 查找待接单的订单
            query = (
                db.query(Orders, Task, User)
                .join(User, Orders.UserID == User.UserID)
                .outerjoin(
                    Task,
                    and_(Task.BidDeadline >= Orders.CreationTime, Task.TaskType != ""),
                )
                .filter(
                    and_(
                        Orders.OrderStatus == "pending",
                        Orders.AssignmentStatus == "open",
                    )
                )
            )

            # 添加任务类型筛选
            if task_type:
                query = query.filter(Task.TaskType == task_type)

            # 只显示竞价截止时间未到的订单
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            query = query.filter(
                or_(Task.BidDeadline.is_(None), Task.BidDeadline > current_time)
            )

            # 总数统计
            total = query.count()

            # 分页查询
            results = (
                query.order_by(desc(Orders.CreationTime))
                .offset((page - 1) * per_page)
                .limit(per_page)
                .all()
            )

            # 构建返回数据
            orders_list = []
            for order, task, user in results:
                # 获取当前竞价数
                bid_count = 0
                if task:
                    bid_count = (
                        db.query(BidRecord)
                        .filter(BidRecord.TaskID == task.TaskID)
                        .count()
                    )

                order_data = {
                    "order_id": str(order.OUserID),
                    "user_name": user.Username,
                    "user_address": user.Address,
                    "order_type": order.OrderType,
                    "creation_time": order.CreationTime,
                    "assignment_type": order.AssignmentType,
                    "task_info": {
                        "task_id": str(task.TaskID) if task else "",
                        "task_type": task.TaskType if task else "",
                        "description": task.Description if task else "",
                        "estimated_time": task.EstimatedTime if task else "",
                        "bid_deadline": task.BidDeadline if task else "",
                        "bid_count": bid_count,
                    },
                }
                orders_list.append(order_data)

            return {
                "orders": orders_list,
                "pagination": {
                    "current_page": page,
                    "per_page": per_page,
                    "total": total,
                    "total_pages": (total + per_page - 1) // per_page,
                },
            }

        except Exception as e:
            raise Exception(f"获取可接单列表失败: {str(e)}")

    @staticmethod
    def assign_order_to_staff(
        db: Session, order_id: Decimal, staff_id: Decimal
    ) -> bool:
        """
        将订单分配给代办人员
        Args:
            db: 数据库会话
            order_id: 订单ID
            staff_id: 代办人员ID
        """
        try:
            # 查询订单
            order = db.query(Orders).filter(Orders.OUserID == order_id).first()
            if not order:
                return False

            # 状态验证
            if order.OrderStatus != "pending" or order.AssignmentStatus != "open":
                return False

            # 更新订单状态
            order.OrderStatus = "assigned"
            order.AssignmentStatus = "assigned"

            # 更新相关任务的当前竞价者
            task = (
                db.query(Task)
                .filter(Task.BidDeadline >= order.CreationTime)
                .order_by(Task.TaskID.desc())
                .first()
            )

            if task:
                task.CurrentBidder = str(staff_id)

            db.commit()
            return True

        except Exception as e:
            db.rollback()
            raise Exception(f"分配订单失败: {str(e)}")

    @staticmethod
    def get_order_statistics(db: Session, user_id: Decimal) -> Dict[str, Any]:
        """
        获取用户订单统计信息
        Args:
            db: 数据库会话
            user_id: 用户ID
        """
        try:
            # 统计各状态订单数量
            total_orders = db.query(Orders).filter(Orders.UserID == user_id).count()
            pending_orders = (
                db.query(Orders)
                .filter(and_(Orders.UserID == user_id, Orders.OrderStatus == "pending"))
                .count()
            )
            in_progress_orders = (
                db.query(Orders)
                .filter(
                    and_(Orders.UserID == user_id, Orders.OrderStatus == "in_progress")
                )
                .count()
            )
            completed_orders = (
                db.query(Orders)
                .filter(
                    and_(Orders.UserID == user_id, Orders.OrderStatus == "completed")
                )
                .count()
            )
            cancelled_orders = (
                db.query(Orders)
                .filter(
                    and_(Orders.UserID == user_id, Orders.OrderStatus == "cancelled")
                )
                .count()
            )

            return {
                "total_orders": total_orders,
                "pending_orders": pending_orders,
                "in_progress_orders": in_progress_orders,
                "completed_orders": completed_orders,
                "cancelled_orders": cancelled_orders,
            }

        except Exception as e:
            raise Exception(f"获取订单统计失败: {str(e)}")
