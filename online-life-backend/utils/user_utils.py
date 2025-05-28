from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from models import User, Reputation, Points, Admin, Client, Staff
from decimal import Decimal
from typing import Optional, Dict, List, Any
import logging

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
                                admin_info.AdminLevel
                                if hasattr(admin_info, "AdminLevel")
                                else None
                            ),
                            "permissions": (
                                admin_info.Permissions
                                if hasattr(admin_info, "Permissions")
                                else None
                            ),
                        }
                    )
            elif user.Role == "client":
                client_info = db.query(Client).filter(Client.UserID == user_id).first()
                if client_info:
                    user_info.update(
                        {
                            "client_type": (
                                client_info.ClientType
                                if hasattr(client_info, "ClientType")
                                else None
                            ),
                            "registration_date": (
                                client_info.RegistrationDate.isoformat()
                                if hasattr(client_info, "RegistrationDate")
                                else None
                            ),
                        }
                    )
            elif user.Role == "staff":
                staff_info = db.query(Staff).filter(Staff.UserID == user_id).first()
                if staff_info:
                    user_info.update(
                        {
                            "department": (
                                staff_info.Department
                                if hasattr(staff_info, "Department")
                                else None
                            ),
                            "position": (
                                staff_info.Position
                                if hasattr(staff_info, "Position")
                                else None
                            ),
                        }
                    )

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
            # 获取用户所有信誉记录
            reputations = (
                db.query(Reputation).filter(Reputation.UserID == user_id).all()
            )

            if not reputations:
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

                    recent_reviews.append(
                        {
                            "score": score,
                            "review": rep.Review,
                            "reviewer": reviewer_name,
                            "reviewer_id": str(rep.RUserID),
                        }
                    )
                except (ValueError, TypeError):
                    continue

            # 按评价时间排序（假设有时间字段，这里按ID倒序）
            recent_reviews = sorted(
                recent_reviews, key=lambda x: x["reviewer_id"], reverse=True
            )[:10]

            average_score = sum(scores) / len(scores) if scores else 0.0

            return {
                "average_score": round(average_score, 2),
                "total_reviews": len(scores),
                "score_distribution": score_distribution,
                "recent_reviews": recent_reviews,
            }

        except Exception as e:
            logger.error(f"获取信誉信息失败: {str(e)}")
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
                    db.query(
                        func.avg(func.cast(Reputation.Score, db.bind.dialect.FLOAT))
                    )
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
        db: Session, reviewer_id: Decimal, target_user_id: Decimal
    ) -> bool:
        """
        检查是否可以评价用户（防止重复评价等）

        Args:
            db: 数据库会话
            reviewer_id: 评价者ID
            target_user_id: 被评价者ID

        Returns:
            是否可以评价
        """
        try:
            # 不能评价自己
            if reviewer_id == target_user_id:
                return False

            # 检查是否已经评价过（可根据业务需求调整）
            existing_review = (
                db.query(Reputation)
                .filter(
                    and_(
                        Reputation.RUserID == reviewer_id,
                        Reputation.UserID == target_user_id,
                    )
                )
                .first()
            )

            return existing_review is None

        except Exception as e:
            logger.error(f"检查评价权限失败: {str(e)}")
            return False

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
                db.query(func.avg(func.cast(Reputation.Score, db.bind.dialect.FLOAT)))
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
                                    else Points.Value
                                ),
                                db.bind.dialect.INTEGER,
                            )
                        )
                    )
                    .filter(Points.UserID == user_id)
                    .scalar()
                )
                total_points = int(points_sum) if points_sum else 0
            except:
                total_points = 0

            return {
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

        except Exception as e:
            logger.error(f"获取用户统计信息失败: {str(e)}")
            return {}
