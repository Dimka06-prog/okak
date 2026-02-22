"""
Менеджер конфигурации приложения
"""
import json
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigManager:
    """Управление конфигурацией приложения"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self._config = {}
        self._load_default_config()
        
    def _load_default_config(self):
        """Загрузка конфигурации по умолчанию"""
        self._config = {
            'app': {
                'name': 'Предать или Сотрудничать',
                'version': '1.0.0',
                'debug': False
            },
            'database': {
                'type': 'firebase',
                'config_file': 'firebase_config.json'
            },
            'game': {
                'max_players_per_game': 2,
                'questions_per_round': 10,
                'ping_interval': 10,  # секунды
                'online_timeout': 30  # секунды
            },
            'ui': {
                'window_width': 800,
                'window_height': 600,
                'theme': 'default'
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        }
    
    def load_config(self, config_file: str = "app_config.json") -> bool:
        """Загрузка конфигурации из файла"""
        config_path = self.config_dir / config_file
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    self._merge_config(user_config)
                logger.info(f"Конфигурация загружена из {config_path}")
                return True
            except Exception as e:
                logger.error(f"Ошибка загрузки конфигурации: {e}")
                return False
        else:
            logger.info(f"Файл конфигурации {config_path} не найден, используем настройки по умолчанию")
            self.save_config(config_file)
            return False
    
    def save_config(self, config_file: str = "app_config.json") -> bool:
        """Сохранение конфигурации в файл"""
        config_path = self.config_dir / config_file
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
            logger.info(f"Конфигурация сохранена в {config_path}")
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения конфигурации: {e}")
            return False
    
    def _merge_config(self, user_config: Dict[str, Any]):
        """Слияние пользовательской конфигурации с конфигурацией по умолчанию"""
        def merge_dict(default: dict, user: dict) -> dict:
            result = default.copy()
            for key, value in user.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = merge_dict(result[key], value)
                else:
                    result[key] = value
            return result
        
        self._config = merge_dict(self._config, user_config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Получение значения конфигурации по ключу"""
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """Установка значения конфигурации"""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_firebase_config_path(self) -> str:
        """Получение пути к файлу конфигурации Firebase (кроссплатформенно)"""
        import sys
        config_file = self.get('database.config_file')
        
        if getattr(sys, 'frozen', False):
            # Если запущено как .exe файл
            base_path = os.path.dirname(sys.executable)
        else:
            # Если запущено как .py файл
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        return os.path.join(base_path, "src", "config", config_file)
    
    def get_database_config(self) -> Dict[str, Any]:
        """Получение конфигурации базы данных"""
        return self.get('database', {})
    
    def get_game_config(self) -> Dict[str, Any]:
        """Получение конфигурации игры"""
        return self.get('game', {})
    
    def get_ui_config(self) -> Dict[str, Any]:
        """Получение конфигурации UI"""
        return self.get('ui', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Получение конфигурации логирования"""
        return self.get('logging', {})

# Глобальный экземпляр конфигурации
config = ConfigManager()
