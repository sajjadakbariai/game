# backend/admin/dashboard.py
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy import func, and_
from ..core.database import Session
from ..core import models

class AdminDashboard:
    """کلاس برای مدیریت داده‌های داشبورد ادمین"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_system_stats(self) -> Dict[str, Any]:
        """دریافت آمار کلی سیستم"""
        stats = {}
        
        # تعداد کاربران
        stats["total_users"] = self.db.query(func.count(models.User.id)).scalar()
        stats["active_users"] = self.db.query(func.count(models.User.id))\
            .filter(models.User.is_active == True)\
            .scalar()
        
        # تعداد تراکنش‌ها
        stats["total_transactions"] = self.db.query(func.count(models.Transaction.id)).scalar()
        stats["deposit_amount"] = self.db.query(func.coalesce(func.sum(models.Transaction.amount), 0))\
            .filter(models.Transaction.type == models.TransactionType.DEPOSIT.value)\
            .scalar()
        stats["withdrawal_amount"] = self.db.query(func.coalesce(func.sum(models.Transaction.amount), 0))\
            .filter(models.Transaction.type == models.TransactionType.WITHDRAWAL.value)\
            .scalar()
        
        # تعداد بازی‌ها
        stats["total_games"] = self.db.query(func.count(models.Game.id)).scalar()
        stats["active_games"] = self.db.query(func.count(models.Game.id))\
            .filter(models.Game.status == models.GameStatus.ACTIVE.value)\
            .scalar()
        
        return stats
    
    def get_recent_activity(self, days: int = 7) -> Dict[str, Any]:
        """دریافت فعالیت‌های اخیر"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        activity = {}
        
        # کاربران جدید
        activity["new_users"] = self.db.query(models.User)\
            .filter(and_(
                models.User.created_at >= start_date,
                models.User.created_at <= end_date
            ))\
            .count()
        
        # تراکنش‌های اخیر
        activity["recent_transactions"] = self.db.query(models.Transaction)\
            .filter(and_(
                models.Transaction.created_at >= start_date,
                models.Transaction.created_at <= end_date
            ))\
            .order_by(models.Transaction.created_at.desc())\
            .limit(10)\
            .all()
        
        # بازی‌های اخیر
        activity["recent_games"] = self.db.query(models.Game)\
            .filter(and_(
                models.Game.created_at >= start_date,
                models.Game.created_at <= end_date
            ))\
            .order_by(models.Game.created_at.desc())\
            .limit(10)\
            .all()
        
        return activity
    
    def get_user_activity_report(self, user_id: str) -> Dict[str, Any]:
        """گزارش فعالیت کاربر"""
        report = {}
        
        # اطلاعات پایه کاربر
        user = self.db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        report["user_info"] = {
            "username": user.username,
            "email": user.email,
            "join_date": user.created_at,
            "last_login": user.last_login,
            "is_active": user.is_active
        }
        
        # اطلاعات کیف پول
        wallet = self.db.query(models.Wallet).filter(models.Wallet.user_id == user_id).first()
        report["wallet_info"] = {
            "credit": wallet.credit if wallet else 0,
            "real_balance": wallet.real_balance if wallet else 0,
            "locked_credit": wallet.locked_credit if wallet else 0
        }
        
        # آخرین تراکنش‌ها
        report["recent_transactions"] = self.db.query(models.Transaction)\
            .filter(models.Transaction.user_id == user_id)\
            .order_by(models.Transaction.created_at.desc())\
            .limit(5)\
            .all()
        
        # آخرین بازی‌ها
        report["recent_games"] = self.db.query(models.Game)\
            .join(models.GamePlayer)\
            .filter(models.GamePlayer.user_id == user_id)\
            .order_by(models.Game.created_at.desc())\
            .limit(5)\
            .all()
        
        return report
