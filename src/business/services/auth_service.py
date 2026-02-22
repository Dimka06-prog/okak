"""
Сервис аутентификации
"""
import logging
import bcrypt
from typing import Optional
from ..exceptions import AuthenticationError, ValidationError
from ...data.repositories.player_repository import PlayerRepository
from ...data.models.player import Player

logger = logging.getLogger(__name__)

class AuthService:
    """Сервис для аутентификации и регистрации пользователей"""
    
    def __init__(self, player_repository: PlayerRepository):
        self.player_repo = player_repository
    
    def _validate_username(self, username: str) -> bool:
        """Валидация имени пользователя"""
        if not username:
            return False
        if len(username) < 3 or len(username) > 20:
            return False
        # Разрешаем буквы, цифры, _ и -
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
        return all(c in allowed_chars for c in username)
    
    def _validate_password(self, password: str) -> bool:
        """Валидация пароля"""
        if not password or len(password) < 6:
            return False
        return True
    
    def _hash_password(self, password: str) -> str:
        """Хеширование пароля"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def register(self, username: str, password: str) -> Optional[str]:
        """
        Регистрация нового пользователя
        
        Args:
            username: Имя пользователя
            password: Пароль
            
        Returns:
            ID нового пользователя или None в случае ошибки
            
        Raises:
            ValidationError: если данные невалидны
            AuthenticationError: если пользователь уже существует
        """
        # Валидация
        if not self._validate_username(username):
            raise ValidationError("Имя пользователя должно содержать от 3 до 20 символов (буквы, цифры, _, -)")
        
        if not self._validate_password(password):
            raise ValidationError("Пароль должен содержать минимум 6 символов")
        
        # Проверка существования пользователя
        existing_player = self.player_repo.get_player_by_username(username)
        if existing_player:
            raise AuthenticationError("Пользователь с таким именем уже существует")
        
        try:
            # Хеширование пароля
            hashed_password = self._hash_password(password)
            
            # Создание пользователя
            player_id = self.player_repo.create_player(username, hashed_password)
            
            if player_id:
                logger.info(f"Пользователь {username} успешно зарегистрирован")
                return player_id
            else:
                raise AuthenticationError("Не удалось создать пользователя")
                
        except Exception as e:
            logger.error(f"Ошибка при регистрации пользователя {username}: {e}")
            raise AuthenticationError("Ошибка при регистрации. Попробуйте позже.")
    
    def login(self, username: str, password: str) -> Optional[str]:
        """
        Вход пользователя
        
        Args:
            username: Имя пользователя
            password: Пароль
            
        Returns:
            ID пользователя или None в случае ошибки
            
        Raises:
            ValidationError: если данные невалидны
            AuthenticationError: если логин/пароль неверны
        """
        if not username or not password:
            raise ValidationError("Заполните все поля")
        
        if not self._validate_username(username):
            raise ValidationError("Неверный формат имени пользователя")
        
        try:
            player_id = self.player_repo.verify_password(username, password)
            
            if player_id:
                # Обновляем онлайн статус
                self.player_repo.update_online_status(player_id, True)
                self.player_repo.update_ping(player_id)
                logger.info(f"Пользователь {username} успешно вошел")
                return player_id
            else:
                raise AuthenticationError("Неверное имя пользователя или пароль")
                
        except Exception as e:
            logger.error(f"Ошибка при входе пользователя {username}: {e}")
            raise AuthenticationError("Ошибка при входе. Попробуйте позже.")
    
    def logout(self, player_id: str) -> bool:
        """
        Выход пользователя
        
        Args:
            player_id: ID пользователя
            
        Returns:
            True если успешно, иначе False
        """
        try:
            success = self.player_repo.update_online_status(player_id, False)
            if success:
                logger.info(f"Пользователь {player_id} вышел")
            return success
        except Exception as e:
            logger.error(f"Ошибка при выходе пользователя {player_id}: {e}")
            return False
