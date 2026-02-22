"""
Главный файл приложения с правильной архитектурой и улучшенным UI
"""
import sys
import os
import logging
import platform
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QSplashScreen
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QPainter

# Добавляем src в путь для импортов (кроссплатформенно)
if getattr(sys, 'frozen', False):
    # Если запущено как .exe файл
    application_path = os.path.dirname(sys.executable)
else:
    # Если запущено как .py файл
    application_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, os.path.join(application_path, "src"))

from src.config.config_manager import config
from src.data.database.firebase_player_repository import FirebasePlayerRepository
from src.business.services.auth_service import AuthService
from src.presentation.controllers.login_controller import LoginController
from src.presentation.styles import StyleManager

# Настройка логирования
def setup_logging():
    """Настройка логирования"""
    logging_config = config.get_logging_config()
    logging.basicConfig(
        level=getattr(logging, logging_config.get('level', 'INFO')),
        format=logging_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )

class SplashScreen(QSplashScreen):
    """Заставка приложения"""
    
    def __init__(self):
        super().__init__()
        # Создаем простую заставку (кроссплатформенно)
        pixmap = QPixmap(400, 300)
        pixmap.fill(Qt.GlobalColor.white)
        
        painter = QPainter(pixmap)
        painter.setPen(Qt.GlobalColor.black)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "GAME\nPredator or Collaborator\nLoading...")
        painter.end()
        
        super().__init__(pixmap)
        self.setFixedSize(400, 300)

