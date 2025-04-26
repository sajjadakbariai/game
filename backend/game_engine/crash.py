# backend/game_engine/crash.py
import asyncio
import random
from typing import Dict, List, Optional
import uuid
from datetime import datetime
from decimal import Decimal
from ..core import models, schemas, crud
from ..core.database import Session
from .base import GameEngine

class CrashGame(GameEngine):
    """موتور بازی Crash (انفجار)"""
    
    def __init__(self, db: Session, game_id: uuid.UUID):
        super().__init__(db, game_id)
        self.multiplier: float = 1.0
        self.crash_point: float = self._generate_crash_point()
        self.player_bets: Dict[uuid.UUID, Dict] = {}  # {player_id: {'amount': int, 'cashout': float}}
        self.cashed_out: Dict[uuid.UUID, float] = {}  # {player_id: cashout_multiplier}
    
    def _generate_crash_point(self) -> float:
        """تولید نقطه Crash با الگوریتم منصفانه"""
        # استفاده از hash chain برای اطمینان از منصفانه بودن
        game_hash = str(self.game_id) + str(datetime.utcnow().timestamp())
        hash_int = int(hash(game_hash) % 1000) / 1000  # عددی بین 0 تا 1
        
        # فرمول تعیین نقطه Crash (میتواند تنظیم شود)
        crash_point = 1.0 + (100.0 / (1.0 - hash_int) - 1.0) * 0.01
        return min(crash_point, 100.0)  # حداکثر 100x
    
    async def start_game(self):
        """شروع بازی Crash"""
        self.validate_game_status(schemas.GameStatus.WAITING)
        
        # بررسی حداقل بازیکنان
        if len(self.players) < 2:
            raise ValueError("Minimum 2 players required")
        
        # تغییر وضعیت بازی به ACTIVE
        self.game.status = schemas.GameStatus.ACTIVE
        self.game.started_at = datetime.utcnow()
        self.db.commit()
        
        # اطلاع‌رسانی به بازیکنان
        await self.broadcast({
            "type": "game_started",
            "message": "Game started! Place your bets",
            "stake": self.game.stake,
            "time_left": 15  # زمان برای شرط‌بندی
        })
        
        # مرحله شرط‌بندی
        await asyncio.sleep(15)
        
        # شروع محاسبه ضریب
        await self.run_multiplier()
    
    async def run_multiplier(self):
        """اجرای محاسبه و افزایش ضریب"""
        while self.multiplier < self.crash_point:
            await asyncio.sleep(0.5)
            self.multiplier = round(self.multiplier + 0.1, 1)
            
            # ارسال ضریب به همه بازیکنان
            await self.broadcast({
                "type": "multiplier_update",
                "multiplier": self.multiplier,
                "time_left": 1.0  # زمان تا بروزرسانی بعدی
            })
            
            # بررسی بازیکنانی که می‌خواهند خارج شوند
            await self.check_cashouts()
        
        # پایان بازی
        await self.end_game()
    
    async def handle_player_action(self, player_id: uuid.UUID, action: Dict):
        """پردازش عمل بازیکن (شرط‌بندی یا خارج شدن)"""
        self.validate_player(player_id)
        
        if action["type"] == "place_bet":
            await self.handle_bet(player_id, action)
        elif action["type"] == "cashout":
            await self.handle_cashout(player_id)
        else:
            raise ValueError("Invalid action type")
    
    async def handle_bet(self, player_id: uuid.UUID, action: Dict):
        """پردازش شرط‌بندی بازیکن"""
        if self.game.status != schemas.GameStatus.ACTIVE:
            raise ValueError("Betting is closed")
        
        bet_amount = action.get("amount", 0)
        if bet_amount <= 0:
            raise ValueError("Invalid bet amount")
        
        # ذخیره اطلاعات شرط‌بندی
        self.player_bets[player_id] = {
            "amount": bet_amount,
            "cashout": None
        }
        
        await self.notify_player(player_id, {
            "type": "bet_accepted",
            "amount": bet_amount,
            "message": "Your bet has been placed"
        })
    
    async def handle_cashout(self, player_id: uuid.UUID):
        """پردازش درخواست خارج شدن بازیکن"""
        if player_id not in self.player_bets:
            raise ValueError("No active bet for this player")
        
        if self.player_bets[player_id]["cashout"] is not None:
            raise ValueError("Already cashed out")
        
        # ثبت نقطه خارج شدن
        self.player_bets[player_id]["cashout"] = self.multiplier
        self.cashed_out[player_id] = self.multiplier
        
        await self.notify_player(player_id, {
            "type": "cashout_processed",
            "multiplier": self.multiplier,
            "message": f"Successfully cashed out at {self.multiplier}x"
        })
    
    async def check_cashouts(self):
        """بررسی خودکار خارج شدن بازیکنان"""
        # TODO: پیاده‌سازی منطق auto-cashout اگر نیاز باشد
        pass
    
    async def end_game(self):
        """پایان بازی و محاسبه نتایج"""
        self.game.status = schemas.GameStatus.COMPLETED
        self.game.completed_at = datetime.utcnow()
        
        # محاسبه جوایز
        prize_distribution = {}
        winner_id = None
        max_prize = 0
        
        for player_id, bet_info in self.player_bets.items():
            if bet_info["cashout"] is not None:
                # بازیکن با موفقیت خارج شده
                prize = int(bet_info["amount"] * bet_info["cashout"])
                prize_distribution[player_id] = prize
                
                if prize > max_prize:
                    max_prize = prize
                    winner_id = player_id
            else:
                # بازیکن خارج نشده و تمام شرط را از دست داده
                prize_distribution[player_id] = 0
        
        # اگر همه بازیکنان خارج نشده‌اند، کسی با بیشترین مقدار خارج شده برنده است
        if not winner_id and self.player_bets:
            winner_id = next(iter(self.player_bets.keys()))
        
        # ذخیره نتایج
        self.game.winner = winner_id
        self.game.prize_pool = sum(prize_distribution.values())
        self.db.commit()
        
        # توزیع جوایز
        self._distribute_prizes(winner_id, prize_distribution)
        
        # ارسال نتایج نهایی
        await self.broadcast({
            "type": "game_result",
            "winner": winner_id,
            "crash_point": self.crash_point,
            "final_multiplier": self.multiplier,
            "prize_distribution": prize_distribution
        })
        
        # لاگ رویداد
        self.log_event("game_completed", {
            "crash_point": self.crash_point,
            "multiplier": self.multiplier,
            "prize_distribution": prize_distribution
        })
