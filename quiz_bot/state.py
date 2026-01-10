from aiogram.fsm.state import StatesGroup, State



class UploadQuestion(StatesGroup):
    upload_1 = State()
    upload_2 = State()

class QuizSearch(StatesGroup):
    query = State()


active_quiz = {}        
quiz_sessions = {}      
deadline_tasks = {}   
poll_chat_map = {}       
poll_correct_map = {}
quiz_correct = {}          
quiz_answered = {}         
quiz_start_time = {}       # chat_id -> session
quiz_scores = {}         # chat_id -> asyncio.Task
ready_users= {} 