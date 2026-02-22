from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QMessageBox, QGridLayout)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QFont
from improved_database import ImprovedFirebaseDatabase
import time

class GameListener(QThread):
    """Поток для прослушивания изменений в игре"""
    opponent_answered = pyqtSignal(str, str)  # opponent_choice, question_number
    both_answered = pyqtSignal(dict)  # choices dict
    
    def __init__(self, game_id, round_id, player_id, db):
        super().__init__()
        self.game_id = game_id
        self.round_id = round_id
        self.player_id = player_id
        self.db = db
        self.running = True
        
    def run(self):
        """Прослушивание изменений в реальном времени"""
        def on_question_change(data):
            if not data or not self.running:
                return
                
            # Проверяем ответы на текущий вопрос
            current_question = 1  # Здесь нужно получать текущий вопрос
            choices = self.db.get_question_choices(str(self.round_id), current_question)
            
            # Определяем какой игрок мы
            game_data = self.db.ref.child('games').child(self.game_id).get()
            if not game_data:
                return
                
            is_player1 = self.player_id == game_data.get('player1_id')
            
            # Проверяем ответил ли соперник
            if is_player1:
                opponent_choice = choices.get('player2_choice')
            else:
                opponent_choice = choices.get('player1_choice')
                
            if opponent_choice:
                self.opponent_answered.emit(opponent_choice, str(current_question))
                
                # Проверяем оба ли ответили
                if choices.get('player1_choice') and choices.get('player2_choice'):
                    self.both_answered.emit(choices)
        
        # Начинаем прослушивание
        self.db.listen_to_questions(str(self.round_id), on_question_change)
        
        # Поддерживаем поток активным
        while self.running:
            time.sleep(1)
    
    def stop(self):
        self.running = False

class RealtimeGameWindow(QWidget):
    """Окно игры с реальным временем"""
    game_completed = pyqtSignal()
    
    def __init__(self, game_id, round_id, player_id, db):
        super().__init__()
        self.game_id = game_id
        self.round_id = round_id
        self.player_id = player_id
        self.db = db
        self.current_question = 1
        self.total_questions = 10
        self.choices = {}
        self.opponent_choice = None
        self.waiting_for_opponent = False
        
        self.init_ui()
        self.setup_listeners()
        
        # Запускаем ping для поддержания онлайн статуса
        self.ping_timer = QTimer()
        self.ping_timer.timeout.connect(self.ping)
        self.ping_timer.start(10000)  # Каждые 10 секунд
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок
        self.title = QLabel(f"❓ Вопрос {self.current_question}/{self.total_questions}")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(self.title)
        
        # Информация о статусе
        self.status_label = QLabel("Ожидание вашего ответа...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #e3f2fd;
                color: #1976d2;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.status_label)
        
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
            QPushButton:disabled {
                background-color: #cccccc;
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
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        choices_layout.addWidget(self.betray_btn)
        
        layout.addLayout(choices_layout)
        
        # Статус соперника
        self.opponent_status = QLabel("Соперник думает...")
        self.opponent_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.opponent_status.setStyleSheet("""
            QLabel {
                background-color: #fff3e0;
                color: #f57c00;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.opponent_status)
        
        # Прогресс
        self.progress_label = QLabel(f"Прогресс: {self.current_question}/{self.total_questions}")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progress_label)
        
        self.setLayout(layout)
    
    def setup_listeners(self):
        """Настройка слушателей реального времени"""
        self.listener = GameListener(self.game_id, self.round_id, self.player_id, self.db)
        self.listener.opponent_answered.connect(self.on_opponent_answered)
        self.listener.both_answered.connect(self.on_both_answered)
        self.listener.start()
    
    def get_question_text(self, question_num):
        """Получение текста вопроса"""
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
        if self.waiting_for_opponent:
            return  # Уже ответили, ждем соперника
            
        sender = self.sender()
        choice = "cooperate" if sender == self.cooperate_btn else "betray"
        
        # Сохраняем выбор (передаем round_id как строку)
        self.db.save_question_choice(str(self.round_id), self.current_question, self.player_id, choice)
        self.choices[self.current_question] = choice
        
        # Блокируем кнопки
        self.cooperate_btn.setEnabled(False)
        self.betray_btn.setEnabled(False)
        
        # Обновляем статус
        self.status_label.setText("Вы ответили! Ожидание соперника...")
        self.waiting_for_opponent = True
        
        # Обновляем статус готовности в игре
        self.db.update_game_status(self.game_id, self.player_id, True)
    
    def on_opponent_answered(self, opponent_choice, question_number):
        """Когда соперник ответил"""
        if int(question_number) == self.current_question:
            self.opponent_choice = opponent_choice
            choice_text = "Сотрудничать" if opponent_choice == "cooperate" else "Предать"
            self.opponent_status.setText(f"Соперник ответил: {choice_text}")
            self.opponent_status.setStyleSheet("""
                QLabel {
                    background-color: #e8f5e8;
                    color: #2e7d32;
                    padding: 10px;
                    border-radius: 5px;
                    font-weight: bold;
                }
            """)
    
    def on_both_answered(self, choices):
        """Когда оба игрока ответили"""
        if self.current_question in self.choices:
            # Показываем результат на 2 секунды
            self.show_result()
            
            # Переходим к следующему вопросу через 2 секунды
            QTimer.singleShot(2000, self.next_question)
    
    def show_result(self):
        """Показать результат текущего вопроса"""
        player_choice = self.choices[self.current_question]
        opponent_choice = self.opponent_choice
        
        player_text = "Сотрудничать" if player_choice == "cooperate" else "Предать"
        opponent_text = "Сотрудничать" if opponent_choice == "cooperate" else "Предать"
        
        result_text = f"Вы: {player_text}\nСоперник: {opponent_text}"
        
        self.status_label.setText(result_text)
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #f3e5f5;
                color: #7b1fa2;
                padding: 15px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
    
    def next_question(self):
        """Переход к следующему вопросу"""
        self.current_question += 1
        
        if self.current_question > self.total_questions:
            self.complete_game()
            return
        
        # Сбрасываем интерфейс для нового вопроса
        self.waiting_for_opponent = False
        self.opponent_choice = None
        
        self.title.setText(f"❓ Вопрос {self.current_question}/{self.total_questions}")
        self.question_text.setText(self.get_question_text(self.current_question))
        self.progress_label.setText(f"Прогресс: {self.current_question}/{self.total_questions}")
        
        self.status_label.setText("Ожидание вашего ответа...")
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #e3f2fd;
                color: #1976d2;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        
        self.opponent_status.setText("Соперник думает...")
        self.opponent_status.setStyleSheet("""
            QLabel {
                background-color: #fff3e0;
                color: #f57c00;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        
        # Разблокируем кнопки
        self.cooperate_btn.setEnabled(True)
        self.betray_btn.setEnabled(True)
    
    def complete_game(self):
        """Завершение игры"""
        self.listener.stop()
        self.game_completed.emit()
    
    def ping(self):
        """Поддержание онлайн статуса"""
        self.db.ping_player(self.player_id)
    
    def closeEvent(self, event):
        """Очистка при закрытии"""
        try:
            self.listener.stop()
            self.listener.wait()
        except:
            pass
        event.accept()
