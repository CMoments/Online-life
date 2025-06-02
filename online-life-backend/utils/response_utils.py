from flask import jsonify
from datetime import datetime


def success_response(data=None, message="操作成功", status_code=200):
    """成功响应"""
    response = {
        "success": True,
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat(),
    }
    return jsonify(response), status_code


def error_response(message="操作失败", status_code=400, error_code=None):
    """错误响应"""
    response = {
        "success": False,
        "message": message,
        "error_code": error_code,
        "timestamp": datetime.now().isoformat(),
    }
    return jsonify(response), status_code


def paginated_response(items, total, page, per_page, message="获取数据成功"):
    """分页响应"""
    data = {
        "items": items,
        "pagination": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page,
            "has_prev": page > 1,
            "has_next": page * per_page < total,
        },
    }
    return success_response(data, message)


def validation_error_response(errors):
    """验证错误响应"""
    return error_response(
        message="数据验证失败", status_code=422, error_code="VALIDATION_ERROR"
    )


class ResponseFormatter:
    """响应格式化器"""

    @staticmethod
    def format_user_info(user):
        """格式化用户信息"""
        if not user:
            return None

        return {
            "user_id": str(user.UserID),
            "username": user.Username,
            "email": user.Email,
            "phone": user.Phone,
            "address": user.Address,
            "role": user.Role,
        }

    @staticmethod
    def format_order_info(order):
        """格式化订单信息"""
        if not order:
            return None

        return {
            "order_id": str(order.OUserID),
            "order_type": order.OrderType,
            "order_status": order.OrderStatus,
            "creation_time": order.CreationTime,
            "completion_time": order.CompletionTime,
            "assignment_type": order.AssignmentType,
            "assignment_status": order.AssignmentStatus,
            "user_id": str(order.UserID),
        }

    @staticmethod
    def format_task_info(task):
        """格式化任务信息"""
        if not task:
            return None

        return {
            "task_id": str(task.TaskID),
            "task_type": task.TaskType,
            "description": task.Description,
            "estimated_time": task.EstimatedTime,
            "actual_time": task.ActualTime,
            "current_bidder": task.CurrentBidder,
            "bid_deadline": task.BidDeadline,
        }

    @staticmethod
    def format_points_info(points):
        """格式化积分信息"""
        if not points:
            return {"points": 0}

        return {
            "user_id": str(points.UserID),
            "points": int(points.Points) if points.Points.isdigit() else 0,
        }

    @staticmethod
    def format_reputation_info(reputation_list):
        """格式化信誉信息"""
        if not reputation_list:
            return {"average_score": 0, "total_reviews": 0, "reviews": []}

        total_score = sum(
            float(rep.Score)
            for rep in reputation_list
            if rep.Score.replace(".", "").isdigit()
        )
        average_score = total_score / len(reputation_list) if reputation_list else 0

        reviews = []
        for rep in reputation_list:
            reviews.append(
                {
                    "reviewer_id": str(rep.RUserID),
                    "score": (
                        float(rep.Score) if rep.Score.replace(".", "").isdigit() else 0
                    ),
                    "review": rep.Review,
                }
            )

        return {
            "average_score": round(average_score, 2),
            "total_reviews": len(reputation_list),
            "reviews": reviews,
        }
