# backend/core/exception_handlers.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

def setup_exception_handlers(app: FastAPI):
    """تنظیم هندلرهای سفارشی برای خطاها"""
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, 
        exc: RequestValidationError
    ):
        """هندلر خطاهای اعتبارسنجی"""
        logger.warning(f"Validation error: {str(exc)}")
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Validation error",
                "errors": exc.errors()
            },
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, 
        exc: StarletteHTTPException
    ):
        """هندلر خطاهای HTTP"""
        logger.warning(f"HTTP error: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request, 
        exc: Exception
    ):
        """هندلر کلی برای سایر خطاها"""
        logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An unexpected error occurred",
                "error": str(exc)
            },
        )
    
    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(
        request: Request, 
        exc: ValidationError
    ):
        """هندلر خطاهای اعتبارسنجی Pydantic"""
        logger.warning(f"Pydantic validation error: {str(exc)}")
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Data validation error",
                "errors": exc.errors()
            },
        )

class CustomHTTPException(StarletteHTTPException):
    """خطای سفارشی HTTP با قابلیت اضافه کردن داده‌های بیشتر"""
    
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Dict[str, str] = None,
        extra: Dict[str, Any] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.extra = extra or {}
