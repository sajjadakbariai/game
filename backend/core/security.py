# backend/core/security.py
import re
from typing import Optional
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from ..core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def is_password_strong(password: str) -> bool:
    """بررسی قدرت رمز عبور"""
    if len(password) < 8:
        return False
    
    # بررسی وجود حداقل یک حرف بزرگ
    if not re.search(r"[A-Z]", password):
        return False
    
    # بررسی وجود حداقل یک حرف کوچک
    if not re.search(r"[a-z]", password):
        return False
    
    # بررسی وجود حداقل یک عدد
    if not re.search(r"\d", password):
        return False
    
    # بررسی وجود حداقل یک کاراکتر خاص
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    
    return True

def create_verification_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """ایجاد توکن تایید ایمیل/موبایل"""
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

def verify_verification_token(token: str) -> Optional[dict]:
    """تایید توکن تایید ایمیل/موبایل"""
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.JWTError:
        return None

def generate_password_reset_token(email: str) -> str:
    """ایجاد توکن بازنشانی رمز عبور"""
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {
            "exp": exp,
            "nbf": now,
            "sub": email,
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt

def verify_password_reset_token(token: str) -> Optional[str]:
    """تایید توکن بازنشانی رمز عبور"""
    try:
        decoded_token = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return decoded_token["sub"]
    except jwt.JWTError:
        return None

def get_password_hash(password: str) -> str:
    """تولید هش رمز عبور"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """تایید تطابق رمز عبور با هش"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """ایجاد توکن دسترسی JWT"""
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
