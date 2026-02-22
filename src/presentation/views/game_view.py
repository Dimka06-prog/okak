"""
Интерфейс игры с кнопками Предать/Сотрудничать
"""
from typing import Dict
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QMessageBox, QFrame, QProgressBar,
                            QTextEdit, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPixmap, QPalette, QColor
from ..styles import StyleManager
from ...business.services.game_service import AnswerType
import asyncio

class GameView(QWidget):
    """Интерфейс игры с реальным временем"""
    
    # Сигналы
    answer_submitted = pyqtSignal(str, int, int, str)  # game_id, round, question, answer
    game_finished = pyqtSignal(str)  # game_id
    back_to_menu = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.style_manager = StyleManager()
        self.current_game_id = None
        self.current_round = 1
        self.current_question = 1
        self.player_id = None
        self.opponent_name = "Ожидание соперника..."
        self.waiting_for_opponent = False
        self.answers_shown = False
        
        self.setup_ui()
        self.setup_animations()
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setWindowTitle("Игра - Предать или Сотрудничать")
        self.setMinimumSize(800, 600)
        
        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок игры
        self.setup_header(main_layout)
        
        # Информация об игроках
        self.setup_players_info(main_layout)
        
        # Прогресс раунда
        self.setup_progress(main_layout)
        
        # Область вопроса
        self.setup_question_area(main_layout)
        
        # Кнопки ответов
        self.setup_answer_buttons(main_layout)
        
        # Область результатов
        self.setup_results_area(main_layout)
        
        # Кнопка управления
        self.setup_control_buttons(main_layout)
        
        self.setLayout(main_layout)
        self.apply_styles()
        
    def setup_header(self, layout):
        """Настройка заголовка"""
        header_layout = QHBoxLayout()
        
        self.game_title = QLabel("🎮 Игра: Предать или Сотрудничать")
        self.game_title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.game_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header_layout.addWidget(self.game_title)
        layout.addLayout(header_layout)
        
    def setup_players_info(self, layout):
        """Настройка информации об игроках"""
        players_frame = QFrame()
        players_frame.setFrameStyle(QFrame.Shape.Box)
        players_layout = QHBoxLayout(players_frame)
        
        # Информация о текущем игроке
        player_frame = QFrame()
        player_frame.setStyleSheet(self.style_manager.get_player_card_style())
        player_layout = QVBoxLayout(player_frame)
        
        self.player_label = QLabel("Вы")
        self.player_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.player_score_label = QLabel("Очки: 0")
        self.player_status_label = QLabel("Готов")
        
        player_layout.addWidget(self.player_label)
        player_layout.addWidget(self.player_score_label)
        player_layout.addWidget(self.player_status_label)
        
        # VS разделитель
        vs_label = QLabel("VS")
        vs_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        vs_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vs_label.setStyleSheet("color: #ff6b6b; padding: 0 20px;")
        
        # Информация о противнике
        opponent_frame = QFrame()
        opponent_frame.setStyleSheet(self.style_manager.get_opponent_card_style())
        opponent_layout = QVBoxLayout(opponent_frame)
        
        self.opponent_label = QLabel("Соперник")
        self.opponent_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.opponent_name_label = QLabel(self.opponent_name)
        self.opponent_score_label = QLabel("Очки: 0")
        self.opponent_status_label = QLabel("Ожидание...")
        
        opponent_layout.addWidget(self.opponent_label)
        opponent_layout.addWidget(self.opponent_name_label)
        opponent_layout.addWidget(self.opponent_score_label)
        opponent_layout.addWidget(self.opponent_status_label)
        
        players_layout.addWidget(player_frame)
        players_layout.addWidget(vs_label)
        players_layout.addWidget(opponent_frame)
        
        layout.addWidget(players_frame)
        
    def setup_progress(self, layout):
        """Настройка прогресса игры"""
        progress_frame = QFrame()
        progress_layout = QVBoxLayout(progress_frame)
        
        # Прогресс раунда
        round_label = QLabel(f"Раунд {self.current_round}/3")
        round_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        round_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.round_progress = QProgressBar()
        self.round_progress.setRange(0, 3)
        self.round_progress.setValue(self.current_round)
        self.round_progress.setStyleSheet(self.style_manager.get_progress_style())
        
        # Прогресс вопросов
        questions_label = QLabel(f"Вопрос {self.current_question}")
        questions_label.setFont(QFont("Arial", 10))
        questions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.question_progress = QProgressBar()
        total_questions = 10 if self.current_round < 3 else 13
        self.question_progress.setRange(0, total_questions)
        self.question_progress.setValue(self.current_question)
        self.question_progress.setStyleSheet(self.style_manager.get_progress_style())
        
        progress_layout.addWidget(round_label)
        progress_layout.addWidget(self.round_progress)
        progress_layout.addWidget(questions_label)
        progress_layout.addWidget(self.question_progress)
        
        layout.addWidget(progress_frame)
        
    def setup_question_area(self, layout):
        """Настройка области вопроса"""
        question_frame = QFrame()
        question_frame.setFrameStyle(QFrame.Shape.Box)
        question_layout = QVBoxLayout(question_frame)
        
        self.question_number_label = QLabel(f"Вопрос {self.current_question}")
        self.question_number_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        
        self.question_text = QTextEdit()
        self.question_text.setReadOnly(True)
        self.question_text.setMaximumHeight(120)
        self.question_text.setFont(QFont("Arial", 11))
        
        self.context_label = QLabel("Контекст:")
        self.context_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        self.context_text = QTextEdit()
        self.context_text.setReadOnly(True)
        self.context_text.setMaximumHeight(80)
        self.context_text.setFont(QFont("Arial", 10))
        
        question_layout.addWidget(self.question_number_label)
        question_layout.addWidget(self.question_text)
        question_layout.addWidget(self.context_label)
        question_layout.addWidget(self.context_text)
        
        layout.addWidget(question_frame)
        
    def setup_answer_buttons(self, layout):
        """Настройка кнопок ответов"""
        buttons_layout = QHBoxLayout()
        
        self.cooperate_button = QPushButton("🤝 СОТРУДНИЧАТЬ")
        self.cooperate_button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.cooperate_button.setMinimumHeight(60)
        self.cooperate_button.clicked.connect(lambda: self.submit_answer(AnswerType.COOPERATE))
        
        self.betray_button = QPushButton("🗡️ ПРЕДАТЬ")
        self.betray_button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.betray_button.setMinimumHeight(60)
        self.betray_button.clicked.connect(lambda: self.submit_answer(AnswerType.BETRAY))
        
        buttons_layout.addWidget(self.cooperate_button)
        buttons_layout.addWidget(self.betray_button)
        
        layout.addLayout(buttons_layout)
        
    def setup_results_area(self, layout):
        """Настройка области результатов"""
        results_frame = QFrame()
        results_frame.setFrameStyle(QFrame.Shape.Box)
        results_layout = QVBoxLayout(results_frame)
        
        self.results_title = QLabel("Результаты ответа:")
        self.results_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.results_title.hide()
        
        self.your_answer_label = QLabel("Ваш ответ: -")
        self.your_answer_label.setFont(QFont("Arial", 11))
        self.your_answer_label.hide()
        
        self.opponent_answer_label = QLabel("Ответ соперника: -")
        self.opponent_answer_label.setFont(QFont("Arial", 11))
        self.opponent_answer_label.hide()
        
        self.scores_label = QLabel("Полученные очки: Вы: 0, Соперник: 0")
        self.scores_label.setFont(QFont("Arial", 11))
        self.scores_label.hide()
        
        results_layout.addWidget(self.results_title)
        results_layout.addWidget(self.your_answer_label)
        results_layout.addWidget(self.opponent_answer_label)
        results_layout.addWidget(self.scores_label)
        
        layout.addWidget(results_frame)
        
    def setup_control_buttons(self, layout):
        """Настройка кнопок управления"""
        control_layout = QHBoxLayout()
        
        self.back_button = QPushButton("🔙 В меню")
        self.back_button.setFont(QFont("Arial", 10))
        self.back_button.clicked.connect(self.back_to_menu.emit)
        
        self.next_button = QPushButton("➡️ Дальше")
        self.next_button.setFont(QFont("Arial", 10))
        self.next_button.clicked.connect(self.next_question)
        self.next_button.hide()
        
        control_layout.addWidget(self.back_button)
        control_layout.addStretch()
        control_layout.addWidget(self.next_button)
        
        layout.addLayout(control_layout)
        
    def setup_animations(self):
        """Настройка анимаций"""
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
    def apply_styles(self):
        """Применение стилей"""
        self.setStyleSheet(self.style_manager.get_game_view_style())
        
        # Стили кнопок
        self.cooperate_button.setStyleSheet(self.style_manager.get_cooperate_button_style())
        self.betray_button.setStyleSheet(self.style_manager.get_betray_button_style())
        self.back_button.setStyleSheet(self.style_manager.get_secondary_button_style())
        self.next_button.setStyleSheet(self.style_manager.get_primary_button_style())
        
    def start_game(self, game_id: str, player_id: str, opponent_name: str):
        """Начать игру"""
        self.current_game_id = game_id
        self.player_id = player_id
        self.opponent_name = opponent_name
        self.current_round = 1
        self.current_question = 1
        self.waiting_for_opponent = False
        self.answers_shown = False
        
        self.opponent_name_label.setText(opponent_name)
        self.opponent_status_label.setText("В игре")
        
        self.update_progress()
        self.enable_answer_buttons()
        
    def update_progress(self):
        """Обновить прогресс"""
        self.round_progress.setValue(self.current_round)
        
        total_questions = 10 if self.current_round < 3 else 13
        self.question_progress.setRange(0, total_questions)
        self.question_progress.setValue(self.current_question)
        
        self.question_number_label.setText(f"Вопрос {self.current_question}/{total_questions}")
        
    def show_question(self, question_data: Dict):
        """Показать вопрос"""
        self.question_text.setPlainText(question_data.get('text', ''))
        self.context_text.setPlainText(question_data.get('context', ''))
        
        # Скрываем результаты предыдущего ответа
        self.hide_results()
        self.enable_answer_buttons()
        self.waiting_for_opponent = False
        
    def submit_answer(self, answer: AnswerType):
        """Отправить ответ"""
        if not self.current_game_id or self.waiting_for_opponent:
            return
            
        self.waiting_for_opponent = True
        self.disable_answer_buttons()
        
        # Отправляем ответ
        self.answer_submitted.emit(
            self.current_game_id,
            self.current_round,
            self.current_question,
            answer.value
        )
        
        # Показываем статус ожидания
        self.opponent_status_label.setText("Обдумывает...")
        
    def show_answer_results(self, your_answer: str, opponent_answer: str, your_score: int, opponent_score: int):
        """Показать результаты ответов"""
        self.answers_shown = True
        
        # Преобразуем ответы в читаемый вид
        answer_map = {
            'cooperate': '🤝 Сотрудничать',
            'betray': '🗡️ Предать'
        }
        
        your_answer_text = answer_map.get(your_answer, your_answer)
        opponent_answer_text = answer_map.get(opponent_answer, opponent_answer)
        
        # Показываем результаты
        self.results_title.show()
        self.your_answer_label.setText(f"Ваш ответ: {your_answer_text}")
        self.your_answer_label.show()
        self.opponent_answer_label.setText(f"Ответ соперника: {opponent_answer_text}")
        self.opponent_answer_label.show()
        self.scores_label.setText(f"Полученные очки: Вы: {your_score}, Соперник: {opponent_score}")
        self.scores_label.show()
        
        # Обновляем общие очки
        current_scores = self.player_score_label.text().split(": ")[1]
        try:
            current_score = int(current_scores)
            new_score = current_score + your_score
            self.player_score_label.setText(f"Очки: {new_score}")
        except:
            pass
            
        self.opponent_status_label.setText("Ответил")
        
        # Показываем кнопку "Дальше"
        self.next_button.show()
        
    def hide_results(self):
        """Скрыть результаты"""
        self.results_title.hide()
        self.your_answer_label.hide()
        self.opponent_answer_label.hide()
        self.scores_label.hide()
        self.next_button.hide()
        
    def next_question(self):
        """Перейти к следующему вопросу"""
        total_questions = 10 if self.current_round < 3 else 13
        
        if self.current_question < total_questions:
            self.current_question += 1
            self.update_progress()
            self.hide_results()
            self.enable_answer_buttons()
            self.waiting_for_opponent = False
            
            # Запрос следующего вопроса
            # Здесь будет сигнал для контроллера
        else:
            # Раунд завершен
            self.next_round()
            
    def next_round(self):
        """Перейти к следующему раунду"""
        if self.current_round < 3:
            self.current_round += 1
            self.current_question = 1
            self.update_progress()
            self.hide_results()
            self.enable_answer_buttons()
            self.waiting_for_opponent = False
            
            # Запрос первого вопроса нового раунда
            # Здесь будет сигнал для контроллера
        else:
            # Игра завершена
            self.finish_game()
            
    def finish_game(self):
        """Завершить игру"""
        self.game_finished.emit(self.current_game_id)
        
    def enable_answer_buttons(self):
        """Включить кнопки ответов"""
        self.cooperate_button.setEnabled(True)
        self.betray_button.setEnabled(True)
        
    def disable_answer_buttons(self):
        """Выключить кнопки ответов"""
        self.cooperate_button.setEnabled(False)
        self.betray_button.setEnabled(False)
        
    def update_opponent_status(self, status: str):
        """Обновить статус соперника"""
        self.opponent_status_label.setText(status)
