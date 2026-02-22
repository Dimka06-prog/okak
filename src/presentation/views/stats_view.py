"""
Интерфейс для просмотра статистики игроков
"""
from typing import Dict, List, Optional
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QMessageBox, QFrame, QListWidget,
                            QListWidgetItem, QTextEdit, QTabWidget, QTableWidget,
                            QTableWidgetItem, QHeaderView, QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPixmap, QPalette, QColor
from ..styles import StyleManager
import asyncio

class StatsWidget(QWidget):
    """Базовый виджет для статистики"""
    
    def __init__(self):
        super().__init__()
        self.style_manager = StyleManager()
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
    def apply_styles(self):
        """Применить стили"""
        self.setStyleSheet(self.style_manager.get_main_window_style())

class PlayerStatsWidget(StatsWidget):
    """Виджет статистики текущего игрока"""
    
    def __init__(self, player_id: str, player_name: str):
        super().__init__()
        self.player_id = player_id
        self.player_name = player_name
        self.setup_player_stats_ui()
        
    def setup_player_stats_ui(self):
        """Настройка интерфейса статистики игрока"""
        layout = QVBoxLayout(self)
        
        # Заголовок
        title_label = QLabel(f"📊 Статистика: {self.player_name}")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Основная статистика
        stats_frame = QFrame()
        stats_frame.setFrameStyle(QFrame.Shape.Box)
        stats_layout = QVBoxLayout(stats_frame)
        
        self.total_score_label = QLabel("🏆 Общий счет: 0")
        self.total_score_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        stats_layout.addWidget(self.total_score_label)
        
        self.games_played_label = QLabel("🎮 Игр сыграно: 0")
        self.games_played_label.setFont(QFont("Arial", 12))
        stats_layout.addWidget(self.games_played_label)
        
        self.last_result_label = QLabel("📅 Последний результат: -")
        self.last_result_label.setFont(QFont("Arial", 12))
        stats_layout.addWidget(self.last_result_label)
        
        layout.addWidget(stats_frame)
        
        # Детальная статистика по результатам
        detail_title = QLabel("📈 Детальная статистика:")
        detail_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(detail_title)
        
        self.detail_text = QTextEdit()
        self.detail_text.setMaximumHeight(150)
        self.detail_text.setReadOnly(True)
        layout.addWidget(self.detail_text)
        
        # История игр
        history_title = QLabel("📜 Последние игры:")
        history_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(history_title)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["Соперник", "Счет", "Результат", "Дата"])
        
        # Настройка таблицы
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        self.history_table.setMaximumHeight(200)
        layout.addWidget(self.history_table)
        
        # Кнопка обновления
        refresh_button = QPushButton("🔄 Обновить статистику")
        refresh_button.setStyleSheet(self.style_manager.get_button_style('primary', 'medium'))
        refresh_button.clicked.connect(self.refresh_stats)
        layout.addWidget(refresh_button)
        
        layout.addStretch()
        
    def update_stats(self, stats_data: Dict):
        """Обновить статистику"""
        if not stats_data:
            return
            
        # Обновляем основную статистику
        self.total_score_label.setText(f"🏆 Общий счет: {stats_data.get('total_score', 0)}")
        self.games_played_label.setText(f"🎮 Игр сыграно: {stats_data.get('games_played', 0)}")
        
        # Обновляем последний результат
        last_result = stats_data.get('last_result', '')
        result_descriptions = {
            'cooperate_cooperate': '🤝 Оба сотрудничали',
            'cooperate_betray': '😔 Вас предали',
            'betray_cooperate': '🎯 Вы предали',
            'betray_betray': '⚔️ Оба предали'
        }
        last_result_text = result_descriptions.get(last_result, '-')
        self.last_result_label.setText(f"📅 Последний результат: {last_result_text}")
        
        # Обновляем детальную статистику
        results_count = stats_data.get('results_count', {})
        detail_text = "Результаты по типам:\\n"
        for result_type, count in results_count.items():
            result_desc = result_descriptions.get(result_type, result_type)
            detail_text += f"• {result_desc}: {count} раз\\n"
        
        self.detail_text.setText(detail_text)
        
    def update_history(self, history_data: List[Dict]):
        """Обновить историю игр"""
        self.history_table.setRowCount(len(history_data))
        
        for row, game in enumerate(history_data):
            # Соперник
            opponent_item = QTableWidgetItem(game.get('opponent_name', 'Unknown'))
            self.history_table.setItem(row, 0, opponent_item)
            
            # Счет
            score_text = f"{game.get('player_score', 0)} : {game.get('opponent_score', 0)}"
            score_item = QTableWidgetItem(score_text)
            self.history_table.setItem(row, 1, score_item)
            
            # Результат
            result = game.get('result', 'draw')
            result_text = {'win': '🏆 Победа', 'lose': '� Поражение', 'draw': '🤝 Ничья'}.get(result, result)
            result_item = QTableWidgetItem(result_text)
            self.history_table.setItem(row, 2, result_item)
            
            # Дата
            date_str = game.get('created_at', '')
            if date_str:
                # Форматируем дату
                try:
                    from datetime import datetime
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    formatted_date = date_obj.strftime('%d.%m.%Y %H:%M')
                except:
                    formatted_date = date_str[:10]  # Просто берем первые 10 символов
            else:
                formatted_date = '-'
            
            date_item = QTableWidgetItem(formatted_date)
            self.history_table.setItem(row, 3, date_item)
    
    def refresh_stats(self):
        """Обновить статистику"""
        # Этот метод будет вызываться из контроллера
        pass