class Application(QMainWindow):
    """Главное окно приложения с улучшенным дизайном"""
    
    def __init__(self):
        super().__init__()
        self.style_manager = StyleManager()
        self.controllers = {}
        self.repositories = {}
        self.services = {}
        
        # Применяем стили к приложению
        self.setStyleSheet(self.style_manager.get_main_window_style())
        
        self.init_services()
        self.init_ui()
        
    def init_services(self):
        """Инициализация сервисов с улучшенной обработкой ошибок"""
        try:
            # Загрузка конфигурации
            if not config.load_config():
                logging.warning("Используем конфигурацию по умолчанию")
            
            # Инициализация репозиториев
            firebase_config_path = config.get_firebase_config_path()
            self.repositories['player'] = FirebasePlayerRepository(firebase_config_path)
            
            # Проверка соединения
            if not self.repositories['player'].connect():
                raise ConnectionError("Не удалось подключиться к базе данных")
            
            # Инициализация сервисов
            self.services['auth'] = AuthService(self.repositories['player'])
            
            # Сохраняем ID текущего пользователя
            self.current_player_id = None
            self.current_player_name = None
            
            logging.info("✅ Все сервисы успешно инициализированы")
            
        except Exception as e:
            logging.error(f"❌ Критическая ошибка инициализации сервисов: {e}")
            self.show_critical_error(f"Ошибка инициализации: {e}")
            raise
    
    def init_ui(self):
        """Инициализация пользовательского интерфейса с адаптивным дизайном"""
        # Настройка окна
        self.setWindowTitle(config.get('app.name', 'Предать или Сотрудничать'))
        
        # Адаптивный размер окна
        screen = QApplication.primaryScreen().geometry()
        default_width = min(config.get('ui.window_width', 800), screen.width() - 100)
        default_height = min(config.get('ui.window_height', 600), screen.height() - 100)
        
        self.setGeometry(
            (screen.width() - default_width) // 2,
            (screen.height() - default_height) // 2,
            default_width,
            default_height
        )
        
        # Минимальный размер
        self.setMinimumSize(600, 500)
        
        # Создаем стек виджетов для навигации
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet(f"""
            QStackedWidget {{
                background-color: {StyleManager.COLORS['background']};
                border: none;
            }}
        """)
        
        self.setCentralWidget(self.stacked_widget)
        
        # Инициализация контроллеров
        self.init_controllers()
        
        # Показываем начальный экран
        self.show_login()
        
        # Применяем дополнительные стили
        self.apply_enhanced_styles()
    
    def init_controllers(self):
        """Инициализация контроллеров с улучшенной обработкой"""
        try:
            # Контроллер входа
            self.controllers['login'] = LoginController(self.services['auth'])
            self.controllers['login'].login_success.connect(self.on_login_success)
            
            # Добавляем представление в стек
            login_view = self.controllers['login'].get_view()
            self.stacked_widget.addWidget(login_view)
            
            logging.info("✅ Контроллеры успешно инициализированы")
            
        except Exception as e:
            logging.error(f"❌ Ошибка инициализации контроллеров: {e}")
            self.show_critical_error(f"Ошибка интерфейса: {e}")
            raise
    
    def apply_enhanced_styles(self):
        """Применить улучшенные стили к приложению"""
        # Устанавливаем иконку приложения (если есть)
        # self.setWindowIcon(QIcon('path/to/icon.png'))
        
        # Центрируем окно на экране
        self.center_window()
    
    def center_window(self):
        """Центрировать окно на экране"""
        frame_geometry = self.frameGeometry()
        screen_center = QApplication.primaryScreen().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())
    
    def show_login(self):
        """Показать экран входа с анимацией"""
        if 'login' in self.controllers:
            self.stacked_widget.setCurrentWidget(self.controllers['login'].get_view())
            self.controllers['login'].reset_form()
    
    def on_login_success(self, player_id: str, player_name: str = None):
        """Обработка успешного входа"""
        try:
            logging.info(f"✅ Пользователь {player_id} успешно вошел в систему")
            
            # Сохраняем данные текущего пользователя
            self.current_player_id = player_id
            self.current_player_name = player_name or f"Player_{player_id}"
            
            # Показываем сообщение об успехе
            self.controllers['login'].show_success_message("Добро пожаловать в игру!")
            
            # Показываем главное меню
            QTimer.singleShot(2000, self.show_main_menu)
            
        except Exception as e:
            logging.error(f"❌ Ошибка при обработке входа: {e}")
            self.controllers['login'].show_error_message("Ошибка при входе в систему")
    
    def show_main_menu(self):
        """Показать главное меню (заглушка)"""
        from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget, QPushButton
        
        menu_widget = QWidget()
        layout = QVBoxLayout(menu_widget)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Заголовок
        title = QLabel("🎮 Главное меню")
        title.setStyleSheet(self.style_manager.get_title_style('xlarge'))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Информация
        info = QLabel("👤 Вы успешно вошли в систему")
        info.setStyleSheet(self.style_manager.get_label_style('primary'))
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
        
        # Кнопка статистики
        stats_btn = QPushButton("📊 Статистика")
        stats_btn.setStyleSheet(self.style_manager.get_button_style('info', 'medium'))
        stats_btn.clicked.connect(self.show_stats)
        layout.addWidget(stats_btn)
        
        # Кнопка игры
        game_btn = QPushButton("🎮 Начать игру")
        game_btn.setStyleSheet(self.style_manager.get_button_style('primary', 'medium'))
        game_btn.clicked.connect(self.start_game)
        layout.addWidget(game_btn)
        
        logout_btn = QPushButton("🚪 Выйти")
        logout_btn.setStyleSheet(self.style_manager.get_button_style('warning', 'medium'))
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)
        
        self.stacked_widget.addWidget(menu_widget)
        self.stacked_widget.setCurrentWidget(menu_widget)
    
    def show_stats(self):
        """Показать статистику"""
        try:
            if not self.current_player_id:
                self.show_error_message("Сначала войдите в систему")
                return
                
            # Импортируем здесь, чтобы избежать циклических импортов
            from src.presentation.controllers.stats_controller import StatsController
            
            # Создаем контроллер статистики
            self.controllers['stats'] = StatsController(
                self.repositories['player'],
                self.current_player_id,
                self.current_player_name
            )
            
            # Подключаем сигналы
            self.controllers['stats'].back_to_menu.connect(self.show_main_menu)
            self.controllers['stats'].error_occurred.connect(self.show_error_message)
            
            # Добавляем представление в стек
            stats_view = self.controllers['stats'].get_view()
            self.stacked_widget.addWidget(stats_view)
            self.stacked_widget.setCurrentWidget(stats_view)
            
            # Инициализируем контроллер
            QTimer.singleShot(100, lambda: self._initialize_stats_controller())
            
            logging.info(f"📊 Статистика запущена для игрока {self.current_player_id}")
            
        except Exception as e:
            logging.error(f"❌ Ошибка запуска статистики: {e}")
            self.show_error_message(f"Ошибка запуска статистики: {e}")
    
    def _initialize_stats_controller(self):
        """Инициализация контроллера статистики"""
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.controllers['stats'].initialize())
            loop.close()
        except Exception as e:
            logging.error(f"❌ Ошибка инициализации статистики: {e}")
            self.show_error_message(f"Ошибка инициализации статистики: {e}")
    
    def start_game(self):
        """Начать игру (через комнаты)"""
        try:
            if not self.current_player_id:
                self.show_error_message("Сначала войдите в систему")
                return
                
            # Импортируем здесь, чтобы избежать циклических импортов
            from src.presentation.controllers.room_controller import RoomController
            
            # Создаем контроллер комнат
            self.controllers['room'] = RoomController(
                self.repositories['player'],
                self.current_player_id,
                self.current_player_name
            )
            
            # Подключаем сигналы
            self.controllers['room'].back_to_menu.connect(self.show_main_menu)
            self.controllers['room'].error_occurred.connect(self.show_error_message)
            self.controllers['room'].game_started.connect(self.start_game_session)
            
            # Добавляем представление в стек
            room_view = self.controllers['room'].get_view()
            self.stacked_widget.addWidget(room_view)
            self.stacked_widget.setCurrentWidget(room_view)
            
            # Инициализируем контроллер
            QTimer.singleShot(100, lambda: self._initialize_room_controller())
            
            logging.info(f"🏠 Система комнат запущена для игрока {self.current_player_id}")
            
        except Exception as e:
            logging.error(f"❌ Ошибка запуска комнат: {e}")
            self.show_error_message(f"Ошибка запуска комнат: {e}")
    
    def _initialize_room_controller(self):
        """Инициализация контроллера комнат"""
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.controllers['room'].initialize())
            loop.close()
        except Exception as e:
            logging.error(f"❌ Ошибка инициализации комнат: {e}")
            self.show_error_message(f"Ошибка инициализации комнат: {e}")
    
    def start_game_session(self, game_id: str, player_id: str, opponent_name: str):
        """Начать игровую сессию"""
        try:
            # Импортируем здесь, чтобы избежать циклических импортов
            from src.presentation.controllers.game_controller import GameController
            
            # Создаем игровой контроллер
            self.controllers['game'] = GameController(
                self.repositories['player'],
                player_id,
                f"Player_{player_id}"  # Временно, можно будет улучшить
            )
            
            # Подключаем сигналы
            self.controllers['game'].back_to_menu.connect(self.show_main_menu)
            self.controllers['game'].error_occurred.connect(self.show_error_message)
            
            # Добавляем представление в стек
            game_view = self.controllers['game'].get_view()
            self.stacked_widget.addWidget(game_view)
            self.stacked_widget.setCurrentWidget(game_view)
            
            # Начинаем игру
            QTimer.singleShot(100, lambda: self._start_game_session_async(game_id))
            
            logging.info(f"🎮 Игровая сессия начата для игры {game_id}")
            
        except Exception as e:
            logging.error(f"❌ Ошибка начала игровой сессии: {e}")
            self.show_error_message(f"Ошибка начала игры: {e}")
    
    def _start_game_session_async(self, game_id: str):
        """Асинхронный запуск игровой сессии"""
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.controllers['game'].start_game(game_id))
            loop.close()
        except Exception as e:
            logging.error(f"❌ Ошибка асинхронной игровой сессии: {e}")
            self.show_error_message(f"Ошибка начала игры: {e}")
    
    def show_placeholder(self):
        """Показать заглушку для неработающих функций"""
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("ℹ️ Информация")
        msg.setText("Эта функция находится в разработке")
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {StyleManager.COLORS['background']};
                color: {StyleManager.COLORS['text_primary']};
                font-family: {StyleManager.FONTS['primary']};
            }}
            QPushButton {{
                {self.style_manager.get_button_style('info', 'medium')}
            }}
        """)
        msg.exec()
    
    def logout(self):
        """Выйти из системы"""
        try:
            if self.current_player_id:
                # Выполняем выход через сервис
                self.services['auth'].logout(self.current_player_id)
                
                # Очищаем игровой контроллер если есть
                if 'game' in self.controllers:
                    try:
                        self.controllers['game'].cleanup()
                    except:
                        pass
                    del self.controllers['game']
            
            # Сбрасываем данные пользователя
            self.current_player_id = None
            self.current_player_name = None
            
            logging.info("Пользователь вышел из системы")
            self.show_login()
            
        except Exception as e:
            logging.error(f"Ошибка при выходе: {e}")
            self.show_error_message("Ошибка при выходе из системы")
    
    def show_error_message(self, message: str):
        """Показать сообщение об ошибке"""
        if 'login' in self.controllers:
            self.controllers['login'].show_error_message(message)
    
    def show_critical_error(self, message: str):
        """Показать критическую ошибку"""
        from PyQt6.QtWidgets import QMessageBox
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("❌ Критическая ошибка")
        msg.setText(f"Произошла критическая ошибка:\n\n{message}\n\nПриложение будет закрыто.")
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {StyleManager.COLORS['background']};
                color: {StyleManager.COLORS['text_primary']};
                font-family: {StyleManager.FONTS['primary']};
            }}
            QPushButton {{
                {StyleManager().get_button_style('danger', 'medium')}
            }}
        """)
        msg.exec()
    
    def closeEvent(self, event):
        """Обработка закрытия приложения с улучшенной очисткой"""
        try:
            logging.info("🔄 Начало очистки ресурсов...")
            
            # Очистка контроллеров
            for name, controller in self.controllers.items():
                try:
                    if hasattr(controller, 'cleanup'):
                        controller.cleanup()
                    logging.info(f"✅ Контроллер {name} очищен")
                except Exception as e:
                    logging.error(f"❌ Ошибка очистки контроллера {name}: {e}")
            
            # Закрытие соединений
            for name, repository in self.repositories.items():
                try:
                    if hasattr(repository, 'disconnect'):
                        repository.disconnect()
                    logging.info(f"✅ Репозиторий {name} отключен")
                except Exception as e:
                    logging.error(f"❌ Ошибка отключения репозитория {name}: {e}")
            
            logging.info("✅ Приложение корректно закрыто")
            
        except Exception as e:
            logging.error(f"❌ Ошибка при закрытии приложения: {e}")
        
        event.accept()

