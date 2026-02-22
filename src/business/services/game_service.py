"""
Игровая логика для управления раундами и вопросами
"""
import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from datetime import datetime

from ..data.repositories.player_repository import PlayerRepository

logger = logging.getLogger(__name__)

class AnswerType(Enum):
    COOPERATE = "cooperate"
    BETRAY = "betray"

class QuestionResult:
    """Результат ответа на вопрос"""
    def __init__(self, player1_answer: AnswerType, player2_answer: AnswerType):
        self.player1_answer = player1_answer
        self.player2_answer = player2_answer
        
    def _calculate_results(self, action1: AnswerType, action2: AnswerType) -> Dict:
        """Рассчитать результаты по матрице дилеммы заключенного"""
        # Матрица выплат:
        # C,C = (3,3) - оба сотрудничают
        # C,D = (0,5) - первый сотрудничает, второй предает  
        # D,C = (5,0) - первый предает, второй сотрудничает
        # D,D = (1,1) - оба предают
        
        if action1 == AnswerType.COOPERATE and action2 == AnswerType.COOPERATE:
            return {
                'player1_score': 3,
                'player2_score': 3,
                'result': 'cooperate_cooperate',
                'description': 'Оба сотрудничали'
            }
        elif action1 == AnswerType.COOPERATE and action2 == AnswerType.BETRAY:
            return {
                'player1_score': 0,
                'player2_score': 5,
                'result': 'cooperate_betray',
                'description': 'Игрок 1 сотрудничал, Игрок 2 предал'
            }
        elif action1 == AnswerType.BETRAY and action2 == AnswerType.COOPERATE:
            return {
                'player1_score': 5,
                'player2_score': 0,
                'result': 'betray_cooperate',
                'description': 'Игрок 1 предал, Игрок 2 сотрудничал'
            }
        elif action1 == AnswerType.BETRAY and action2 == AnswerType.BETRAY:
            return {
                'player1_score': 1,
                'player2_score': 1,
                'result': 'betray_betray',
                'description': 'Оба предали'
            }
        else:
            raise ValueError("Действия должны быть COOPERATE или BETRAY")

    def get_scores(self) -> Tuple[int, int]:
        """Получить очки для обоих игроков"""
        results = self._calculate_results(self.player1_answer, self.player2_answer)
        return results['player1_score'], results['player2_score']

