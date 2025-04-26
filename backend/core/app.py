# backend/core/app.py
from fastapi import FastAPI, Depends, HTTPException, status, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
import uuid
from . import models, schemas, crud, auth
from .database import SessionLocal, engine
from .config import settings

# ایجاد جداول دیتابیس (برای محیط توسعه)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Gaming Platform API",
    description="API for online betting game platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# تنظیمات CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----- Authentication Endpoints -----
@app.post("/api/auth/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """ثبت نام کاربر جدید"""
    try:
        db_user = auth.register_new_user(db, user)
        return db_user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/api/auth/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """ورود کاربر و دریافت توکن"""
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # به‌روزرسانی آخرین زمان ورود
    crud.update_user_last_login(db, user.id)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# ----- User Endpoints -----
@app.get("/api/users/me", response_model=schemas.UserResponse)
def read_current_user(
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """دریافت اطلاعات کاربر جاری"""
    return current_user

# ----- Wallet Endpoints -----
@app.get("/api/wallet", response_model=schemas.WalletResponse)
def get_user_wallet(
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """دریافت موجودی کیف پول کاربر"""
    wallet = crud.get_wallet(db, current_user.id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet

@app.post("/api/wallet/deposit")
def deposit_to_wallet(
    deposit_data: schemas.DepositRequest,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """واریز به کیف پول"""
    try:
        # در اینجا باید منطق اتصال به درگاه پرداخت پیاده‌سازی شود
        # برای نمونه، مستقیماً موجودی را افزایش می‌دهیم
        
        # افزایش موجودی ریالی
        wallet = crud.get_wallet(db, current_user.id)
        wallet.real_balance += deposit_data.amount
        db.commit()
        
        # ثبت تراکنش
        crud.create_transaction(
            db,
            current_user.id,
            deposit_data.amount,
            schemas.TransactionType.DEPOSIT,
            f"Deposit via {deposit_data.payment_method}"
        )
        
        return {"status": "success", "new_balance": wallet.real_balance}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ----- Game Endpoints -----
@app.post("/api/games", response_model=schemas.GameResponse)
def create_new_game(
    game_data: schemas.GameBase,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """ایجاد بازی جدید"""
    try:
        game = crud.create_game(db, game_data, current_user.id)
        return game
    except crud.CRUDException as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/games/{game_id}/join")
def join_game(
    game_id: uuid.UUID,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """پیوستن به بازی موجود"""
    try:
        player = crud.add_player_to_game(db, game_id, current_user.id)
        return {"status": "success", "game_id": game_id}
    except crud.CRUDException as e:
        raise HTTPException(status_code=400, detail=str(e))

# ----- WebSocket Endpoints -----
@app.websocket("/api/games/{game_id}/ws")
async def game_websocket(
    websocket: WebSocket,
    game_id: uuid.UUID,
    token: str,
    db: Session = Depends(get_db)
):
    """اتصال WebSocket برای بازی‌های زنده"""
    try:
        # احراز هویت کاربر
        user = await auth.get_current_user_from_token(token, db)
        
        await websocket.accept()
        
        # TODO: پیاده‌سازی منطق بازی
        
        while True:
            data = await websocket.receive_json()
            # پردازش رویدادهای بازی
            
    except HTTPException as e:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    except Exception as e:
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