def main():
    """Главная функция с улучшенной обработкой запуска"""
    splash = None
    
    try:
        # Настройка логирования
        setup_logging()
        logging.info("🚀 Запуск приложения...")
        
        # Создание приложения
        app = QApplication(sys.argv)
        app.setApplicationName(config.get('app.name', 'Предать или Сотрудничать'))
        app.setApplicationVersion(config.get('app.version', '2.0.0'))
        app.setStyle('Fusion')  # Современный стиль
        
        # Показываем заставку
        splash = SplashScreen()
        splash.show()
        app.processEvents()
        
        # Имитация загрузки
        QTimer.singleShot(2000, splash.close)
        
        # Создание главного окна
        window = Application()
        
        # Показываем окно после скрытия заставки
        QTimer.singleShot(2500, window.show)
        
        # Запуск приложения
        sys.exit(app.exec())
        
    except Exception as e:
        logging.error(f"❌ Критическая ошибка при запуске приложения: {e}")
        
        # Показываем ошибку даже если GUI не запустился
        try:
            from PyQt6.QtWidgets import QMessageBox
            error_app = QApplication(sys.argv)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("❌ Критическая ошибка")
            msg.setText(f"Не удалось запустить приложение:\n\n{e}")
            msg.exec()
        except:
            print(f"Критическая ошибка: {e}")
        
        sys.exit(1)
    finally:
        if splash:
            splash.close()

if __name__ == "__main__":
    main()
