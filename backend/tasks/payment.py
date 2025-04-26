# backend/tasks/payment.py
from ..core.celery_app import celery_app
from ..payment_gateway.service import PaymentService
from ..core.database import SessionLocal
from ..core import models, schemas
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="process_payment_verification")
def process_payment_verification(self, transaction_id: str, authority: str):
    """وظیفه تایید پرداخت"""
    db = SessionLocal()
    try:
        payment_service = PaymentService(db)
        result = payment_service.verify_deposit(transaction_id, authority)
        
        if not result.get("success"):
            raise Exception(result.get("message", "Payment verification failed"))
        
        return {"status": "success", "transaction_id": transaction_id}
    except Exception as e:
        logger.error(f"Payment verification failed: {str(e)}")
        raise self.retry(exc=e, countdown=60)
    finally:
        db.close()

@celery_app.task(name="check_pending_payments")
def check_pending_payments():
    """وظیفه بررسی پرداخت‌های معلق"""
    db = SessionLocal()
    try:
        from ..payment_gateway.providers import get_payment_provider
        payment_service = PaymentService(db)
        provider = get_payment_provider()
        
        # یافتن تراکنش‌های pending قدیمی
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        pending_transactions = db.query(models.Transaction).filter(
            models.Transaction.type == schemas.TransactionType.DEPOSIT.value,
            models.Transaction.created_at < cutoff_time,
            models.Transaction.description.like("%pending%")
        ).all()
        
        results = []
        for transaction in pending_transactions:
            try:
                # تلاش برای تایید پرداخت
                # (در اینجا باید authority از description استخراج شود)
                authority = extract_authority_from_description(transaction.description)
                if authority:
                    result = provider.verify_payment(authority, transaction.amount)
                    if result.get("status") == "success":
                        payment_service.verify_deposit(
                            transaction.id,
                            authority,
                            "success"
                        )
                        results.append({
                            "transaction_id": str(transaction.id),
                            "status": "verified"
                        })
                    else:
                        results.append({
                            "transaction_id": str(transaction.id),
                            "status": "still_pending"
                        })
            except Exception as e:
                logger.error(f"Error checking transaction {transaction.id}: {str(e)}")
                results.append({
                    "transaction_id": str(transaction.id),
                    "status": "error",
                    "error": str(e)
                })
        
        return results
    finally:
        db.close()

def extract_authority_from_description(description: str) -> Optional[str]:
    """استخراج authority از description تراکنش"""
    # این تابع بسته به درگاه پرداخت می‌تواند متفاوت باشد
    if "authority:" in description:
        return description.split("authority:")[1].strip()
    return None

@celery_app.task(name="process_withdrawal")
def process_withdrawal(transaction_id: str):
    """وظیفه پردازش برداشت"""
    db = SessionLocal()
    try:
        transaction = db.query(models.Transaction).filter(
            models.Transaction.id == transaction_id,
            models.Transaction.type == schemas.TransactionType.WITHDRAWAL.value
        ).first()
        
        if not transaction:
            raise ValueError("Transaction not found")
        
        # TODO: پیاده‌سازی منطق واقعی پردازش برداشت
        # اینجا می‌توانید به API بانک یا سرویس پرداخت متصل شوید
        
        # پس از پردازش موفق:
        transaction.description = "Withdrawal processed successfully"
        db.commit()
        
        return {"status": "success", "transaction_id": transaction_id}
    except Exception as e:
        logger.error(f"Withdrawal processing failed: {str(e)}")
        raise
    finally:
        db.close()
