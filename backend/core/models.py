# backend/core/models.py
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, 
    ForeignKey, Numeric, Text, Enum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.core.database import Base

class User(Base):
    """مدل کاربران سیستم"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    phone = Column(String(15), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    wallet = relationship("Wallet", back_populates="user", uselist=False)
    transactions = relationship("Transaction", back_populates="user")


class Wallet(Base):
    """مدل کیف پول کاربران"""
    __tablename__ = "wallets"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    credit = Column(Integer, default=100)  # امتیاز اولیه
    real_balance = Column(Numeric(15, 2), default=0)  # موجودی ریالی
    locked_credit = Column(Integer, default=0)  # امتیاز قفل شده در بازی
    last_transaction = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="wallet")


class TransactionType(str, PyEnum):
    """انواع تراکنش‌ها"""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    GAME_STAKE = "game_stake"
    GAME_WIN = "game_win"
    GAME_LOSS = "game_loss"
    COMMISSION = "commission"


class Transaction(Base):
    """مدل تراکنش‌های مالی"""
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    amount = Column(Numeric(15, 2))
    type = Column(Enum(TransactionType))
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    reference_id = Column(UUID(as_uuid=True), nullable=True)  # برای پیوند به بازی یا پرداخت

    user = relationship("User", back_populates="transactions")


class GameType(str, PyEnum):
    """انواع بازی‌های موجود"""
    CRASH = "crash"
    POKER = "poker"
    HOKM = "hokm"
    RPS = "rock_paper_scissors"


class GameStatus(str, PyEnum):
    """وضعیت‌های مختلف بازی"""
    WAITING = "waiting"
    ACTIVE = "active"
    COMPLETED = "completed"
    ABORTED = "aborted"


class Game(Base):
    """مدل پایه برای بازی‌ها"""
    __tablename__ = "games"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_type = Column(Enum(GameType))
    status = Column(Enum(GameStatus), default=GameStatus.WAITING)
    stake = Column(Integer)  # میزان شرط هر بازیکن
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    winner = Column(UUID(as_uuid=True), nullable=True)
    prize_pool = Column(Integer, nullable=True)

    # رابطه با کاربران از طریق جدول واسط
    players = relationship(
        "User",
        secondary="game_players",
        back_populates="games"
    )


# جدول واسط برای رابطه چندبهچند کاربران و بازی‌ها
class GamePlayer(Base):
    """جدول واسط برای ارتباط کاربران با بازی‌ها"""
    __tablename__ = "game_players"

    game_id = Column(UUID(as_uuid=True), ForeignKey("games.id"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    joined_at = Column(DateTime, default=datetime.utcnow)
    position = Column(Integer)  # موقعیت بازیکن در بازی
    credit_change = Column(Integer, default=0)  # تغییر امتیاز در پایان بازی

# اضافه کردن رابطه به مدل User
User.games = relationship(
    "Game",
    secondary="game_players",
    back_populates="players"
)
