"""
Репозиторий для работы с игроками
"""
import logging
from abc import abstractmethod
from typing import List, Optional
from .base_repository import BaseRepository
from ..models.player import Player

logger = logging.getLogger(__name__)

class PlayerRepository(BaseRepository):
    """Репозиторий для управления игроками"""
    
    @abstractmethod
    def create_player(self, username: str, hashed_password: str) -> Optional[str]:
        """Создать нового игрока, возвращает ID"""
        pass
    
    @abstractmethod
    def get_player_by_username(self, username: str) -> Optional[Player]:
        """Получить игрока по имени пользователя"""
        pass
    
    @abstractmethod
    def get_player_by_id(self, player_id: str) -> Optional[Player]:
        """Получить игрока по ID"""
        pass
    
    @abstractmethod
    def update_player(self, player: Player) -> bool:
        """Обновить данные игрока"""
        pass
    
    @abstractmethod
    def delete_player(self, player_id: str) -> bool:
        """Удалить игрока"""
        pass
    
    @abstractmethod
    def get_online_players(self, exclude_player_id: Optional[str] = None) -> List[Player]:
        """Получить список онлайн игроков"""
        pass
    
    @abstractmethod
    def verify_password(self, username: str, password: str) -> Optional[str]:
        """Проверить пароль и вернуть ID игрока"""
        pass
    
    @abstractmethod
    def update_online_status(self, player_id: str, is_online: bool) -> bool:
        """Обновить онлайн статус игрока"""
        pass
    
    @abstractmethod
    def update_ping(self, player_id: str) -> bool:
        """Обновить ping для поддержания онлайн статуса"""
        pass
