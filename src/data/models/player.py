"""
Модель игрока
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Player:
    """Модель данных игрока"""
    id: str
    username: str
    total_score: int = 0
    games_played: int = 0
    is_online: bool = False
    created_at: Optional[datetime] = None
    last_online: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_online is None:
            self.last_online = datetime.now()
    
    @property
    def average_score(self) -> float:
        """Средний счет за игру"""
        if self.games_played == 0:
            return 0.0
        return self.total_score / self.games_played
    
    def to_dict(self) -> dict:
        """Преобразование в словарь для сохранения в БД"""
        return {
            'id': self.id,
            'username': self.username,
            'total_score': self.total_score,
            'games_played': self.games_played,
            'is_online': self.is_online,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_online': self.last_online.isoformat() if self.last_online else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Player':
        """Создание из словаря из БД"""
        created_at = None
        if data.get('created_at'):
            created_at = datetime.fromisoformat(data['created_at'])
        
        last_online = None
        if data.get('last_online'):
            last_online = datetime.fromisoformat(data['last_online'])
        
        return cls(
            id=data['id'],
            username=data['username'],
            total_score=data.get('total_score', 0),
            games_played=data.get('games_played', 0),
            is_online=data.get('is_online', False),
            created_at=created_at,
            last_online=last_online
        )
