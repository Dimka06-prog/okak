"""
Централизованный менеджер стилей для UI компонентов
"""

class StyleManager:
    """Менеджер стилей для приложения"""
    
    # Цветовая схема
    COLORS = {
        'primary': '#2196F3',        # Синий
        'primary_dark': '#1976D2',   # Темно-синий
        'success': '#4CAF50',        # Зеленый
        'success_dark': '#45a049',   # Темно-зеленый
        'warning': '#FF9800',        # Оранжевый
        'warning_dark': '#F57C00',   # Темно-оранжевый
        'danger': '#f44336',         # Красный
        'danger_dark': '#da190b',    # Темно-красный
        'info': '#00BCD4',           # Голубой
        'info_dark': '#0097A7',      # Темно-голубой
        
        'background': '#ffffff',     # Белый
        'surface': '#f8f9fa',        # Светло-серый
        'card': '#ffffff',           # Белый для карточек
        'border': '#dee2e6',         # Границы
        'text_primary': '#212529',   # Основной текст
        'text_secondary': '#6c757d', # Вторичный текст
        'text_muted': '#adb5bd',     # Приглушенный текст
        'shadow': 'rgba(0, 0, 0, 0.1)', # Тень
    }
    
    # Размеры
    SIZES = {
        'border_radius': '8px',
        'border_radius_small': '4px',
        'border_radius_large': '12px',
        'padding_small': '8px',
        'padding_medium': '12px',
        'padding_large': '16px',
        'padding_xlarge': '24px',
        'margin_small': '4px',
        'margin_medium': '8px',
        'margin_large': '16px',
        'font_size_small': '12px',
        'font_size_medium': '14px',
        'font_size_large': '16px',
        'font_size_xlarge': '18px',
        'font_size_xxlarge': '24px',
    }
    
    # Шрифты
    FONTS = {
        'primary': 'Arial, Helvetica, sans-serif',
        'secondary': 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif',
    }
    
    @classmethod
    def get_button_style(cls, variant: str = 'primary', size: str = 'medium') -> str:
        """Получить стиль кнопки"""
        colors = {
            'primary': (cls.COLORS['primary'], cls.COLORS['primary_dark']),
            'success': (cls.COLORS['success'], cls.COLORS['success_dark']),
            'warning': (cls.COLORS['warning'], cls.COLORS['warning_dark']),
            'danger': (cls.COLORS['danger'], cls.COLORS['danger_dark']),
            'info': (cls.COLORS['info'], cls.COLORS['info_dark']),
        }
        
        sizes = {
            'small': (cls.SIZES['padding_small'], cls.SIZES['font_size_small']),
            'medium': (cls.SIZES['padding_medium'], cls.SIZES['font_size_medium']),
            'large': (cls.SIZES['padding_large'], cls.SIZES['font_size_large']),
        }
        
        bg_color, hover_color = colors.get(variant, colors['primary'])
        padding, font_size = sizes.get(size, sizes['medium'])
        
        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border: none;
                border-radius: {cls.SIZES['border_radius']};
                padding: {padding} {cls.SIZES['padding_large']};
                font-size: {font_size};
                font-weight: bold;
                font-family: {cls.FONTS['primary']};
                min-height: 20px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {hover_color};
                transform: translateY(1px);
            }}
            QPushButton:disabled {{
                background-color: {cls.COLORS['text_muted']};
                color: {cls.COLORS['text_secondary']};
            }}
        """
    
    @classmethod
    def get_input_style(cls, state: str = 'normal') -> str:
        """Получить стиль поля ввода"""
        border_color = cls.COLORS['primary'] if state == 'focus' else cls.COLORS['border']
        border_width = '2px' if state == 'focus' else '1px'
        
        return f"""
            QLineEdit {{
                border: {border_width} solid {border_color};
                border-radius: {cls.SIZES['border_radius_small']};
                padding: {cls.SIZES['padding_medium']};
                font-size: {cls.SIZES['font_size_medium']};
                font-family: {cls.FONTS['primary']};
                background-color: {cls.COLORS['background']};
                color: {cls.COLORS['text_primary']};
                selection-background-color: {cls.COLORS['primary']};
            }}
            QLineEdit:focus {{
                border: 2px solid {cls.COLORS['primary']};
                outline: none;
            }}
            QLineEdit::placeholder {{
                color: {cls.COLORS['text_muted']};
            }}
        """
    
    @classmethod
    def get_card_style(cls) -> str:
        """Получить стиль карточки"""
        return f"""
            QFrame {{
                background-color: {cls.COLORS['card']};
                border: 1px solid {cls.COLORS['border']};
                border-radius: {cls.SIZES['border_radius_large']};
                padding: {cls.SIZES['padding_xlarge']};
            }}
        """
    
    @classmethod
    def get_title_style(cls, size: str = 'large') -> str:
        """Получить стиль заголовка"""
        sizes = {
            'small': cls.SIZES['font_size_medium'],
            'medium': cls.SIZES['font_size_large'],
            'large': cls.SIZES['font_size_xlarge'],
            'xlarge': cls.SIZES['font_size_xxlarge'],
        }
        
        font_size = sizes.get(size, sizes['large'])
        
        return f"""
            color: {cls.COLORS['text_primary']};
            font-size: {font_size};
            font-weight: bold;
            font-family: {cls.FONTS['primary']};
            margin: 0px;
            padding: 0px;
        """
    
    @classmethod
    def get_label_style(cls, variant: str = 'primary') -> str:
        """Получить стиль текста"""
        colors = {
            'primary': cls.COLORS['text_primary'],
            'secondary': cls.COLORS['text_secondary'],
            'muted': cls.COLORS['text_muted'],
            'success': cls.COLORS['success'],
            'warning': cls.COLORS['warning'],
            'danger': cls.COLORS['danger'],
            'info': cls.COLORS['info'],
        }
        
        color = colors.get(variant, colors['primary'])
        
        return f"""
            color: {color};
            font-size: {cls.SIZES['font_size_medium']};
            font-family: {cls.FONTS['primary']};
            background-color: transparent;
            border: none;
        """
    
    @classmethod
    def get_status_box_style(cls, status: str = 'info') -> str:
        """Получить стиль блока статуса"""
        colors = {
            'success': (cls.COLORS['success'], '#d4edda'),
            'warning': (cls.COLORS['warning'], '#fff3cd'),
            'danger': (cls.COLORS['danger'], '#f8d7da'),
            'info': (cls.COLORS['info'], '#d1ecf1'),
        }
        
        text_color, bg_color = colors.get(status, colors['info'])
        
        return f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {text_color};
                border-radius: {cls.SIZES['border_radius_small']};
                padding: {cls.SIZES['padding_small']} {cls.SIZES['padding_medium']};
                font-size: {cls.SIZES['font_size_small']};
                font-weight: bold;
                font-family: {cls.FONTS['primary']};
            }}
        """
    
    @classmethod
    def get_button_style(cls, variant: str = 'primary', size: str = 'medium') -> str:
        """Универсальный метод получения стиля кнопки"""
        size_map = {
            'small': {'padding': f"{cls.SIZES['padding_small']} {cls.SIZES['padding_medium']}", 'font_size': cls.SIZES['font_size_small']},
            'medium': {'padding': f"{cls.SIZES['padding_medium']} {cls.SIZES['padding_large']}", 'font_size': cls.SIZES['font_size_medium']},
            'large': {'padding': f"{cls.SIZES['padding_large']} {cls.SIZES['padding_xlarge']}", 'font_size': cls.SIZES['font_size_large']}
        }
        
        variant_map = {
            'primary': {
                'bg': cls.COLORS['primary'],
                'bg_dark': cls.COLORS['primary_dark'],
                'border': 'none'
            },
            'success': {
                'bg': cls.COLORS['success'],
                'bg_dark': cls.COLORS['success_dark'],
                'border': 'none'
            },
            'warning': {
                'bg': cls.COLORS['warning'],
                'bg_dark': cls.COLORS['warning_dark'],
                'border': 'none'
            },
            'danger': {
                'bg': cls.COLORS['danger'],
                'bg_dark': cls.COLORS['danger_dark'],
                'border': 'none'
            },
            'info': {
                'bg': cls.COLORS['info'],
                'bg_dark': cls.COLORS['info_dark'],
                'border': f"1px solid {cls.COLORS['info_dark']}"
            }
        }
        
        size_config = size_map.get(size, size_map['medium'])
        variant_config = variant_map.get(variant, variant_map['primary'])
        
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {variant_config['bg']}, stop:1 {variant_config['bg_dark']});
                border: {variant_config['border']};
                border-radius: {cls.SIZES['border_radius']};
                padding: {size_config['padding']};
                color: white;
                font-weight: bold;
                font-size: {size_config['font_size']};
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {variant_config['bg_dark']}, stop:1 {variant_config['bg']});
            }}
            QPushButton:pressed {{
                background: {variant_config['bg_dark']};
            }}
            QPushButton:disabled {{
                background: {cls.COLORS['text_muted']};
                color: {cls.COLORS['text_secondary']};
            }}
        """

    @classmethod
    def get_game_view_style(cls) -> str:
        """Получить стиль игрового интерфейса"""
        return f"""
            QWidget {{
                background-color: {cls.COLORS['background']};
                color: {cls.COLORS['text_primary']};
                font-family: {cls.FONTS['primary']};
            }}
            QFrame[frameShape="1"] {{
                border: 2px solid {cls.COLORS['border']};
                border-radius: {cls.SIZES['border_radius']};
                background-color: {cls.COLORS['card']};
                padding: {cls.SIZES['padding_medium']};
            }}
            QTextEdit {{
                border: 1px solid {cls.COLORS['border']};
                border-radius: {cls.SIZES['border_radius_small']};
                padding: {cls.SIZES['padding_medium']};
                background-color: {cls.COLORS['surface']};
                color: {cls.COLORS['text_primary']};
                font-size: {cls.SIZES['font_size_medium']};
            }}
            QProgressBar {{
                border: 1px solid {cls.COLORS['border']};
                border-radius: {cls.SIZES['border_radius_small']};
                text-align: center;
                font-weight: bold;
                background-color: {cls.COLORS['surface']};
            }}
            QProgressBar::chunk {{
                background-color: {cls.COLORS['primary']};
                border-radius: {cls.SIZES['border_radius_small']};
            }}
        """
    
    @classmethod
    def get_player_card_style(cls) -> str:
        """Получить стиль карточки игрока"""
        return f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {cls.COLORS['primary']}, stop:1 {cls.COLORS['primary_dark']});
                border: 2px solid {cls.COLORS['primary_dark']};
                border-radius: {cls.SIZES['border_radius']};
                padding: {cls.SIZES['padding_large']};
                color: white;
            }}
            QLabel {{
                color: white;
                font-weight: bold;
                background: transparent;
            }}
        """
    
    @classmethod
    def get_opponent_card_style(cls) -> str:
        """Получить стиль карточки противника"""
        return f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {cls.COLORS['danger']}, stop:1 {cls.COLORS['danger_dark']});
                border: 2px solid {cls.COLORS['danger_dark']};
                border-radius: {cls.SIZES['border_radius']};
                padding: {cls.SIZES['padding_large']};
                color: white;
            }}
            QLabel {{
                color: white;
                font-weight: bold;
                background: transparent;
            }}
        """
    
    @classmethod
    def get_cooperate_button_style(cls) -> str:
        """Получить стиль кнопки сотрудничества"""
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {cls.COLORS['success']}, stop:1 {cls.COLORS['success_dark']});
                border: none;
                border-radius: {cls.SIZES['border_radius']};
                padding: {cls.SIZES['padding_large']};
                color: white;
                font-weight: bold;
                font-size: {cls.SIZES['font_size_large']};
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {cls.COLORS['success_dark']}, stop:1 {cls.COLORS['success']});
            }}
            QPushButton:pressed {{
                background: {cls.COLORS['success_dark']};
            }}
            QPushButton:disabled {{
                background: {cls.COLORS['text_muted']};
                color: {cls.COLORS['text_secondary']};
            }}
        """
    
    @classmethod
    def get_betray_button_style(cls) -> str:
        """Получить стиль кнопки предательства"""
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {cls.COLORS['danger']}, stop:1 {cls.COLORS['danger_dark']});
                border: none;
                border-radius: {cls.SIZES['border_radius']};
                padding: {cls.SIZES['padding_large']};
                color: white;
                font-weight: bold;
                font-size: {cls.SIZES['font_size_large']};
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {cls.COLORS['danger_dark']}, stop:1 {cls.COLORS['danger']});
            }}
            QPushButton:pressed {{
                background: {cls.COLORS['danger_dark']};
            }}
            QPushButton:disabled {{
                background: {cls.COLORS['text_muted']};
                color: {cls.COLORS['text_secondary']};
            }}
        """
    
    @classmethod
    def get_progress_style(cls) -> str:
        """Получить стиль прогресс-бара"""
        return f"""
            QProgressBar {{
                border: 2px solid {cls.COLORS['border']};
                border-radius: {cls.SIZES['border_radius_large']};
                text-align: center;
                font-weight: bold;
                font-size: {cls.SIZES['font_size_medium']};
                background-color: {cls.COLORS['surface']};
                color: {cls.COLORS['text_primary']};
                padding: 2px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {cls.COLORS['primary']}, stop:1 {cls.COLORS['primary_dark']});
                border-radius: {cls.SIZES['border_radius']};
                margin: 2px;
            }}
        """

    @classmethod
    def get_primary_button_style(cls) -> str:
        """Получить стиль основной кнопки"""
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {cls.COLORS['primary']}, stop:1 {cls.COLORS['primary_dark']});
                border: none;
                border-radius: {cls.SIZES['border_radius']};
                padding: {cls.SIZES['padding_medium']} {cls.SIZES['padding_large']};
                color: white;
                font-weight: bold;
                font-size: {cls.SIZES['font_size_medium']};
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {cls.COLORS['primary_dark']}, stop:1 {cls.COLORS['primary']});
            }}
            QPushButton:pressed {{
                background: {cls.COLORS['primary_dark']};
            }}
            QPushButton:disabled {{
                background: {cls.COLORS['text_muted']};
                color: {cls.COLORS['text_secondary']};
            }}
        """
    
    @classmethod
    def get_secondary_button_style(cls) -> str:
        """Получить стиль вторичной кнопки"""
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {cls.COLORS['info']}, stop:1 {cls.COLORS['info_dark']});
                border: 1px solid {cls.COLORS['info_dark']};
                border-radius: {cls.SIZES['border_radius']};
                padding: {cls.SIZES['padding_small']} {cls.SIZES['padding_medium']};
                color: white;
                font-weight: bold;
                font-size: {cls.SIZES['font_size_small']};
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {cls.COLORS['info_dark']}, stop:1 {cls.COLORS['info']});
            }}
            QPushButton:pressed {{
                background: {cls.COLORS['info_dark']};
            }}
            QPushButton:disabled {{
                background: {cls.COLORS['text_muted']};
                color: {cls.COLORS['text_secondary']};
            }}
        """

    @classmethod
    def get_main_window_style(cls) -> str:
        """Получить стиль главного окна"""
        return f"""
            QMainWindow {{
                background-color: {cls.COLORS['background']};
                color: {cls.COLORS['text_primary']};
                font-family: {cls.FONTS['primary']};
            }}
        """
    
    @classmethod
    def get_list_widget_style(cls) -> str:
        """Получить стиль списка"""
        return f"""
            QListWidget {{
                border: 1px solid {cls.COLORS['border']};
                border-radius: {cls.SIZES['border_radius_small']};
                background-color: {cls.COLORS['background']};
                color: {cls.COLORS['text_primary']};
                font-size: {cls.SIZES['font_size_medium']};
                font-family: {cls.FONTS['primary']};
                padding: {cls.SIZES['padding_small']};
            }}
            QListWidget::item {{
                padding: {cls.SIZES['padding_medium']};
                border-bottom: 1px solid {cls.COLORS['border']};
                border-radius: {cls.SIZES['border_radius_small']};
                margin: 2px;
            }}
            QListWidget::item:selected {{
                background-color: {cls.COLORS['primary']};
                color: white;
            }}
            QListWidget::item:hover {{
                background-color: {cls.COLORS['surface']};
            }}
        """
    
    @classmethod
    def apply_font(cls, widget, size: str = 'medium', bold: bool = False):
        """Применить шрифт к виджету"""
        from PyQt6.QtGui import QFont
        
        sizes = {
            'small': cls.SIZES['font_size_small'],
            'medium': cls.SIZES['font_size_medium'],
            'large': cls.SIZES['font_size_large'],
            'xlarge': cls.SIZES['font_size_xlarge'],
            'xxlarge': cls.SIZES['font_size_xxlarge'],
        }
        
        font_size = int(sizes.get(size, sizes['medium']).replace('px', ''))
        font = QFont(cls.FONTS['primary'], font_size)
        font.setBold(bold)
        widget.setFont(font)
