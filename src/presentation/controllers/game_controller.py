"""
Контроллер для управления игровой логикой и интерфейсом
"""
import asyncio
import logging
from typing import Optional, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QMessageBox

from ..views.game_view import GameView
from ...business.services.game_service import GameService, AnswerType
from ...business.services.matchmaking_service import MatchmakingService

logger = logging.getLogger(__name__)

class GameController(QObject):
    """Контроллер управления игрой"""
    
    # Сигналы
    game_started = pyqtSignal(str, str, str)  # game_id, player_id, opponent_name
    game_finished = pyqtSignal(str, dict)     # game_id, results
    back_to_menu = pyqtSignal()
    error_occurred = pyqtSignal(str)           # error_message
    
    def __init__(self, database, player_id: str, player_name: str):
        super().__init__()
        self.database = database
        self.player_id = player_id
        self.player_name = player_name
        self.current_game_id = None
        
        # Сервисы
        self.game_service = GameService(database)
        self.matchmaking_service = MatchmakingService(database)
        
        # Представление
        self.view = GameView()
        self.setup_connections()
        
        # Таймеры для проверки обновлений
        self.answer_check_timer = QTimer()
        self.answer_check_timer.timeout.connect(self.check_opponent_answer)
        self.answer_check_timer.setInterval(2000)  # Проверять каждые 2 секунды
        
        self.game_state_timer = QTimer()
        self.game_state_timer.timeout.connect(self.check_game_state)
        self.game_state_timer.setInterval(5000)  # Проверять каждые 5 секунд
        
    def setup_connections(self):
        """Настройка соединений сигналов"""
        self.view.answer_submitted.connect(self.on_answer_submitted)
        self.view.game_finished.connect(self.on_game_finished)
        self.view.back_to_menu.connect(self.back_to_menu.emit)
        
    def get_view(self) -> GameView:
        """Получить представление"""
        return self.view
        
    async def start_matchmaking(self):
        """Начать поиск игры"""
        try:
            self.view.update_opponent_status("Поиск соперника...")
            
            # Проверяем, есть ли онлайн игроки
            online_players = self.database.get_online_players()
            
            # Исключаем себя из списка
            other_players = [p for p in online_players if p.id != self.player_id]
            
            if not other_players:
                QMessageBox.information(
                    self.view, 
                    "Поиск игры", 
                    "😔 Сейчас нет других игроков в сети.\\n\\nПопробуйте позже или пригласите друзей!"
                )
                self.back_to_menu.emit()
                return
            
            # Начинаем поиск
            game_id = await self.matchmaking_service.start_matchmaking(self.player_id, self.player_name)
            
            if game_id:
                # Игра найдена
                await self.start_game(game_id)
            else:
                # Добавляем в очередь ожидания
                self.view.update_opponent_status("В очереди ожидания...")
                QMessageBox.information(
                    self.view,
                    "В очереди",
                    "🕐 Вы добавлены в очередь ожидания.\\n\\nСистема найдет вам соперника автоматически."
                )
                # Запускаем проверку статуса матчмейкинга
                self.start_matchmaking_check()
                
        except Exception as e:
            logger.error(f"Error in matchmaking: {e}")
            QMessageBox.critical(
                self.view,
                "Ошибка поиска игры",
                f"❌ Не удалось начать поиск игры:\\n\\n{e}\\n\\nПопробуйте позже."
            )
            self.back_to_menu.emit()
            
    def start_matchmaking_check(self):
        """Начать проверку статуса матчмейкинга"""
        # Здесь можно добавить периодическую проверку
        # Пока просто ждем, пока игра не будет найдена
        pass
        
    async def start_game(self, game_id: str):
        """Начать игру"""
        try:
            self.current_game_id = game_id
            
            # Получаем информацию об игре
            game_info = await self.database.get_game_info(game_id)
            if not game_info:
                QMessageBox.critical(
                    self.view,
                    "Ошибка игры",
                    "❌ Не удалось получить информацию об игре.\\n\\nПопробуйте начать новую игру."
                )
                self.back_to_menu.emit()
                return
                
            # Определяем ID и имя противника
            if game_info['player1_id'] == self.player_id:
                opponent_id = game_info['player2_id']
                opponent_name = game_info.get('player2_name', 'Соперник')
            else:
                opponent_id = game_info['player1_id']
                opponent_name = game_info.get('player1_name', 'Соперник')
                
            # Показываем сообщение о начале игры
            QMessageBox.information(
                self.view,
                "Игра началась!",
                f"🎮 Игра началась!\\n\\nВаш соперник: {opponent_name}\\n\\nУдачи!"
            )
                
            # Начинаем игру в представлении
            self.view.start_game(game_id, self.player_id, opponent_name)
            
            # Показываем первый вопрос
            await self.show_current_question()
            
            # Запускаем таймеры
            self.answer_check_timer.start()
            self.game_state_timer.start()
            
            # Излучаем сигнал о начале игры
            self.game_started.emit(game_id, self.player_id, opponent_name)
            
        except Exception as e:
            logger.error(f"Error starting game: {e}")
            QMessageBox.critical(
                self.view,
                "Ошибка начала игры",
                f"❌ Не удалось начать игру:\\n\\n{e}\\n\\nПопробуйте позже."
            )
            self.back_to_menu.emit()
            
    async def show_current_question(self):
        """Показать текущий вопрос"""
        try:
            if not self.current_game_id:
                return
                
            # Получаем информацию об игре
            game_info = await self.database.get_game_info(self.current_game_id)
            if not game_info:
                return
                
            current_round = game_info.get('current_round', 1)
            current_question = game_info.get('current_question', 1)
            
            # Обновляем в представлении
            self.view.current_round = current_round
            self.view.current_question = current_question
            self.view.update_progress()
            
            # Получаем вопрос
            question_data = await self.game_service.get_question(current_round, current_question)
            if question_data:
                self.view.show_question(question_data)
                
        except Exception as e:
            logger.error(f"Error showing current question: {e}")
            
    async def on_answer_submitted(self, game_id: str, round_num: int, question_num: int, answer: str):
        """Обработка отправленного ответа"""
        try:
            answer_type = AnswerType.COOPERATE if answer == 'cooperate' else AnswerType.BETRAY
            
            # Отправляем ответ
            success = await self.game_service.submit_answer(game_id, self.player_id, round_num, question_num, answer_type)
            
            if success:
                # Ответ успешно отправлен и оба игрока ответили
                await self.show_answer_results(round_num, question_num)
            else:
                # Ждем ответа соперника
                self.view.update_opponent_status("Ожидание ответа соперника...")
                
        except Exception as e:
            logger.error(f"Error submitting answer: {e}")
            QMessageBox.warning(
                self.view,
                "Ошибка ответа",
                f"⚠️ Не удалось отправить ответ:\\n\\n{e}\\n\\nПопробуйте ответить еще раз."
            )
            self.view.enable_answer_buttons()
    
    def on_game_finished(self, game_id: str):
        """Обработка завершения игры"""
        try:
            # Останавливаем таймеры
            self.answer_check_timer.stop()
            self.game_state_timer.stop()
            
            # Показываем финальные результаты
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.finish_game())
            finally:
                loop.close()
            
        except Exception as e:
            logger.error(f"Error in on_game_finished: {e}")
            self.back_to_menu.emit()
            
    async def check_opponent_answer(self):
        """Проверить ответ соперника"""
        try:
            if not self.current_game_id or self.view.waiting_for_opponent:
                return
                
            # Получаем информацию об игре
            game_info = await self.database.get_game_info(self.current_game_id)
            if not game_info:
                return
                
            current_round = game_info.get('current_round', 1)
            current_question = game_info.get('current_question', 1)
            
            # Проверяем, ответил ли соперник
            opponent_id = game_info['player1_id'] if self.player_id == game_info['player2_id'] else game_info['player2_id']
            
            opponent_answer = await self.database.get_answer(self.current_game_id, current_round, current_question, opponent_id)
            
            if opponent_answer:
                # Соперник ответил - показываем результаты
                await self.show_answer_results(current_round, current_question)
                
        except Exception as e:
            logger.error(f"Error checking opponent answer: {e}")
            
    async def show_answer_results(self, round_num: int, question_num: int):
        """Показать результаты ответов"""
        try:
            # Получаем ответы обоих игроков
            your_answer = await self.database.get_answer(self.current_game_id, round_num, question_num, self.player_id)
            
            game_info = await self.database.get_game_info(self.current_game_id)
            opponent_id = game_info['player1_id'] if self.player_id == game_info['player2_id'] else game_info['player2_id']
            opponent_answer = await self.database.get_answer(self.current_game_id, round_num, question_num, opponent_id)
            
            if your_answer and opponent_answer:
                # Получаем результаты
                results = await self.database.get_question_result(self.current_game_id, round_num, question_num)
                
                if results:
                    your_score = results.get(f'player_{self.player_id}_score', 0)
                    opponent_score = results.get(f'player_{opponent_id}_score', 0)
                    
                    # Показываем результаты в представлении
                    self.view.show_answer_results(your_answer, opponent_answer, your_score, opponent_score)
                    
        except Exception as e:
            logger.error(f"Error showing answer results: {e}")
            
    async def next_question(self):
        """Перейти к следующему вопросу"""
        try:
            if not self.current_game_id:
                return
                
            # Получаем информацию об игре
            game_info = await self.database.get_game_info(self.current_game_id)
            if not game_info:
                return
                
            current_round = game_info.get('current_round', 1)
            current_question = game_info.get('current_question', 1)
            
            total_questions = 10 if current_round < 3 else 13
            
            if current_question < total_questions:
                # Переходим к следующему вопросу
                new_question = current_question + 1
                await self.database.update_game_progress(self.current_game_id, current_round, new_question)
                await self.show_current_question()
            else:
                # Раунд завершен
                await self.next_round()
                
        except Exception as e:
            logger.error(f"Error in next question: {e}")
            
    async def next_round(self):
        """Перейти к следующему раунду"""
        try:
            if not self.current_game_id:
                return
                
            # Получаем информацию об игре
            game_info = await self.database.get_game_info(self.current_game_id)
            if not game_info:
                return
                
            current_round = game_info.get('current_round', 1)
            
            if current_round < 3:
                # Переходим к следующему раунду
                new_round = current_round + 1
                await self.database.update_game_progress(self.current_game_id, new_round, 1)
                await self.show_current_question()
            else:
                # Игра завершена
                await self.finish_game()
                
        except Exception as e:
            logger.error(f"Error in next round: {e}")
            
    async def finish_game(self):
        """Завершить игру"""
        try:
            if not self.current_game_id:
                return
                
            # Останавливаем таймеры
            self.answer_check_timer.stop()
            self.game_state_timer.stop()
            
            # Получаем финальные результаты
            results = await self.game_service.get_game_results(self.current_game_id)
            
            # Обновляем статус игры
            await self.database.update_game_status(self.current_game_id, "finished")
            
            # Обновляем статусы игроков
            game_info = await self.database.get_game_info(self.current_game_id)
            if game_info:
                await self.database.update_player_status(game_info['player1_id'], "online")
                await self.database.update_player_status(game_info['player2_id'], "online")
            
            # Показываем результаты
            self.show_final_results(results)
            
            # Излучаем сигнал о завершении игры
            self.game_finished.emit(self.current_game_id, results or {})
            
        except Exception as e:
            logger.error(f"Error finishing game: {e}")
            
    def show_final_results(self, results: Dict):
        """Показать финальные результаты"""
        try:
            if not results:
                QMessageBox.information(self.view, "Игра завершена", "Игра завершена!")
                return
                
            # Формируем сообщение с результатами
            player_score = results.get(f'player_{self.player_id}_total_score', 0)
            opponent_score = results.get('opponent_total_score', 0)
            
            if player_score > opponent_score:
                result_text = "🎉 Вы победили!"
            elif player_score < opponent_score:
                result_text = "😔 Вы проиграли"
            else:
                result_text = "🤝 Ничья!"
                
            message = f"{result_text}\\n\\nВаши очки: {player_score}\\nОчки соперника: {opponent_score}"
            
            QMessageBox.information(self.view, "Игра завершена", message)
            
        except Exception as e:
            logger.error(f"Error showing final results: {e}")
            
    async def check_game_state(self):
        """Проверить состояние игры"""
        try:
            if not self.current_game_id:
                return
                
            # Проверяем, не отключился ли соперник
            game_info = await self.database.get_game_info(self.current_game_id)
            if not game_info:
                return
                
            # Проверяем статус игры
            if game_info.get('status') == 'finished':
                await self.finish_game()
                return
                
            # Проверяем статус соперника
            opponent_id = game_info['player1_id'] if self.player_id == game_info['player2_id'] else game_info['player2_id']
            opponent_status = await self.database.get_player_status(opponent_id)
            
            if opponent_status == 'offline' or opponent_status == 'disconnected':
                QMessageBox.warning(
                    self.view,
                    "Соперник отключился",
                    "😔 Ваш соперник отключился от игры.\\n\\nИгра завершена."
                )
                await self.leave_game()
                
        except Exception as e:
            logger.error(f"Error checking game state: {e}")
            
    async def leave_game(self):
        """Покинуть игру"""
        try:
            reply = QMessageBox.question(
                self.view,
                "Покинуть игру",
                "🚪 Вы уверены, что хотите покинуть игру?\\n\\nТекущий прогресс будет потерян.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                return
                
            # Останавливаем таймеры
            self.answer_check_timer.stop()
            self.game_state_timer.stop()
            
            # Покидаем игру через сервис матчмейкинга
            if self.current_game_id:
                await self.matchmaking_service.leave_game(self.player_id)
                self.current_game_id = None
                
            # Возвращаемся в меню
            self.back_to_menu.emit()
            
        except Exception as e:
            logger.error(f"Error leaving game: {e}")
            QMessageBox.warning(
                self.view,
                "Ошибка",
                f"⚠️ Не удалось покинуть игру:\\n\\n{e}\\n\\nВозвращаемся в меню..."
            )
            self.back_to_menu.emit()
            
    def cleanup(self):
        """Очистка ресурсов"""
        try:
            self.answer_check_timer.stop()
            self.game_state_timer.stop()
        except:
            pass
