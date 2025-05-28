from typing import Optional

from sqlalchemy import DECIMAL, String, Float
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
    Address: Mapped[str] = mapped_column(String(256))
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


class Client(Base):
    __tablename__ = "Client"

    UserID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0), primary_key=True)
    Username: Mapped[str] = mapped_column(String(32))
    Password: Mapped[str] = mapped_column(String(128))
    Email: Mapped[str] = mapped_column(String(64))
    Phone: Mapped[str] = mapped_column(String(30))
    Address: Mapped[str] = mapped_column(String(256))
    Role: Mapped[str] = mapped_column(String(30))
    ClientID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0))


class GroupTask(Base):
    __tablename__ = "GroupTask"

    GroupTaskID: Mapped[decimal.Decimal] = mapped_column(
        DECIMAL(20, 0), primary_key=True
    )
    TaskID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0))
    ParticipatingUserID: Mapped[str] = mapped_column(String(30))
    JoinTime: Mapped[str] = mapped_column(String(30))
    endTime: Mapped[Optional[str]] = mapped_column(String(30))


class GroupTaskUser(Base):
    __tablename__ = "GroupTaskUser"
    __table_args__ = {"comment": "һ   Ű    ˿    ɶ   û     \r\nһ   û    Բ      Ű     "}

    UserID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0), primary_key=True)
    GroupTaskID: Mapped[decimal.Decimal] = mapped_column(
        DECIMAL(20, 0), primary_key=True
    )


class Orders(Base):
    __tablename__ = "Orders"

    OrderType: Mapped[str] = mapped_column(String(30))
    OrderStatus: Mapped[str] = mapped_column(String(30))
    CreationTime: Mapped[str] = mapped_column(String(30))
    CompletionTime: Mapped[str] = mapped_column(String(30))
    AssignmentType: Mapped[str] = mapped_column(String(30))
    AssignmentStatus: Mapped[str] = mapped_column(String(30))
    OUserID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0), primary_key=True)
    UserID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0))


class Points(Base):
    __tablename__ = "Points"

    UserID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0), primary_key=True)
    Points: Mapped[str] = mapped_column(String(30))


class Reputation(Base):
    __tablename__ = "Reputation"

    Score: Mapped[str] = mapped_column(String(30))
    Review: Mapped[str] = mapped_column(String(30))
    RUserID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0), primary_key=True)
    UserID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0))


class Staff(Base):
    __tablename__ = "Staff"

    UserID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0), primary_key=True)
    Username: Mapped[str] = mapped_column(String(32))
    Password: Mapped[str] = mapped_column(String(128))
    Email: Mapped[str] = mapped_column(String(64))
    Phone: Mapped[str] = mapped_column(String(30))
    Address: Mapped[str] = mapped_column(String(256))
    Role: Mapped[str] = mapped_column(String(30))
    StaffID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0))
    Salary: Mapped[str] = mapped_column(String(30))


class Task(Base):
    __tablename__ = "Task"

    TaskID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0), primary_key=True)
    TaskType: Mapped[str] = mapped_column(String(30))
    Description: Mapped[str] = mapped_column(String(256))
    EstimatedTime: Mapped[str] = mapped_column(String(30))
    ActualTime: Mapped[str] = mapped_column(String(30))
    CurrentBidder: Mapped[str] = mapped_column(String(30))
    BidDeadline: Mapped[str] = mapped_column(String(30))


class User(Base):
    __tablename__ = "User"

    UserID: Mapped[decimal.Decimal] = mapped_column(DECIMAL(20, 0), primary_key=True)
    Username: Mapped[str] = mapped_column(String(32))
    Password: Mapped[str] = mapped_column(String(128))
    Email: Mapped[str] = mapped_column(String(64))
    Phone: Mapped[str] = mapped_column(String(30))
    Address: Mapped[str] = mapped_column(String(256))
    Role: Mapped[str] = mapped_column(String(30))
