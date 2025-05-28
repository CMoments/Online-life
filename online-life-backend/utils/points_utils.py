from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import Dict, List, Optional, Any
from models import Points, User
import logging

logger = logging.getLogger(__name__)


class PointsUtils:
    """积分管理工具类"""

    @staticmethod
    def get_user_points_balance(db: Session, user_id: Decimal) -> int:
        """
        获取用户积分余额

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            int: 用户积分余额，如果用户不存在则返回0
        """
        try:
            points_record = db.query(Points).filter(Points.UserID == user_id).first()
            if points_record:
                return int(points_record.Points) if points_record.Points else 0
            return 0
        except Exception as e:
            logger.error(f"获取用户积分余额失败: {str(e)}")
            return 0

    @staticmethod
    def _ensure_user_points_record(db: Session, user_id: Decimal) -> Points:
        """
        确保用户积分记录存在，如果不存在则创建

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            Points: 用户积分记录
        """
        points_record = db.query(Points).filter(Points.UserID == user_id).first()
        if not points_record:
            points_record = Points(UserID=user_id, Points="0")
            db.add(points_record)
            db.flush()  # 立即执行插入但不提交
        return points_record

    @staticmethod
    def add_points(
        db: Session, user_id: Decimal, points_amount: int, reason: str
    ) -> bool:
        """
        增加用户积分

        Args:
            db: 数据库会话
            user_id: 用户ID
            points_amount: 要增加的积分数量
            reason: 增加积分的原因

        Returns:
            bool: 操作是否成功
        """
        try:
            # 确保用户积分记录存在
            points_record = PointsUtils._ensure_user_points_record(db, user_id)

            # 更新积分
            current_points = int(points_record.Points) if points_record.Points else 0
            new_points = current_points + points_amount
            points_record.Points = str(new_points)

            # 记录积分变更日志
            PointsUtils._log_points_transaction(
                db, user_id, points_amount, "ADD", reason, current_points, new_points
            )

            db.commit()
            logger.info(
                f"用户 {user_id} 积分增加成功: +{points_amount}, 原因: {reason}"
            )
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"增加积分失败: {str(e)}")
            return False

    @staticmethod
    def deduct_points(
        db: Session, user_id: Decimal, points_amount: int, reason: str
    ) -> bool:
        """
        扣除用户积分

        Args:
            db: 数据库会话
            user_id: 用户ID
            points_amount: 要扣除的积分数量
            reason: 扣除积分的原因

        Returns:
            bool: 操作是否成功
        """
        try:
            # 获取用户积分记录
            points_record = db.query(Points).filter(Points.UserID == user_id).first()
            if not points_record:
                logger.warning(f"用户 {user_id} 积分记录不存在")
                return False

            current_points = int(points_record.Points) if points_record.Points else 0

            # 检查积分是否足够
            if current_points < points_amount:
                logger.warning(
                    f"用户 {user_id} 积分不足: 当前{current_points}, 需要扣除{points_amount}"
                )
                return False

            # 扣除积分
            new_points = current_points - points_amount
            points_record.Points = str(new_points)

            # 记录积分变更日志
            PointsUtils._log_points_transaction(
                db,
                user_id,
                -points_amount,
                "DEDUCT",
                reason,
                current_points,
                new_points,
            )

            db.commit()
            logger.info(
                f"用户 {user_id} 积分扣除成功: -{points_amount}, 原因: {reason}"
            )
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"扣除积分失败: {str(e)}")
            return False

    @staticmethod
    def transfer_points(
        db: Session,
        from_user_id: Decimal,
        to_user_id: Decimal,
        points_amount: int,
        message: str,
    ) -> bool:
        """
        积分转账

        Args:
            db: 数据库会话
            from_user_id: 转出用户ID
            to_user_id: 转入用户ID
            points_amount: 转账积分数量
            message: 转账留言

        Returns:
            bool: 操作是否成功
        """
        try:
            # 检查转出用户积分
            from_points_record = (
                db.query(Points).filter(Points.UserID == from_user_id).first()
            )
            if not from_points_record:
                logger.warning(f"转出用户 {from_user_id} 积分记录不存在")
                return False

            current_from_points = (
                int(from_points_record.Points) if from_points_record.Points else 0
            )
            if current_from_points < points_amount:
                logger.warning(f"转出用户 {from_user_id} 积分不足")
                return False

            # 确保转入用户积分记录存在
            to_points_record = PointsUtils._ensure_user_points_record(db, to_user_id)
            current_to_points = (
                int(to_points_record.Points) if to_points_record.Points else 0
            )

            # 执行转账
            new_from_points = current_from_points - points_amount
            new_to_points = current_to_points + points_amount

            from_points_record.Points = str(new_from_points)
            to_points_record.Points = str(new_to_points)

            # 记录转账日志
            transfer_reason = f"转账给用户{to_user_id}: {message}"
            receive_reason = f"收到用户{from_user_id}转账: {message}"

            PointsUtils._log_points_transaction(
                db,
                from_user_id,
                -points_amount,
                "TRANSFER_OUT",
                transfer_reason,
                current_from_points,
                new_from_points,
            )

            PointsUtils._log_points_transaction(
                db,
                to_user_id,
                points_amount,
                "TRANSFER_IN",
                receive_reason,
                current_to_points,
                new_to_points,
            )

            db.commit()
            logger.info(
                f"积分转账成功: {from_user_id} -> {to_user_id}, 数量: {points_amount}"
            )
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"积分转账失败: {str(e)}")
            return False

    @staticmethod
    def get_points_history(
        db: Session, user_id: Decimal, page: int = 1, per_page: int = 20
    ) -> Dict[str, Any]:
        """
        获取用户积分历史记录

        Args:
            db: 数据库会话
            user_id: 用户ID
            page: 页码
            per_page: 每页记录数

        Returns:
            Dict: 包含历史记录和分页信息的字典
        """
        try:
            # 由于当前模型设计较简单，这里返回模拟数据
            # 在实际项目中，您可能需要创建一个 PointsHistory 表来记录详细的积分变更历史

            current_balance = PointsUtils.get_user_points_balance(db, user_id)

            # 模拟历史记录（实际项目中应该从积分历史表查询）
            mock_history = [
                {
                    "id": 1,
                    "points_change": "+100",
                    "transaction_type": "ADD",
                    "reason": "每日签到奖励",
                    "balance_after": current_balance,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            ]

            return {
                "records": mock_history,
                "current_page": page,
                "per_page": per_page,
                "total_records": len(mock_history),
                "total_pages": 1,
                "current_balance": current_balance,
            }

        except Exception as e:
            logger.error(f"获取积分历史失败: {str(e)}")
            return {
                "records": [],
                "current_page": page,
                "per_page": per_page,
                "total_records": 0,
                "total_pages": 0,
                "current_balance": 0,
            }

    # @staticmethod
    # def get_points_ranking(db: Session, limit: int = 50) -> List[Dict[str, Any]]:
    #     """
    #     获取积分排行榜

    #     Args:
    #         db: 数据库会话
    #         limit: 返回记录数限制

    #     Returns:
    #         List[Dict]: 积分排行榜列表
    #     """
    #     try:
    #         # 查询积分排行榜
    #         ranking_query = (
    #             db.query(Points)
    #             .filter(Points.Points.isnot(None))
    #             .order_by(desc(func.cast(Points.Points, func.INTEGER())))
    #             .limit(limit)
    #         )

    #         ranking_list = []
    #         for idx, points_record in enumerate(ranking_query.all(), 1):
    #             ranking_list.append(
    #                 {
    #                     "rank": idx,
    #                     "username": str(points_record.UserID),
    #                     "points": (
    #                         int(points_record.Points) if points_record.Points else 0
    #                     ),
    #                 }
    #             )

    #         return ranking_list

    #     except Exception as e:
    #         logger.error(f"获取积分排行榜失败: {str(e)}")
    #         return []
    @staticmethod
    def get_points_ranking(db: Session, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取积分排行榜

        Args:
            db: 数据库会话
            limit: 返回记录数限制

        Returns:
            List[Dict]: 积分排行榜列表, 包含 'rank', 'username', 'points'
        """
        try:
            ranking_query = (
                db.query(
                    User.Username,  # 选择 User 表中的 Username
                    Points.Points,  # 选择 Points 表中的 Points
                )
                .join(User, Points.UserID == User.UserID)  # 通过 UserID 关联两个表
                .filter(Points.Points.isnot(None))  # 过滤掉 Points 为空的记录
                .order_by(
                    desc(func.cast(Points.Points, func.INTEGER()))
                )  # 按 Points 降序排列 (转换为整数比较)
                .limit(limit)  # 限制返回的记录数
            )

            ranking_list = []
            for idx, (username, points_value) in enumerate(ranking_query.all(), 1):
                ranking_list.append(
                    {
                        "rank": idx,
                        "username": username,
                        "points": int(points_value) if points_value else 0,
                    }
                )

            return ranking_list

        except Exception as e:
            logger.error(f"获取积分排行榜失败: {str(e)}")
            return []

    @staticmethod
    def _log_points_transaction(
        db: Session,
        user_id: Decimal,
        points_change: int,
        transaction_type: str,
        reason: str,
        balance_before: int,
        balance_after: int,
    ) -> None:
        """
        记录积分变更日志（私有方法）

        Args:
            db: 数据库会话
            user_id: 用户ID
            points_change: 积分变更数量
            transaction_type: 交易类型
            reason: 变更原因
            balance_before: 变更前余额
            balance_after: 变更后余额
        """
        try:
            # 这里只是日志记录，实际项目中您可能需要将这些信息存储到积分历史表中
            log_message = (
                f"积分变更 - 用户: {user_id}, 类型: {transaction_type}, "
                f"变更: {points_change}, 原因: {reason}, "
                f"余额: {balance_before} -> {balance_after}"
            )
            logger.info(log_message)

        except Exception as e:
            logger.error(f"记录积分变更日志失败: {str(e)}")

    @staticmethod
    def batch_add_points(
        db: Session, user_points_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        批量增加积分

        Args:
            db: 数据库会话
            user_points_list: 用户积分列表，格式: [{"user_id": Decimal, "points": int, "reason": str}]

        Returns:
            Dict: 操作结果统计
        """
        success_count = 0
        fail_count = 0
        fail_details = []

        try:
            for item in user_points_list:
                user_id = item.get("user_id")
                points = item.get("points")
                reason = item.get("reason", "批量增加积分")

                if PointsUtils.add_points(db, user_id, points, reason):
                    success_count += 1
                else:
                    fail_count += 1
                    fail_details.append(
                        {
                            "user_id": str(user_id),
                            "points": points,
                            "reason": "操作失败",
                        }
                    )

            return {
                "success_count": success_count,
                "fail_count": fail_count,
                "fail_details": fail_details,
                "total_processed": len(user_points_list),
            }

        except Exception as e:
            logger.error(f"批量增加积分失败: {str(e)}")
            return {
                "success_count": 0,
                "fail_count": len(user_points_list),
                "fail_details": [{"error": str(e)}],
                "total_processed": len(user_points_list),
            }

    @staticmethod
    def check_points_sufficient(
        db: Session, user_id: Decimal, required_points: int
    ) -> bool:
        """
        检查用户积分是否充足

        Args:
            db: 数据库会话
            user_id: 用户ID
            required_points: 需要的积分数量

        Returns:
            bool: 积分是否充足
        """
        current_balance = PointsUtils.get_user_points_balance(db, user_id)
        return current_balance >= required_points
