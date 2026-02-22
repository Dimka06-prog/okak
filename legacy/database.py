import sqlite3
import datetime
from typing import List, Dict, Optional

class GameDatabase:
    def __init__(self, db_name="game_database.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Таблица игроков
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_online TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_online BOOLEAN DEFAULT 0,
                total_score INTEGER DEFAULT 0,
                games_played INTEGER DEFAULT 0
            )
        ''')
        
        # Таблица игр
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player1_id INTEGER,
                player2_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (player1_id) REFERENCES players (id),
                FOREIGN KEY (player2_id) REFERENCES players (id)
            )
        ''')
        
        # Таблица раундов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rounds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER,
                round_number INTEGER,
                player1_choice TEXT,
                player2_choice TEXT,
                player1_score INTEGER DEFAULT 0,
                player2_score INTEGER DEFAULT 0,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (game_id) REFERENCES games (id)
            )
        ''')
        
        # Таблица вопросов в раундах
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS round_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                round_id INTEGER,
                question_number INTEGER,
                player1_choice TEXT,
                player2_choice TEXT,
                FOREIGN KEY (round_id) REFERENCES rounds (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_player(self, username: str, password: str) -> bool:
        """Регистрация нового игрока"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO players (username, password) VALUES (?, ?)", 
                         (username, password))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def login_player(self, username: str, password: str) -> Optional[int]:
        """Авторизация игрока"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM players WHERE username = ? AND password = ?", 
                      (username, password))
        result = cursor.fetchone()
        
        if result:
            player_id = result[0]
            # Обновляем статус онлайн
            cursor.execute("UPDATE players SET is_online = 1, last_online = CURRENT_TIMESTAMP WHERE id = ?", 
                          (player_id,))
            conn.commit()
            conn.close()
            return player_id
        
        conn.close()
        return None
    
    def logout_player(self, player_id: int):
        """Выход игрока"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("UPDATE players SET is_online = 0 WHERE id = ?", (player_id,))
        conn.commit()
        conn.close()
    
    def get_online_players(self, exclude_player_id: int = None) -> List[Dict]:
        """Получение списка онлайн игроков"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        query = "SELECT id, username, total_score, games_played FROM players WHERE is_online = 1"
        params = []
        
        if exclude_player_id:
            query += " AND id != ?"
            params.append(exclude_player_id)
        
        cursor.execute(query, params)
        players = []
        
        for row in cursor.fetchall():
            players.append({
                'id': row[0],
                'username': row[1],
                'total_score': row[2],
                'games_played': row[3]
            })
        
        conn.close()
        return players
    
    def create_game(self, player1_id: int, player2_id: int) -> int:
        """Создание новой игры"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO games (player1_id, player2_id) VALUES (?, ?)", 
                      (player1_id, player2_id))
        game_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return game_id
    
    def create_round(self, game_id: int, round_number: int) -> int:
        """Создание нового раунда"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO rounds (game_id, round_number) VALUES (?, ?)", 
                      (game_id, round_number))
        round_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return round_id
    
    def save_question_choice(self, round_id: int, question_number: int, 
                            player_id: int, choice: str):
        """Сохранение выбора игрока в вопросе"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Определяем, какой игрок (1 или 2)
        cursor.execute("SELECT game_id FROM rounds WHERE id = ?", (round_id,))
        game_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT player1_id, player2_id FROM games WHERE id = ?", (game_id,))
        player1_id, player2_id = cursor.fetchone()
        
        if player_id == player1_id:
            cursor.execute('''
                INSERT OR REPLACE INTO round_questions 
                (round_id, question_number, player1_choice) 
                VALUES (?, ?, ?)
            ''', (round_id, question_number, choice))
        else:
            cursor.execute('''
                INSERT OR REPLACE INTO round_questions 
                (round_id, question_number, player2_choice) 
                VALUES (?, ?, ?)
            ''', (round_id, question_number, choice))
        
        conn.commit()
        conn.close()
    
    def get_player_stats(self, player_id: int) -> Dict:
        """Получение статистики игрока"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute("SELECT username, total_score, games_played FROM players WHERE id = ?", 
                      (player_id,))
        result = cursor.fetchone()
        
        if result:
            stats = {
                'username': result[0],
                'total_score': result[1],
                'games_played': result[2]
            }
        else:
            stats = {}
        
        conn.close()
        return stats
