# backend/game_engine/hokm.py
import asyncio
import random
from typing import Dict, List, Optional, Tuple
import uuid
from enum import Enum
from datetime import datetime
from ..core import models, schemas, crud
from ..core.database import Session
from .base import GameEngine

class Suit(Enum):
    HEARTS = "hearts"
    DIAMONDS = "diamonds"
    CLUBS = "clubs"
    SPADES = "spades"

class Rank(Enum):
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"

class Card:
    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank
    
    def __str__(self):
        return f"{self.rank.value}{self.suit.value[0].upper()}"

class HokmGame(GameEngine):
    """موتور بازی حکم (Hokm)"""
    
    def __init__(self, db: Session, game_id: uuid.UUID):
        super().__init__(db, game_id)
        self.deck: List[Card] = []
        self.trump_suit: Optional[Suit] = None
        self.hakem_index: int = 0  # ایندکس بازیکن حکم‌دهنده
        self.current_turn: int = 0
        self.current_round: int = 1
        self.teams: List[Tuple] = [
            (self.players[0].id, self.players[2].id),  # تیم 1
            (self.players[1].id, self.players[3].id)   # تیم 2
        ]
        self.player_hands: Dict[uuid.UUID, List[Card]] = {}
        self.played_cards: List[Dict] = []  # لیست کارت‌های بازی شده در دور جاری
        self.scores: Dict[int, int] = {0: 0, 1: 0}  # امتیازات تیم‌ها
        self.game_rounds: List[Dict] = []  # تاریخچه دورها

    def _initialize_deck(self):
        """آماده‌سازی دسته کارت"""
        self.deck = [
            Card(suit, rank)
            for suit in Suit
            for rank in Rank
        ]
        random.shuffle(self.deck)
    
    def _deal_cards(self):
        """تقسیم کارت‌ها بین بازیکنان"""
        self.player_hands = {player.id: [] for player in self.players}
        
        # تقسیم 5 کارت به هر بازیکن
        for i in range(5):
            for player in self.players:
                self.player_hands[player.id].append(self.deck.pop())
    
    async def start_game(self):
        """شروع بازی حکم"""
        self.validate_game_status(schemas.GameStatus.WAITING)
        
        # بررسی تعداد بازیکنان
        if len(self.players) != 4:
            raise ValueError("Hokm requires exactly 4 players")
        
        # تغییر وضعیت بازی
        self.game.status = schemas.GameStatus.ACTIVE
        self.game.started_at = datetime.utcnow()
        self.db.commit()
        
        # آماده‌سازی بازی
        self._initialize_deck()
        self._deal_cards()
        
        # انتخاب تصادفی حکم‌دهنده اول
        self.hakem_index = random.randint(0, 3)
        hakem = self.players[self.hakem_index]
        
        # اطلاع‌رسانی به بازیکنان
        await self.broadcast({
            "type": "game_started",
            "message": "Game started!",
            "hakem": hakem.id,
            "your_hand": [
                str(card) for card in self.player_hands[hakem.id]
            ] if self.current_user.id == hakem.id else None
        })
        
        # شروع دور اول
        await self.start_round()
    
    async def start_round(self):
        """شروع یک دور جدید"""
        hakem = self.players[self.hakem_index]
        await self.notify_player(hakem.id, {
            "type": "choose_trump",
            "message": "Please choose trump suit",
            "your_hand": [str(card) for card in self.player_hands[hakem.id]],
            "options": [suit.value for suit in Suit]
        })
    
    async def handle_player_action(self, player_id: uuid.UUID, action: Dict):
        """پردازش عمل بازیکن"""
        self.validate_player(player_id)
        
        if action["type"] == "choose_trump":
            await self.handle_trump_selection(player_id, action)
        elif action["type"] == "play_card":
            await self.handle_play_card(player_id, action)
        else:
            raise ValueError("Invalid action type")
    
    async def handle_trump_selection(self, player_id: uuid.UUID, action: Dict):
        """پردازش انتخاب حکم توسط بازیکن"""
        if player_id != self.players[self.hakem_index].id:
            raise ValueError("Only hakem can choose trump")
        
        try:
            self.trump_suit = Suit(action["suit"])
        except ValueError:
            raise ValueError("Invalid suit selected")
        
        # تقسیم بقیه کارت‌ها (حکم‌دهنده 5 کارت اضافه می‌گیرد)
        for _ in range(5):
            self.player_hands[player_id].append(self.deck.pop())
        
        # اطلاع‌رسانی به همه بازیکنان
        await self.broadcast({
            "type": "trump_selected",
            "trump_suit": self.trump_suit.value,
            "hakem": player_id,
            "message": f"Trump suit is {self.trump_suit.value}"
        })
        
        # شروع بازی
        self.current_turn = self.hakem_index
        await self.next_turn()
    
    async def handle_play_card(self, player_id: uuid.UUID, action: Dict):
        """پردازش بازی کردن کارت توسط بازیکن"""
        if self.current_turn != self._get_player_index(player_id):
            raise ValueError("Not your turn")
        
        # یافتن کارت در دست بازیکن
        card_str = action["card"]
        card = self._parse_card(card_str)
        
        if card not in self.player_hands[player_id]:
            raise ValueError("Card not in your hand")
        
        # حذف کارت از دست بازیکن
        self.player_hands[player_id].remove(card)
        
        # ذخیره کارت بازی شده
        self.played_cards.append({
            "player_id": player_id,
            "card": card_str,
            "team": 0 if player_id in self.teams[0] else 1
        })
        
        # اطلاع‌رسانی به همه بازیکنان
        await self.broadcast({
            "type": "card_played",
            "player_id": player_id,
            "card": card_str,
            "remaining_players": 4 - len(self.played_cards)
        })
        
        # اگر دور کامل شده
        if len(self.played_cards) == 4:
            await self.end_round()
        else:
            # نوبت بازیکن بعدی
            self.current_turn = (self.current_turn + 1) % 4
            await self.next_turn()
    
    async def end_round(self):
        """پایان یک دور و محاسبه برنده دور"""
        # تعیین برنده دور
        winning_card, winning_team = self._determine_round_winner()
        
        # افزایش امتیاز تیم برنده
        self.scores[winning_team] += 1
        
        # ذخیره اطلاعات دور
        self.game_rounds.append({
            "round": self.current_round,
            "played_cards": self.played_cards.copy(),
            "winning_team": winning_team,
            "winning_card": winning_card,
            "scores": self.scores.copy()
        })
        
        # پاکسازی کارت‌های بازی شده
        self.played_cards.clear()
        
        # بررسی پایان بازی
        if max(self.scores.values()) >= 7:  # معمولاً بازی تا 7 امتیاز است
            await self.end_game()
        else:
            # شروع دور جدید
            self.current_round += 1
            self.current_turn = winning_team * 2  # اولین بازیکن تیم برنده
            await self.next_turn()
    
    async def end_game(self):
        """پایان بازی و محاسبه نتایج نهایی"""
        self.game.status = schemas.GameStatus.COMPLETED
        self.game.completed_at = datetime.utcnow()
        
        # تعیین تیم برنده
        winning_team = 0 if self.scores[0] > self.scores[1] else 1
        winner_ids = self.teams[winning_team]
        
        # محاسبه جوایز (در بازی شرطی)
        prize_distribution = {}
        for player in self.players:
            prize = self.game.stake * 2 if player.id in winner_ids else 0
            prize_distribution[player.id] = prize
        
        # ذخیره نتایج
        self.game.winner = winner_ids[0]  # اولین بازیکن تیم برنده
        self.game.prize_pool = sum(prize_distribution.values())
        self.db.commit()
        
        # توزیع جوایز
        self._distribute_prizes(self.game.winner, prize_distribution)
        
        # ارسال نتایج نهایی
        await self.broadcast({
            "type": "game_result",
            "winning_team": winning_team,
            "team_members": winner_ids,
            "final_scores": self.scores,
            "prize_distribution": prize_distribution
        })
    
    def _determine_round_winner(self) -> Tuple[str, int]:
        """تعیین برنده دور بر اساس کارت‌های بازی شده"""
        # اولین کارت تعیین کننده رنگ دور است
        first_card = self._parse_card(self.played_cards[0]["card"])
        leading_suit = first_card.suit
        
        # پیدا کردن قوی‌ترین کارت
        winning_card = first_card
        winning_index = 0
        
        for i, played in enumerate(self.played_cards[1:], start=1):
            card = self._parse_card(played["card"])
            
            # کارت حکم همیشه برنده است
            if card.suit == self.trump_suit:
                if winning_card.suit != self.trump_suit or self._compare_ranks(card.rank, winning_card.rank) > 0:
                    winning_card = card
                    winning_index = i
            # کارت با رنگ اصلی دور
            elif card.suit == leading_suit and winning_card.suit != self.trump_suit:
                if self._compare_ranks(card.rank, winning_card.rank) > 0:
                    winning_card = card
                    winning_index = i
        
        winning_team = self.played_cards[winning_index]["team"]
        return str(winning_card), winning_team
    
    async def next_turn(self):
        """آماده‌سازی برای نوبت بعدی"""
        current_player = self.players[self.current_turn]
        
        # ارسال اطلاعات به بازیکن فعلی
        await self.notify_player(current_player.id, {
            "type": "your_turn",
            "message": "It's your turn to play",
            "your_hand": [str(card) for card in self.player_hands[current_player.id]],
            "played_cards": [pc["card"] for pc in self.played_cards],
            "trump_suit": self.trump_suit.value,
            "leading_suit": self.played_cards[0]["card"][-1].lower() if self.played_cards else None
        })
    
    def _get_player_index(self, player_id: uuid.UUID) -> int:
        """دریافت ایندکس بازیکن در لیست بازیکنان"""
        for i, player in enumerate(self.players):
            if player.id == player_id:
                return i
        raise ValueError("Player not found")
    
    def _parse_card(self, card_str: str) -> Card:
        """تبدیل رشته کارت به شی Card"""
        rank_str = card_str[:-1]
        suit_char = card_str[-1].lower()
        
        try:
            rank = Rank(rank_str)
            suit = {
                'h': Suit.HEARTS,
                'd': Suit.DIAMONDS,
                'c': Suit.CLUBS,
                's': Suit.SPADES
            }[suit_char]
            return Card(suit, rank)
        except (KeyError, ValueError):
            raise ValueError("Invalid card format")
    
    def _compare_ranks(self, rank1: Rank, rank2: Rank) -> int:
        """مقایسه ارزش دو کارت"""
        rank_order = [
            Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.SIX,
            Rank.SEVEN, Rank.EIGHT, Rank.NINE, Rank.TEN,
            Rank.JACK, Rank.QUEEN, Rank.KING, Rank.ACE
        ]
        return rank_order.index(rank1) - rank_order.index(rank2)
