"""
Представление для окна входа и регистрации с улучшенным UI
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox, QFrame,
                            QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPixmap
from ..styles import StyleManager

class LoginView(QWidget):
    """Представление для входа и регистрации с улучшенным дизайном"""
    
    # Сигналы
    register_requested = pyqtSignal(str, str)  # username, password
    login_requested = pyqtSignal(str, str)     # username, password
    
    def __init__(self):
        super().__init__()
        self.style_manager = StyleManager()
        self.init_ui()
        self.apply_styles()
        
    def init_ui(self):
        # Основной контейнер с прокруткой для адаптивности
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Заголовок приложения
        self._create_header(layout)
        
        # Основная карточка с формами
        self._create_main_card(layout)
        
        # Футер
        self._create_footer(layout)
        
        scroll_area.setWidget(main_widget)
        
        # Основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        
        # Применяем стиль главного окна
        self.setStyleSheet(self.style_manager.get_main_window_style())
    
    def _create_header(self, layout):
        """Создать заголовок"""
        header_layout = QVBoxLayout()
        header_layout.setSpacing(10)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Иконка или логотип
        icon_label = QLabel("🎮")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.style_manager.apply_font(icon_label, 'xxlarge')
        header_layout.addWidget(icon_label)
        
        # Заголовок
        title = QLabel("Предать или Сотрудничать")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(self.style_manager.get_title_style('xlarge'))
        header_layout.addWidget(title)
        
        # Подзаголовок
        subtitle = QLabel("Многопользовательская игра на основе дилеммы заключенного")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(self.style_manager.get_label_style('secondary'))
        self.style_manager.apply_font(subtitle, 'small')
        header_layout.addWidget(subtitle)
        
        layout.addLayout(header_layout)
    
    def _create_main_card(self, layout):
        """Создать основную карточку с формами"""
        card = QFrame()
        card.setStyleSheet(self.style_manager.get_card_style())
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(30)
        
        # Форма регистрации
        self._create_registration_form(card_layout)
        
        # Разделитель
        self._create_separator(card_layout)
        
        # Форма входа
        self._create_login_form(card_layout)
        
        layout.addWidget(card)
    
    def _create_registration_form(self, layout):
        """Создать форму регистрации"""
        reg_layout = QVBoxLayout()
        reg_layout.setSpacing(15)
        
        # Заголовок формы
        reg_title = QLabel("📝 Регистрация")
        reg_title.setStyleSheet(self.style_manager.get_title_style('large'))
        reg_layout.addWidget(reg_title)
        
        # Поля ввода
        self.reg_username = QLineEdit()
        self.reg_username.setPlaceholderText("Имя пользователя (3-20 символов)")
        self.reg_username.setStyleSheet(self.style_manager.get_input_style())
        reg_layout.addWidget(self.reg_username)
        
        self.reg_password = QLineEdit()
        self.reg_password.setPlaceholderText("Пароль (минимум 6 символов)")
        self.reg_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.reg_password.setStyleSheet(self.style_manager.get_input_style())
        reg_layout.addWidget(self.reg_password)
        
        # Подсказка
        hint_label = QLabel("💡 Используйте буквы, цифры, _ и -")
        hint_label.setStyleSheet(self.style_manager.get_label_style('muted'))
        self.style_manager.apply_font(hint_label, 'small')
        reg_layout.addWidget(hint_label)
        
        # Кнопка регистрации
        self.register_btn = QPushButton("✨ Зарегистрироваться")
        self.register_btn.clicked.connect(self._on_register_clicked)
        self.register_btn.setStyleSheet(self.style_manager.get_button_style('success', 'large'))
        self.register_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reg_layout.addWidget(self.register_btn)
        
        layout.addLayout(reg_layout)
    
    def _create_separator(self, layout):
        """Создать разделитель"""
        separator_layout = QHBoxLayout()
        separator_layout.setSpacing(10)
        
        left_line = QLabel()
        left_line.setStyleSheet(f"background-color: {StyleManager.COLORS['border']}; height: 1px;")
        left_line.setMaximumHeight(1)
        separator_layout.addWidget(left_line)
        
        separator_text = QLabel("ИЛИ")
        separator_text.setStyleSheet(self.style_manager.get_label_style('muted'))
        separator_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        separator_layout.addWidget(separator_text)
        
        right_line = QLabel()
        right_line.setStyleSheet(f"background-color: {StyleManager.COLORS['border']}; height: 1px;")
        right_line.setMaximumHeight(1)
        separator_layout.addWidget(right_line)
        
        layout.addLayout(separator_layout)
    
    def _create_login_form(self, layout):
        """Создать форму входа"""
        login_layout = QVBoxLayout()
        login_layout.setSpacing(15)
        
        # Заголовок формы
        login_title = QLabel("🔐 Вход")
        login_title.setStyleSheet(self.style_manager.get_title_style('large'))
        login_layout.addWidget(login_title)
        
        # Поля ввода
        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Имя пользователя")
        self.login_username.setStyleSheet(self.style_manager.get_input_style())
        login_layout.addWidget(self.login_username)
        
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Пароль")
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_password.setStyleSheet(self.style_manager.get_input_style())
        login_layout.addWidget(self.login_password)
        
        # Кнопка входа
        self.login_btn = QPushButton("🚀 Войти")
        self.login_btn.clicked.connect(self._on_login_clicked)
        self.login_btn.setStyleSheet(self.style_manager.get_button_style('primary', 'large'))
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_layout.addWidget(self.login_btn)
        
        layout.addLayout(login_layout)
    
    def _create_footer(self, layout):
        """Создать футер"""
        footer_layout = QVBoxLayout()
        footer_layout.setSpacing(10)
        footer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Информационный текст
        info_label = QLabel("Ваши данные надежно защищены и хешируются")
        info_label.setStyleSheet(self.style_manager.get_label_style('muted'))
        self.style_manager.apply_font(info_label, 'small')
        footer_layout.addWidget(info_label)
        
        version_label = QLabel("Версия 2.0.0")
        version_label.setStyleSheet(self.style_manager.get_label_style('muted'))
        self.style_manager.apply_font(version_label, 'small')
        footer_layout.addWidget(version_label)
        
        layout.addLayout(footer_layout)
    
    def apply_styles(self):
        """Применить дополнительные стили и анимации"""
        # Устанавливаем минимальную ширину для лучшего вида
        self.setMinimumWidth(500)
        
        # Применяем стили к полям при фокусе
        self.reg_username.textChanged.connect(lambda: self._update_input_style(self.reg_username))
        self.reg_password.textChanged.connect(lambda: self._update_input_style(self.reg_password))
        self.login_username.textChanged.connect(lambda: self._update_input_style(self.login_username))
        self.login_password.textChanged.connect(lambda: self._update_input_style(self.login_password))
    
    def _update_input_style(self, input_field):
        """Обновить стиль поля ввода при изменении текста"""
        if input_field.text():
            input_field.setStyleSheet(self.style_manager.get_input_style('focus'))
        else:
            input_field.setStyleSheet(self.style_manager.get_input_style())
    
    def _on_register_clicked(self):
        """Обработка клика по кнопке регистрации с анимацией"""
        self._animate_button(self.register_btn)
        
        username = self.reg_username.text().strip()
        password = self.reg_password.text().strip()
        
        if not username or not password:
            self.show_warning("⚠️ Заполните все поля!")
            return
        
        self.register_requested.emit(username, password)
    
    def _on_login_clicked(self):
        """Обработка клика по кнопке входа с анимацией"""
        self._animate_button(self.login_btn)
        
        username = self.login_username.text().strip()
        password = self.login_password.text().strip()
        
        if not username or not password:
            self.show_warning("⚠️ Заполните все поля!")
            return
        
        self.login_requested.emit(username, password)
    
    def _animate_button(self, button):
        """Анимация нажатия кнопки"""
        animation = QPropertyAnimation(button, b"geometry")
        animation.setDuration(100)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        original_geometry = button.geometry()
        smaller_geometry = button.geometry().adjusted(2, 2, -2, -2)
        
        animation.setStartValue(original_geometry)
        animation.setEndValue(smaller_geometry)
        animation.start()
        
        # Возвращаем исходный размер
        animation.finished.connect(lambda: self._restore_button_size(button, original_geometry))
    
    def _restore_button_size(self, button, geometry):
        """Восстановить размер кнопки"""
        button.setGeometry(geometry)
    
    def show_success(self, message: str):
        """Показать сообщение об успехе с улучшенным дизайном"""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle("✅ Успех")
        msg_box.setText(message)
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {StyleManager.COLORS['background']};
                color: {StyleManager.COLORS['text_primary']};
                font-family: {StyleManager.FONTS['primary']};
            }}
            QMessageBox QLabel {{
                color: {StyleManager.COLORS['text_primary']};
                font-size: {StyleManager.SIZES['font_size_medium']};
            }}
            QPushButton {{
                {self.style_manager.get_button_style('primary', 'medium')}
            }}
        """)
        msg_box.exec()
    
    def show_error(self, message: str):
        """Показать сообщение об ошибке с улучшенным дизайном"""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("❌ Ошибка")
        msg_box.setText(message)
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {StyleManager.COLORS['background']};
                color: {StyleManager.COLORS['text_primary']};
                font-family: {StyleManager.FONTS['primary']};
            }}
            QMessageBox QLabel {{
                color: {StyleManager.COLORS['text_primary']};
                font-size: {StyleManager.SIZES['font_size_medium']};
            }}
            QPushButton {{
                {self.style_manager.get_button_style('danger', 'medium')}
            }}
        """)
        msg_box.exec()
    
    def show_warning(self, message: str):
        """Показать предупреждение с улучшенным дизайном"""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("⚠️ Предупреждение")
        msg_box.setText(message)
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {StyleManager.COLORS['background']};
                color: {StyleManager.COLORS['text_primary']};
                font-family: {StyleManager.FONTS['primary']};
            }}
            QMessageBox QLabel {{
                color: {StyleManager.COLORS['text_primary']};
                font-size: {StyleManager.SIZES['font_size_medium']};
            }}
            QPushButton {{
                {self.style_manager.get_button_style('warning', 'medium')}
            }}
        """)
        msg_box.exec()
    
    def clear_fields(self):
        """Очистить все поля с анимацией"""
        self.reg_username.clear()
        self.reg_password.clear()
        self.login_username.clear()
        self.login_password.clear()
        
        # Сбрасываем стили полей
        self.reg_username.setStyleSheet(self.style_manager.get_input_style())
        self.reg_password.setStyleSheet(self.style_manager.get_input_style())
        self.login_username.setStyleSheet(self.style_manager.get_input_style())
        self.login_password.setStyleSheet(self.style_manager.get_input_style())
    
    def set_loading(self, loading: bool):
        """Установить состояние загрузки"""
        self.register_btn.setEnabled(not loading)
        self.login_btn.setEnabled(not loading)
        
        if loading:
            self.register_btn.setText("⏳ Регистрация...")
            self.login_btn.setText("⏳ Вход...")
        else:
            self.register_btn.setText("✨ Зарегистрироваться")
            self.login_btn.setText("🚀 Войти")
