"""
Утилиты для работы с UI
"""
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QTimer
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)

class UIHelper:
    """Вспомогательные методы для работы с UI"""
    
    @staticmethod
    def show_message_box(title: str, message: str, icon_type: str = 'info', 
                        parent=None, style_manager=None) -> None:
        """Показать стандартное сообщение"""
        icons = {
            'info': QMessageBox.Icon.Information,
            'warning': QMessageBox.Icon.Warning,
            'error': QMessageBox.Icon.Critical,
            'question': QMessageBox.Icon.Question
        }
        
        icon = icons.get(icon_type, QMessageBox.Icon.Information)
        
        msg_box = QMessageBox(icon, title, message, parent=parent)
        
        if style_manager:
            msg_box.setStyleSheet(f"""
                QMessageBox {{
                    background-color: {style_manager.COLORS['background']};
                    color: {style_manager.COLORS['text_primary']};
                    font-family: {style_manager.FONTS['primary']};
                }}
                QMessageBox QLabel {{
                    color: {style_manager.COLORS['text_primary']};
                    font-size: {style_manager.SIZES['font_size_medium']};
                }}
                QPushButton {{
                    {style_manager.get_button_style('primary', 'medium')}
                }}
            """)
        
        msg_box.exec()
    
    @staticmethod
    def delayed_callback(callback: Callable, delay_ms: int = 100) -> None:
        """Выполнить callback с задержкой"""
        QTimer.singleShot(delay_ms, callback)
    
    @staticmethod
    def safe_connect(signal, slot) -> bool:
        """Безопасное подключение сигнала к слоту"""
        try:
            signal.connect(slot)
            return True
        except Exception as e:
            logger.error(f"Ошибка подключения сигнала: {e}")
            return False
    
    @staticmethod
    def safe_disconnect(signal, slot) -> bool:
        """Безопасное отключение сигнала от слота"""
        try:
            signal.disconnect(slot)
            return True
        except Exception as e:
            logger.error(f"Ошибка отключения сигнала: {e}")
            return False

class ValidationHelper:
    """Вспомогательные методы для валидации"""
    
    @staticmethod
    def validate_username(username: str) -> tuple[bool, Optional[str]]:
        """Валидация имени пользователя"""
        if not username:
            return False, "Имя пользователя не может быть пустым"
        
        if len(username) < 3:
            return False, "Имя пользователя должно содержать минимум 3 символа"
        
        if len(username) > 20:
            return False, "Имя пользователя должно содержать не более 20 символов"
        
        # Проверка допустимых символов
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
        if not all(c in allowed_chars for c in username):
            return False, "Имя пользователя может содержать только буквы, цифры, _ и -"
        
        return True, None
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, Optional[str]]:
        """Валидация пароля"""
        if not password:
            return False, "Пароль не может быть пустым"
        
        if len(password) < 6:
            return False, "Пароль должен содержать минимум 6 символов"
        
        return True, None
    
    @staticmethod
    def validate_email(email: str) -> tuple[bool, Optional[str]]:
        """Валидация email"""
        if not email:
            return False, "Email не может быть пустым"
        
        if '@' not in email or '.' not in email:
            return False, "Неверный формат email"
        
        return True, None

class AnimationHelper:
    """Вспомогательные методы для анимаций"""
    
    @staticmethod
    def fade_in_widget(widget, duration_ms: int = 300):
        """Анимация появления виджета"""
        from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
        
        widget.setWindowOpacity(0.0)
        widget.show()
        
        animation = QPropertyAnimation(widget, b"windowOpacity")
        animation.setDuration(duration_ms)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()
    
    @staticmethod
    def fade_out_widget(widget, duration_ms: int = 300, callback=None):
        """Анимация исчезновения виджета"""
        from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
        
        animation = QPropertyAnimation(widget, b"windowOpacity")
        animation.setDuration(duration_ms)
        animation.setStartValue(1.0)
        animation.setEndValue(0.0)
        animation.setEasingCurve(QEasingCurve.Type.InCubic)
        
        if callback:
            animation.finished.connect(callback)
        
        animation.start()

class ThemeHelper:
    """Вспомогательные методы для тем"""
    
    @staticmethod
    def get_system_theme() -> str:
        """Получить системную тему"""
        import sys
        if sys.platform == 'win32':
            import winreg
            try:
                registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                key = winreg.OpenKey(registry, r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize')
                value, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
                winreg.CloseKey(key)
                return 'light' if value == 1 else 'dark'
            except:
                pass
        elif sys.platform == 'darwin':
            # macOS
            import subprocess
            try:
                result = subprocess.run(['defaults', 'read', '-g', 'AppleInterfaceStyle'], 
                                      capture_output=True, text=True)
                return 'dark' if 'Dark' in result.stdout else 'light'
            except:
                pass
        
        return 'light'  # По умолчанию
    
    @staticmethod
    def apply_system_theme(style_manager) -> None:
        """Применить системную тему"""
        theme = ThemeHelper.get_system_theme()
        if theme == 'dark':
            # Темная тема
            style_manager.COLORS.update({
                'background': '#1e1e1e',
                'surface': '#2d2d2d',
                'card': '#252526',
                'border': '#3e3e42',
                'text_primary': '#ffffff',
                'text_secondary': '#cccccc',
                'text_muted': '#969696',
            })
        else:
            # Светлая тема (уже установлена по умолчанию)
            pass
