from aiogram.fsm.state import StatesGroup, State


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
user_info = {}

class Register(StatesGroup):
    every_one = State()
    
class UploadQuestion(StatesGroup):
    upload_1 = State()  # title
    upload_2 = State()  # docx
    upload_3 = State()  # limit
    upload_4 = State()  # deadline