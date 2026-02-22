"""
Базовый абстрактный репозиторий
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Callable, Any

class BaseRepository(ABC):
    """Базовый класс для всех репозиториев"""
    
    def __init__(self):
        self._listeners: Dict[str, Callable] = {}
    
    @abstractmethod
    def connect(self) -> bool:
        """Установить соединение с базой данных"""
        pass
    
    @abstractmethod
    def disconnect(self):
        """Закрыть соединение с базой данных"""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Проверить статус соединения"""
        pass
    
    def add_listener(self, key: str, callback: Callable):
        """Добавить слушателя изменений"""
        self._listeners[key] = callback
    
    def remove_listener(self, key: str):
        """Удалить слушателя изменений"""
        if key in self._listeners:
            del self._listeners[key]
    
    def _notify_listeners(self, event: str, data: Any = None):
        """Уведомить всех слушателей"""
        for callback in self._listeners.values():
            try:
                callback(event, data)
            except Exception as e:
                print(f"Ошибка в обработчике слушателя: {e}")
