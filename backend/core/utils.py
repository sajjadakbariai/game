# backend/core/utils.py
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from decimal import Decimal
import random
import string
import hashlib
from ..core.config import settings

def generate_unique_id() -> str:
    """تولید یک شناسه منحصر به فرد"""
    return str(uuid.uuid4())

def generate_random_string(length: int = 8) -> str:
    """تولید رشته تصادفی"""
    return ''.join(
        random.choices(
            string.ascii_letters + string.digits,
            k=length
        )
    )

def generate_secure_hash(data: str) -> str:
    """تولید هش امن از داده ورودی"""
    salt = settings.SECRET_KEY.encode()
    data_bytes = data.encode()
    return hashlib.sha256(salt + data_bytes).hexdigest()

def validate_hash(data: str, hash_value: str) -> bool:
    """اعتبارسنجی هش داده"""
    return generate_secure_hash(data) == hash_value

def convert_decimal_to_dict(value: Decimal) -> Dict[str, Any]:
    """تبدیل Decimal به dict برای سریالایز کردن"""
    return {
        '__decimal__': True,
        'value': str(value)
    }

def convert_dict_to_decimal(data: Dict[str, Any]) -> Optional[Decimal]:
    """تبدیل dict به Decimal"""
    if '__decimal__' in data:
        return Decimal(data['value'])
    return None

def calculate_fairness_hash(server_seed: str, client_seed: str, nonce: int) -> str:
    """محاسبه هش منصفانه برای بازی‌ها"""
    data = f"{server_seed}:{client_seed}:{nonce}"
    return hashlib.sha256(data.encode()).hexdigest()

def generate_fair_random(server_seed: str, client_seed: str, nonce: int) -> float:
    """تولید عدد تصادفی منصفانه برای بازی‌ها"""
    hash_value = calculate_fairness_hash(server_seed, client_seed, nonce)
    return int(hash_value[:8], 16) / 0xFFFFFFFF

def format_timedelta(delta: timedelta) -> str:
    """فرمت‌دهی timedelta به رشته خوانا"""
    total_seconds = delta.total_seconds()
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

def sanitize_input(input_data: Any) -> Any:
    """پاکسازی ورودی‌های کاربر"""
    if isinstance(input_data, str):
        # حذف تگ‌های HTML و JavaScript
        import re
        input_data = re.sub(r'<[^>]*>', '', input_data)
        input_data = re.sub(r'javascript:', '', input_data, flags=re.IGNORECASE)
    return input_data

def calculate_pagination(page: int, page_size: int) -> tuple:
    """محاسبه محدوده صفحه‌بندی"""
    skip = (page - 1) * page_size
    return skip, page_size

def validate_iranian_national_id(national_id: str) -> bool:
    """اعتبارسنجی کد ملی ایران"""
    if not national_id.isdigit() or len(national_id) != 10:
        return False
    
    check = int(national_id[9])
    s = sum(int(national_id[i]) * (10 - i) for i in range(9)) % 11
    return (s < 2 and check == s) or (s >= 2 and check + s == 11)

def validate_iranian_phone_number(phone: str) -> bool:
    """اعتبارسنجی شماره تلفن ایرانی"""
    import re
    pattern = r'^(\+98|0)?9\d{9}$'
    return re.match(pattern, phone) is not None
