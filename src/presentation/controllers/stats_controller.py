"""
Контроллер для управления статистикой
"""
import asyncio
import logging
from typing import Optional, Dict, List
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QMessageBox

from ..views.stats_view import StatsView

logger = logging.getLogger(__name__)

class StatsController(QObject):
    """Контроллер управления статистикой"""
    
    # Сигналы
    back_to_menu = pyqtSignal()
    error_occurred = pyqtSignal(str)           # error_message
    
    def __init__(self, database, player_id: str, player_name: str):
        super().__init__()
        self.database = database
        self.player_id = player_id
        self.player_name = player_name
        
        # Представление
        self.view = StatsView()
        self.view.set_player_info(player_id, player_name)
        self.setup_connections()
        
        # Таймер обновления
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_all_stats)
        self.refresh_timer.setInterval(30000)  # Обновлять каждые 30 секунд
        
    def setup_connections(self):
        """Настройка соединений сигналов"""
        self.view.back_to_menu.connect(self.back_to_menu.emit)
        self.view.refresh_requested.connect(self.refresh_all_stats)
        
    def get_view(self) -> StatsView:
        """Получить представление"""
        return self.view
        
    async def initialize(self):
        """Инициализация контроллера"""
        try:
            await self.refresh_all_stats()
            self.refresh_timer.start()
        except Exception as e:
            logger.error(f"Error initializing stats controller: {e}")
            self.error_occurred.emit(f"Ошибка инициализации статистики: {e}")
            
    async def refresh_all_stats(self):
        """Обновить всю статистику"""
        try:
            # Обновляем статистику игрока
            await self.refresh_player_stats()
            
            # Обновляем топ игроков
            await self.refresh_top_players()
            
        except Exception as e:
            logger.error(f"Error refreshing stats: {e}")
            self.error_occurred.emit(f"Ошибка обновления статистики: {e}")
            
    async def refresh_player_stats(self):
        """Обновить статистику игрока"""
        try:
            # Получаем статистику игрока
            stats_data = await self.database.get_player_stats(self.player_id)
            if stats_data:
                self.view.update_player_stats(stats_data)
            else:
                # Если статистики нет, создаем пустую
                default_stats = {
                    'total_score': 0,
                    'games_played': 0,
                    'last_result': '',
                    'results_count': {}
                }
                self.view.update_player_stats(default_stats)
            
            # Получаем историю игр
            history_data = await self.database.get_player_game_history(self.player_id, limit=10)
            self.view.update_player_history(history_data)
            
        except Exception as e:
            logger.error(f"Error refreshing player stats: {e}")
            
    async def refresh_top_players(self):
        """Обновить топ игроков"""
        try:
            top_data = await self.database.get_top_players(limit=20)
            self.view.update_top_players(top_data)
        except Exception as e:
            logger.error(f"Error refreshing top players: {e}")
            
    def cleanup(self):
        """Очистка ресурсов"""
        try:
            self.refresh_timer.stop()
        except:
            pass
