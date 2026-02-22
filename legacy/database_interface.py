from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Callable

class DatabaseInterface(ABC):
    """Абстрактный интерфейс для базы данных игры"""
    
    @abstractmethod
    def register_player(self, username: str, password: str) -> bool:
        """Регистрация нового игрока"""
        pass
    
    @abstractmethod
    def login_player(self, username: str, password: str) -> Optional[str]:
        """Авторизация игрока, возвращает player_id"""
        pass
    
    @abstractmethod
    def logout_player(self, player_id: str):
        """Выход игрока"""
        pass
    
    @abstractmethod
    def get_online_players(self, exclude_player_id: str = None) -> List[Dict]:
        """Получение списка онлайн игроков"""
        pass
    
    @abstractmethod
    def create_game(self, player1_id: str, player2_id: str) -> str:
        """Создание новой игры"""
        pass
    
    @abstractmethod
    def create_round(self, game_id: str, round_number: int) -> str:
        """Создание нового раунда"""
        pass
    
    @abstractmethod
    def save_question_choice(self, round_id: str, question_number: int, player_id: str, choice: str):
        """Сохранение выбора игрока в вопросе"""
        pass
    
    @abstractmethod
    def get_player_stats(self, player_id: str) -> Dict:
        """Получение статистики игрока"""
        pass
    
    @abstractmethod
    def ping_player(self, player_id: str):
        """Обновление ping для поддержания онлайн статуса"""
        pass
    
    @abstractmethod
    def listen_to_game(self, game_id: str, callback: Callable):
        """Слушать изменения в игре"""
        pass
    
    @abstractmethod
    def listen_to_round(self, round_id: str, callback: Callable):
        """Слушать изменения в раунде"""
        pass
    
    @abstractmethod
    def listen_to_questions(self, round_id: str, callback: Callable):
        """Слушать изменения в вопросах раунда"""
        pass
    
    @abstractmethod
    def update_game_status(self, game_id: str, player_id: str, ready: bool):
        """Обновить статус готовности игрока"""
        pass
    
    @abstractmethod
    def get_question_choices(self, round_id: str, question_number: int) -> Dict:
        """Получить выборы обоих игроков для вопроса"""
        pass
