# backend/core/auth.py
from datetime import datetime, timedelta
from typing import Optional
import uuid
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import get_db
from .models import User
from .schemas import Token, TokenData, UserCreate
from .config import settings

# تنظیمات امنیتی
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """بررسی تطابق رمز عبور با هش ذخیره شده"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """تولید هش از رمز عبور"""
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """احراز هویت کاربر"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """تولید توکن JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """دریافت کاربر جاری از توکن"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """بررسی فعال بودن کاربر"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def register_new_user(db: Session, user_data: UserCreate) -> User:
    """ثبت نام کاربر جدید"""
    # بررسی تکراری نبودن نام کاربری
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    
    # بررسی تکراری نبودن ایمیل
    if user_data.email and db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # بررسی تکراری نبودن شماره تلفن
    if user_data.phone and db.query(User).filter(User.phone == user_data.phone).first():
        raise HTTPException(
            status_code=400,
            detail="Phone number already registered"
        )
    
    # ایجاد کاربر جدید
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        id=uuid.uuid4(),
        username=user_data.username,
        email=user_data.email,
        phone=user_data.phone,
        password_hash=hashed_password,
        is_active=True,
        is_verified=False,
        created_at=datetime.utcnow()
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # ایجاد کیف پول برای کاربر جدید
    from .crud import create_wallet
    create_wallet(db, user_id=db_user.id)
    
    return db_user
