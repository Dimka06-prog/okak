"""
Контроллер для управления игровыми комнатами - простая версия
"""
import logging
from typing import Optional, Dict, List
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QMessageBox

from ..views.room_view import RoomView
from ...business.services.room_service import RoomService

logger = logging.getLogger(__name__)

class RoomController(QObject):
    """Контроллер управления игровыми комнатами"""
    
    # Сигналы
    game_started = pyqtSignal(str, str, str)  # game_id, player_id, opponent_name
    back_to_menu = pyqtSignal()
    error_occurred = pyqtSignal(str)           # error_message
    
    def __init__(self, database, player_id: str, player_name: str):
        super().__init__()
        self.database = database
        self.player_id = player_id
        self.player_name = player_name
        
        # Сервис
        self.room_service = RoomService(database)
        
        # Представление
        self.view = RoomView()
        self.view.set_player_info(player_id, player_name)
        self.setup_connections()
        
        # Таймер обновления
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.setInterval(10000)  # Обновлять каждые 10 секунд
        
        self.current_room_id = None
        
    def setup_connections(self):
        """Настройка соединений сигналов"""
        self.view.create_room_requested.connect(self.create_room)
        self.view.join_room_requested.connect(self.join_room)
        self.view.toggle_ready_requested.connect(self.toggle_ready)
        self.view.start_game_requested.connect(self.start_game)
        self.view.leave_room_requested.connect(self.leave_room)
        self.view.back_to_menu.connect(self.back_to_menu.emit)
        
    def get_view(self) -> RoomView:
        """Получить представление"""
        return self.view
        
    def initialize(self):
        """Инициализация контроллера"""
        try:
            self.refresh_rooms()
            self.refresh_timer.start()
        except Exception as e:
            logger.error(f"Error initializing room controller: {e}")
            self.error_occurred.emit(f"Ошибка инициализации: {e}")
            
    def refresh_rooms(self):
        """Обновить список комнат"""
        try:
            # Очищаем неактивные комнаты
            cleaned_count = self.room_service.cleanup_inactive_rooms()
            if cleaned_count > 0:
                logger.info(f"Очищено {cleaned_count} неактивных комнат")
            
            rooms = self.room_service.get_available_rooms()
            self.view.update_rooms_list(rooms)
        except Exception as e:
            logger.error(f"Error refreshing rooms: {e}")
            
    def refresh_data(self):
        """Обновить данные (вызывается таймером)"""
        try:
            if self.current_room_id:
                self.update_room_info()
            else:
                self.refresh_rooms()
        except Exception as e:
            logger.error(f"Error refreshing data: {e}")
            
    def create_room(self, room_name: str = None):
        """Создать комнату"""
        try:
            room_id = self.room_service.create_room(
                self.player_id, 
                self.player_name, 
                room_name
            )
            
            if room_id:
                self.current_room_id = room_id
                self.view.show_room_view()
                self.update_room_info()
                
                QMessageBox.information(
                    self.view,
                    "Комната создана",
                    f"🏠 Комната успешно создана!\\n\\nID: {room_id[:8]}...\\n\\nОжидайте других игроков."
                )
            else:
                QMessageBox.critical(
                    self.view,
                    "Ошибка",
                    "❌ Не удалось создать комнату"
                )
                
        except Exception as e:
            logger.error(f"Error creating room: {e}")
            QMessageBox.critical(
                self.view,
                "Ошибка создания комнаты",
                f"❌ Не удалось создать комнату:\\n\\n{e}"
            )
            
    def join_room(self, room_id: str):
        """Присоединиться к комнате"""
        try:
            success = self.room_service.join_room(room_id, self.player_id, self.player_name)
            
            if success:
                self.current_room_id = room_id
                
                # Получаем информацию о комнате
                room_info = self.room_service.get_room_info(room_id)
                if room_info:
                    players_count = len(room_info['players'])
                    
                    # Если в комнате 2 игрока, автоматически начинаем игру
                    if players_count == 2:
                        logger.info(f"Два игрока в комнате, автоматический запуск игры")
                        self.start_game(room_id)
                    else:
                        # Иначе обновляем интерфейс комнаты
                        self.update_room_info()
                        
                        QMessageBox.information(
                            self.view,
                            "Присоединение к комнате",
                            f"✅ Вы присоединились к комнате!\\n\\n"
                            f"Игроков в комнате: {players_count}/2\\n"
                            f"Ожидайте второго игрока для начала игры..."
                        )
                
                self.refresh_rooms()
            else:
                QMessageBox.warning(
                    self.view,
                    "Ошибка присоединения",
                    "⚠️ Не удалось присоединиться к комнате\\n\\n"
                    "Возможные причины:\\n"
                    "• Комната заполнена\\n"
                    "• Игра уже началась\\n"
                    "• Вы уже в этой комнате"
                )
                
        except Exception as e:
            logger.error(f"Error joining room: {e}")
            QMessageBox.critical(
                self.view,
                "Ошибка присоединения",
                f"❌ Не удалось присоединиться к комнате:\\n\\n{e}"
            )
            
    def leave_room(self):
        """Покинуть комнату"""
        try:
            if not self.current_room_id:
                return
                
            reply = QMessageBox.question(
                self.view,
                "Покинуть комнату",
                "🚪 Вы уверены, что хотите покинуть комнату?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.room_service.leave_room(self.current_room_id, self.player_id)
                self.current_room_id = None
                self.view.show_rooms_list()
                self.refresh_rooms()
                
                QMessageBox.information(
                    self.view,
                    "Выход из комнаты",
                    "✅ Вы покинули комнату"
                )
                
        except Exception as e:
            logger.error(f"Error leaving room: {e}")
            QMessageBox.critical(
                self.view,
                "Ошибка выхода",
                f"❌ Не удалось покинуть комнату:\\n\\n{e}"
            )
            
    def toggle_ready(self):
        """Переключить готовность"""
        try:
            if not self.current_room_id:
                return
                
            room = self.room_service.get_room_info(self.current_room_id)
            if not room:
                return
                
            current_ready = room['players'][self.player_id]['ready']
            new_ready = not current_ready
            
            success = self.room_service.set_player_ready(
                self.current_room_id, 
                self.player_id, 
                new_ready
            )
            
            if success:
                self.update_room_info()
            else:
                QMessageBox.warning(
                    self.view,
                    "Ошибка",
                    "⚠️ Не удалось изменить статус готовности"
                )
                
        except Exception as e:
            logger.error(f"Error toggling ready: {e}")
            QMessageBox.critical(
                self.view,
                "Ошибка готовности",
                f"❌ Не удалось изменить готовность:\\n\\n{e}"
            )
            
    def start_game(self, room_id: str):
        """Начать игру"""
        try:
            game_id = self.room_service.start_game(room_id, self.player_id)
            
            if game_id:
                # Останавливаем таймер обновления комнат
                self.refresh_timer.stop()
                
                QMessageBox.information(
                    self.view,
                    "Игра началась!",
                    f"🎮 Игра началась!\\n\\nУдачи!"
                )
                
                # Излучаем сигнал о начале игры
                self.game_started.emit(game_id, self.player_id, "Соперник")
            else:
                # Показываем конкретную причину почему игра не началась
                room = self.room_service.get_room_info(room_id)
                if room:
                    if room['creator_id'] != self.player_id:
                        QMessageBox.warning(
                            self.view,
                            "Ошибка начала игры",
                            "⚠️ Только создатель комнаты может начать игру"
                        )
                    elif len(room['players']) < 2:
                        QMessageBox.warning(
                            self.view,
                            "Ошибка начала игры",
                            "⚠️ Для начала игры нужно 2 игрока\\n\\nОжидайте подключения второго игрока"
                        )
                    else:
                        # Проверяем кто не готов
                        not_ready = []
                        for pid, player in room['players'].items():
                            if not player['ready']:
                                not_ready.append(player['name'])
                        
                        QMessageBox.warning(
                            self.view,
                            "Ошибка начала игры",
                            f"⚠️ Не все игроки готовы:\\n\\nНе готовы: {', '.join(not_ready)}"
                        )
                else:
                    QMessageBox.warning(
                        self.view,
                        "Ошибка начала игры",
                        "⚠️ Не удалось начать игру"
                    )
                
        except Exception as e:
            logger.error(f"Error starting game: {e}")
            QMessageBox.critical(
                self.view,
                "Ошибка начала игры",
                f"❌ Не удалось начать игру:\\n\\n{e}"
            )
            
    def update_room_info(self):
        """Обновить информацию о комнате"""
        try:
            if not self.current_room_id:
                return
                
            room_info = self.room_service.get_room_info(self.current_room_id)
            if room_info:
                self.view.update_room_info(room_info)
                
                # Проверяем нужно ли начинать игру (для создателя когда 2 игрока)
                if len(room_info['players']) == 2 and room_info['creator_id'] == self.player_id:
                    logger.info(f"Создатель обнаружил 2 игроков, автоматически начинаем игру")
                    self.start_game(self.current_room_id)
            else:
                # Комната была удалена
                self.current_room_id = None
                self.view.show_room_list()
                self.refresh_rooms()
                QMessageBox.information(
                    self.view,
                    "Комната удалена",
                    "Комната была удалена (возможно, из-за неактивности)"
                )
                
        except Exception as e:
            logger.error(f"Error updating room info: {e}")
            
    def cleanup(self):
        """Очистка ресурсов"""
        try:
            self.refresh_timer.stop()
        except:
            pass
