# backend/payment_gateway/service.py
from typing import Optional, Dict
import uuid
from decimal import Decimal
import requests
from fastapi import HTTPException
from ..core.config import settings
from ..core import models, schemas, crud
from ..core.database import Session

class PaymentService:
    """سرویس مدیریت پرداخت‌ها"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_deposit_request(
        self,
        user_id: uuid.UUID,
        amount: Decimal,
        payment_method: str
    ) -> Dict:
        """ایجاد درخواست واریز"""
        # اعتبارسنجی مقدار
        if amount < Decimal(settings.MIN_DEPOSIT):
            raise HTTPException(
                status_code=400,
                detail=f"Minimum deposit is {settings.MIN_DEPOSIT}"
            )
        
        # ایجاد تراکنش در حالت pending
        transaction = crud.create_transaction(
            self.db,
            user_id,
            amount,
            schemas.TransactionType.DEPOSIT,
            f"Deposit request via {payment_method}"
        )
        
        # اتصال به درگاه پرداخت
        payment_url = await self._connect_to_gateway(
            amount,
            transaction.id,
            payment_method
        )
        
        return {
            "payment_url": payment_url,
            "transaction_id": transaction.id
        }
    
    async def verify_deposit(
        self,
        transaction_id: uuid.UUID,
        authority: str,
        status: str
    ) -> Dict:
        """تایید پرداخت و افزایش موجودی"""
        transaction = self.db.query(models.Transaction).filter(
            models.Transaction.id == transaction_id
        ).first()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        if transaction.type != schemas.TransactionType.DEPOSIT.value:
            raise HTTPException(status_code=400, detail="Invalid transaction type")
        
        # تایید پرداخت با درگاه
        is_verified = await self._verify_payment(
            transaction.amount,
            authority,
            status
        )
        
        if not is_verified:
            raise HTTPException(status_code=400, detail="Payment verification failed")
        
        # افزایش موجودی کیف پول
        wallet = crud.get_wallet(self.db, transaction.user_id)
        wallet.real_balance += transaction.amount
        self.db.commit()
        
        # به‌روزرسانی وضعیت تراکنش
        transaction.description = "Deposit completed successfully"
        self.db.commit()
        
        return {
            "status": "success",
            "new_balance": wallet.real_balance
        }
    
    async def create_withdrawal_request(
        self,
        user_id: uuid.UUID,
        amount: Decimal,
        bank_account_id: uuid.UUID
    ) -> Dict:
        """ایجاد درخواست برداشت"""
        # اعتبارسنجی مقدار
        if amount < Decimal(settings.MIN_WITHDRAWAL):
            raise HTTPException(
                status_code=400,
                detail=f"Minimum withdrawal is {settings.MIN_WITHDRAWAL}"
            )
        
        # بررسی موجودی کافی
        wallet = crud.get_wallet(self.db, user_id)
        if wallet.real_balance < amount:
            raise HTTPException(
                status_code=400,
                detail="Insufficient balance"
            )
        
        # کسر موقت موجودی
        wallet.real_balance -= amount
        self.db.commit()
        
        # ایجاد تراکنش
        transaction = crud.create_transaction(
            self.db,
            user_id,
            amount,
            schemas.TransactionType.WITHDRAWAL,
            f"Withdrawal request to bank account {bank_account_id}"
        )
        
        return {
            "status": "pending",
            "transaction_id": transaction.id
        }
    
    async def _connect_to_gateway(
        self,
        amount: Decimal,
        transaction_id: uuid.UUID,
        payment_method: str
    ) -> str:
        """اتصال به درگاه پرداخت خارجی"""
        # این بخش بسته به درگاه پرداخت می‌تواند متفاوت باشد
        # نمونه کد برای درگاه زرین‌پال:
        
        if settings.PAYMENT_PROVIDER == "zarinpal":
            amount_in_rials = int(amount * 10)  # تبدیل به ریال
            
            data = {
                "merchant_id": settings.ZARINPAL_MERCHANT_ID,
                "amount": amount_in_rials,
                "callback_url": settings.PAYMENT_CALLBACK_URL,
                "description": f"Deposit for transaction {transaction_id}",
                "metadata": {
                    "transaction_id": str(transaction_id),
                    "payment_method": payment_method
                }
            }
            
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            try:
                response = requests.post(
                    "https://api.zarinpal.com/pg/v4/payment/request.json",
                    json=data,
                    headers=headers,
                    timeout=10
                )
                response.raise_for_status()
                result = response.json()
                
                if result['data']['code'] == 100:
                    return f"https://www.zarinpal.com/pg/StartPay/{result['data']['authority']}"
                else:
                    raise HTTPException(
                        status_code=400,
                        detail="Payment gateway error"
                    )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Payment gateway connection failed: {str(e)}"
                )
        
        raise HTTPException(
            status_code=501,
            detail="Payment provider not implemented"
        )
    
    async def _verify_payment(
        self,
        amount: Decimal,
        authority: str,
        status: str
    ) -> bool:
        """تایید پرداخت با درگاه خارجی"""
        if status != "OK":
            return False
        
        if settings.PAYMENT_PROVIDER == "zarinpal":
            amount_in_rials = int(amount * 10)  # تبدیل به ریال
            
            data = {
                "merchant_id": settings.ZARINPAL_MERCHANT_ID,
                "amount": amount_in_rials,
                "authority": authority
            }
            
            try:
                response = requests.post(
                    "https://api.zarinpal.com/pg/v4/payment/verify.json",
                    json=data,
                    timeout=10
                )
                response.raise_for_status()
                result = response.json()
                
                return result['data']['code'] == 100
            except Exception:
                return False
        
        return False
