# backend/notification/email.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import BackgroundTasks
from typing import Optional
from ..core.config import settings
from ..core import schemas
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """سرویس ارسال ایمیل"""
    
    def __init__(self):
        self.smtp_server = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.sender = settings.EMAIL_FROM
    
    async def send_email(self, email_to: str, subject: str, body: str, is_html: bool = False):
        """ارسال ایمیل"""
        if not all([self.smtp_server, self.smtp_port, self.sender]):
            logger.warning("Email settings not configured, skipping send email")
            return False
        
        try:
            message = MIMEMultipart()
            message["From"] = self.sender
            message["To"] = email_to
            message["Subject"] = subject
            
            if is_html:
                message.attach(MIMEText(body, "html"))
            else:
                message.attach(MIMEText(body, "plain"))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(message)
            
            logger.info(f"Email sent to {email_to}")
            return True
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    async def send_verification_email(self, email_to: str, token: str):
        """ارسال ایمیل تایید حساب"""
        subject = "Verify your email"
        verification_url = f"{settings.SERVER_HOST}/verify-email?token={token}"
        body = f"""
        <html>
            <body>
                <p>Please click the link below to verify your email:</p>
                <p><a href="{verification_url}">{verification_url}</a></p>
                <p>If you did not create an account, please ignore this email.</p>
            </body>
        </html>
        """
        return await self.send_email(email_to, subject, body, is_html=True)
    
    async def send_password_reset_email(self, email_to: str, token: str):
        """ارسال ایمیل بازنشانی رمز عبور"""
        subject = "Password reset request"
        reset_url = f"{settings.SERVER_HOST}/reset-password?token={token}"
        body = f"""
        <html>
            <body>
                <p>Please click the link below to reset your password:</p>
                <p><a href="{reset_url}">{reset_url}</a></p>
                <p>If you did not request a password reset, please ignore this email.</p>
            </body>
        </html>
        """
        return await self.send_email(email_to, subject, body, is_html=True)
    
    async def send_welcome_email(self, email_to: str, username: str):
        """ارسال ایمیل خوش‌آمدگویی"""
        subject = "Welcome to our gaming platform"
        body = f"""
        <html>
            <body>
                <p>Hi {username},</p>
                <p>Welcome to our gaming platform! Your account has been successfully created.</p>
                <p>You have received {settings.INITIAL_CREDIT} free credits to start playing.</p>
                <p>Enjoy your games!</p>
            </body>
        </html>
        """
        return await self.send_email(email_to, subject, body, is_html=True)

def send_email_in_background(
    background_tasks: BackgroundTasks,
    email_service: EmailService,
    email_to: str,
    subject: str,
    body: str,
    is_html: bool = False
):
    """ارسال ایمیل در پس‌زمینه"""
    background_tasks.add_task(
        email_service.send_email,
        email_to=email_to,
        subject=subject,
        body=body,
        is_html=is_html
    )
