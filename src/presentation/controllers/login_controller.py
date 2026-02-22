"""
Контроллер для логики входа и регистрации с улучшенной обработкой
"""
import logging
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication
from ...business.services.auth_service import AuthService
from ...business.exceptions import AuthenticationError, ValidationError
from ..views.login_view import LoginView

logger = logging.getLogger(__name__)

class LoginController(QObject):
    """Контроллер для управления логикой входа и регистрации"""
    
    # Сигналы
    login_success = pyqtSignal(str)  # player_id
    
    def __init__(self, auth_service: AuthService):
        super().__init__()
        self.auth_service = auth_service
        self.view = None
        self._setup_view()
        
    def _setup_view(self):
        """Настройка представления"""
        self.view = LoginView()
        self.view.register_requested.connect(self._handle_register)
        self.view.login_requested.connect(self._handle_login)
        
        # Применяем дополнительные настройки
        self._enhance_view()
    
    def _enhance_view(self):
        """Улучшить представление дополнительными функциями"""
        # Устанавливаем фокус на первое поле
        self.view.reg_username.setFocus()
        
        # Добавляем горячие клавиши
        self._setup_shortcuts()
    
    def _setup_shortcuts(self):
        """Настроить горячие клавиши"""
        # Enter для регистрации/входа
        self.view.reg_username.returnPressed.connect(self._focus_next_field)
        self.view.reg_password.returnPressed.connect(self._trigger_register)
        self.view.login_username.returnPressed.connect(self._focus_login_password)
        self.view.login_password.returnPressed.connect(self._trigger_login)
    
    def _focus_next_field(self):
        """Переключить фокус на следующее поле"""
        if self.view.reg_username.hasFocus():
            self.view.reg_password.setFocus()
        elif self.view.login_username.hasFocus():
            self.view.login_password.setFocus()
    
    def _focus_login_password(self):
        """Переключить фокус на пароль входа"""
        self.view.login_password.setFocus()
    
    def _trigger_register(self):
        """Активировать регистрацию по Enter"""
        if self.view.reg_password.hasFocus():
            self._handle_register(
                self.view.reg_username.text().strip(),
                self.view.reg_password.text().strip()
            )
    
    def _trigger_login(self):
        """Активировать вход по Enter"""
        if self.view.login_password.hasFocus():
            self._handle_login(
                self.view.login_username.text().strip(),
                self.view.login_password.text().strip()
            )
    
    def _handle_register(self, username: str, password: str):
        """Обработка запроса на регистрацию с улучшенным UX"""
        # Показываем состояние загрузки
        self.view.set_loading(True)
        
        # Используем QTimer для асинхронной обработки
        QTimer.singleShot(100, lambda: self._process_registration(username, password))
    
    def _process_registration(self, username: str, password: str):
        """Асинхронная обработка регистрации"""
        try:
            # Валидация на клиенте для быстрой обратной связи
            self._validate_input(username, password)
            
            # Попытка регистрации
            player_id = self.auth_service.register(username, password)
            
            if player_id:
                self.view.show_success("✅ Регистрация прошла успешно!")
                logger.info(f"Пользователь {username} успешно зарегистрирован")
                
                # Небольшая задержка для показа сообщения
                QTimer.singleShot(1500, lambda: self._auto_login_after_register(username, password))
            else:
                self.view.show_error("❌ Не удалось зарегистрировать пользователя")
                
        except ValidationError as e:
            self.view.show_warning(f"⚠️ {str(e)}")
            logger.warning(f"Ошибка валидации при регистрации: {e}")
        except AuthenticationError as e:
            self.view.show_error(f"❌ {str(e)}")
            logger.warning(f"Ошибка аутентификации при регистрации: {e}")
        except Exception as e:
            logger.error(f"Неожиданная ошибка при регистрации: {e}")
            self.view.show_error("❌ Произошла ошибка при регистрации. Попробуйте позже.")
        finally:
            self.view.set_loading(False)
    
    def _auto_login_after_register(self, username: str, password: str):
        """Автоматический вход после успешной регистрации"""
        try:
            player_id = self.auth_service.login(username, password)
            if player_id:
                self.view.clear_fields()
                self.login_success.emit(player_id)
            else:
                self.view.show_warning("⚠️ Регистрация прошла успешно, но не удалось войти автоматически. Попробуйте войти вручную.")
        except Exception as e:
            logger.error(f"Ошибка при автоматическом входе: {e}")
            self.view.show_warning("⚠️ Регистрация прошла успешно, но не удалось войти автоматически. Попробуйте войти вручную.")
    
    def _handle_login(self, username: str, password: str):
        """Обработка запроса на вход с улучшенным UX"""
        # Показываем состояние загрузки
        self.view.set_loading(True)
        
        # Используем QTimer для асинхронной обработки
        QTimer.singleShot(100, lambda: self._process_login(username, password))
    
    def _process_login(self, username: str, password: str):
        """Асинхронная обработка входа"""
        try:
            # Валидация на клиенте для быстрой обратной связи
            self._validate_input(username, password)
            
            # Попытка входа
            player_id = self.auth_service.login(username, password)
            
            if player_id:
                self.view.clear_fields()
                self.view.show_success("✅ Вход выполнен успешно!")
                logger.info(f"Пользователь {username} успешно вошел")
                
                # Небольшая задержка для показа сообщения
                QTimer.singleShot(1000, lambda: self.login_success.emit(player_id))
            else:
                self.view.show_error("❌ Неверное имя пользователя или пароль")
                
        except ValidationError as e:
            self.view.show_warning(f"⚠️ {str(e)}")
            logger.warning(f"Ошибка валидации при входе: {e}")
        except AuthenticationError as e:
            self.view.show_error(f"❌ {str(e)}")
            logger.warning(f"Ошибка аутентификации при входе: {e}")
        except Exception as e:
            logger.error(f"Неожиданная ошибка при входе: {e}")
            self.view.show_error("❌ Произошла ошибка при входе. Попробуйте позже.")
        finally:
            self.view.set_loading(False)
    
    def _validate_input(self, username: str, password: str):
        """Дополнительная валидация на клиенте"""
        if not username or not password:
            raise ValidationError("Заполните все поля")
        
        if len(username) < 3:
            raise ValidationError("Имя пользователя должно содержать минимум 3 символа")
        
        if len(username) > 20:
            raise ValidationError("Имя пользователя должно содержать не более 20 символов")
        
        if len(password) < 6:
            raise ValidationError("Пароль должен содержать минимум 6 символов")
        
        # Проверка допустимых символов
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
        if not all(c in allowed_chars for c in username):
            raise ValidationError("Имя пользователя может содержать только буквы, цифры, _ и -")
    
    def get_view(self) -> LoginView:
        """Получить представление"""
        return self.view
    
    def reset_form(self):
        """Сбросить форму в начальное состояние"""
        if self.view:
            self.view.clear_fields()
            self.view.set_loading(False)
            self.view.reg_username.setFocus()
    
    def show_error_message(self, message: str):
        """Показать сообщение об ошибке (для внешнего вызова)"""
        if self.view:
            self.view.show_error(f"❌ {message}")
    
    def show_success_message(self, message: str):
        """Показать сообщение об успехе (для внешнего вызова)"""
        if self.view:
            self.view.show_success(f"✅ {message}")
    
    def cleanup(self):
        """Очистка ресурсов"""
        if self.view:
            try:
                self.view.register_requested.disconnect()
                self.view.login_requested.disconnect()
            except:
                pass
        
        logger.info("LoginController очищен")
