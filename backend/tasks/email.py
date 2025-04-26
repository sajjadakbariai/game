# backend/tasks/email.py
from ..core.celery_app import celery_app
from ..notification.email import EmailService
from ..core.database import SessionLocal
from ..core import models
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="send_email_task")
def send_email_task(self, email_to: str, subject: str, body: str, is_html: bool = False):
    """وظیفه ارسال ایمیل"""
    try:
        email_service = EmailService()
        success = email_service.send_email(email_to, subject, body, is_html)
        if not success:
            raise Exception("Failed to send email")
        return {"status": "success", "email": email_to}
    except Exception as e:
        logger.error(f"Email task failed: {str(e)}")
        raise self.retry(exc=e, countdown=60)

@celery_app.task(name="send_bulk_emails")
def send_bulk_emails(emails: list, subject: str, body: str, is_html: bool = False):
    """وظیفه ارسال گروهی ایمیل"""
    email_service = EmailService()
    results = []
    for email in emails:
        try:
            success = email_service.send_email(email, subject, body, is_html)
            results.append({"email": email, "status": "success" if success else "failed"})
        except Exception as e:
            logger.error(f"Failed to send email to {email}: {str(e)}")
            results.append({"email": email, "status": "error", "error": str(e)})
    return results

@celery_app.task(name="send_daily_stats_email")
def send_daily_stats_email():
    """وظیفه ارسال آمار روزانه به ادمین"""
    db = SessionLocal()
    try:
        from ..admin.dashboard import AdminDashboard
        dashboard = AdminDashboard(db)
        
        # جمع‌آوری آمار
        stats = dashboard.get_system_stats()
        activity = dashboard.get_recent_activity()
        
        # آماده‌سازی محتوای ایمیل
        subject = "Daily System Stats Report"
        body = f"""
        <html>
            <body>
                <h1>Daily System Stats Report</h1>
                <h2>General Stats</h2>
                <ul>
                    <li>Total Users: {stats['total_users']}</li>
                    <li>Active Users: {stats['active_users']}</li>
                    <li>Total Transactions: {stats['total_transactions']}</li>
                    <li>Total Deposit Amount: {stats['deposit_amount']}</li>
                    <li>Total Withdrawal Amount: {stats['withdrawal_amount']}</li>
                    <li>Total Games: {stats['total_games']}</li>
                    <li>Active Games: {stats['active_games']}</li>
                </ul>
                
                <h2>Recent Activity</h2>
                <p>New Users: {activity['new_users']}</p>
                
                <p>Report generated at: {datetime.utcnow()}</p>
            </body>
        </html>
        """
        
        # ارسال به ادمین‌ها
        admins = db.query(models.User).filter(models.User.is_admin == True).all()
        if admins:
            emails = [admin.email for admin in admins if admin.email]
            return send_bulk_emails(emails, subject, body, is_html=True)
        return {"status": "skipped", "message": "No admin emails found"}
    finally:
        db.close()