class GameService:
    """Сервис управления игровой логикой"""
    
    def __init__(self, database):
        self.database = database
        self.game_questions = self._generate_questions()
        
    def _generate_questions(self) -> Dict[int, List[Dict]]:
        """Генерация вопросов для игры"""
        questions = {
            1: [],  # Раунд 1 - 10 вопросов
            2: [],  # Раунд 2 - 10 вопросов  
            3: []   # Раунд 3 - 13 вопросов
        }
        
        # База вопросов для дилеммы заключенного
        base_questions = [
            {
                "text": "Вы и ваш партнер пойманы за преступлением. У вас есть выбор: сотрудничать с полицией или молчать.",
                "context": "Если оба молчите - по 1 году. Если один предает, а другой молчит - предатель выходит свободным, молчун получает 5 лет. Если оба предают - по 3 года."
            },
            {
                "text": "Два конкурента могут договориться о ценах или начать ценовую войну.",
                "context": "Если оба договорятся - хорошая прибыль для обоих. Если один нарушит договор, а другой нет - нарушитель получает сверхприбыль. Если оба нарушат - низкая прибыль для всех."
            },
            {
                "text": "Вы и коллега работаете над проектом. Можно помочь друг другу или работать только в своих интересах.",
                "context": "Если оба помогут - отличный результат и премия для обоих. Если один помогает, а другой нет - помогающий теряет время, другой получает всю награду. Если оба не помогают - средний результат."
            },
            {
                "text": "Две страны могут сократить вооружения или продолжить гонку вооружений.",
                "context": "Если обе сократят - мир и экономия. Если одна сокращает, а другая нет - сокращающая становится уязвимой. Если обе продолжают - дорогая гонка вооружений."
            },
            {
                "text": "Два друга могут честно разделить находку или попытаться обмануть друг друга.",
                "context": "Если оба честны - поровну всем. Если один честен, а другой нет - нечестный забирает всё. Если оба нечестны - находку конфискуют."
            },
            {
                "text": "Соседи могут договориться о тишине или каждый будет делать что хочет.",
                "context": "Если оба соблюдают тишину - комфорт для всех. Если один шумит, а другой нет - шумящий получает удовольствие, другой страдает. Если оба шумят - все страдают от шума."
            },
            {
                "text": "Две компании могут поделиться рынком или бороться за монополию.",
                "context": "Если поделятся - стабильная прибыль для обеих. Если одна борется, а другая нет - борющаяся получает большую долю. Если обе борются - высокие издержки и неопределенность."
            },
            {
                "text": "Пассажиры могут соблюдать очередь или пытаться прорваться вперед.",
                "context": "Если все в очереди - справедливость для всех. Если один прыгает, а другие нет - прыгнувший экономит время. Если все прыгают - хаос и задержки."
            },
            {
                "text": "Фермеры могут договориться об объемах урожая или каждый выращивает сколько хочет.",
                "context": "Если договорятся - стабильные цены. Если один нарушает, а другие нет - нарушитель получает сверхприбыль. Если все нарушают - падение цен."
            },
            {
                "text": "Студенты могут честно выполнять тест или пытаться списать.",
                "context": "Если все честны - справедливые оценки. Если один списывает, а другие нет - списывающий получает высокую оценку. Если все списывают - возможные санкции."
            },
            {
                "text": "Водители могут соблюдать правила дорожного движения или нарушать их.",
                "context": "Если все соблюдают - безопасность и порядок. Если один нарушает, а другие нет - нарушитель едет быстрее. Если все нарушают - хаос и аварии."
            },
            {
                "text": "Торговцы могут честно торговать или обманывать покупателей.",
                "context": "Если все честны - доверие и стабильный бизнес. Если один обманывает, а другие нет - обманщик получает больше прибыли. Если все обманывают - потеря доверия и банкротство."
            },
            {
                "text": "Соседи по общежитию могут поддерживать чистоту или мусорить.",
                "context": "Если все убирают - чистота для всех. Если один мусорит, а другие нет - мусорящий экономит усилия. Если все мусорят - антисанитария."
            },
            {
                "text": "Спортсмены могут играть честно или использовать допинг.",
                "context": "Если все честны - справедливая конкуренция. Если один использует допинг, а другие нет - преимущество для допингового. Если все используют - вред здоровью и дисквалификация."
            },
            {
                "text": "Партнеры по бизнесу могут инвестировать в качество или экономить.",
                "context": "если оба инвестируют - премиум-продукт и высокая прибыль. Если один экономит, а другой нет - экономящий получает больше прибыли сейчас. Если оба экономят - потеря репутации."
            },
            {
                "text": "Друзья могут поддерживать друг друга в трудную минуту или позаботиться только о себе.",
                "context": "Если оба поддержат - взаимопомощь и крепкая дружба. Если один поддерживает, а другой нет - поддерживающий тратит ресурсы. Если оба позаботятся о себе - потеря дружбы."
            },
            {
                "text": "Коллеги могут делиться информацией или скрывать ее.",
                "context": "Если все делятся - эффективная работа для всех. Если один скрывает, а другие делятся - скрывающий получает преимущество. Если все скрывают - inefficiency."
            },
            {
                "text": "Участники аукциона могут договориться о ценах или конкурировать.",
                "context": "Если договорятся - низкие цены для всех. Если один нарушает, а другие нет - нарушитель получает товар дешево. Если все конкурируют - высокие цены для всех."
            },
            {
                "text": "Соседние страны могут открыть границы или закрыть их.",
                "context": "Если откроют все - торговля и туризм для всех. Если одна открывает, а другие нет - открытая получает преимущества. Если закрывают все - изоляция."
            },
            {
                "text": "Пользователи соцсетей могут быть вежливыми или токсичными.",
                "context": "Если все вежливы - приятная коммуникация. Если один токсичный, а другие вежливы - токсичный получает внимание. Если все токсичны - токсичная среда."
            },
            {
                "text": "Работники могут работать усердно или отлынивать.",
                "context": "Если все работают усердно - успех компании и премии. Если один отлынивает, а другие работают - отлынивающий получает зарплату без усилий. Если все отлынивают - банкротство компании."
            },
            {
                "text": "Покупатели могут уважать очередь или требовать обслуживания вне очереди.",
                "context": "Если все в очереди - справедливость. Если один требует, а другие нет - требующий обслуживается быстрее. Если все требуют - хаос."
            },
            {
                "text": "Участники группы проекта могут работать вместе или саботировать работу других.",
                "context": "Если все работают вместе - отличный результат. Если один саботирует, а другие работают - саботирующий получает преимущества. Если все саботируют - провал проекта."
            },
            {
                "text": "Владельцы домашних животных могут убирать за своими животными или игнорировать.",
                "context": "Если все убирают - чистота. Если один не убирает, а другие убирают - неубирающий экономит усилия. Если все не убирают - грязь везде."
            },
            {
                "text": "Пассажиры транспорта могут уступать места или занимать их.",
                "context": "Если все уступают - вежливость. Если один не уступает, а другие уступают - неуступающий получает место. Если все не уступают - конфликты."
            },
            {
                "text": "Дети могут делиться игрушками или драться за них.",
                "context": "Если все делятся - веселье для всех. Если один не делится, а другие делятся - неделяющийся получает все игрушки. Если все не делятся - конфликты и слезы."
            },
            {
                "text": "Водители на парковке могут парковаться корректно или занимать два места.",
                "context": "Если все паркуются корректно - места для всех. Если один занимает два места, а другие нет - занимающий имеет удобство. Если все занимают по два места - нехватка мест."
            },
            {
                "text": "Посетители кафе могут убирать за собой или оставлять мусор.",
                "context": "Если все убирают - чистота и хороший сервис. Если один не убирает, а другие убирают - неубирающий экономит время. Если все не убирают - грязное кафе."
            },
            {
                "text": "Соседи по лестничной клетке могут поддерживать порядок или игнорировать.",
                "context": "Если все поддерживают - уют для всех. Если один игнорирует, а другие поддерживают - игнорирующий экономит усилия. Если все игнорируют - беспорядок."
            },
            {
                "text": "Участники онлайн-игры могут играть честно или использовать читы.",
                "context": "Если все честны - сбалансированная игра. Если один использует читы, а другие нет - читер получает преимущество. Если все используют читы - игра теряет смысл."
            },
            {
                "text": "Покупатели в магазине могут уважать товар или портить его.",
                "context": "Если все уважают - качественный товар для всех. Если один портит, а другие нет - портящий получает удовлетворение. Если все портят - убытки для магазина."
            },
            {
                "text": "Работники офиса могут поддерживать чистоту на кухне или мусорить.",
                "context": "Если все убирают - приятная обстановка. Если один мусорит, а другие убирают - мусорящий экономит время. Если все мусорят - антисанитария."
            },
            {
                "text": "Пешеходы могут соблюдать правила перехода или переходить где попало.",
                "context": "Если все соблюдают - безопасность. Если один нарушает, а другие соблюдают - нарушитель экономит время. Если все нарушают - хаос и аварии."
            }
        ]
        
        # Распределяем вопросы по раундам
        random.shuffle(base_questions)
        
        # Раунд 1 - первые 10 вопросов
        questions[1] = base_questions[:10]
        
        # Раунд 2 - следующие 10 вопросов  
        questions[2] = base_questions[10:20]
        
        # Раунд 3 - оставшиеся 13 вопросов
        questions[3] = base_questions[20:33]
        
        return questions
    
    async def create_game(self, player_ids: List[str], player_names: List[str], settings: Dict = None) -> str:
        """Создать новую игру"""
        try:
            import uuid
            game_id = str(uuid.uuid4())
            
            if not settings:
                settings = {
                    'rounds': 3,
                    'questions_per_round': [10, 10, 13]
                }
            
            game_data = {
                'id': game_id,
                'player1_id': player_ids[0],
                'player1_name': player_names[0],
                'player2_id': player_ids[1] if len(player_ids) > 1 else None,
                'player2_name': player_names[1] if len(player_names) > 1 else None,
                'current_round': 1,
                'current_question': 1,
                'status': 'playing',
                'created_at': datetime.datetime.now().isoformat(),
                'settings': settings,
                'scores': {
                    player_ids[0]: 0,
                    player_ids[1]: 0 if len(player_ids) > 1 else 0
                }
            }
            
            # Создаем раунды и вопросы
            rounds_data = {}
            for round_num in range(1, settings['rounds'] + 1):
                questions_count = settings['questions_per_round'][round_num - 1]
                rounds_data[str(round_num)] = {
                    'questions': {}
                }
                
                for question_num in range(1, questions_count + 1):
                    rounds_data[str(round_num)]['questions'][str(question_num)] = {
                        'text': f'Вопрос {round_num}.{question_num}',
                        'context': f'Контекст для вопроса {round_num}.{question_num}',
                        'answers': {},
                        'results': {}
                    }
            
            game_data['rounds'] = rounds_data
            
            # Сохраняем игру
            success = await self.database.create_game(game_id, game_data)
            
            if success:
                logger.info(f"Game {game_id} created")
                return game_id
            else:
                logger.error("Failed to create game")
                return None
                
        except Exception as e:
            logger.error(f"Error creating game: {e}")
            return None
    
    async def submit_answer(self, game_id: str, player_id: str, round_num: int, question_num: int, answer: AnswerType) -> bool:
        """Отправить ответ на вопрос"""
        try:
            # Сохраняем ответ в базу данных
            success = await self.database.submit_answer(game_id, round_num, question_num, player_id, answer.value)
            
            if not success:
                return False
            
            # Проверяем, ответил ли второй игрок
            game_info = await self.database.get_game_info(game_id)
            if not game_info:
                return False
            
            # Определяем ID второго игрока
            if game_info['player1_id'] == player_id:
                opponent_id = game_info['player2_id']
            else:
                opponent_id = game_info['player1_id']
            
            # Проверяем ответ соперника
            opponent_answer = await self.database.get_answer(game_id, round_num, question_num, opponent_id)
            
            if opponent_answer is not None:
                # Оба игрока ответили - рассчитываем результаты
                opponent_answer_type = AnswerType.COOPERATE if opponent_answer == 'cooperate' else AnswerType.BETRAY
                
                results = self._calculate_results(answer, opponent_answer_type)
                
                # Сохраняем результаты
                await self._save_question_results(game_id, round_num, question_num, player_id, opponent_id, results)
                
                # Обновляем счет
                await self._update_scores(game_id, player_id, opponent_id, results)
                
                return True  # Оба игрока ответили
            
            return False  # Ждем ответа второго игрока
            
        except Exception as e:
            logger.error(f"Error submitting answer: {e}")
            return False
    
    async def get_question(self, round_num: int, question_num: int) -> Optional[Dict]:
        """Получить вопрос по номеру раунда и вопроса"""
        try:
            if round_num in self.game_questions and question_num <= len(self.game_questions[round_num]):
                return self.game_questions[round_num][question_num - 1]
            return None
        except Exception as e:
            logger.error(f"Error getting question: {e}")
            return None
    
    async def get_round_results(self, game_id: str, round_num: int) -> Optional[Dict]:
        """Получить результаты раунда"""
        try:
            return await self.database.get_round_results(game_id, round_num)
        except Exception as e:
            logger.error(f"Error getting round results: {e}")
            return None
    
    async def get_game_results(self, game_id: str) -> Optional[Dict]:
        """Получить общие результаты игры"""
        try:
            return await self.database.get_game_results(game_id)
        except Exception as e:
            logger.error(f"Error getting game results: {e}")
            return None

    async def _save_question_results(self, game_id: str, round_num: int, question_num: int, player1_id: str, player2_id: str, results: Dict):
        """Сохранить результаты вопроса"""
        try:
            # Сохраняем детальные результаты в базу данных
            result_data = {
                'player1_id': player1_id,
                'player2_id': player2_id,
                'player1_score': results['player1_score'],
                'player2_score': results['player2_score'],
                'result_type': results['result'],
                'description': results['description'],
                'timestamp': datetime.now().isoformat()
            }
            
            # Сохраняем в структуру игры
            result_path = f'games/{game_id}/rounds/{round_num}/questions/{question_num}/results'
            await self.database.update_game_result(result_path, result_data)
            
            # Также сохраняем в статистику игроков
            await self._update_player_statistics(player1_id, player2_id, results)
            
        except Exception as e:
            logger.error(f"Error saving question results: {e}")

    async def _update_player_statistics(self, player1_id: str, player2_id: str, results: Dict):
        """Обновить статистику игроков"""
        try:
            # Обновляем статистику для первого игрока
            await self.database.update_player_stats(player1_id, {
                'total_score': results['player1_score'],
                'games_played': 1,
                'last_result': results['result']
            })
            
            # Обновляем статистику для второго игрока
            await self.database.update_player_stats(player2_id, {
                'total_score': results['player2_score'],
                'games_played': 1,
                'last_result': results['result']
            })
            
        except Exception as e:
            logger.error(f"Error updating player statistics: {e}")
            return None
