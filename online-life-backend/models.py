from typing import Optional

from sqlalchemy import DECIMAL, String, Integer, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import decimal


class Base(DeclarativeBase):
    pass


class Admin(Base):
    __tablename__ = "Admin"

    UserID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0), primary_key=True)
    Username: Mapped[str] = mapped_column(String(32))
    Password: Mapped[str] = mapped_column(String(128))
    Email: Mapped[str] = mapped_column(String(64))
    Phone: Mapped[str] = mapped_column(String(30))
    Address: Mapped[str] = mapped_column(String(255))
    Role: Mapped[str] = mapped_column(String(30))
    JoinDate: Mapped[str] = mapped_column(String(30))
    Adlevel: Mapped[str] = mapped_column(String(30))


class BidRecord(Base):
    __tablename__ = "BidRecord"

    UserID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0), primary_key=True)
    TaskID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0), primary_key=True)
    BidID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0))
    BidTime: Mapped[str] = mapped_column(String(30))
    BidStatus: Mapped[str] = mapped_column(String(30))
    # BidAmount: Mapped[str] = mapped_column(String(30))


class Client(Base):
    __tablename__ = "Client"

    UserID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0), primary_key=True)
    Username: Mapped[str] = mapped_column(String(32))
    Password: Mapped[str] = mapped_column(String(128))
    Email: Mapped[str] = mapped_column(String(64))
    Phone: Mapped[str] = mapped_column(String(30))
    Address: Mapped[str] = mapped_column(String(255))
    Role: Mapped[str] = mapped_column(String(30))
    ClientID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0))


class GroupTask(Base):
    __tablename__ = "GroupTask"

    GroupTaskID: Mapped[decimal.Decimal] = mapped_column(
        DECIMAL(20, 0), primary_key=True
    )
    # TaskID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0))
    # ParticipatingUserID: Mapped[str] = mapped_column(String(30))
    JoinTime: Mapped[str] = mapped_column(String(30))
    endTime: Mapped[Optional[str]] = mapped_column(String(30))


class GroupTaskUser(Base):
    __tablename__ = "GroupTaskUser"
    # __table_args__ = {"comment": "һ   Ű    ˿    ɶ   û     \r\nһ   û    Բ      Ű     "}

    UserID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0), primary_key=True)
    TaskID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0), primary_key=True)
    GroupTaskID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0))


class Orders(Base):
    __tablename__ = "Orders"

    OrderType: Mapped[str] = mapped_column(String(30))
    OrderStatus: Mapped[str] = mapped_column(String(30))
    CreationTime: Mapped[str] = mapped_column(String(30))
    CompletionTime: Mapped[str] = mapped_column(String(30))
    EstimatedTime: Mapped[str] = mapped_column(String(30))
    AssignmentType: Mapped[str] = mapped_column(String(30))
    AssignmentStatus: Mapped[str] = mapped_column(String(30))
    OrderID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0), primary_key=True)
    ClientID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0))
    OrderLocation: Mapped[str] = mapped_column(String(255))
    StaffID: Mapped[Optional[decimal.Decimal]] = mapped_column(
        DECIMAL(20, 0), nullable=True
    )
    Amount: Mapped[str] = mapped_column(String(20, 0))
    ShopAddress: Mapped[Optional[str]] = mapped_column(String(255), comment="商家地址")

    def to_dict(self):
        return {
            "order_id": str(self.OrderID),
            "order_type": self.OrderType,
            "client_id": str(self.ClientID),
            "order_status": self.OrderStatus,
            "creation_time": self.CreationTime if isinstance(self.CreationTime, str) else self.CreationTime.strftime("%Y-%m-%d %H:%M:%S"),
            "completion_time": self.CompletionTime,
            "estimated_time": self.EstimatedTime,
            "assignment_type": self.AssignmentType,
            "assignment_status": self.AssignmentStatus,
            "order_location": self.OrderLocation,
            "staff_id": str(self.StaffID) if self.StaffID else None,
            "amount": self.Amount,
            "shop_address": self.ShopAddress,
            # 可根据需要补充更多字段
        }


class Points(Base):
    __tablename__ = "Points"

    UserID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0), primary_key=True)
    Points: Mapped[str] = mapped_column(String(30))


class Reputation(Base):
    __tablename__ = "Reputation"

    ReputationID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Score: Mapped[str] = mapped_column(String(30))
    Review: Mapped[str] = mapped_column(String(30))
    RUserID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0))
    UserID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0))
    OrderID: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(20, 0), nullable=True)
    ReviewTime: Mapped[str] = mapped_column(String(30), default="")

    __table_args__ = (
        UniqueConstraint('RUserID', 'OrderID', name='idx_user_order'),
    )


class Staff(Base):
    __tablename__ = "Staff"

    UserID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0), primary_key=True)
    Username: Mapped[str] = mapped_column(String(32))
    Password: Mapped[str] = mapped_column(String(128))
    Email: Mapped[str] = mapped_column(String(64))
    Phone: Mapped[str] = mapped_column(String(30))
    Address: Mapped[str] = mapped_column(String(255))
    Role: Mapped[str] = mapped_column(String(30))
    StaffID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0))
    Salary: Mapped[str] = mapped_column(String(30))


class TaskParticipant(Base):
    __tablename__ = "TaskParticipant"

    UserID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0), primary_key=True)
    TaskID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0), primary_key=True)
    JoinTime: Mapped[str] = mapped_column(String(30))
    Status: Mapped[str] = mapped_column(
        String(30), default="active"
    )  # active, completed, left


class Task(Base):
    __tablename__ = "Task"

    TaskID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0), primary_key=True)
    TaskType: Mapped[str] = mapped_column(String(30))
    Description: Mapped[str] = mapped_column(String(255))
    EstimatedTime: Mapped[str] = mapped_column(String(30))
    ActualTime: Mapped[str] = mapped_column(String(30))
    CurrentBidder: Mapped[str] = mapped_column(String(30))
    BidDeadline: Mapped[str] = mapped_column(String(30))
    GroupTaskID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0))
    TaskLocation: Mapped[str] = mapped_column(String(255))
    MaxParticipants: Mapped[int] = mapped_column(
        DECIMAL(2, 0), default=5
    )  # 最大参与人数
    Status: Mapped[str] = mapped_column(
        String(30), default="recruiting"
    )  # recruiting, full, assigned, completed


class User(Base):
    __tablename__ = "User"

    UserID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0), primary_key=True)
    Username: Mapped[str] = mapped_column(String(32))
    Password: Mapped[str] = mapped_column(String(128))
    Email: Mapped[str] = mapped_column(String(64))
    Phone: Mapped[str] = mapped_column(String(30))
    Address: Mapped[str] = mapped_column(String(255))
    Role: Mapped[str] = mapped_column(String(30))
