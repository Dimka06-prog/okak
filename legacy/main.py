import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QListWidget, QListWidgetItem, QMessageBox, QStackedWidget,
                            QGridLayout, QFrame, QButtonGroup, QRadioButton)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
from improved_database import GameDatabase
from realtime_game_window import RealtimeGameWindow
import random

class LoginWindow(QWidget):
    """Окно регистрации и авторизации"""
    login_success = pyqtSignal(int)  # Сигнал успешного входа с ID игрока
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Заголовок
        title = QLabel("🎮 Предать или Сотрудничать")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Форма входа
        login_frame = QFrame()
        login_frame.setFrameStyle(QFrame.Shape.Box)
        login_frame.setStyleSheet("background-color: #f0f0f0; border-radius: 10px; padding: 20px;")
        login_layout = QVBoxLayout()
        
        # Регистрация
        reg_label = QLabel("Регистрация")
        reg_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        login_layout.addWidget(reg_label)
        
        self.reg_username = QLineEdit()
        self.reg_username.setPlaceholderText("Имя пользователя")
        login_layout.addWidget(self.reg_username)
        
        self.reg_password = QLineEdit()
        self.reg_password.setPlaceholderText("Пароль")
        self.reg_password.setEchoMode(QLineEdit.EchoMode.Password)
        login_layout.addWidget(self.reg_password)
        
        self.register_btn = QPushButton("Зарегистрироваться")
        self.register_btn.clicked.connect(self.register)
        self.register_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        login_layout.addWidget(self.register_btn)
        
        # Разделитель
        separator = QLabel("- ИЛИ -")
        separator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_layout.addWidget(separator)
        
        # Вход
        login_label = QLabel("Вход")
        login_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        login_layout.addWidget(login_label)
        
        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Имя пользователя")
        login_layout.addWidget(self.login_username)
        
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Пароль")
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        login_layout.addWidget(self.login_password)
        
        self.login_btn = QPushButton("Войти")
        self.login_btn.clicked.connect(self.login)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        login_layout.addWidget(self.login_btn)
        
        login_frame.setLayout(login_layout)
        layout.addWidget(login_frame)
        
        self.setLayout(layout)
    
    def register(self):
        username = self.reg_username.text().strip()
        password = self.reg_password.text().strip()
        
        # Валидация на клиенте
        if len(username) < 3:
            QMessageBox.warning(self, "Ошибка", "Имя пользователя должно содержать минимум 3 символа!")
            return
        
        if len(username) > 20:
            QMessageBox.warning(self, "Ошибка", "Имя пользователя должно содержать не более 20 символов!")
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "Ошибка", "Пароль должен содержать минимум 6 символов!")
            return
        
        # Проверка допустимых символов
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
        if not all(c in allowed_chars for c in username):
            QMessageBox.warning(self, "Ошибка", "Имя пользователя может содержать только буквы, цифры, _ и -")
            return
        
        try:
            if self.db.register_player(username, password):
                QMessageBox.information(self, "Успех", "Регистрация прошла успешно!")
                # Автоматический вход после регистрации
                player_id = self.db.login_player(username, password)
                if player_id:
                    self.login_success.emit(player_id)
                else:
                    QMessageBox.warning(self, "Ошибка", "Регистрация прошла успешно, но не удалось войти. Попробуйте войти вручную.")
            else:
                QMessageBox.warning(self, "Ошибка", "Имя пользователя уже занято!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", "Произошла ошибка при регистрации. Попробуйте позже.")
    
    def login(self):
        username = self.login_username.text().strip()
        password = self.login_password.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return
        
        try:
            player_id = self.db.login_player(username, password)
            if player_id:
                self.login_success.emit(player_id)
            else:
                QMessageBox.warning(self, "Ошибка", "Неверное имя пользователя или пароль!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", "Произошла ошибка при входе. Попробуйте позже.")

class PlayersListWindow(QWidget):
    """Окно со списком онлайн игроков"""
    player_selected = pyqtSignal(int)  # Сигнал выбора игрока с его ID
    
    def __init__(self, db, current_player_id):
        super().__init__()
        self.db = db
        self.current_player_id = current_player_id
        self.init_ui()
        self.update_players_list()
        
        # Таймер для обновления списка игроков
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_players_list)
        self.timer.start(5000)  # Обновление каждые 5 секунд
        
        # Таймер для ping
        self.ping_timer = QTimer()
        self.ping_timer.timeout.connect(self.ping)
        self.ping_timer.start(10000)  # Ping каждые 10 секунд
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("👥 Игроки онлайн")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Информация о текущем игроке
        player_stats = self.db.get_player_stats(self.current_player_id)
        if player_stats:
            info_label = QLabel(f"Вы: {player_stats['username']} | Счет: {player_stats['total_score']} | Игр: {player_stats['games_played']}")
            info_label.setStyleSheet("background-color: #e3f2fd; padding: 10px; border-radius: 5px;")
            layout.addWidget(info_label)
        
        # Список игроков
        self.players_list = QListWidget()
        self.players_list.itemDoubleClicked.connect(self.on_player_selected)
        layout.addWidget(self.players_list)
        
        # Кнопка обновления
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.clicked.connect(self.update_players_list)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        layout.addWidget(refresh_btn)
        
        self.setLayout(layout)
    
    def update_players_list(self):
        self.players_list.clear()
        players = self.db.get_online_players(self.current_player_id)
        
        if not players:
            self.players_list.addItem("Нет других игроков онлайн")
            return
        
        for player in players:
            item_text = f"🎮 {player['username']} | Счет: {player['total_score']} | Игр: {player['games_played']}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, player['id'])
            self.players_list.addItem(item)
    
    def on_player_selected(self, item):
        opponent_id = item.data(Qt.ItemDataRole.UserRole)
        if opponent_id:
            self.player_selected.emit(opponent_id)
    
    def ping(self):
        """Поддержание онлайн статуса"""
        self.db.ping_player(self.current_player_id)

