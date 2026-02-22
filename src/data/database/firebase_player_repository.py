"""
Firebase реализация репозитория игроков
"""
import json
import time
import logging
import bcrypt
import firebase_admin
from typing import List, Optional
from firebase_admin import credentials, db
from datetime import datetime
from ..repositories.player_repository import PlayerRepository
from ..models.player import Player

logger = logging.getLogger(__name__)

class FirebasePlayerRepository(PlayerRepository):
    """Firebase реализация репозитория игроков"""
    
    def __init__(self, config_path: str = "src/config/firebase_config.json"):
        self.config_path = config_path
        self.ref = None
        self._connected = False
        self._load_config()
        self._init_firebase()
    
    def _load_config(self):
        """Загрузка конфигурации Firebase"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            logger.info("Конфигурация Firebase успешно загружена")
        except FileNotFoundError:
            logger.error(f"Файл конфигурации {self.config_path} не найден")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
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
            self._connected = True
            logger.info("Firebase успешно инициализирован")
        except Exception as e:
            logger.error(f"Ошибка инициализации Firebase: {e}")
            self._connected = False
    
    def _ensure_connection(self):
        """Проверка и восстановление соединения"""
        try:
            if not self._connected:
                self._init_firebase()
            
            # Простая проверка соединения
            self.ref.child('connection_test').get()
            return True
        except Exception as e:
            logger.warning(f"Потеря соединения: {e}")
            try:
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
                    time.sleep(2 ** attempt)
        
        if last_exception:
            raise last_exception
        return None
    
    def connect(self) -> bool:
        """Установить соединение"""
        return self._ensure_connection()
    
    def disconnect(self):
        """Закрыть соединение"""
        self._connected = False
        logger.info("Соединение с Firebase закрыто")
    
    def is_connected(self) -> bool:
        """Проверить статус соединения"""
        return self._connected
    
    def create_player(self, username: str, hashed_password: str) -> Optional[str]:
        """Создать нового игрока"""
        def _create():
            players_ref = self.ref.child('players')
            all_players = players_ref.get()
            
            # Проверка уникальности имени
            if all_players:
                for player_data in all_players.values():
                    if player_data.get('username') == username:
                        return None
            
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
            
            result = players_ref.push(new_player)
            return result.key
        
        try:
            return self._safe_operation(_create)
        except Exception as e:
            logger.error(f"Ошибка создания игрока: {e}")
            return None
    
    def get_player_by_username(self, username: str) -> Optional[Player]:
        """Получить игрока по имени пользователя"""
        def _get():
            players_ref = self.ref.child('players')
            players = players_ref.get()
            
            if players:
                for player_id, player_data in players.items():
                    if player_data.get('username') == username:
                        return Player.from_dict({
                            'id': player_id,
                            **player_data
                        })
            return None
        
        try:
            return self._safe_operation(_get)
        except Exception as e:
            logger.error(f"Ошибка получения игрока по username: {e}")
            return None
    
    def get_player_by_id(self, player_id: str) -> Optional[Player]:
        """Получить игрока по ID"""
        def _get():
            player_data = self.ref.child('players').child(player_id).get()
            if player_data:
                return Player.from_dict({
                    'id': player_id,
                    **player_data
                })
            return None
        
        try:
            return self._safe_operation(_get)
        except Exception as e:
            logger.error(f"Ошибка получения игрока по ID: {e}")
            return None
    
    def update_player(self, player: Player) -> bool:
        """Обновить данные игрока"""
        def _update():
            self.ref.child('players').child(player.id).update(player.to_dict())
            return True
        
        try:
            return self._safe_operation(_update) or False
        except Exception as e:
            logger.error(f"Ошибка обновления игрока: {e}")
            return False
    
    def delete_player(self, player_id: str) -> bool:
        """Удалить игрока"""
        def _delete():
            self.ref.child('players').child(player_id).delete()
            return True
        
        try:
            return self._safe_operation(_delete) or False
        except Exception as e:
            logger.error(f"Ошибка удаления игрока: {e}")
            return False
    
    def get_online_players(self, exclude_player_id: Optional[str] = None) -> List[Player]:
        """Получить список онлайн игроков"""
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
                        
                        online_players.append(Player.from_dict({
                            'id': player_id,
                            **player_data
                        }))
            
            return online_players
        
        try:
            return self._safe_operation(_get_online) or []
        except Exception as e:
            logger.error(f"Ошибка получения онлайн игроков: {e}")
            return []
    
    def verify_password(self, username: str, password: str) -> Optional[str]:
        """Проверить пароль и вернуть ID игрока"""
        def _verify():
            players_ref = self.ref.child('players')
            players = players_ref.get()
            
            if players:
                for player_id, player_data in players.items():
                    if player_data.get('username') == username:
                        try:
                            if bcrypt.checkpw(password.encode('utf-8'), 
                                            player_data.get('password').encode('utf-8')):
                                return player_id
                        except Exception as e:
                            logger.error(f"Ошибка проверки пароля: {e}")
                            return None
            return None
        
        try:
            return self._safe_operation(_verify)
        except Exception as e:
            logger.error(f"Ошибка проверки пароля: {e}")
            return None
    
    def update_online_status(self, player_id: str, is_online: bool) -> bool:
        """Обновить онлайн статус игрока"""
        def _update_status():
            self.ref.child('players').child(player_id).update({
                'is_online': is_online,
                'last_online': datetime.now().isoformat(),
                'last_ping': datetime.now().timestamp()
            })
            return True
        
        try:
            return self._safe_operation(_update_status) or False
        except Exception as e:
            logger.error(f"Ошибка обновления онлайн статуса: {e}")
            return False
    
    def update_ping(self, player_id: str) -> bool:
        """Обновить ping для поддержания онлайн статуса"""
        def _ping():
            self.ref.child('players').child(player_id).update({
                'last_ping': datetime.now().timestamp()
            })
            return True
        
        try:
            return self._safe_operation(_ping) or False
        except Exception as e:
            logger.error(f"Ошибка обновления ping: {e}")
            return False
    
    def update_player_status(self, player_id: str, status: str) -> bool:
        """Обновить статус игрока"""
        def _update_status():
            self.ref.child('players').child(player_id).update({
                'status': status,
                'last_status_change': datetime.now().isoformat()
            })
            return True
        
        try:
            return self._safe_operation(_update_status) or False
        except Exception as e:
            logger.error(f"Ошибка обновления статуса игрока: {e}")
            return False
    
    # Методы для работы с комнатами
    def create_room(self, room_id: str, room_data: dict) -> bool:
        """Создать комнату"""
        def _create():
            self.ref.child('rooms').child(room_id).set(room_data)
            return True
        
        try:
            return self._safe_operation(_create) or False
        except Exception as e:
            logger.error(f"Ошибка создания комнаты: {e}")
            return False
    
    def get_room(self, room_id: str) -> Optional[dict]:
        """Получить информацию о комнате"""
        def _get():
            room_data = self.ref.child('rooms').child(room_id).get()
            return room_data
        
        try:
            return self._safe_operation(_get)
        except Exception as e:
            logger.error(f"Ошибка получения комнаты: {e}")
            return None
    
    def get_all_rooms(self) -> List[dict]:
        """Получить все комнаты"""
        def _get_all():
            rooms_data = self.ref.child('rooms').get()
            if rooms_data:
                return [{'id': room_id, **room_data} for room_id, room_data in rooms_data.items()]
            return []
        
        try:
            return self._safe_operation(_get_all) or []
        except Exception as e:
            logger.error(f"Ошибка получения всех комнат: {e}")
            return []
    
    def update_room(self, room_id: str, room_data: dict) -> bool:
        """Обновить информацию о комнате"""
        def _update():
            self.ref.child('rooms').child(room_id).update(room_data)
            return True
        
        try:
            return self._safe_operation(_update) or False
        except Exception as e:
            logger.error(f"Ошибка обновления комнаты: {e}")
            return False
    
    def delete_room(self, room_id: str) -> bool:
        """Удалить комнату"""
        def _delete():
            self.ref.child('rooms').child(room_id).delete()
            return True
        
        try:
            return self._safe_operation(_delete) or False
        except Exception as e:
            logger.error(f"Ошибка удаления комнаты: {e}")
            return False
    
    # Методы для работы с играми
    def create_game(self, game_id: str, game_data: dict) -> bool:
        """Создать игру"""
        def _create():
            self.ref.child('games').child(game_id).set(game_data)
            return True
        
        try:
            return self._safe_operation(_create) or False
        except Exception as e:
            logger.error(f"Ошибка создания игры: {e}")
            return False
    
    def get_game_info(self, game_id: str) -> Optional[dict]:
        """Получить информацию об игре"""
        def _get():
            game_data = self.ref.child('games').child(game_id).get()
            return game_data
        
        try:
            return self._safe_operation(_get)
        except Exception as e:
            logger.error(f"Ошибка получения информации об игре: {e}")
            return None
    
    def update_game_progress(self, game_id: str, round_num: int, question_num: int) -> bool:
        """Обновить прогресс игры"""
        def _update():
            self.ref.child('games').child(game_id).update({
                'current_round': round_num,
                'current_question': question_num
            })
            return True
        
        try:
            return self._safe_operation(_update) or False
        except Exception as e:
            logger.error(f"Ошибка обновления прогресса игры: {e}")
            return False
    
    def update_game_status(self, game_id: str, status: str) -> bool:
        """Обновить статус игры"""
        def _update():
            self.ref.child('games').child(game_id).update({'status': status})
            return True
        
        try:
            return self._safe_operation(_update) or False
        except Exception as e:
            logger.error(f"Ошибка обновления статуса игры: {e}")
            return False
    
    def submit_answer(self, game_id: str, round_num: int, question_num: int, player_id: str, answer: str) -> bool:
        """Отправить ответ"""
        def _submit():
            answer_path = f'games/{game_id}/rounds/{round_num}/questions/{question_num}/answers/{player_id}'
            self.ref.child(answer_path).set({
                'answer': answer,
                'timestamp': datetime.now().isoformat()
            })
            return True
        
        try:
            return self._safe_operation(_submit) or False
        except Exception as e:
            logger.error(f"Ошибка отправки ответа: {e}")
            return False
    
    def get_answer(self, game_id: str, round_num: int, question_num: int, player_id: str) -> Optional[str]:
        """Получить ответ игрока"""
        def _get():
            answer_path = f'games/{game_id}/rounds/{round_num}/questions/{question_num}/answers/{player_id}'
            answer_data = self.ref.child(answer_path).get()
            return answer_data.get('answer') if answer_data else None
        
        try:
            return self._safe_operation(_get)
        except Exception as e:
            logger.error(f"Ошибка получения ответа: {e}")
            return None
    
    def get_question_result(self, game_id: str, round_num: int, question_num: int) -> Optional[dict]:
        """Получить результат вопроса"""
        def _get():
            result_path = f'games/{game_id}/rounds/{round_num}/questions/{question_num}/results'
            return self.ref.child(result_path).get()
        
        try:
            return self._safe_operation(_get)
        except Exception as e:
            logger.error(f"Ошибка получения результата вопроса: {e}")
            return None
    
    def update_game_result(self, result_path: str, result_data: dict) -> bool:
        """Обновить результат игры"""
        def _update():
            self.ref.child(result_path).set(result_data)
            return True
        
        try:
            return self._safe_operation(_update) or False
        except Exception as e:
            logger.error(f"Ошибка обновления результата игры: {e}")
            return False
    
    # Методы для работы со статистикой игроков
    def update_player_stats(self, player_id: str, stats_data: dict) -> bool:
        """Обновить статистику игрока"""
        def _update_stats():
            # Получаем текущую статистику
            current_stats = self.ref.child('player_stats').child(player_id).get() or {}
            
            # Обновляем статистику
            if 'total_score' in stats_data:
                current_stats['total_score'] = current_stats.get('total_score', 0) + stats_data['total_score']
            
            if 'games_played' in stats_data:
                current_stats['games_played'] = current_stats.get('games_played', 0) + stats_data['games_played']
            
            if 'last_result' in stats_data:
                current_stats['last_result'] = stats_data['last_result']
                current_stats['last_played'] = datetime.now().isoformat()
            
            # Обновляем детальную статистику по результатам
            result_type = stats_data.get('last_result', '')
            if result_type:
                if 'results_count' not in current_stats:
                    current_stats['results_count'] = {}
                current_stats['results_count'][result_type] = current_stats['results_count'].get(result_type, 0) + 1
            
            # Сохраняем обновленную статистику
            self.ref.child('player_stats').child(player_id).update(current_stats)
            return True
        
        try:
            return self._safe_operation(_update_stats) or False
        except Exception as e:
            logger.error(f"Ошибка обновления статистики игрока: {e}")
            return False
    
    def get_player_stats(self, player_id: str) -> Optional[dict]:
        """Получить статистику игрока"""
        def _get_stats():
            stats = self.ref.child('player_stats').child(player_id).get()
            return stats
        
        try:
            return self._safe_operation(_get_stats)
        except Exception as e:
            logger.error(f"Ошибка получения статистики игрока: {e}")
            return None
    
    def get_top_players(self, limit: int = 10) -> List[dict]:
        """Получить топ игроков по очкам"""
        def _get_top():
            all_stats = self.ref.child('player_stats').get()
            if not all_stats:
                return []
            
            # Сортируем по total_score
            sorted_players = sorted(
                [(player_id, stats) for player_id, stats in all_stats.items()],
                key=lambda x: x[1].get('total_score', 0),
                reverse=True
            )
            
            # Получаем информацию об игроках
            top_players = []
            for player_id, stats in sorted_players[:limit]:
                player_info = self.ref.child('players').child(player_id).get()
                if player_info:
                    top_players.append({
                        'player_id': player_id,
                        'username': player_info.get('username', 'Unknown'),
                        'total_score': stats.get('total_score', 0),
                        'games_played': stats.get('games_played', 0),
                        'last_played': stats.get('last_played'),
                        'results_count': stats.get('results_count', {})
                    })
            
            return top_players
        
        try:
            return self._safe_operation(_get_top) or []
        except Exception as e:
            logger.error(f"Ошибка получения топ игроков: {e}")
            return []
    
    def get_player_game_history(self, player_id: str, limit: int = 10) -> List[dict]:
        """Получить историю игр игрока"""
        def _get_history():
            # Ищем игры, в которых участвовал игрок
            all_games = self.ref.child('games').get()
            if not all_games:
                return []
            
            player_games = []
            for game_id, game_data in all_games.items():
                if (game_data.get('player1_id') == player_id or 
                    game_data.get('player2_id') == player_id):
                    
                    # Определяем результат игрока
                    player_score = 0
                    opponent_score = 0
                    opponent_name = 'Unknown'
                    
                    if game_data.get('player1_id') == player_id:
                        player_score = game_data.get('scores', {}).get(player_id, 0)
                        opponent_id = game_data.get('player2_id')
                        opponent_name = game_data.get('player2_name', 'Unknown')
                        if opponent_id:
                            opponent_score = game_data.get('scores', {}).get(opponent_id, 0)
                    else:
                        player_score = game_data.get('scores', {}).get(player_id, 0)
                        opponent_id = game_data.get('player1_id')
                        opponent_name = game_data.get('player1_name', 'Unknown')
                        if opponent_id:
                            opponent_score = game_data.get('scores', {}).get(opponent_id, 0)
                    
                    player_games.append({
                        'game_id': game_id,
                        'created_at': game_data.get('created_at'),
                        'status': game_data.get('status'),
                        'player_score': player_score,
                        'opponent_score': opponent_score,
                        'opponent_name': opponent_name,
                        'result': 'win' if player_score > opponent_score else 'lose' if player_score < opponent_score else 'draw'
                    })
            
            # Сортируем по дате (новые первые)
            player_games.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            return player_games[:limit]
        
        try:
            return self._safe_operation(_get_history) or []
        except Exception as e:
            logger.error(f"Ошибка получения истории игр: {e}")
            return []
