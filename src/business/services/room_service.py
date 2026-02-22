"""
Сервис для управления игровыми комнатами
"""
import asyncio
import uuid
from typing import Optional, Dict, List, Any
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class RoomStatus(Enum):
    WAITING = "waiting"      # Ожидание игроков
    READY = "ready"         # Все игроки готовы
    PLAYING = "playing"     # Игра идет
    FINISHED = "finished"   # Игра завершена

class RoomService:
    """Сервис для управления игровыми комнатами"""
    
    def __init__(self, database):
        self.database = database
        
    def create_room(self, creator_id: str, creator_name: str, room_name: str = None) -> str:
        """Создать новую комнату"""
        try:
            room_id = str(uuid.uuid4())
            
            if not room_name:
                room_name = f"Комната {room_id[:8]}"
            
            room_data = {
                'id': room_id,
                'name': room_name,
                'creator_id': creator_id,
                'creator_name': creator_name,
                'players': {
                    creator_id: {
                        'id': creator_id,
                        'name': creator_name,
                        'ready': False,
                        'joined_at': datetime.now().isoformat()
                    }
                },
                'max_players': 2,
                'status': RoomStatus.WAITING.value,
                'created_at': datetime.now().isoformat(),
                'game_id': None
            }
            
            self.database.create_room(room_id, room_data)
            self.database.update_player_status(creator_id, "in_room")
            
            logger.info(f"Room {room_id} created by {creator_name}")
            return room_id
            
        except Exception as e:
            logger.error(f"Error creating room: {e}")
            raise
    
    def get_available_rooms(self) -> List[Dict]:
        """Получить список доступных комнат"""
        try:
            rooms = self.database.get_all_rooms()
            available_rooms = []
            
            for room in rooms:
                if (room['status'] == RoomStatus.WAITING.value and 
                    len(room['players']) < room['max_players']):
                    available_rooms.append({
                        'id': room['id'],
                        'name': room['name'],
                        'creator_name': room['creator_name'],
                        'players_count': len(room['players']),
                        'max_players': room['max_players'],
                        'created_at': room['created_at']
                    })
            
            return available_rooms
            
        except Exception as e:
            logger.error(f"Error getting available rooms: {e}")
            return []
    
    def join_room(self, room_id: str, player_id: str, player_name: str) -> bool:
        """Присоединиться к комнате"""
        try:
            room = self.database.get_room(room_id)
            if not room:
                return False
            
            if room['status'] != RoomStatus.WAITING.value:
                return False
            
            if len(room['players']) >= room['max_players']:
                return False
            
            if player_id in room['players']:
                return False
            
            # Добавляем игрока в комнату
            room['players'][player_id] = {
                'id': player_id,
                'name': player_name,
                'ready': False,
                'joined_at': datetime.now().isoformat()
            }
            
            self.database.update_room(room_id, room)
            self.database.update_player_status(player_id, "in_room")
            
            logger.info(f"Player {player_name} joined room {room_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error joining room: {e}")
            return False
    
    def leave_room(self, room_id: str, player_id: str) -> bool:
        """Покинуть комнату"""
        try:
            room = self.database.get_room(room_id)
            if not room:
                return False
            
            if player_id not in room['players']:
                return False
            
            # Удаляем игрока из комнаты
            del room['players'][player_id]
            
            # Если комната пустая, удаляем ее
            if len(room['players']) == 0:
                self.database.delete_room(room_id)
                logger.info(f"Room {room_id} deleted (empty)")
            else:
                # Если вышел создатель, передаем права другому игроку
                if room['creator_id'] == player_id:
                    new_creator_id = next(iter(room['players']))
                    room['creator_id'] = new_creator_id
                    room['creator_name'] = room['players'][new_creator_id]['name']
                
                self.database.update_room(room_id, room)
            
            self.database.update_player_status(player_id, "online")
            
            logger.info(f"Player {player_id} left room {room_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error leaving room: {e}")
            return False
    
    def set_player_ready(self, room_id: str, player_id: str, ready: bool = True) -> bool:
        """Установить готовность игрока"""
        try:
            room = self.database.get_room(room_id)
            if not room:
                return False
            
            if player_id not in room['players']:
                return False
            
            room['players'][player_id]['ready'] = ready
            self.database.update_room(room_id, room)
            
            logger.info(f"Player {player_id} ready status set to {ready} in room {room_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting player ready: {e}")
            return False
    
    def start_game(self, room_id: str, player_id: str) -> Optional[str]:
        """Начать игру (только создатель комнаты)"""
        try:
            room = self.database.get_room(room_id)
            if not room:
                return None
            
            # Проверяем, что создатель комнаты запускает игру
            if room['creator_id'] != player_id:
                logger.warning(f"Only creator can start game. Creator: {room['creator_id']}, Player: {player_id}")
                return None
            
            # Проверяем, что достаточно игроков для игры
            if len(room['players']) < 2:
                logger.warning(f"Not enough players to start game. Players: {len(room['players'])}")
                return None
            
            # Проверяем, что все игроки готовы
            for player in room['players'].values():
                if not player['ready']:
                    logger.warning(f"Not all players are ready")
                    return None
            
            # Создаем игру
            from .game_service import GameService
            game_service = GameService(self.database)
            
            players = list(room['players'].keys())
            game_id = game_service.create_game(players[0], players[1])
            
            if game_id:
                # Обновляем статус комнаты
                room['status'] = RoomStatus.PLAYING.value
                room['game_id'] = game_id
                self.database.update_room(room_id, room)
                
                logger.info(f"Game {game_id} started in room {room_id}")
                return game_id
            
            return None
            
        except Exception as e:
            logger.error(f"Error starting game: {e}")
            return None
    
    def get_room_info(self, room_id: str) -> Optional[Dict]:
        """Получить информацию о комнате"""
        try:
            return self.database.get_room(room_id)
        except Exception as e:
            logger.error(f"Error getting room info: {e}")
            return None
    
    def cleanup_inactive_rooms(self):
        """Удалить комнаты, бездействующие более 3 минут"""
        try:
            rooms = self.database.get_all_rooms()
            current_time = datetime.now()
            rooms_to_delete = []
            
            for room in rooms:
                # Пропускаем комнаты с игрой
                if room['status'] != RoomStatus.WAITING.value:
                    continue
                
                # Проверяем время создания
                created_at = datetime.fromisoformat(room['created_at'])
                time_diff = (current_time - created_at).total_seconds()
                
                # Если комнате больше 3 минут и она пустая или только с создателем
                if time_diff > 180:  # 3 минуты = 180 секунд
                    if len(room['players']) <= 1:
                        rooms_to_delete.append(room['id'])
            
            # Удаляем найденные комнаты
            for room_id in rooms_to_delete:
                self.database.delete_room(room_id)
                logger.info(f"Удалена неактивная комната: {room_id}")
            
            return len(rooms_to_delete)
            
        except Exception as e:
            logger.error(f"Error cleaning up inactive rooms: {e}")
            return 0