class RoundSelectionWindow(QWidget):
    """Окно выбора раунда"""
    round_selected = pyqtSignal(int)  # Сигнал выбора раунда
    
    def __init__(self, game_id, db):
        super().__init__()
        self.game_id = game_id
        self.db = db
        self.available_rounds = [1, 2, 3]  # Доступные раунды
        self.selected_round = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("🎯 Выберите раунд")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Информация
        info = QLabel("Выберите один из доступных раундов для начала игры")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
        
        # Кнопки выбора раунда
        rounds_layout = QGridLayout()
        
        self.round_buttons = QButtonGroup()
        
        for i, round_num in enumerate(self.available_rounds):
            btn = QPushButton(f"Раунд {round_num}")
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #9C27B0;
                    color: white;
                    border-radius: 10px;
                    padding: 20px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:checked {
                    background-color: #7B1FA2;
                }
                QPushButton:hover {
                    background-color: #8E24AA;
                }
            """)
            
            self.round_buttons.addButton(btn, round_num)
            row, col = i // 3, i % 3
            rounds_layout.addWidget(btn, row, col)
        
        layout.addLayout(rounds_layout)
        
        # Кнопка начала игры
        self.start_btn = QPushButton("🚀 Начать игру")
        self.start_btn.clicked.connect(self.start_game)
        self.start_btn.setEnabled(False)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        layout.addWidget(self.start_btn)
        
        # Подключение сигнала выбора раунда
        self.round_buttons.buttonClicked.connect(self.on_round_selected)
        
        self.setLayout(layout)
    
    def on_round_selected(self, button):
        self.start_btn.setEnabled(True)
        self.selected_round = self.round_buttons.id(button)
    
    def start_game(self):
        if self.selected_round:
            # Создаем раунд в базе данных
            round_id = self.db.create_round(self.game_id, self.selected_round)
            self.round_selected.emit(self.selected_round)

class GameWindow(QWidget):
    """Окно игры с 10 вопросами"""
    game_completed = pyqtSignal()  # Сигнал завершения игры
    
    def __init__(self, game_id, round_id, player_id, db):
        super().__init__()
        self.game_id = game_id
        self.round_id = round_id
        self.player_id = player_id
        self.db = db
        self.current_question = 1
        self.total_questions = 10
        self.choices = []
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок
        self.title = QLabel(f"❓ Вопрос {self.current_question}/{self.total_questions}")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(self.title)
        
        # Текст вопроса
        self.question_text = QLabel(self.get_question_text(self.current_question))
        self.question_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.question_text.setWordWrap(True)
        self.question_text.setFont(QFont("Arial", 14))
        self.question_text.setStyleSheet("""
            QLabel {
                background-color: #f5f5f5;
                padding: 20px;
                border-radius: 10px;
                border: 2px solid #ddd;
            }
        """)
        layout.addWidget(self.question_text)
        
        # Кнопки выбора
        choices_layout = QHBoxLayout()
        
        self.cooperate_btn = QPushButton("🤝 Сотрудничать")
        self.cooperate_btn.clicked.connect(self.make_choice)
        self.cooperate_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 10px;
                padding: 20px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        choices_layout.addWidget(self.cooperate_btn)
        
        self.betray_btn = QPushButton("🗡️ Предать")
        self.betray_btn.clicked.connect(self.make_choice)
        self.betray_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border-radius: 10px;
                padding: 20px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        choices_layout.addWidget(self.betray_btn)
        
        layout.addLayout(choices_layout)
        
        # Прогресс бар
        self.progress_label = QLabel(f"Прогресс: {self.current_question}/{self.total_questions}")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progress_label)
        
        self.setLayout(layout)
    
    def get_question_text(self, question_num):
        """Получение текста вопроса по номеру"""
        questions = [
            "Вы и ваш партнер пойманы за преступлением. Вы можете сотрудничать (молчать) или предать (свидетельствовать).",
            "Два бизнеса конкурируют на рынке. Вы можете договориться о ценах или сбить цены конкурента.",
            "Вы делитесь ресурсами в ограниченной среде. Кооперация или личная выгода?",
            "В командном проекте: работать вместе или использовать чужие результаты?",
            "Две страны делят территорию: мирное разделение или конфликт за ресурсы?",
            "В аукционе: договориться о низкой цене или перебить предложение конкурента?",
            "Обмен информацией: делиться знаниями или сохранить в секрете?",
            "Экологическая проблема: совместные усилия или перекладывание ответственности?",
            "Инвестиционный пул: доверять партнерам или действовать в одиночку?",
            "Социальная дилемма: следовать правилам или нарушать для выгоды?"
        ]
        return questions[question_num - 1] if question_num <= len(questions) else "Вопрос не найден"
    
    def make_choice(self):
        """Обработка выбора игрока"""
        sender = self.sender()
        choice = "cooperate" if sender == self.cooperate_btn else "betray"
        
        # Сохраняем выбор в базе данных
        self.db.save_question_choice(self.round_id, self.current_question, self.player_id, choice)
        self.choices.append(choice)
        
        # Переходим к следующему вопросу или завершаем игру
        if self.current_question < self.total_questions:
            self.current_question += 1
            self.update_question()
        else:
            self.complete_game()
    
    def update_question(self):
        """Обновление интерфейса для следующего вопроса"""
        self.title.setText(f"❓ Вопрос {self.current_question}/{self.total_questions}")
        self.question_text.setText(self.get_question_text(self.current_question))
        self.progress_label.setText(f"Прогресс: {self.current_question}/{self.total_questions}")
    
    def complete_game(self):
        """Завершение игры"""
        self.game_completed.emit()

class StatisticsWindow(QWidget):
    """Окно статистики после раунда"""
    back_to_menu = pyqtSignal()  # Сигнал возврата в меню
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("📊 Статистика раунда")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Здесь будет отображаться статистика
        self.stats_label = QLabel("Статистика будет отображена здесь...")
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stats_label.setWordWrap(True)
        layout.addWidget(self.stats_label)
        
        # Кнопка возврата
        back_btn = QPushButton("🏠 Вернуться в меню")
        back_btn.clicked.connect(self.back_to_menu.emit)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                padding: 15px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        layout.addWidget(back_btn)
        
        self.setLayout(layout)

class MainWindow(QMainWindow):
    """Главное окно приложения"""
    def __init__(self):
        super().__init__()
        self.db = GameDatabase()
        self.current_player_id = None
        self.current_game_id = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Предать или Сотрудничать")
        self.setGeometry(100, 100, 800, 600)
        
        # Создаем стек виджетов для навигации
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Создаем окна
        self.login_window = LoginWindow(self.db)
        self.login_window.login_success.connect(self.on_login_success)
        self.stacked_widget.addWidget(self.login_window)
        
        # Устанавливаем начальное окно
        self.stacked_widget.setCurrentWidget(self.login_window)
    
    def on_login_success(self, player_id):
        """Обработка успешного входа"""
        self.current_player_id = player_id
        
        # Создаем окно со списком игроков
        self.players_window = PlayersListWindow(self.db, player_id)
        self.players_window.player_selected.connect(self.on_player_selected)
        self.stacked_widget.addWidget(self.players_window)
        self.stacked_widget.setCurrentWidget(self.players_window)
    
    def on_player_selected(self, opponent_id):
        """Обработка выбора игрока"""
        # Создаем игру
        self.current_game_id = self.db.create_game(self.current_player_id, opponent_id)
        
        # Создаем окно выбора раунда
        self.round_selection_window = RoundSelectionWindow(self.current_game_id, self.db)
        self.round_selection_window.round_selected.connect(self.on_round_selected)
        self.stacked_widget.addWidget(self.round_selection_window)
        self.stacked_widget.setCurrentWidget(self.round_selection_window)
    
    def on_round_selected(self, round_number):
        """Обработка выбора раунда"""
        # Создаем раунд в базе данных
        round_id = self.db.create_round(self.current_game_id, round_number)
        
        # Создаем окно игры с реальным временем
        self.game_window = RealtimeGameWindow(self.current_game_id, round_id, self.current_player_id, self.db)
        self.game_window.game_completed.connect(self.on_game_completed)
        self.stacked_widget.addWidget(self.game_window)
        self.stacked_widget.setCurrentWidget(self.game_window)
    
    def on_game_completed(self):
        """Обработка завершения игры"""
        # Создаем окно статистики
        self.statistics_window = StatisticsWindow(self)
        self.statistics_window.back_to_menu.connect(self.back_to_players_list)
        self.stacked_widget.addWidget(self.statistics_window)
        self.stacked_widget.setCurrentWidget(self.statistics_window)
    
    def back_to_players_list(self):
        """Возврат к списку игроков"""
        self.stacked_widget.setCurrentWidget(self.players_window)
    
    def closeEvent(self, event):
        """Обработка закрытия приложения"""
        if self.current_player_id:
            self.db.logout_player(self.current_player_id)
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())