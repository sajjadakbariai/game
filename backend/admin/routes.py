# backend/admin/routes.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
import uuid
from datetime import datetime, timedelta
from ..core import models, schemas, crud, auth
from ..core.database import Session, get_db
from ..core.config import settings

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_current_active_user)]
)

security = HTTPBearer()

async def get_admin_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """احراز هویت کاربر ادمین"""
    user = await auth.get_current_user_from_token(credentials.credentials, db)
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Access forbidden")
    return user

@router.get("/users", response_model=List[schemas.UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(get_admin_user)
):
    """لیست تمام کاربران"""
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=schemas.UserResponse)
async def get_user_details(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(get_admin_user)
):
    """دریافت جزئیات کاربر"""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/users/{user_id}/activate")
async def activate_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(get_admin_user)
):
    """فعالسازی حساب کاربر"""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = True
    db.commit()
    return {"status": "success", "message": "User activated"}

@router.post("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(get_admin_user)
):
    """غیرفعالسازی حساب کاربر"""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = False
    db.commit()
    return {"status": "success", "message": "User deactivated"}

@router.get("/transactions", response_model=List[schemas.TransactionResponse])
async def list_transactions(
    user_id: Optional[uuid.UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(get_admin_user)
):
    """لیست تراکنش‌ها با امکان فیلتر"""
    query = db.query(models.Transaction)
    
    if user_id:
        query = query.filter(models.Transaction.user_id == user_id)
    
    if start_date:
        query = query.filter(models.Transaction.created_at >= start_date)
    
    if end_date:
        query = query.filter(models.Transaction.created_at <= end_date)
    
    transactions = query.order_by(models.Transaction.created_at.desc()).offset(skip).limit(limit).all()
    return transactions

@router.get("/games", response_model=List[schemas.GameResponse])
async def list_games(
    status: Optional[schemas.GameStatus] = None,
    game_type: Optional[schemas.GameType] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(get_admin_user)
):
    """لیست بازی‌ها با امکان فیلتر"""
    query = db.query(models.Game)
    
    if status:
        query = query.filter(models.Game.status == status)
    
    if game_type:
        query = query.filter(models.Game.game_type == game_type)
    
    games = query.order_by(models.Game.created_at.desc()).offset(skip).limit(limit).all()
    return games

@router.post("/system/maintenance")
async def toggle_maintenance_mode(
    enable: bool,
    admin_user: models.User = Depends(get_admin_user)
):
    """تغییر حالت تعمیرات سیستم"""
    # TODO: پیاده‌سازی منطق تغییر حالت تعمیرات
    return {
        "status": "success",
        "message": f"Maintenance mode {'enabled' if enable else 'disabled'}"
    }
