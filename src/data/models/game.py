"""
Модели игры и связанных сущностей
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum

class GameStatus(Enum):
    """Статус игры"""
    WAITING = "waiting"
    ACTIVE = "active"
    COMPLETED = "completed"
    ABORTED = "aborted"

class Choice(Enum):
    """Выбор игрока в дилемме"""
    COOPERATE = "cooperate"
    BETRAY = "betray"

@dataclass
class Game:
    """Модель игры"""
    id: str
    player1_id: str
    player2_id: str
    status: GameStatus = GameStatus.WAITING
    created_at: Optional[datetime] = None
    current_round: int = 1
    current_question: int = 1
    player1_ready: bool = False
    player2_ready: bool = False
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    @property
    def is_ready(self) -> bool:
        """Готова ли игра к началу"""
        return self.player1_ready and self.player2_ready
    
    def to_dict(self) -> dict:
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'player1_id': self.player1_id,
            'player2_id': self.player2_id,
            'status': self.status.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'current_round': self.current_round,
            'current_question': self.current_question,
            'player1_ready': self.player1_ready,
            'player2_ready': self.player2_ready
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Game':
        """Создание из словаря"""
        created_at = None
        if data.get('created_at'):
            created_at = datetime.fromisoformat(data['created_at'])
        
        return cls(
            id=data['id'],
            player1_id=data['player1_id'],
            player2_id=data['player2_id'],
            status=GameStatus(data.get('status', GameStatus.WAITING.value)),
            created_at=created_at,
            current_round=data.get('current_round', 1),
            current_question=data.get('current_question', 1),
            player1_ready=data.get('player1_ready', False),
            player2_ready=data.get('player2_ready', False)
        )

@dataclass
class Round:
    """Модель раунда"""
    id: str
    game_id: str
    round_number: int
    player1_choice: Optional[Choice] = None
    player2_choice: Optional[Choice] = None
    player1_score: int = 0
    player2_score: int = 0
    completed_at: Optional[datetime] = None
    
    @property
    def is_completed(self) -> bool:
        """Завершен ли раунд"""
        return (self.player1_choice is not None and 
                self.player2_choice is not None)
    
    def to_dict(self) -> dict:
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'game_id': self.game_id,
            'round_number': self.round_number,
            'player1_choice': self.player1_choice.value if self.player1_choice else None,
            'player2_choice': self.player2_choice.value if self.player2_choice else None,
            'player1_score': self.player1_score,
            'player2_score': self.player2_score,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Round':
        """Создание из словаря"""
        completed_at = None
        if data.get('completed_at'):
            completed_at = datetime.fromisoformat(data['completed_at'])
        
        player1_choice = None
        if data.get('player1_choice'):
            player1_choice = Choice(data['player1_choice'])
        
        player2_choice = None
        if data.get('player2_choice'):
            player2_choice = Choice(data['player2_choice'])
        
        return cls(
            id=data['id'],
            game_id=data['game_id'],
            round_number=data['round_number'],
            player1_choice=player1_choice,
            player2_choice=player2_choice,
            player1_score=data.get('player1_score', 0),
            player2_score=data.get('player2_score', 0),
            completed_at=completed_at
        )

@dataclass
class Question:
    """Модель вопроса"""
    id: str
    round_id: str
    question_number: int
    player1_choice: Optional[Choice] = None
    player2_choice: Optional[Choice] = None
    
    @property
    def both_answered(self) -> bool:
        """Ответили ли оба игрока"""
        return (self.player1_choice is not None and 
                self.player2_choice is not None)
    
    def to_dict(self) -> dict:
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'round_id': self.round_id,
            'question_number': self.question_number,
            'player1_choice': self.player1_choice.value if self.player1_choice else None,
            'player2_choice': self.player2_choice.value if self.player2_choice else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Question':
        """Создание из словаря"""
        player1_choice = None
        if data.get('player1_choice'):
            player1_choice = Choice(data['player1_choice'])
        
        player2_choice = None
        if data.get('player2_choice'):
            player2_choice = Choice(data['player2_choice'])
        
        return cls(
            id=data['id'],
            round_id=data['round_id'],
            question_number=data['question_number'],
            player1_choice=player1_choice,
            player2_choice=player2_choice
        )
