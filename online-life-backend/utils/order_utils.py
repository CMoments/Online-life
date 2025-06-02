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
from models import Orders, Task, User, Points, BidRecord, Staff, Reputation
from utils.points_utils import PointsUtils
from utils.user_utils import UserUtils
from utils.map_utils import MapUtils
import logging

logger = logging.getLogger(__name__)


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
        db: Session, user_id: Decimal, order_data: Dict[str, Any], estimated_time: int = None
    ) -> Decimal:
        """
        创建订单
        Args:
            db: 数据库会话
            user_id: 用户ID
            order_data: 订单数据
            estimated_time: 预计时间（秒）
        Returns:
            订单ID
        """
        try:
            # 生成ID
            order_id = OrderUtils.generate_order_id()

            # 验证订单类型
            order_type = order_data.get("order_type", "immediate")
            if order_type not in ["immediate", "scheduled"]:
                raise ValueError("无效的订单类型")

            # 直接用 estimated_time 参数，不再重复计算
            total_seconds = estimated_time if estimated_time is not None else 45 * 60

            # 创建订单记录
            order = Orders(
                OrderID=order_id,
                ClientID=user_id,
                OrderType=order_type,
                OrderStatus="pending",  # 待接单
                CreationTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                CompletionTime="",
                EstimatedTime=str(total_seconds),  # 存储总秒数
                AssignmentType=order_data.get("assignment_type", "direct"),
                AssignmentStatus="open",  # 分配状态：open开放, assigned已分配, closed已关闭
                OrderLocation=order_data.get("orderlocation", ""),
                ShopAddress=order_data.get("shop_address", ""),  # 新增：商家地址
                StaffID=None,
                Amount="0.00"  # 初始化为0，后续会更新
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
            query = db.query(Orders).filter(Orders.ClientID == user_id)

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
                order_data = {
                    "type": "order",
                    "order_id": str(order.OrderID),
                    "order_type": order.OrderType,
                    "order_status": order.OrderStatus,
                    "creation_time": order.CreationTime,
                    "completion_time": order.CompletionTime,
                    "assignment_type": order.AssignmentType,
                    "assignment_status": order.AssignmentStatus,
                    "order_location": order.OrderLocation,  # 收货地址
                    "shop_address": getattr(order, "ShopAddress", ""),  # 商家地址
                    "estimated_time": order.EstimatedTime,
                    "estimated_time_status": "calculated" if order.EstimatedTime and order.EstimatedTime != "2700" else "estimated",
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
        db: Session, order_id: Decimal, user_id: Decimal, is_staff: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        获取订单详情
        Args:
            db: 数据库会话
            order_id: 订单ID
            user_id: 用户ID（用于权限验证）
            is_staff: 是否是staff用户
        """
        try:
            # 查询订单
            order = db.query(Orders).filter(Orders.OrderID == order_id).first()
            if not order:
                return None

            # 权限验证：客户只能查看自己的订单，staff只能查看分配给自己的订单
            if is_staff:
                if order.StaffID != user_id:
                    return None
            else:
                if order.ClientID != user_id:
                    return None

            # 获取用户信息
            client = db.query(User).filter(User.UserID == order.ClientID).first()
            staff = db.query(User).filter(User.UserID == order.StaffID).first() if order.StaffID else None

            order_detail = {
                "type": "order",
                "order_id": str(order.OrderID),
                "client_id": str(order.ClientID),
                "client_name": client.Username if client else "",
                "staff_id": str(order.StaffID) if order.StaffID else None,
                "staff_name": staff.Username if staff else "",
                "order_type": order.OrderType,
                "order_status": order.OrderStatus,
                "creation_time": order.CreationTime,
                "completion_time": order.CompletionTime,
                "assignment_type": order.AssignmentType,
                "assignment_status": order.AssignmentStatus,
                "order_location": order.OrderLocation,
                "shop_address": order.ShopAddress,
                "amount": order.Amount,
                "estimated_time": order.EstimatedTime
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
            order = db.query(Orders).filter(Orders.OrderID == order_id).first()
            if not order:
                return False

            # 权限验证
            if order.ClientID != user_id:
                return False

            # 状态验证
            if order.OrderStatus not in ["pending", "assigned"]:
                return False  # 只有待接单和已分配的订单可以取消

            # 更新订单状态
            order.OrderStatus = "cancelled"
            order.AssignmentStatus = "closed"

            db.commit()
            return True

        except Exception as e:
            db.rollback()
            raise Exception(f"取消订单失败: {str(e)}")

    @staticmethod
    def complete_order(db: Session, order_id: Decimal, staff_id: Decimal) -> bool:
        """
        骑手完成订单
        Args:
            db: 数据库会话
            order_id: 订单ID
            staff_id: 骑手ID
        """
        try:
            # 查询订单
            order = db.query(Orders).filter(Orders.OrderID == order_id).first()
            if not order:
                print(f"订单不存在: {order_id}")
                return False

            # 权限验证：必须是接单的骑手才能完成
            if order.StaffID != staff_id:
                print(f"权限验证失败: 骑手{staff_id}不是订单{order_id}的接单人")
                print(f"骑手{order.StaffID}是订单{order_id}的接单人")
                return False

            # 状态验证
            if order.OrderStatus != "assigned":
                print(f"状态验证失败: 订单{order_id}状态为{order.OrderStatus}，不是assigned")
                return False

            # 更新订单状态
            order.OrderStatus = "completed"
            order.CompletionTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            order.AssignmentStatus = "closed"

            db.commit()
            return True

        except Exception as e:
            db.rollback()
            print(f"完成订单异常: {str(e)}")
            raise Exception(f"完成订单失败: {str(e)}")

    @staticmethod
    def get_order_points_info(
        db: Session, order_id: Decimal, user_id: Decimal
    ) -> Dict[str, Any]:
        """
        获取订单的积分支付信息
        Args:
            db: 数据库会话
            order_id: 订单ID
            user_id: 用户ID
        Returns:
            订单积分支付信息
        """
        try:
            # 查询订单
            order = db.query(Orders).filter(Orders.OrderID == order_id).first()
            if not order:
                raise Exception("订单不存在")

            # 权限验证
            if order.ClientID != user_id:
                raise Exception("无权限操作此订单")

            # 状态验证
            if order.OrderStatus not in ["completed"]:
                raise Exception("订单状态不允许使用积分支付")

            # 检查用户信誉度
            user_reputation = UserUtils.get_user_reputation(db, user_id)
            reputation_score = user_reputation.get("average_score", 0.0)

            # 如果信誉低于80，不支持积分支付
            if reputation_score < 80.0:
                return {
                    "type": "order",
                    "order_id": str(order_id),
                    "order_amount": float(getattr(order, "TotalAmount", 0)),
                    "points_payment_available": False,
                    "reason": f"用户信誉度不足（当前: {reputation_score}，要求: ≥80.0），不支持积分支付",
                    "current_reputation": reputation_score,
                    "required_reputation": 80.0,
                    "available_points": 0,
                    "max_points_can_use": 0,
                    "max_deductible_amount": 0.0,
                    "can_fully_pay_with_points": False,
                }

            # 获取用户积分信息
            user_points_info = PointsUtils.get_user_points_balance(db, user_id)
            available_points = user_points_info["available_points"]

            # 获取订单金额（假设有TotalAmount字段）
            order_amount = float(getattr(order, "TotalAmount", 0))

            # 计算可用积分抵扣金额 (100积分=1元)
            max_deductible_amount = available_points / 100.0  # 最大可抵扣金额
            max_points_can_use = min(
                available_points, int(order_amount * 100)
            )  # 最大可用积分数
            actual_max_deduction = min(
                max_deductible_amount, order_amount
            )  # 实际最大抵扣金额

            return {
                "type": "order",
                "order_id": str(order_id),
                "order_amount": order_amount,
                "points_payment_available": True,
                "current_reputation": reputation_score,
                "required_reputation": 80.0,
                "available_points": available_points,
                "max_points_can_use": max_points_can_use,  # 最大可使用的积分数量
                "max_deductible_amount": round(
                    actual_max_deduction, 2
                ),  # 最大可抵扣金额
                "points_rate": 100,  # 100积分=1元
                "remaining_amount_after_max_deduction": round(
                    order_amount - actual_max_deduction, 2
                ),
                "can_fully_pay_with_points": available_points
                >= int(order_amount * 100),
            }

        except Exception as e:
            raise Exception(f"订单积分信息查询失败: {str(e)}")

    @staticmethod
    def process_payment(
        db: Session, order_id: Decimal, user_id: Decimal, payment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        处理支付（支持积分、混合、现金支付）
        Args:
            db: 数据库会话
            order_id: 订单ID
            user_id: 用户ID
            payment_data: 支付数据，包含支付方式、金额、积分数等
        """
        try:
            # 查询订单
            order = db.query(Orders).filter(Orders.OrderID == order_id).first()
            if not order:
                raise Exception("订单不存在")

            # 权限验证
            if order.ClientID != user_id:
                raise Exception("无权限操作此订单")

            # 状态验证：只允许已完成或待支付的订单进行支付
            if order.OrderStatus not in ["completed", "paid"]:
                raise Exception("订单状态不允许支付")

            # 验证支付金额
            total_amount = float(payment_data.get("amount", 0))
            if total_amount <= 0:
                raise Exception("支付金额无效")

            payment_method = payment_data.get("payment_method", "")
            points_deduction = int(payment_data.get("points_deduction", 0))

            # 如果用户选择使用积分，检查信誉度
            if points_deduction > 0:
                user_reputation = UserUtils.get_user_reputation(db, user_id)
                reputation_score = user_reputation.get("average_score", 0.0)

                if reputation_score < 80.0:
                    raise Exception(
                        f"用户信誉度不足（当前: {reputation_score}，要求: ≥80.0），不支持积分支付"
                    )

            # 计算积分抵扣金额 (100积分=1元)
            points_deduction_amount = points_deduction / 100.0 if points_deduction > 0 else 0

            # 支付结果信息
            payment_result = {
                "payment_id": f"PAY_{int(datetime.now().timestamp())}",
                "order_id": str(order_id),
                "total_amount": total_amount,
                "points_used": 0,
                "points_deduction_amount": 0.0,
                "cash_payment": total_amount,
                "payment_method": payment_method,
                "status": "success",
                "paid_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            # 处理积分抵扣
            if points_deduction > 0:
                print(f"[DEBUG] 开始处理积分抵扣，用户ID: {user_id}, 请求扣除积分: {points_deduction}")

                # 获取用户积分记录
                points_record = db.query(Points).filter(Points.UserID == user_id).first()
                if not points_record:
                    raise Exception("积分记录不存在，请联系管理员处理")

                try:
                    current_points = int(points_record.Points)
                except ValueError:
                    raise Exception("积分数据异常，请检查数据库中的积分值是否合法")

                print(f"[DEBUG] 当前积分: {current_points}")

                if current_points < points_deduction:
                    raise Exception(f"积分不足，当前积分：{current_points}，需要积分：{points_deduction}")

                # 扣除积分
                new_points = current_points - points_deduction
                print('[DEBUG] 扣除积分成功，新积分: {new_points}')
                points_record.Points = str(new_points)
                db.add(points_record)

                # 记录积分扣除日志
                PointsUtils._log_points_transaction(
                    db,
                    user_id,
                    -points_deduction,
                    "DEDUCT",
                    f"订单支付抵扣-订单号：{order_id}",
                    current_points,
                    new_points,
                )

                # 更新支付结果
                payment_result["points_used"] = points_deduction
                payment_result["points_deduction_amount"] = round(points_deduction_amount, 2)
                payment_result["cash_payment"] = round(total_amount - points_deduction_amount, 2)

            # 如果完全用积分支付
            if payment_result["cash_payment"] == 0:
                payment_result["payment_method"] = "points_only"
            elif points_deduction > 0:
                payment_result["payment_method"] = f"mixed_{payment_method}_points"

            # 处理现金部分支付
            if payment_method == "points":
                pass  # 积分支付跳过验证
            elif payment_result["cash_payment"] > 0:
                if payment_method not in ["alipay", "wechat", "bank_card"]:
                    raise Exception("现金支付部分需要选择有效的支付方式")

            # 更新订单状态
            if order.OrderStatus in ["completed"]:
                order.OrderStatus = "paid"

            # 只有现金支付或混合支付才奖励积分
            if payment_method != "points" and payment_result["cash_payment"] > 0:
                cash_amount = int(payment_result["cash_payment"])  # 取整数部分
                if cash_amount > 0:
                    points_to_add = cash_amount * 100  # 1元=100积分
                    success = PointsUtils.add_points(
                        db,
                        user_id,
                        points_to_add,
                        f"订单支付奖励-订单号：{order_id}，支付金额：{cash_amount}元",
                    )
                    if success:
                        payment_result["points_earned"] = points_to_add
                        payment_result["points_earned_reason"] = (
                            f"现金支付{cash_amount}元获得{points_to_add}积分"
                        )
                    else:
                        logger.warning(f"订单 {order_id} 支付成功，但积分奖励失败")

            db.commit()
            return payment_result

        except Exception as e:
            db.rollback()
            raise Exception(f"支付处理失败: {str(e)}")    
    @staticmethod
    def get_available_orders(
        db: Session,
        page: int = 1,
        per_page: int = 10,
        task_type: str = "",
        staff_id: Optional[Decimal] = None,
    ) -> Dict[str, Any]:
        """
        获取可接单列表（代办人员使用）
        Args:
            db: 数据库会话
            page: 页码
            per_page: 每页数量
            task_type: 任务类型筛选
            staff_id: 员工ID（用于排除已接取的订单）
        """
        try:
            # 构建查询 - 查找待接单的订单
            query = (
                db.query(Orders, User)
                .join(User, Orders.ClientID == User.UserID)
                .filter(
                    and_(
                        Orders.OrderStatus == "pending",
                        Orders.AssignmentStatus == "open",
                        Orders.StaffID.is_(None),
                    )
                )
            )

            # 添加任务类型筛选
            if task_type:
                query = query.filter(Orders.OrderType == task_type)

            # 分页查询
            total = query.count()
            results = (
                query.order_by(desc(Orders.CreationTime))
                .offset((page - 1) * per_page)
                .limit(per_page)
                .all()
            )

            # 构建返回数据
            orders_list = []
            for order, user in results:
                order_data = {
                    "type": "order",
                    "order_id": str(order.OrderID),
                    "client_name": user.Username,
                    "client_address": user.Address,
                    "order_type": order.OrderType,
                    "order_location": order.OrderLocation,
                    "shop_address": order.ShopAddress,  # 添加商家地址
                    "creation_time": order.CreationTime,
                    "assignment_type": order.AssignmentType,
                    "order_status": order.OrderStatus,
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
            order = db.query(Orders).filter(Orders.OrderID == order_id).first()
            if not order:
                return False

            # 状态验证
            if order.OrderStatus != "pending" or order.AssignmentStatus != "open":
                return False

            # 更新订单状态
            order.OrderStatus = "assigned"
            order.AssignmentStatus = "assigned"
            order.StaffID = staff_id  # 设置接单的staff_id

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
            total_orders = db.query(Orders).filter(Orders.ClientID == user_id).count()
            pending_orders = (
                db.query(Orders)
                .filter(
                    and_(Orders.ClientID == user_id, Orders.OrderStatus == "pending")
                )
                .count()
            )
            assigned_orders = (
                db.query(Orders)
                .filter(
                    and_(Orders.ClientID == user_id, Orders.OrderStatus == "assigned")
                )
                .count()
            )
            completed_orders = (
                db.query(Orders)
                .filter(
                    and_(Orders.ClientID == user_id, Orders.OrderStatus == "completed")
                )
                .count()
            )
            cancelled_orders = (
                db.query(Orders)
                .filter(
                    and_(Orders.ClientID == user_id, Orders.OrderStatus == "cancelled")
                )
                .count()
            )
            paid_orders = (
                db.query(Orders)
                .filter(
                    and_(
                        Orders.ClientID == user_id, Orders.OrderStatus == "paid"
                    )
                )
                .count()
            )

            return {
                "total_orders": total_orders,
                "pending_orders": pending_orders,
                "paid_orders": paid_orders,
                "completed_orders": completed_orders,
                "cancelled_orders": cancelled_orders,
            }

        except Exception as e:
            raise Exception(f"获取订单统计失败: {str(e)}")

    @staticmethod
    def accept_order(
        db: Session, order_id: Decimal, staff_id: Decimal
    ) -> Dict[str, Any]:
        """
        代办人员接取订单
        Args:
            db: 数据库会话
            order_id: 订单ID
            staff_id: 代办人员ID
        Returns:
            接单结果
        """
        try:
            # 查询订单
            order = db.query(Orders).filter(Orders.OrderID == order_id).first()
            if not order:
                raise Exception("订单不存在")

            # 验证订单状态
            if order.OrderStatus != "pending" or order.AssignmentStatus != "open":
                raise Exception("订单状态不允许接单")

            # 验证代办人员
            staff = db.query(Staff).filter(Staff.UserID == staff_id).first()
            if not staff:
                raise Exception("代办人员不存在")

            # 更新订单状态
            order.StaffID = staff_id  # 写入骑手ID
            order.OrderStatus = "assigned"  # 已分配
            order.AssignmentStatus = "assigned"  # 已分配状态

            # 记录接单时间
            accept_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            db.commit()

            return {
                "type": "order",
                "order_id": str(order_id),
                "staff_id": str(staff_id),
                "staff_name": staff.Username,
                "accept_time": accept_time,
                "status": "success",
            }

        except Exception as e:
            db.rollback()
            raise Exception(f"接单失败: {str(e)}")

    @staticmethod
    def get_staff_orders(
        db: Session,
        staff_id: Decimal,
        page: int = 1,
        per_page: int = 10,
        status: str = "",
        order_type: str = "",
    ) -> Dict[str, Any]:
        """
        获取代办人员订单列表
        Args:
            db: 数据库会话
            staff_id: 代办人员ID
            page: 页码
            per_page: 每页数量
            status: 订单状态筛选
            order_type: 订单类型筛选
        """
        try:
            # 构建查询
            query = db.query(Orders).filter(Orders.StaffID == staff_id)

            # 添加筛选条件
            if status:
                if status == "completed":
                    # 对于completed状态，同时包含completed和paid状态的订单
                    query = query.filter(Orders.OrderStatus.in_(["completed", "paid"]))
                else:
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
                # 获取客户信息
                client = db.query(User).filter(User.UserID == order.ClientID).first()

                order_data = {
                    "type": "order",
                    "order_id": str(order.OrderID),
                    "order_type": order.OrderType,
                    "order_status": order.OrderStatus,
                    "creation_time": order.CreationTime,
                    "completion_time": order.CompletionTime,
                    "assignment_type": order.AssignmentType,
                    "assignment_status": order.AssignmentStatus,
                    "order_location": order.OrderLocation,
                    "shop_address": order.ShopAddress,  # 添加商家地址
                    "client_id": str(order.ClientID),
                    "client_name": client.Username if client else "",
                    "estimated_time": order.EstimatedTime,  # 添加预计时间
                }

                # 检查是否已评价
                has_reviewed = (
                    db.query(Reputation)
                    .filter(
                        and_(
                            Reputation.RUserID == staff_id,
                            Reputation.OrderID == order.OrderID,
                        )
                    )
                    .first()
                    is not None
                )
                order_data["has_reviewed"] = has_reviewed
                order_data["can_review"] = not has_reviewed

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
            raise Exception(f"获取代办人员订单列表失败: {str(e)}")

    @staticmethod
    def get_available_orders_map(
        db: Session,
        page: int = 1,
        per_page: int = 10,
        task_type: str = "",
        staff_id: Optional[Decimal] = None,
    ) -> Dict[str, Any]:
        """
        获取可接单列表（地图模式，带经纬度）
        Args:
            db: 数据库会话
            page: 页码
            per_page: 每页数量
            task_type: 任务类型筛选
            staff_id: 员工ID（用于排除已接取的订单）
        """
        try:
            query = (
                db.query(Orders, User)
                .join(User, Orders.ClientID == User.UserID)
                .filter(
                    and_(
                        Orders.OrderStatus == "pending",
                        Orders.AssignmentStatus == "open",
                        Orders.StaffID.is_(None),
                    )
                )
            )
            if task_type:
                query = query.filter(Orders.OrderType == task_type)
            total = query.count()
            results = (
                query.order_by(desc(Orders.CreationTime))
                .offset((page - 1) * per_page)
                .limit(per_page)
                .all()
            )
            orders_list = []
            for order, user in results:
                orders_list.append({
                    "type": "order",
                    "order_id": str(order.OrderID),
                    "client_name": user.Username,
                    "client_address": user.Address,
                    "order_type": order.OrderType,
                    "order_location": order.OrderLocation,
                    "creation_time": order.CreationTime,
                    "assignment_type": order.AssignmentType,
                    "order_status": order.OrderStatus,
                })
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
            raise Exception(f"获取可接单地图列表失败: {str(e)}")
