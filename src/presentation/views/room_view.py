"""
Интерфейс для управления игровыми комнатами
"""
from typing import Dict, List, Optional
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QMessageBox, QFrame, QListWidget,
                            QListWidgetItem, QLineEdit, QTextEdit, QDialog)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QPixmap, QPalette, QColor
from ..styles import StyleManager
import asyncio

class RoomListItem(QWidget):
    """Элемент списка комнат"""
    
    room_selected = pyqtSignal(str)  # room_id
    
    def __init__(self, room_data: Dict):
        super().__init__()
        self.room_data = room_data
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Информация о комнате
        info_layout = QVBoxLayout()
        
        name_label = QLabel(self.room_data['name'])
        name_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        info_layout.addWidget(name_label)
        
        creator_label = QLabel(f"Создатель: {self.room_data['creator_name']}")
        creator_label.setFont(QFont("Arial", 10))
        info_layout.addWidget(creator_label)
        
        players_label = QLabel(f"Игроки: {self.room_data['players_count']}/{self.room_data['max_players']}")
        players_label.setFont(QFont("Arial", 10))
        info_layout.addWidget(players_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # Кнопка присоединения
        join_button = QPushButton("Присоединиться")
        join_button.setStyleSheet(StyleManager().get_button_style('success', 'small'))
        join_button.clicked.connect(self.on_join_clicked)
        layout.addWidget(join_button)
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {StyleManager.COLORS['surface']};
                border: 1px solid {StyleManager.COLORS['border']};
                border-radius: {StyleManager.SIZES['border_radius_small']};
                margin: 2px;
            }}
            QWidget:hover {{
                background-color: {StyleManager.COLORS['card']};
            }}
        """)
        
    def on_join_clicked(self):
        self.room_selected.emit(self.room_data['id'])

class CreateRoomDialog(QDialog):
    """Диалог создания комнаты"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Создать комнату")
        self.setMinimumSize(400, 200)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Заголовок
        title = QLabel("Создание новой комнаты")
        title.setStyleSheet(StyleManager().get_title_style('large'))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Название комнаты
        name_label = QLabel("Название комнаты (необязательно):")
        layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Оставьте пустым для автоматического названия")
        layout.addWidget(self.name_input)
        
        # Информация
        info_label = QLabel("💡 Максимальное количество игроков: 2")
        info_label.setStyleSheet(StyleManager().get_label_style('muted'))
        layout.addWidget(info_label)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        cancel_button = QPushButton("Отмена")
        cancel_button.setStyleSheet(StyleManager().get_button_style('secondary', 'medium'))
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        create_button = QPushButton("Создать")
        create_button.setStyleSheet(StyleManager().get_button_style('primary', 'medium'))
        create_button.clicked.connect(self.accept)
        button_layout.addWidget(create_button)
        
        layout.addLayout(button_layout)
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {StyleManager.COLORS['background']};
            }}
        """)
    
    def get_room_name(self):
        return self.name_input.text().strip()

class RoomView(QWidget):
    """Интерфейс управления комнатами"""
    
    # Сигналы
    create_room_requested = pyqtSignal(str)  # room_name
    join_room_requested = pyqtSignal(str)    # room_id
    toggle_ready_requested = pyqtSignal()    # toggle ready status
    start_game_requested = pyqtSignal(str)   # room_id
    leave_room_requested = pyqtSignal()      # leave room
    back_to_menu = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.style_manager = StyleManager()
        self.current_room = None
        self.player_id = None
        self.player_name = None
        self.is_creator = False
        
        self.setup_ui()
        self.apply_styles()
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        self.setup_header(main_layout)
        
        # Основной контент (переключается между списком комнат и комнатой)
        self.content_stack = []
        self.setup_rooms_list(main_layout)
        self.setup_room_view(main_layout)
        
        # Показываем список комнат по умолчанию
        self.show_rooms_list()
        
        self.setLayout(main_layout)
        
    def setup_header(self, layout):
        """Настройка заголовка"""
        header_layout = QHBoxLayout()
        
        self.back_button = QPushButton("🔙 В меню")
        self.back_button.setFont(QFont("Arial", 10))
        self.back_button.clicked.connect(self.back_to_menu.emit)
        header_layout.addWidget(self.back_button)
        
        header_layout.addStretch()
        
        self.title_label = QLabel("🎮 Игровые комнаты")
        self.title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        self.refresh_button = QPushButton("🔄 Обновить")
        self.refresh_button.setFont(QFont("Arial", 10))
        self.refresh_button.clicked.connect(self.refresh_rooms)
        header_layout.addWidget(self.refresh_button)
        
        layout.addLayout(header_layout)
        
    def setup_rooms_list(self, layout):
        """Настройка списка комнат"""
        rooms_container = QWidget()
        rooms_layout = QVBoxLayout(rooms_container)
        
        # Кнопка создания комнаты
        create_button = QPushButton("➕ Создать комнату")
        create_button.setStyleSheet(self.style_manager.get_button_style('primary', 'large'))
        create_button.clicked.connect(self.show_create_room_dialog)
        rooms_layout.addWidget(create_button)
        
        # Список комнат
        rooms_label = QLabel("📋 Доступные комнаты:")
        rooms_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        rooms_layout.addWidget(rooms_label)
        
        self.rooms_list = QListWidget()
        self.rooms_list.setMinimumHeight(300)
        rooms_layout.addWidget(self.rooms_list)
        
        layout.addWidget(rooms_container)
        self.rooms_list_widget = rooms_container
        
    def setup_room_view(self, layout):
        """Настройка вида комнаты"""
        room_container = QWidget()
        room_layout = QVBoxLayout(room_container)
        
        # Информация о комнате
        self.room_info_frame = QFrame()
        self.room_info_frame.setFrameStyle(QFrame.Shape.Box)
        self.setup_room_info()
        room_layout.addWidget(self.room_info_frame)
        
        # Список игроков
        players_label = QLabel("👥 Игроки в комнате:")
        players_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        room_layout.addWidget(players_label)
        
        self.players_list = QListWidget()
        self.players_list.setMaximumHeight(150)
        room_layout.addWidget(self.players_list)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        self.ready_button = QPushButton("✅ Готов")
        self.ready_button.setStyleSheet(self.style_manager.get_button_style('success', 'medium'))
        self.ready_button.clicked.connect(self.toggle_ready)
        buttons_layout.addWidget(self.ready_button)
        
        self.start_button = QPushButton("🎮 Начать игру")
        self.start_button.setStyleSheet(self.style_manager.get_button_style('primary', 'medium'))
        self.start_button.clicked.connect(self.start_game)
        buttons_layout.addWidget(self.start_button)
        
        self.leave_button = QPushButton("🚪 Покинуть")
        self.leave_button.setStyleSheet(self.style_manager.get_button_style('warning', 'medium'))
        self.leave_button.clicked.connect(self.leave_room_requested.emit)
        buttons_layout.addWidget(self.leave_button)
        
        room_layout.addLayout(buttons_layout)
        
        layout.addWidget(room_container)
        self.room_widget = room_container
        self.room_widget.hide()
        
    def setup_room_info(self):
        """Настройка информации о комнате"""
        layout = QVBoxLayout(self.room_info_frame)
        
        self.room_name_label = QLabel("Название комнаты")
        self.room_name_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(self.room_name_label)
        
        self.room_status_label = QLabel("Статус: Ожидание")
        layout.addWidget(self.room_status_label)
        
    def apply_styles(self):
        """Применить стили"""
        self.setStyleSheet(self.style_manager.get_main_window_style())
        
    def set_player_info(self, player_id: str, player_name: str):
        """Установить информацию о игроке"""
        self.player_id = player_id
        self.player_name = player_name
        
    def show_rooms_list(self):
        """Показать список комнат"""
        self.room_widget.hide()
        self.rooms_list_widget.show()
        self.title_label.setText("🎮 Игровые комнаты")
        
    def show_room_view(self):
        """Показать вид комнаты"""
        self.rooms_list_widget.hide()
        self.room_widget.show()
        self.title_label.setText("🏠 Комната")
        
    def update_rooms_list(self, rooms: List[Dict]):
        """Обновить список комнат"""
        self.rooms_list.clear()
        
        if not rooms:
            item = QListWidgetItem("😔 Нет доступных комнат")
            item.setFont(QFont("Arial", 12))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.rooms_list.addItem(item)
            return
        
        for room in rooms:
            item = QListWidgetItem()
            room_widget = RoomListItem(room)
            room_widget.room_selected.connect(self.join_room_requested.emit)
            item.setSizeHint(room_widget.sizeHint())
            self.rooms_list.addItem(item)
            self.rooms_list.setItemWidget(item, room_widget)
            
    def update_room_info(self, room_data: Dict):
        """Обновить информацию о комнате"""
        self.current_room = room_data
        self.is_creator = room_data['creator_id'] == self.player_id
        
        # Обновляем基本信息
        self.room_name_label.setText(room_data['name'])
        
        status_map = {
            'waiting': '⏳ Ожидание игроков',
            'ready': '✅ Все готовы',
            'playing': '🎮 Игра идет',
            'finished': '🏁 Игра завершена'
        }
        status_text = status_map.get(room_data['status'], room_data['status'])
        self.room_status_label.setText(f"Статус: {status_text}")
        
        # Обновляем список игроков
        self.players_list.clear()
        for player_id, player_info in room_data['players'].items():
            status = "✅ Готов" if player_info['ready'] else "⏳ Не готов"
            if player_id == room_data['creator_id']:
                status += " (👑 Создатель)"
            
            item_text = f"{player_info['name']} - {status}"
            item = QListWidgetItem(item_text)
            self.players_list.addItem(item)
        
        # Обновляем кнопки
        self.update_buttons(room_data)
        
    def update_buttons(self, room_data: Dict):
        """Обновить состояние кнопок"""
        # Кнопка "Готов"
        is_ready = room_data['players'][self.player_id]['ready']
        if is_ready:
            self.ready_button.setText("❌ Не готов")
            self.ready_button.setStyleSheet(self.style_manager.get_button_style('warning', 'medium'))
        else:
            self.ready_button.setText("✅ Готов")
            self.ready_button.setStyleSheet(self.style_manager.get_button_style('success', 'medium'))
        
        # Кнопка "Начать игру" (только для создателя)
        can_start = (
            self.is_creator and 
            room_data['status'] == 'ready' and
            len(room_data['players']) == room_data['max_players']
        )
        self.start_button.setEnabled(can_start)
        
    def show_create_room_dialog(self):
        """Показать диалог создания комнаты"""
        dialog = CreateRoomDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            room_name = dialog.get_room_name()
            self.create_room_requested.emit(room_name)
            
    def refresh_rooms(self):
        """Обновить список комнат"""
        # Этот метод будет вызываться из контроллера
        pass
        
    def toggle_ready(self):
        """Переключить готовность"""
        if self.current_room:
            self.toggle_ready_requested.emit()
            
    def start_game(self):
        """Начать игру"""
        if self.current_room and self.is_creator:
            self.start_game_requested.emit(self.current_room['id'])