class TopPlayersWidget(StatsWidget):
    """Виджет топ игроков"""
    
    def __init__(self):
        super().__init__()
        self.setup_top_players_ui()
        
    def setup_top_players_ui(self):
        """Настройка интерфейса топ игроков"""
        layout = QVBoxLayout(self)
        
        # Заголовок
        title_label = QLabel("🏆 Топ игроков")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Таблица топ игроков
        self.top_table = QTableWidget()
        self.top_table.setColumnCount(5)
        self.top_table.setHorizontalHeaderLabels(["Место", "Игрок", "Общий счет", "Игр сыграно", "Последняя игра"])
        
        # Настройка таблицы
        header = self.top_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.top_table)
        
        # Кнопка обновления
        refresh_button = QPushButton("🔄 Обновить топ")
        refresh_button.setStyleSheet(self.style_manager.get_button_style('primary', 'medium'))
        refresh_button.clicked.connect(self.refresh_top)
        layout.addWidget(refresh_button)
        
    def update_top_players(self, top_data: List[Dict]):
        """Обновить топ игроков"""
        self.top_table.setRowCount(len(top_data))
        
        for row, player in enumerate(top_data):
            # Место
            place_item = QTableWidgetItem(f"#{row + 1}")
            place_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.top_table.setItem(row, 0, place_item)
            
            # Имя игрока
            name_item = QTableWidgetItem(player.get('username', 'Unknown'))
            self.top_table.setItem(row, 1, name_item)
            
            # Общий счет
            score_item = QTableWidgetItem(str(player.get('total_score', 0)))
            score_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.top_table.setItem(row, 2, score_item)
            
            # Игр сыграно
            games_item = QTableWidgetItem(str(player.get('games_played', 0)))
            games_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.top_table.setItem(row, 3, games_item)
            
            # Последняя игра
            last_played = player.get('last_played', '')
            if last_played:
                try:
                    from datetime import datetime
                    date_obj = datetime.fromisoformat(last_played.replace('Z', '+00:00'))
                    formatted_date = date_obj.strftime('%d.%m.%Y')
                except:
                    formatted_date = last_played[:10]
            else:
                formatted_date = '-'
            
            date_item = QTableWidgetItem(formatted_date)
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.top_table.setItem(row, 4, date_item)
    
    def refresh_top(self):
        """Обновить топ игроков"""
        # Этот метод будет вызываться из контроллера
        pass

class StatsView(QWidget):
    """Главный интерфейс статистики"""
    
    # Сигналы
    back_to_menu = pyqtSignal()
    refresh_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.style_manager = StyleManager()
        self.player_id = None
        self.player_name = None
        self.setup_ui()
        self.apply_styles()
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        self.setup_header(main_layout)
        
        # Вкладки со статистикой
        self.tab_widget = QTabWidget()
        
        # Вкладка личной статистики
        self.player_stats_widget = None
        
        # Вкладка топ игроков
        self.top_players_widget = TopPlayersWidget()
        self.tab_widget.addTab(self.top_players_widget, "🏆 Топ игроков")
        
        main_layout.addWidget(self.tab_widget)
        
        self.setLayout(main_layout)
        
    def setup_header(self, layout):
        """Настройка заголовка"""
        header_layout = QHBoxLayout()
        
        self.back_button = QPushButton("🔙 В меню")
        self.back_button.setFont(QFont("Arial", 10))
        self.back_button.clicked.connect(self.back_to_menu.emit)
        header_layout.addWidget(self.back_button)
        
        header_layout.addStretch()
        
        self.title_label = QLabel("📊 Статистика")
        self.title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        self.refresh_button = QPushButton("🔄 Обновить всё")
        self.refresh_button.setFont(QFont("Arial", 10))
        self.refresh_button.clicked.connect(self.refresh_requested.emit)
        header_layout.addWidget(self.refresh_button)
        
        layout.addLayout(header_layout)
        
    def set_player_info(self, player_id: str, player_name: str):
        """Установить информацию о игроке"""
        self.player_id = player_id
        self.player_name = player_name
        
        # Создаем виджет личной статистики
        if self.player_stats_widget:
            self.tab_widget.removeTab(0)
            
        self.player_stats_widget = PlayerStatsWidget(player_id, player_name)
        self.tab_widget.insertTab(0, self.player_stats_widget, "👤 Моя статистика")
        self.tab_widget.setCurrentIndex(0)
        
    def update_player_stats(self, stats_data: Dict):
        """Обновить статистику игрока"""
        if self.player_stats_widget:
            self.player_stats_widget.update_stats(stats_data)
            
    def update_player_history(self, history_data: List[Dict]):
        """Обновить историю игр игрока"""
        if self.player_stats_widget:
            self.player_stats_widget.update_history(history_data)
            
    def update_top_players(self, top_data: List[Dict]):
        """Обновить топ игроков"""
        if self.top_players_widget:
            self.top_players_widget.update_top_players(top_data)
            
    def apply_styles(self):
        """Применить стили"""
        self.setStyleSheet(self.style_manager.get_main_window_style())
