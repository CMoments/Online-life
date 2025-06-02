from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from sqlalchemy import Float, Integer
from models import User, Reputation, Points, Admin, Client, Staff, Orders
from decimal import Decimal
from typing import Optional, Dict, List, Any
import logging
from datetime import datetime
import traceback

# 配置日志
logger = logging.getLogger(__name__)


class UserUtils:
    """用户相关工具类"""

    @staticmethod
    def get_user_info(db: Session, user_id: Decimal) -> Optional[Dict[str, Any]]:
        """
        获取用户详细信息

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            用户信息字典或None
        """
        try:
            user = db.query(User).filter(User.UserID == user_id).first()
            if not user:
                return None

            user_info = {
                "user_id": str(user.UserID),
                "username": user.Username,
                "email": user.Email,
                "phone": user.Phone,
                "address": user.Address,
                "role": user.Role,
            }

            # 根据角色获取额外信息
            if user.Role == "admin":
                admin_info = db.query(Admin).filter(Admin.UserID == user_id).first()
                if admin_info:
                    user_info.update(
                        {
                            "admin_level": (
                                admin_info.Adlevel
                                if hasattr(admin_info, "AdminLevel")
                                else None
                            ),
                            # "permissions": (
                            #     admin_info.Permissions
                            #     if hasattr(admin_info, "Permissions")
                            #     else None
                            # ),
                        }
                    )
            # elif user.Role == "client":
            #     client_info = db.query(Client).filter(Client.UserID == user_id).first()
            #     if client_info:
            #         user_info.update(
            #             {
            #                 "client_type": (
            #                     client_info.ClientType
            #                     if hasattr(client_info, "ClientType")
            #                     else None
            #                 ),
            #                 "registration_date": (
            #                     client_info.RegistrationDate.isoformat()
            #                     if hasattr(client_info, "RegistrationDate")
            #                     else None
            #                 ),
            #             }
            #         )
            # elif user.Role == "staff":
            #     staff_info = db.query(Staff).filter(Staff.UserID == user_id).first()
            #     if staff_info:
            #         user_info.update(
            #             {
            #                 "department": (
            #                     staff_info.Department
            #                     if hasattr(staff_info, "Department")
            #                     else None
            #                 ),
            #                 "position": (
            #                     staff_info.Position
            #                     if hasattr(staff_info, "Position")
            #                     else None
            #                 ),
            #             }
            #         )

            return user_info

        except Exception as e:
            logger.error(f"获取用户信息失败: {str(e)}")
            return None

    @staticmethod
    def update_user_info(db: Session, user_id: Decimal, data: Dict[str, Any]) -> bool:
        """
        更新用户信息

        Args:
            db: 数据库会话
            user_id: 用户ID
            data: 更新数据

        Returns:
            更新是否成功
        """
        try:
            user = db.query(User).filter(User.UserID == user_id).first()
            if not user:
                return False

            # 可更新的字段
            updatable_fields = ["username", "email", "phone", "address"]

            for field in updatable_fields:
                if field in data and data[field] is not None:
                    # 转换字段名为数据库字段名
                    db_field = field.capitalize() if field != "username" else "Username"
                    setattr(user, db_field, data[field])

            db.commit()
            return True

        except Exception as e:
            logger.error(f"更新用户信息失败: {str(e)}")
            db.rollback()
            return False

    @staticmethod
    def update_password(db: Session, user_id: Decimal, new_password_hash: str) -> bool:
        """
        更新用户密码

        Args:
            db: 数据库会话
            user_id: 用户ID
            new_password_hash: 新密码哈希值

        Returns:
            更新是否成功
        """
        try:
            user = db.query(User).filter(User.UserID == user_id).first()
            if not user:
                return False

            user.Password = new_password_hash
            db.commit()
            return True

        except Exception as e:
            logger.error(f"更新密码失败: {str(e)}")
            db.rollback()
            return False

    @staticmethod
    def get_user_reputation(db: Session, user_id: Decimal) -> Dict[str, Any]:
        """
        获取用户信誉信息

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            信誉信息字典
        """
        try:
            logger.info(f"开始获取用户 {user_id} 的信誉信息")
            
            # 获取用户所有信誉记录
            reputations = (
                db.query(Reputation)
                .filter(Reputation.UserID == user_id)
                .order_by(desc(Reputation.ReviewTime))  # 按评价时间倒序排序
                .all()
            )
            
            logger.info(f"查询到 {len(reputations)} 条信誉记录")

            if not reputations:
                logger.info(f"用户 {user_id} 没有信誉记录")
                return {
                    "average_score": 0.0,
                    "total_reviews": 0,
                    "score_distribution": {},
                    "recent_reviews": [],
                }

            # 计算平均分
            scores = []
            score_distribution = {}
            recent_reviews = []

            for rep in reputations:
                try:
                    score = float(rep.Score)
                    scores.append(score)

                    # 统计分数分布
                    score_key = str(int(score))
                    score_distribution[score_key] = (
                        score_distribution.get(score_key, 0) + 1
                    )

                    # 获取评价者信息
                    reviewer = db.query(User).filter(User.UserID == rep.RUserID).first()
                    reviewer_name = reviewer.Username if reviewer else "匿名用户"

                    # 获取订单信息（如果有）
                    order_info = ""
                    if rep.OrderID:
                        order = db.query(Orders).filter(Orders.OrderID == rep.OrderID).first()
                        if order:
                            order_info = f" (订单: {order.OrderID})"

                    recent_reviews.append(
                        {
                            "score": score,
                            "review": rep.Review,
                            "reviewer": reviewer_name,
                            "reviewer_id": str(rep.RUserID),
                            "review_time": rep.ReviewTime,
                            "order_info": order_info
                        }
                    )
                except (ValueError, TypeError) as e:
                    logger.error(f"处理信誉记录时出错: {str(e)}, 记录ID: {rep.ReputationID}")
                    continue

            # 按评价时间排序
            recent_reviews.sort(key=lambda x: x.get("review_time", ""), reverse=True)
            recent_reviews = recent_reviews[:10]  # 只返回最近10条

            average_score = sum(scores) / len(scores) if scores else 0.0
            
            result = {
                "average_score": round(average_score, 2),
                "total_reviews": len(scores),
                "score_distribution": score_distribution,
                "recent_reviews": recent_reviews,
            }
            
            logger.info(f"用户 {user_id} 的信誉信息: {result}")
            return result

        except Exception as e:
            logger.error(f"获取信誉信息失败: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "average_score": 0.0,
                "total_reviews": 0,
                "score_distribution": {},
                "recent_reviews": [],
            }

    @staticmethod
    def get_user_points(db: Session, user_id: Decimal) -> Dict[str, Any]:
        """
        获取用户积分信息

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            积分信息字典
        """
        try:
            # 获取用户积分记录
            points_records = db.query(Points).filter(Points.UserID == user_id).all()

            if not points_records:
                return {
                    "total_points": 0,
                    "available_points": 0,
                    "used_points": 0,
                    "points_history": [],
                }

            total_points = 0
            points_history = []

            for record in points_records:
                # 假设Points表有以下字段，根据实际情况调整
                points_value = getattr(record, "Points", 0) or getattr(
                    record, "Value", 0
                )
                try:
                    points_value = int(points_value) if points_value else 0
                except (ValueError, TypeError):
                    points_value = 0

                total_points += points_value

                points_history.append(
                    {
                        "points": points_value,
                        "type": getattr(record, "Type", "未知") or "积分变动",
                        "description": getattr(record, "Description", "") or "积分记录",
                        "date": (
                            getattr(record, "CreateTime", "").isoformat()
                            if hasattr(getattr(record, "CreateTime", None), "isoformat")
                            else "未知时间"
                        ),
                    }
                )

            # 按时间倒序排列
            points_history = sorted(
                points_history, key=lambda x: x["date"], reverse=True
            )[:20]

            return {
                "total_points": total_points,
                "available_points": max(
                    0, total_points
                ),  # 简化处理，实际可能需要更复杂的计算
                "used_points": 0,  # 需要根据实际业务逻辑计算
                "points_history": points_history,
            }

        except Exception as e:
            logger.error(f"获取积分信息失败: {str(e)}")
            return {
                "total_points": 0,
                "available_points": 0,
                "used_points": 0,
                "points_history": [],
            }

    @staticmethod
    def get_users_list(
        db: Session, page: int = 1, per_page: int = 10, role: str = ""
    ) -> Dict[str, Any]:
        """
        获取用户列表（分页）

        Args:
            db: 数据库会话
            page: 页码
            per_page: 每页数量
            role: 角色筛选

        Returns:
            用户列表字典
        """
        try:
            # 构建查询
            query = db.query(User)

            # 角色筛选
            if role and role.strip():
                query = query.filter(User.Role == role.strip())

            # 获取总数
            total = query.count()

            # 分页查询
            offset = (page - 1) * per_page
            users = query.offset(offset).limit(per_page).all()

            # 构建返回数据
            users_data = []
            for user in users:
                user_data = {
                    "user_id": str(user.UserID),
                    "username": user.Username,
                    "email": user.Email,
                    "phone": user.Phone,
                    "address": user.Address,
                    "role": user.Role,
                }

                # 获取信誉评分
                avg_score = (
                    db.query(func.avg(func.cast(Reputation.Score, Float)))
                    .filter(Reputation.UserID == user.UserID)
                    .scalar()
                )
                user_data["reputation_score"] = (
                    round(float(avg_score), 2) if avg_score else 0.0
                )

                # 获取评价数量
                review_count = (
                    db.query(func.count(Reputation.RUserID))
                    .filter(Reputation.UserID == user.UserID)
                    .scalar()
                )
                user_data["review_count"] = review_count or 0

                users_data.append(user_data)

            # 计算分页信息
            total_pages = (total + per_page - 1) // per_page

            return {
                "users": users_data,
                "pagination": {
                    "current_page": page,
                    "per_page": per_page,
                    "total": total,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1,
                },
            }

        except Exception as e:
            traceback.print_exc()
            logger.error(f"获取用户列表失败: {str(e)}")
            return {
                "users": [],
                "pagination": {
                    "current_page": page,
                    "per_page": per_page,
                    "total": 0,
                    "total_pages": 0,
                    "has_next": False,
                    "has_prev": False,
                },
            }

    @staticmethod
    def user_exists(db: Session, user_id: Decimal) -> bool:
        """
        检查用户是否存在

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            用户是否存在
        """
        try:
            return db.query(User).filter(User.UserID == user_id).first() is not None
        except Exception as e:
            logger.error(f"检查用户存在性失败: {str(e)}")
            return False

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """
        根据用户名获取用户

        Args:
            db: 数据库会话
            username: 用户名

        Returns:
            用户对象或None
        """
        try:
            return db.query(User).filter(User.Username == username).first()
        except Exception as e:
            logger.error(f"根据用户名获取用户失败: {str(e)}")
            return None

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        根据邮箱获取用户

        Args:
            db: 数据库会话
            email: 邮箱

        Returns:
            用户对象或None
        """
        try:
            return db.query(User).filter(User.Email == email).first()
        except Exception as e:
            logger.error(f"根据邮箱获取用户失败: {str(e)}")
            return None

    @staticmethod
    def check_reputation_permission(
        db: Session, reviewer_id: Decimal, target_user_id: Decimal, order_id: Optional[Decimal] = None
    ) -> bool:
        """
        检查是否可以评价用户（防止重复评价等）

        Args:
            db: 数据库会话
            reviewer_id: 评价者ID
            target_user_id: 被评价者ID
            order_id: 订单ID（可选）

        Returns:
            是否可以评价
        """
        try:
            # 不能评价自己
            if reviewer_id == target_user_id:
                return False

            # 如果指定了订单ID，检查该订单是否已被评价
            if order_id:
                existing_review = (
                    db.query(Reputation)
                    .filter(
                        and_(
                            Reputation.RUserID == reviewer_id,
                            Reputation.OrderID == order_id
                        )
                    )
                    .first()
                )
                return existing_review is None

            # 如果没有指定订单ID，则允许评价（因为现在支持对不同订单评价）
            return True

        except Exception as e:
            logger.error(f"检查评价权限失败: {str(e)}")
            return False

    @staticmethod
    def add_order_reputation(
        db: Session,
        reviewer_id: Decimal,
        target_user_id: Decimal,
        order_id: Decimal,
        score: float,
        review: str,
    ) -> bool:
        """
        添加订单相关的信誉评价（client对staff）
        """
        try:
            # 查找订单
            order = db.query(Orders).filter(Orders.OrderID == order_id).first()
            if not order:
                logger.warning(f"订单不存在: order_id={order_id}")
                return False
            # 只允许client对staff评价
            if order.ClientID != reviewer_id:
                logger.warning(f"不是订单客户评价: order.ClientID={order.ClientID}, reviewer_id={reviewer_id}")
                return False
            if order.StaffID != target_user_id:
                logger.warning(f"不是订单职员被评价: order.StaffID={order.StaffID}, target_user_id={target_user_id}")
                return False
            # 检查订单状态
            if order.OrderStatus not in ["paid", "completed"]:
                logger.warning(f"订单状态不允许评价: order.OrderStatus={order.OrderStatus}")
                return False
            # 检查是否已评价
            existing = db.query(Reputation).filter(
                Reputation.RUserID == reviewer_id,
                Reputation.UserID == target_user_id,
                Reputation.OrderID == order_id
            ).first()
            if existing:
                logger.warning(f"已评价过: reviewer_id={reviewer_id}, target_user_id={target_user_id}, order_id={order_id}")
                return False
            # 写入Reputation表
            rep = Reputation(
                Score=int(score),
                Review=review,
                RUserID=reviewer_id,
                UserID=target_user_id,
                OrderID=order_id,
                ReviewTime=datetime.now()
            )
            db.add(rep)
            db.commit()
            return True
        except Exception as e:
            logger.error(f"写入订单评价异常: {str(e)}")
            logger.error(traceback.format_exc())
            db.rollback()
            return False

    @staticmethod
    def get_order_reputation(db: Session, order_id: Decimal) -> Dict[str, Any]:
        """
        获取订单相关的评价信息

        Args:
            db: 数据库会话
            order_id: 订单ID

        Returns:
            订单评价信息
        """
        try:
            # 查询订单相关的评价
            reputations = (
                db.query(Reputation).filter(Reputation.OrderID == order_id).all()
            )

            if not reputations:
                return {"client_to_staff": None, "staff_to_client": None}

            # 获取订单信息
            order = db.query(Orders).filter(Orders.OrderID == order_id).first()
            if not order:
                return {"client_to_staff": None, "staff_to_client": None}

            client_id = order.ClientID
            staff_id = order.StaffID

            result = {"client_to_staff": None, "staff_to_client": None}

            for rep in reputations:
                # 客户评价代办人员
                if rep.RUserID == client_id and rep.UserID == staff_id:
                    client = db.query(User).filter(User.UserID == client_id).first()
                    staff = db.query(User).filter(User.UserID == staff_id).first()

                    result["client_to_staff"] = {
                        "reviewer": client.Username if client else "未知用户",
                        "target": staff.Username if staff else "未知用户",
                        "score": float(rep.Score),
                        "review": rep.Review,
                        "review_time": rep.ReviewTime,
                    }

                # 代办人员评价客户
                if rep.RUserID == staff_id and rep.UserID == client_id:
                    client = db.query(User).filter(User.UserID == client_id).first()
                    staff = db.query(User).filter(User.UserID == staff_id).first()

                    result["staff_to_client"] = {
                        "reviewer": staff.Username if staff else "未知用户",
                        "target": client.Username if client else "未知用户",
                        "score": float(rep.Score),
                        "review": rep.Review,
                        "review_time": rep.ReviewTime,
                    }

            return result

        except Exception as e:
            logger.error(f"获取订单评价失败: {str(e)}")
            return {"client_to_staff": None, "staff_to_client": None}

    @staticmethod
    def get_user_statistics(db: Session, user_id: Decimal) -> Dict[str, Any]:
        """
        获取用户统计信息

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            统计信息字典
        """
        try:
            user = db.query(User).filter(User.UserID == user_id).first()
            if not user:
                return {}

            # 获取信誉统计
            reputation_count = (
                db.query(func.count(Reputation.RUserID))
                .filter(Reputation.UserID == user_id)
                .scalar()
                or 0
            )

            avg_reputation = (
                db.query(func.avg(func.cast(Reputation.Score, Float)))
                .filter(Reputation.UserID == user_id)
                .scalar()
                or 0.0
            )

            # 获取积分统计
            total_points = 0
            try:
                points_sum = (
                    db.query(
                        func.sum(
                            func.cast(
                                (
                                    Points.Points
                                    if hasattr(Points, "Points")
                                    else Points.Points
                                ),
                                Integer,
                            )
                        )
                    )
                    .filter(Points.UserID == user_id)
                    .scalar()
                )
                total_points = int(points_sum) if points_sum else 0
            except:
                total_points = 0

            result = {
                "user_info": {
                    "user_id": str(user.UserID),
                    "username": user.Username,
                    "role": user.Role,
                },
                "reputation": {
                    "average_score": round(float(avg_reputation), 2),
                    "total_reviews": reputation_count,
                },
                "points": {"total_points": total_points},
            }

            # 如果角色为staff，额外获取salary信息
            if user.Role == "staff":
                staff = db.query(Staff).filter(Staff.UserID == user_id).first()
                if staff and hasattr(staff, "Salary"):
                    result["staff_info"] = {
                        "salary": staff.Salary,
                        "staff_id": (
                            str(staff.StaffID) if hasattr(staff, "StaffID") else ""
                        ),
                    }

            return result

        except Exception as e:
            traceback.print_exc()
            logger.error(f"获取用户统计信息失败: {str(e)}")
            return {}

    @staticmethod
    def admin_update_user_info(
        db: Session, admin_id: Decimal, user_id: Decimal, data: Dict[str, Any]
    ) -> bool:
        """
        管理员更新用户信息

        Args:
            db: 数据库会话
            admin_id: 管理员ID
            user_id: 被修改的用户ID
            data: 更新数据

        Returns:
            更新是否成功
        """
        try:
            # 验证管理员权限
            admin = (
                db.query(User)
                .filter(User.UserID == admin_id, User.Role == "admin")
                .first()
            )
            if not admin:
                logger.error(f"管理员权限验证失败: {admin_id}")
                return False

            # 查找目标用户
            user = db.query(User).filter(User.UserID == user_id).first()
            if not user:
                logger.error(f"用户不存在: {user_id}")
                return False

            # 可更新的字段
            updatable_fields = ["username", "email", "phone", "address", "role"]

            for field in updatable_fields:
                if field in data and data[field] is not None:
                    # 转换字段名为数据库字段名
                    db_field = field.capitalize() if field != "username" else "Username"
                    setattr(user, db_field, data[field])

            # 如果修改了角色，需要确保相应的角色表中也有记录
            if "role" in data and data["role"] != user.Role:
                # 这里可以添加角色变更的逻辑，如果需要的话
                # 例如：如果用户从client变为staff，需要在Staff表中添加记录
                pass

            db.commit()
            logger.info(f"管理员 {admin_id} 成功更新用户 {user_id} 的信息")
            return True

        except Exception as e:
            logger.error(f"管理员更新用户信息失败: {str(e)}")
            db.rollback()
            return False

    @staticmethod
    def admin_reset_user_password(
        db: Session, admin_id: Decimal, user_id: Decimal, new_password_hash: str
    ) -> bool:
        """
        管理员重置用户密码

        Args:
            db: 数据库会话
            admin_id: 管理员ID
            user_id: 被重置密码的用户ID
            new_password_hash: 新密码哈希值

        Returns:
            重置是否成功
        """
        try:
            # 验证管理员权限
            admin = (
                db.query(User)
                .filter(User.UserID == admin_id, User.Role == "admin")
                .first()
            )
            if not admin:
                logger.error(f"管理员权限验证失败: {admin_id}")
                return False

            # 查找目标用户
            user = db.query(User).filter(User.UserID == user_id).first()
            if not user:
                logger.error(f"用户不存在: {user_id}")
                return False

            # 更新密码
            user.Password = new_password_hash

            # 如果用户在其他表中也有密码字段，也需要更新
            if user.Role == "admin":
                admin_user = db.query(Admin).filter(Admin.UserID == user_id).first()
                if admin_user:
                    admin_user.Password = new_password_hash
            elif user.Role == "client":
                client_user = db.query(Client).filter(Client.UserID == user_id).first()
                if client_user:
                    client_user.Password = new_password_hash
            elif user.Role == "staff":
                staff_user = db.query(Staff).filter(Staff.UserID == user_id).first()
                if staff_user:
                    staff_user.Password = new_password_hash

            db.commit()
            logger.info(f"管理员 {admin_id} 成功重置用户 {user_id} 的密码")
            return True

        except Exception as e:
            logger.error(f"管理员重置用户密码失败: {str(e)}")
            db.rollback()
            return False
