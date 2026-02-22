import json
import os
import time
import bcrypt
import logging
import firebase_admin
from typing import List, Dict, Optional, Callable
from firebase_admin import credentials, db
from datetime import datetime
from database_interface import DatabaseInterface

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImprovedFirebaseDatabase(DatabaseInterface):
    """Улучшенная реализация базы данных Firebase с хешированием паролей и восстановлением соединения"""
    
    def __init__(self, config_path: str = "src/config/firebase_config.json"):
        self.config_path = config_path
        self.listeners = {}
        self._load_config()
        self._init_firebase()
        logger.info("ImprovedFirebaseDatabase успешно инициализирована")
        
    def _load_config(self):
        """Загрузка конфигурации из файла"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            logger.info("Конфигурация Firebase успешно загружена")
        except FileNotFoundError:
            logger.error(f"Файл конфигурации {self.config_path} не найден")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON в файле конфигурации: {e}")
            raise
    
    def _init_firebase(self):
        """Инициализация Firebase"""
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(self.config)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': self.config['database_url']
                })
            self.ref = db.reference('/')
            logger.info("Firebase успешно инициализирован")
        except Exception as e:
            logger.error(f"Ошибка инициализации Firebase: {e}")
            raise
    
    def _ensure_connection(self):
        """Проверка и восстановление соединения"""
        try:
            # Простая проверка - попытка получить данные
            self.ref.child('connection_test').get()
            return True
        except Exception as e:
            logger.warning(f"Потеря соединения: {e}")
            try:
                # Попытка переподключения
                self._init_firebase()
                return True
            except Exception as e:
                logger.error(f"Не удалось восстановить соединение: {e}")
                return False
    
    def _safe_operation(self, operation, *args, **kwargs):
        """Безопасное выполнение операции с попыткой восстановления"""
        max_retries = 3
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                if self._ensure_connection():
                    return operation(*args, **kwargs)
                else:
                    logger.warning(f"Попытка {attempt + 1} не удалась - нет соединения")
                    time.sleep(1)
            except Exception as e:
                last_exception = e
                logger.error(f"Попытка {attempt + 1} провалилась: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Экспоненциальная задержка
        
        if last_exception:
            raise last_exception
        return None
    
    def _hash_password(self, password: str) -> str:
        """Хеширование пароля"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Проверка пароля"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            logger.error(f"Ошибка проверки пароля: {e}")
            return False
    
    def _validate_username(self, username: str) -> bool:
        """Валидация имени пользователя"""
        if not username:
            return False
        if len(username) < 3 or len(username) > 20:
            return False
        # Разрешаем буквы, цифры, _ и -
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
        return all(c in allowed_chars for c in username)
    
    def _validate_password(self, password: str) -> bool:
        """Валидация пароля"""
        if not password or len(password) < 6:
            return False
        return True
    
    def register_player(self, username: str, password: str) -> bool:
        """Регистрация нового игрока с валидацией"""
        def _register():
            # Валидация
            if not self._validate_username(username):
                logger.warning(f"Невалидное имя пользователя: {username}")
                return False
            
            if not self._validate_password(password):
                logger.warning(f"Слабый пароль для пользователя: {username}")
                return False
            
            players_ref = self.ref.child('players')
            all_players = players_ref.get()
            
            # Проверка уникальности имени
            if all_players:
                for player_data in all_players.values():
                    if player_data.get('username') == username:
                        logger.info(f"Пользователь {username} уже существует")
                        return False
            
            # Хеширование пароля
            hashed_password = self._hash_password(password)
            
            # Создание нового игрока
            new_player = {
                'username': username,
                'password': hashed_password,
                'created_at': datetime.now().isoformat(),
                'last_online': datetime.now().isoformat(),
                'is_online': False,
                'total_score': 0,
                'games_played': 0
            }
            
            players_ref.push(new_player)
            logger.info(f"Пользователь {username} успешно зарегистрирован")
            return True
        
        try:
            return self._safe_operation(_register)
        except Exception as e:
            logger.error(f"Ошибка регистрации: {e}")
            return False
    
    def login_player(self, username: str, password: str) -> Optional[str]:
        """Авторизация с проверкой хешированного пароля"""
        def _login():
            if not self._validate_username(username) or not password:
                return None
            
            players_ref = self.ref.child('players')
            players = players_ref.get()
            
            if players:
                for player_id, player_data in players.items():
                    if player_data.get('username') == username:
                        # Проверка пароля
                        if self._verify_password(password, player_data.get('password')):
                            # Обновление статуса
                            players_ref.child(player_id).update({
                                'is_online': True,
                                'last_online': datetime.now().isoformat(),
                                'last_ping': datetime.now().timestamp()
                            })
                            logger.info(f"Пользователь {username} успешно вошел")
                            return player_id
                        else:
                            logger.warning(f"Неверный пароль для пользователя {username}")
                            return None
            
            logger.info(f"Пользователь {username} не найден")
            return None
        
        try:
            return self._safe_operation(_login)
        except Exception as e:
            logger.error(f"Ошибка входа: {e}")
            return None
    
    def logout_player(self, player_id: str):
        """Выход игрока"""
        def _logout():
            self.ref.child('players').child(player_id).update({
                'is_online': False,
                'last_online': datetime.now().isoformat()
            })
            logger.info(f"Игрок {player_id} вышел")
        
        try:
            self._safe_operation(_logout)
        except Exception as e:
            logger.error(f"Ошибка выхода: {e}")
    
    def get_online_players(self, exclude_player_id: str = None) -> List[Dict]:
        """Получение активных онлайн игроков"""
        def _get_online():
            players_ref = self.ref.child('players')
            players = players_ref.get()
            
            online_players = []
            current_time = datetime.now().timestamp()
            
            if players:
                for player_id, player_data in players.items():
                    # Проверка активности (ping за последние 30 секунд)
                    last_ping = player_data.get('last_ping', 0)
                    is_online = player_data.get('is_online', False)
                    
                    if is_online and (current_time - last_ping) < 30:
                        if exclude_player_id and str(player_id) == str(exclude_player_id):
                            continue
                        
                        online_players.append({
                            'id': str(player_id),
                            'username': player_data.get('username'),
                            'total_score': player_data.get('total_score', 0),
                            'games_played': player_data.get('games_played', 0)
                        })
            
            return online_players
        
        try:
            return self._safe_operation(_get_online) or []
        except Exception as e:
            logger.error(f"Ошибка получения онлайн игроков: {e}")
            return []
    
    def create_game(self, player1_id: str, player2_id: str) -> str:
        """Создание новой игры"""
        def _create_game():
            games_ref = self.ref.child('games')
            
            new_game = {
                'player1_id': player1_id,
                'player2_id': player2_id,
                'created_at': datetime.now().isoformat(),
                'status': 'active',
                'current_round': 1,
                'current_question': 1,
                'player1_ready': False,
                'player2_ready': False
            }
            
            result = games_ref.push(new_game)
            logger.info(f"Создана игра между {player1_id} и {player2_id}")
            return result.key
        
        try:
            return self._safe_operation(_create_game)
        except Exception as e:
            logger.error(f"Ошибка создания игры: {e}")
            return None
    
    def create_round(self, game_id: str, round_number: int) -> str:
        """Создание нового раунда"""
        def _create_round():
            rounds_ref = self.ref.child('rounds')
            
            new_round = {
                'game_id': game_id,
                'round_number': round_number,
                'player1_choice': None,
                'player2_choice': None,
                'player1_score': 0,
                'player2_score': 0,
                'completed_at': None
            }
            
            result = rounds_ref.push(new_round)
            logger.info(f"Создан раунд {round_number} для игры {game_id}")
            return result.key
        
        try:
            return self._safe_operation(_create_round)
        except Exception as e:
            logger.error(f"Ошибка создания раунда: {e}")
            return None
    
    def save_question_choice(self, round_id: str, question_number: int, player_id: str, choice: str):
        """Сохранение выбора игрока в вопросе"""
        def _save_choice():
            round_id_str = str(round_id)
            
            round_data = self.ref.child('rounds').child(round_id_str).get()
            if not round_data:
                return
            
            game_id = round_data.get('game_id')
            game_data = self.ref.child('games').child(game_id).get()
            
            if not game_data:
                return
            
            player1_id = game_data.get('player1_id')
            player2_id = game_data.get('player2_id')
            
            # Определяем, какой игрок
            if player_id == player1_id:
                field = 'player1_choice'
            elif player_id == player2_id:
                field = 'player2_choice'
            else:
                return
            
            # Сохраняем выбор
            questions_ref = self.ref.child('round_questions')
            all_questions = questions_ref.get()
            
            question_key = None
            if all_questions:
                for q_key, q_data in all_questions.items():
                    if (q_data.get('round_id') == round_id_str and 
                        q_data.get('question_number') == question_number):
                        question_key = q_key
                        break
            
            if question_key:
                questions_ref.child(question_key).update({field: choice})
            else:
                new_question = {
                    'round_id': round_id_str,
                    'question_number': question_number,
                    field: choice
                }
                questions_ref.push(new_question)
            
            logger.info(f"Сохранен выбор игрока {player_id} для вопроса {question_number}")
        
        try:
            self._safe_operation(_save_choice)
        except Exception as e:
            logger.error(f"Ошибка сохранения выбора: {e}")
    
    def get_player_stats(self, player_id: str) -> Dict:
        """Получение статистики игрока"""
        def _get_stats():
            player_id_str = str(player_id)
            player_data = self.ref.child('players').child(player_id_str).get()
            
            if player_data:
                return {
                    'username': player_data.get('username'),
                    'total_score': player_data.get('total_score', 0),
                    'games_played': player_data.get('games_played', 0)
                }
            else:
                return {}
        
        try:
            return self._safe_operation(_get_stats) or {}
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {}
    
    def ping_player(self, player_id: str):
        """Обновление ping для поддержания онлайн статуса"""
        def _ping():
            self.ref.child('players').child(player_id).update({
                'last_ping': datetime.now().timestamp()
            })
        
        try:
            self._safe_operation(_ping)
        except Exception as e:
            logger.error(f"Ошибка ping: {e}")
    
    def listen_to_game(self, game_id: str, callback: Callable):
        """Слушать изменения в игре"""
        def listener(event):
            try:
                callback(event.data)
            except Exception as e:
                logger.error(f"Ошибка в обработчике изменений игры: {e}")
        
        try:
            game_ref = self.ref.child('games').child(game_id)
            self.listeners[f'game_{game_id}'] = game_ref.listen(listener)
            logger.info(f"Начато прослушивание игры {game_id}")
        except Exception as e:
            logger.error(f"Ошибка настройки прослушивания игры: {e}")
    
    def listen_to_round(self, round_id: str, callback: Callable):
        """Слушать изменения в раунде"""
        def listener(event):
            try:
                callback(event.data)
            except Exception as e:
                logger.error(f"Ошибка в обработчике изменений раунда: {e}")
        
        try:
            round_ref = self.ref.child('rounds').child(round_id)
            self.listeners[f'round_{round_id}'] = round_ref.listen(listener)
            logger.info(f"Начато прослушивание раунда {round_id}")
        except Exception as e:
            logger.error(f"Ошибка настройки прослушивания раунда: {e}")
    
    def listen_to_questions(self, round_id: str, callback: Callable):
        """Слушать изменения в вопросах раунда"""
        def listener(event):
            try:
                callback(event.data)
            except Exception as e:
                logger.error(f"Ошибка в обработчике изменений вопросов: {e}")
        
        try:
            questions_ref = self.ref.child('round_questions')
            query = questions_ref.order_by_child('round_id').equal_to(round_id)
            self.listeners[f'questions_{round_id}'] = query.listen(listener)
            logger.info(f"Начато прослушивание вопросов раунда {round_id}")
        except Exception as e:
            logger.error(f"Ошибка настройки прослушивания вопросов: {e}")
    
    def update_game_status(self, game_id: str, player_id: str, ready: bool):
        """Обновить статус готовности игрока"""
        def _update_status():
            game_data = self.ref.child('games').child(game_id).get()
            if not game_data:
                return
            
            if player_id == game_data.get('player1_id'):
                self.ref.child('games').child(game_id).update({'player1_ready': ready})
            elif player_id == game_data.get('player2_id'):
                self.ref.child('games').child(game_id).update({'player2_ready': ready})
        
        try:
            self._safe_operation(_update_status)
        except Exception as e:
            logger.error(f"Ошибка обновления статуса игры: {e}")
    
    def get_question_choices(self, round_id: str, question_number: int) -> Dict:
        """Получить выборы обоих игроков для вопроса"""
        def _get_choices():
            round_id_str = str(round_id)
            questions_ref = self.ref.child('round_questions')
            all_questions = questions_ref.get()
            
            choices = {'player1_choice': None, 'player2_choice': None}
            
            if all_questions:
                for q_data in all_questions.values():
                    if (q_data.get('round_id') == round_id_str and 
                        q_data.get('question_number') == question_number):
                        
                        if 'player1_choice' in q_data:
                            choices['player1_choice'] = q_data['player1_choice']
                        if 'player2_choice' in q_data:
                            choices['player2_choice'] = q_data['player2_choice']
                        break
            
            return choices
        
        try:
            return self._safe_operation(_get_choices) or {'player1_choice': None, 'player2_choice': None}
        except Exception as e:
            logger.error(f"Ошибка получения выборов: {e}")
            return {'player1_choice': None, 'player2_choice': None}

# Для совместимости с существующим кодом
GameDatabase = ImprovedFirebaseDatabase
