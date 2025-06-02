import requests
import json
import logging
from typing import Dict, Any, Tuple, Optional
from config import AMAP_KEY
from typing import Dict, Any, Optional
from decimal import Decimal
from models import Orders, Task, Staff, Client, User  # 导入Client模型
from utils.db_utils import get_db_session  # 导入数据库会话工具
from datetime import datetime
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

_geocode_cache = {}

class MapUtils:
    """地图工具类，用于处理地理位置和路径规划"""

    @staticmethod
    def geocode(address: str) -> Optional[Dict[str, float]]:
        """地理编码：将地址转换为经纬度坐标

        Args:
            address: 地址字符串

        Returns:
            包含经纬度的字典 {"longitude": 经度, "latitude": 纬度}
            如果转换失败则返回None
        """
        if address in _geocode_cache:
            return _geocode_cache[address]
        try:
            url = "https://restapi.amap.com/v3/geocode/geo"
            params = {"key": AMAP_KEY, "address": address, "output": "json"}
            full_url = f"{url}?key={AMAP_KEY}&address={address}&output=json"
            print(f"[DEBUG] 请求URL: {full_url}")
            response = requests.get(url, params=params)
            print(f"[DEBUG] 响应内容: {response.text}")
            result = response.json()

            if (
                result.get("status") == "1"
                and result.get("geocodes")
                and len(result["geocodes"]) > 0
            ):
                location = result["geocodes"][0]["location"].split(",")
                coords = {"longitude": float(location[0]), "latitude": float(location[1])}
                _geocode_cache[address] = coords
                return coords
            else:
                logger.error(f"地理编码失败: {result}")
                return None

        except Exception as e:
            logger.error(f"地理编码异常: {str(e)}")
            return None

    @staticmethod
    def calculate_route(origin: str, destination: str) -> Optional[Dict[str, Any]]:
        """计算两点之间的骑行路线

        Args:
            origin: 起点地址或经纬度(经度,纬度)
            destination: 终点地址或经纬度(经度,纬度)

        Returns:
            路线信息字典，包含距离(米)和时间(秒)
            如果计算失败则返回None
        """
        try:
            # 如果输入的是地址而非坐标，先进行地理编码
            if not ("," in origin and "," in destination):
                origin_coords = MapUtils.geocode(origin)
                destination_coords = MapUtils.geocode(destination)

                if not origin_coords or not destination_coords:
                    return {"error": "geocode_failed"}

                origin = f"{origin_coords['longitude']},{origin_coords['latitude']}"
                destination = f"{destination_coords['longitude']},{destination_coords['latitude']}"

            # 调用骑行路径规划API
            url = "https://restapi.amap.com/v4/direction/bicycling"
            params = {
                "key": AMAP_KEY,
                "origin": origin,
                "destination": destination,
                "output": "json",
            }

            response = requests.get(url, params=params)
            result = response.json()
            logger.info(f"[高德路径规划API] 请求: {url} 参数: {params} 响应: {result}")

            if (
                result.get("errcode") == 0
                and result.get("data")
                and result["data"].get("paths")
            ):
                path = result["data"]["paths"][0]
                return {
                    "distance": int(path.get("distance", 0)),
                    "duration": int(path.get("duration", 0)),
                    "route": path,
                }
            else:
                logger.error(f"路径规划失败: {result}")
                return {"error": result}
        except Exception as e:
            logger.error(f"路径规划异常: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    def get_current_location() -> Optional[Tuple[float, float]]:
        """获取当前定位（模拟实现）

        实际项目中应该从前端获取定位信息
        """
        # 模拟位置 - 北京中关村
        return (116.310905, 39.992806)

    @staticmethod
    def estimate_delivery_time(
        shop_address: str, delivery_address: str
    ) -> Dict[str, Any]:
        """估算送达时间

        Args:
            shop_address: 商店地址
            delivery_address: 送达地址

        Returns:
            包含预计时间信息的字典
        """
        result = {
            "to_shop_time": 15 * 60,
            "delivery_time": 30 * 60,
            "total_time": 45 * 60,
            "distance": 5000,
            "status": "estimated",
            "error": None,
        }
        route_info = MapUtils.calculate_route(shop_address, delivery_address)
        if route_info and "duration" in route_info:
            delivery_time = route_info["duration"] + 5 * 60
            result.update({
                "delivery_time": delivery_time,
                "total_time": result["to_shop_time"] + delivery_time,
                "distance": route_info["distance"],
                "status": "calculated",
                "error": None,
            })
        elif route_info and "error" in route_info:
            result["error"] = route_info["error"]
        return result

    @staticmethod
    def parse_location(location_str: str) -> Dict[str, Any]:
        """解析位置信息字符串

        Args:
            location_str: 位置信息字符串,可能是JSON格式或普通地址

        Returns:
            解析后的位置信息字典
        """
        try:
            # 尝试解析为JSON
            location = json.loads(location_str)
            return location
        except json.JSONDecodeError:
            # 如果不是JSON，则视为普通地址字符串
            return {"address": location_str}

    @staticmethod
    def estimate_order_time(
        rider_location: str, store_location: str, delivery_location: str
    ) -> Dict[str, Any]:
        """估算订单总时间（骑手 → 店铺 → 用户）

        Args:
            rider_location: 骑手当前位置（地址或经纬度）
            store_location: 店铺位置（地址或经纬度）
            delivery_location: 用户收货地址（地址或经纬度）

        Returns:
            包含 to_store（骑手到店）、to_user（到用户）、total（总计） 的字典
        """
        route_to_store = MapUtils.calculate_route(rider_location, store_location)
        to_store_time = (
            route_to_store["duration"] if route_to_store else 15 * 60
        )  # 默认15分钟

        route_to_user = MapUtils.calculate_route(store_location, delivery_location)
        to_user_time = (
            route_to_user["duration"] if route_to_user else 30 * 60
        )  # 默认30分钟

        total_time = to_store_time + to_user_time

        return {
            "to_store": to_store_time,
            "to_user": to_user_time,
            "total": total_time,
            "status": (
                "calculated" if (route_to_store and route_to_user) else "estimated"
            ),
        }

    @staticmethod
    def get_order_location(db_session, order_id: Decimal) -> Optional[Dict[str, Any]]:
        """从数据库获取订单位置信息"""
        try:
            order = db_session.query(Orders).filter_by(OrderID=order_id).first()
            if order and order.OrderLocation:
                return MapUtils.parse_location(order.OrderLocation)
            return None
        except Exception as e:
            logger.error(f"获取订单位置失败: {str(e)}")
            return None

    @staticmethod
    def get_staff_location(db_session, staff_id: Decimal) -> Optional[Dict[str, Any]]:
        """从数据库获取骑手位置信息"""
        try:
            staff = db_session.query(Staff).filter_by(UserID=staff_id).first()
            if staff and staff.Address:
                return {"address": staff.Address}
            return None
        except Exception as e:
            logger.error(f"获取骑手位置失败: {str(e)}")
            return None

    @staticmethod
    def get_client_location(db_session, client_id: Decimal) -> Optional[Dict[str, Any]]:
        """从数据库获取客户位置信息"""
        try:
            client = db_session.query(User).filter_by(UserID=client_id).first()
            if client and client.Address:
                return {"address": client.Address}
            return None
        except Exception as e:
            logger.error(f"获取客户位置失败: {str(e)}")
            return None

    @staticmethod
    def get_store_location(db_session, store_id: Decimal = None) -> str:
        """获取店铺位置（示例实现）"""
        # 实际项目中应该从数据库获取店铺地址
        # 这里使用默认值作为示例
        return "北京市海淀区中关村大街1号"  # 示例店铺地址

    @staticmethod
    def update_order_estimated_time(
        db_session, order_id: Decimal, estimated_time: int
    ) -> bool:
        """更新订单的预计时间到数据库"""
        try:
            order = db_session.query(Orders).filter_by(OrderID=order_id).first()
            if order:
                # 假设Orders模型中有EstimatedTime字段
                order.EstimatedTime = str(estimated_time)
                db_session.commit()
                return True
            return False
        except Exception as e:
            db_session.rollback()
            logger.error(f"更新订单预计时间失败: {str(e)}")
            return False

    @staticmethod
    def calculate_order_estimated_time(db: Session, order_location: str, user_id: Decimal, shop_address: str = None) -> Dict[str, Any]:
        """计算订单预计时间"""
        try:
            # 获取商家地址
            if not shop_address:
                shop_address = "北京市海淀区中关村大街1号"
            # 获取客户地址
            client = db.query(User).filter_by(UserID=user_id).first()
            if not client or not client.Address:
                raise Exception("无法获取客户地址")
            # 日志打印
            logger.info(f"[预计时间] 商家地址: {shop_address}, 客户地址: {client.Address}")
            # 计算预计时间
            time_estimate = MapUtils.estimate_delivery_time(
                shop_address=shop_address,
                delivery_address=client.Address
            )
            logger.info(f"[预计时间] 计算结果: {time_estimate}")
            print("!!! 校验条件已更新 !!!")
            return time_estimate
        except Exception as e:
            logger.error(f"计算订单预计时间失败: {str(e)}")
            return {
                "to_shop_time": 15 * 60,
                "delivery_time": 30 * 60,
                "total": 45 * 60,
                "distance": 5000,
                "status": "estimated"
            }