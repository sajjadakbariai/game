# backend/game_engine/base.py
from abc import ABC, abstractmethod
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from ..core import models, schemas, crud
from ..core.database import Session

class GameEngine(ABC):
    """کلاس پایه برای تمام موتورهای بازی"""
    
    def __init__(self, db: Session, game_id: uuid.UUID):
        self.db = db
        self.game_id = game_id
        self.game = self._load_game()
        self.players = self._load_players()
    
    def _load_game(self) -> models.Game:
        """بارگذاری اطلاعات بازی از دیتابیس"""
        game = self.db.query(models.Game).filter(models.Game.id == self.game_id).first()
        if not game:
            raise ValueError("Game not found")
        return game
    
    def _load_players(self) -> List[models.User]:
        """بارگذاری لیست بازیکنان"""
        return [player.user for player in self.game.players]
    
    @abstractmethod
    async def start_game(self):
        """شروع بازی (پیاده‌سازی در کلاس فرزند)"""
        pass
    
    @abstractmethod
    async def handle_player_action(self, player_id: uuid.UUID, action: Dict):
        """پردازش عمل بازیکن (پیاده‌سازی در کلاس فرزند)"""
        pass
    
    @abstractmethod
    async def end_game(self):
        """پایان دادن به بازی (پیاده‌سازی در کلاس فرزند)"""
        pass
    
    async def broadcast(self, message: Dict):
        """ارسال پیام به تمام بازیکنان"""
        # TODO: پیاده‌سازی سیستم broadcast واقعی
        print(f"Broadcasting to all players: {message}")
    
    async def notify_player(self, player_id: uuid.UUID, message: Dict):
        """ارسال پیام به بازیکن خاص"""
        # TODO: پیاده‌سازی سیستم notify واقعی
        print(f"Notifying player {player_id}: {message}")
    
    def _distribute_prizes(self, winner_id: uuid.UUID, prize_distribution: Dict[uuid.UUID, int]):
        """توزیع جوایز به بازیکنان"""
        try:
            updated_game = crud.complete_game(
                self.db,
                self.game_id,
                winner_id,
                prize_distribution
            )
            self.db.refresh(updated_game)
            return updated_game
        except crud.CRUDException as e:
            raise ValueError(f"Prize distribution failed: {str(e)}")
    
    def validate_player(self, player_id: uuid.UUID):
        """اعتبارسنجی اینکه کاربر در این بازی شرکت دارد"""
        if player_id not in [p.id for p in self.players]:
            raise ValueError("Player is not part of this game")
    
    def validate_game_status(self, expected_status: schemas.GameStatus):
        """اعتبارسنجی وضعیت بازی"""
        if self.game.status != expected_status:
            raise ValueError(f"Game is not in {expected_status} state")
    
    def log_event(self, event_type: str, data: Dict):
        """ثبت رویدادهای بازی برای اهداف تحلیلی"""
        # TODO: پیاده‌سازی سیستم لاگ‌گیری
        print(f"Game Event - {event_type}: {data}")

class GameFactory:
    """فکتوری برای ایجاد نمونه‌های موتور بازی"""
    
    @staticmethod
    def create_game(
        game_type: schemas.GameType,
        db: Session,
        game_id: uuid.UUID
    ) -> GameEngine:
        """ایجاد موتور بازی بر اساس نوع بازی"""
        if game_type == schemas.GameType.CRASH:
            from .crash import CrashGame
            return CrashGame(db, game_id)
        elif game_type == schemas.GameType.HOKM:
            from .hokm import HokmGame
            return HokmGame(db, game_id)
        # سایر بازی‌ها...
        else:
            raise ValueError(f"Unsupported game type: {game_type}")
