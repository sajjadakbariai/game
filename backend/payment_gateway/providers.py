# backend/payment_gateway/providers.py
import requests
from typing import Optional, Dict
from decimal import Decimal
from ..core.config import settings
from ..core import schemas

class PaymentProvider:
    """کلاس پایه برای ارائه‌دهندگان پرداخت"""
    
    def __init__(self):
        self.name = "base"
    
    async def initiate_payment(self, amount: Decimal, callback_url: str, description: str) -> Dict:
        """آغاز فرآیند پرداخت"""
        raise NotImplementedError
    
    async def verify_payment(self, authority: str, amount: Decimal) -> bool:
        """تایید پرداخت"""
        raise NotImplementedError


class ZarinpalProvider(PaymentProvider):
    """ارائه‌دهنده زرین‌پال"""
    
    def __init__(self):
        super().__init__()
        self.name = "zarinpal"
        self.base_url = "https://api.zarinpal.com/pg/v4"
        self.merchant_id = settings.ZARINPAL_MERCHANT_ID
    
    async def initiate_payment(self, amount: Decimal, callback_url: str, description: str) -> Dict:
        amount_in_rials = int(amount * 10)  # تبدیل به ریال
        
        data = {
            "merchant_id": self.merchant_id,
            "amount": amount_in_rials,
            "callback_url": callback_url,
            "description": description,
            "metadata": {
                "mobile": None,
                "email": None
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/payment/request.json",
                json=data,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            
            if result['data']['code'] == 100:
                return {
                    "status": "success",
                    "payment_url": f"https://www.zarinpal.com/pg/StartPay/{result['data']['authority']}",
                    "authority": result['data']['authority']
                }
            else:
                return {
                    "status": "failed",
                    "message": result['errors']['message']
                }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def verify_payment(self, authority: str, amount: Decimal) -> Dict:
        amount_in_rials = int(amount * 10)  # تبدیل به ریال
        
        data = {
            "merchant_id": self.merchant_id,
            "amount": amount_in_rials,
            "authority": authority
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/payment/verify.json",
                json=data,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            
            if result['data']['code'] == 100:
                return {
                    "status": "success",
                    "ref_id": result['data']['ref_id'],
                    "amount": Decimal(result['data']['amount']) / 10  # تبدیل به تومان
                }
            else:
                return {
                    "status": "failed",
                    "message": result['errors']['message']
                }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }


class IDPayProvider(PaymentProvider):
    """ارائه‌دهنده IDPay"""
    
    def __init__(self):
        super().__init__()
        self.name = "idpay"
        self.base_url = "https://api.idpay.ir/v1.1"
        self.api_key = settings.IDPAY_API_KEY
    
    async def initiate_payment(self, amount: Decimal, callback_url: str, description: str) -> Dict:
        data = {
            "order_id": str(uuid.uuid4()),
            "amount": int(amount),
            "name": None,
            "phone": None,
            "mail": None,
            "desc": description,
            "callback": callback_url
        }
        
        headers = {
            "X-API-KEY": self.api_key,
            "X-SANDBOX": str(settings.DEBUG).lower()
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/payment",
                json=data,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            
            return {
                "status": "success",
                "payment_url": result['link'],
                "id": result['id']
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def verify_payment(self, payment_id: str, amount: Decimal) -> Dict:
        data = {
            "id": payment_id,
            "order_id": str(uuid.uuid4())
        }
        
        headers = {
            "X-API-KEY": self.api_key,
            "X-SANDBOX": str(settings.DEBUG).lower()
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/payment/verify",
                json=data,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            
            if result['status'] in [100, 101]:
                return {
                    "status": "success",
                    "track_id": result['track_id'],
                    "amount": Decimal(result['amount'])
                }
            else:
                return {
                    "status": "failed",
                    "message": result['message']
                }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }


def get_payment_provider(provider_name: str = None) -> PaymentProvider:
    """فکتوری برای ایجاد نمونه ارائه‌دهنده پرداخت"""
    if not provider_name:
        provider_name = settings.PAYMENT_PROVIDER
    
    if provider_name == "zarinpal":
        return ZarinpalProvider()
    elif provider_name == "idpay":
        return IDPayProvider()
    else:
        raise ValueError(f"Unsupported payment provider: {provider_name}")
