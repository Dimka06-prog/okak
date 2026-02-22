"""
Базовый класс для всех представлений
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal
from typing import Optional, Dict, Any
import logging

from ..styles import StyleManager
from ...utils.ui_helpers import UIHelper, ValidationHelper, AnimationHelper

logger = logging.getLogger(__name__)

class BaseView(QWidget):
    """Базовый класс для всех представлений с общим функционалом"""
    
    # Общие сигналы
    error_occurred = pyqtSignal(str)
    success_message = pyqtSignal(str)
    warning_message = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.style_manager = StyleManager()
        self.ui_helper = UIHelper()
        self.validation_helper = ValidationHelper()
        self.animation_helper = AnimationHelper()
        
        # Применяем базовые стили
        self.setStyleSheet(self.style_manager.get_main_window_style())
        
        # Подключаем сигналы
        self._connect_signals()
    
    def _connect_signals(self):
        """Подключить общие сигналы"""
        self.error_occurred.connect(self.show_error)
        self.success_message.connect(self.show_success)
        self.warning_message.connect(self.show_warning)
    
    def show_error(self, message: str):
        """Показать сообщение об ошибке"""
        self.ui_helper.show_message_box(
            "❌ Ошибка", 
            message, 
            'error', 
            parent=self, 
            style_manager=self.style_manager
        )
    
    def show_success(self, message: str):
        """Показать сообщение об успехе"""
        self.ui_helper.show_message_box(
            "✅ Успех", 
            message, 
            'info', 
            parent=self, 
            style_manager=self.style_manager
        )
    
    def show_warning(self, message: str):
        """Показать предупреждение"""
        self.ui_helper.show_message_box(
            "⚠️ Предупреждение", 
            message, 
            'warning', 
            parent=self, 
            style_manager=self.style_manager
        )
    
    def show_info(self, message: str):
        """Показать информационное сообщение"""
        self.ui_helper.show_message_box(
            "ℹ️ Информация", 
            message, 
            'info', 
            parent=self, 
            style_manager=self.style_manager
        )
    
    def validate_field(self, field_value: str, field_type: str) -> tuple[bool, Optional[str]]:
        """Валидировать поле"""
        if field_type == 'username':
            return self.validation_helper.validate_username(field_value)
        elif field_type == 'password':
            return self.validation_helper.validate_password(field_value)
        elif field_type == 'email':
            return self.validation_helper.validate_email(field_value)
        else:
            return True, None
    
    def set_loading_state(self, loading: bool):
        """Установить состояние загрузки (переопределяется в наследниках)"""
        pass
    
    def reset_form(self):
        """Сбросить форму (переопределяется в наследниках)"""
        pass
    
    def cleanup(self):
        """Очистка ресурсов (переопределяется в наследниках)"""
        try:
            # Отключаем сигналы
            self.error_occurred.disconnect()
            self.success_message.disconnect()
            self.warning_message.disconnect()
        except:
            pass
    
    def emit_error(self, message: str):
        """Отправить сигнал об ошибке"""
        logger.error(f"View error: {message}")
        self.error_occurred.emit(message)
    
    def emit_success(self, message: str):
        """Отправить сигнал об успехе"""
        logger.info(f"View success: {message}")
        self.success_message.emit(message)
    
    def emit_warning(self, message: str):
        """Отправить сигнал предупреждения"""
        logger.warning(f"View warning: {message}")
        self.warning_message.emit(message)

class FormView(BaseView):
    """Базовый класс для представлений с формами"""
    
    def __init__(self):
        super().__init__()
        self.form_fields = {}
        self.validation_rules = {}
    
    def add_form_field(self, field_name: str, widget, validation_type: Optional[str] = None):
        """Добавить поле формы"""
        self.form_fields[field_name] = {
            'widget': widget,
            'validation_type': validation_type
        }
        
        if validation_type:
            widget.textChanged.connect(lambda: self._validate_field_on_change(field_name))
    
    def _validate_field_on_change(self, field_name: str):
        """Валидация поля при изменении"""
        field_data = self.form_fields.get(field_name)
        if not field_data:
            return
        
        widget = field_data['widget']
        validation_type = field_data['validation_type']
        
        if validation_type:
            is_valid, error_message = self.validate_field(widget.text(), validation_type)
            
            if widget.text():  # Применяем стили только если поле не пустое
                if is_valid:
                    widget.setStyleSheet(self.style_manager.get_input_style('focus'))
                else:
                    widget.setStyleSheet(f"""
                        QLineEdit {{
                            border: 2px solid {self.style_manager.COLORS['danger']};
                            border-radius: {self.style_manager.SIZES['border_radius_small']};
                            padding: {self.style_manager.SIZES['padding_medium']};
                            background-color: {self.style_manager.COLORS['background']};
                        }}
                    """)
    
    def validate_form(self) -> tuple[bool, Dict[str, str]]:
        """Валидировать всю форму"""
        errors = {}
        is_valid = True
        
        for field_name, field_data in self.form_fields.items():
            widget = field_data['widget']
            validation_type = field_data['validation_type']
            
            if validation_type:
                field_is_valid, error_message = self.validate_field(widget.text(), validation_type)
                
                if not field_is_valid:
                    errors[field_name] = error_message
                    is_valid = False
        
        return is_valid, errors
    
    def get_form_data(self) -> Dict[str, str]:
        """Получить данные формы"""
        data = {}
        for field_name, field_data in self.form_fields.items():
            widget = field_data['widget']
            data[field_name] = widget.text().strip()
        return data
    
    def clear_form(self):
        """Очистить все поля формы"""
        for field_name, field_data in self.form_fields.items():
            widget = field_data['widget']
            widget.clear()
            widget.setStyleSheet(self.style_manager.get_input_style())
    
    def focus_first_field(self):
        """Установить фокус на первое поле"""
        if self.form_fields:
            first_field = list(self.form_fields.values())[0]['widget']
            first_field.setFocus()
