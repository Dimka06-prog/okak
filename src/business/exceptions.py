"""
Исключения бизнес-логики
"""

class GameError(Exception):
    """Базовое исключение игры"""
    pass

class AuthenticationError(GameError):
    """Ошибка аутентификации"""
    pass

class ValidationError(GameError):
    """Ошибка валидации данных"""
    pass

class GameNotFoundError(GameError):
    """Игра не найдена"""
    pass

class PlayerNotFoundError(GameError):
    """Игрок не найден"""
    pass

class GameAlreadyStartedError(GameError):
    """Игра уже началась"""
    pass

class InvalidGameActionError(GameError):
    """Недопустимое действие в игре"""
    pass

class NetworkError(GameError):
    """Ошибка сети"""
    pass

class DatabaseError(GameError):
    """Ошибка базы данных"""
    pass
