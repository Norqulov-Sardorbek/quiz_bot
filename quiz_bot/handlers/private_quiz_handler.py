from operator import index
import time
import random
import asyncio
import html as html_module
from aiogram import F
from quiz_bot.dispatcher import dp
from quiz_bot.dispatcher import bot
from quiz_bot.buttons.inline import *
from quiz_bot.models import CustomUser, QuizAnswers,Quizes
from quiz_bot.state import active_quiz, quiz_sessions, deadline_tasks, poll_chat_map, poll_correct_map, quiz_correct, quiz_answered, quiz_start_time, quiz_scores, ready_users,user_info




@dp.callback_query(F.data.startswith("quiz_restart_private:"))
async def quiz_restart_private_callback(callback_query):
    await callback_query.message.edit_reply_markup(None)
    user = CustomUser.objects.filter(tg_id=callback_query.from_user.id).first()
    if not user:
        await callback_query.answer("❌ Siz ro'yxatdan o'tmagansiz.", show_alert=True)
        return

    share_code = callback_query.data.split(":")[1]
    quiz = Quizes.objects.filter(share_code=share_code).first()
    if not quiz:
        await callback_query.answer("❌ Bunday quiz topilmadi.", show_alert=True)
        return

    await begin_quiz_in_private(chat_id=callback_query.message.chat.id, share_code=share_code)



async def begin_quiz_in_private(chat_id: int, share_code):
    quiz = Quizes.objects.filter(share_code=share_code).first()
    if not quiz:
        await bot.send_message(chat_id=chat_id, text="❌ Bunday quiz topilmadi.")
        return
    quiz_count = quiz.questions.count()
    if quiz_count == 0:
        await bot.send_message(chat_id=chat_id, text="❌ Ushbu quizda savollar mavjud emas.")
        return
    text = (
        f"🎲 “{quiz.title} (1-{quiz_count})”\n\n"
        f"🖊 {quiz_count} ta savol\n"
        f"⏱ Har bir savol uchun {quiz.deadline} soniya\n"
        "📰 Ovozlar test egasiga koʻrinadigan boʻladi\n\n"
        "🏁 Tayyor boʻlganingizda quyidagi tugmani bosing. Uni toʻxtatish uchun /stop buyrugʻini yuboring.")
    await bot.send_message(chat_id=chat_id, text=text,reply_markup=quiz_ready_private_button(quiz.share_code))
     
     

@dp.callback_query(F.data.startswith("quiz_ready_private:"))
async def quiz_ready_private_callback(callback_query):
    user = CustomUser.objects.filter(tg_id=callback_query.from_user.id).first()
    if not user:
        await callback_query.answer("❌ Siz ro'yxatdan o'tmagansiz.", show_alert=True)
        return

    share_code = callback_query.data.split(":")[1]
    quiz = Quizes.objects.filter(share_code=share_code).first()
    if not quiz:
        await callback_query.answer("❌ Bunday quiz topilmadi.", show_alert=True)
        return
    await callback_query.message.edit_reply_markup(None)
    await callback_query.answer("Qoyilmaqom!")
    
    await counter_handler(callback_query.message.chat.id, share_code)



async def counter_handler(chat_id, share_code):
    msg = await bot.send_message(chat_id, f"3️⃣ ...")
    await asyncio.sleep(1)
    await msg.edit_text("2️⃣ TAYYORMISIZ!")

    await asyncio.sleep(1)
    await msg.edit_text("1️⃣ SOZLANMOQDA!")
    
    await asyncio.sleep(1)
    await msg.edit_text("🏁 START!")
    await msg.delete()
    # quizni boshlash
    await start_quiz_private(chat_id, share_code)



async def start_quiz_private(chat_id, share_code):
    if chat_id in active_quiz:
        await bot.send_message(
            chat_id,
            "❗ Bu chatda allaqachon test ketmoqda. Avval tugashini kuting."
        )
        return
    cleanup_chat(chat_id)

    quiz = Quizes.objects.get(share_code=share_code)
    questions = list(quiz.questions.all())
    random.shuffle(questions)
    active_quiz[chat_id] = share_code
    quiz_sessions[chat_id] = {
        "share_code": share_code,
        "questions": questions,
        "index": 0,
        "deadline": quiz.deadline
    }
    quiz_start_time[chat_id] = time.time()
    quiz_correct[chat_id] = {}
    quiz_answered[chat_id] = {}

    await send_question_bg(chat_id)

async def send_question_bg(chat_id):
    session = quiz_sessions.get(chat_id)
    if not session:
        return

    if session.get("paused"):
        return

    index = session["index"]
    questions = session["questions"]

    if index >= len(questions):
        await finish_quiz_private(chat_id)
        return

    q = questions[index]
    total = len(questions)

    if not q.options or len(q.options) < 2:
        print("INVALID OPTIONS:", q.options, "question=", q.question)
        session["index"] += 1
        await send_question_bg(chat_id)
        return

    if not (0 <= q.correct_index < len(q.options)):
        print(
            "INVALID correct_index:",
            q.correct_index,
            "options_len=", len(q.options),
            "question=", q.question
        )
        q.correct_index = 0

    poll_question = f"[{index+1}/{total}] {q.question}"
    session["active_answered"] = False

    paired = list(enumerate(q.options))
    random.shuffle(paired)

    new_options = []
    used = set()

    for _, opt in paired:
        text = (opt or "").strip()[:100]
        if not text:
            text = "—"
        while text in used:
            text = (text[:99] + " ") if len(text) >= 99 else (text + " ")
        used.add(text)
        new_options.append(text)

    new_correct = None
    for i, (old_i, _) in enumerate(paired):
        if old_i == q.correct_index:
            new_correct = i
            break

    if new_correct is None:
        new_correct = 0

    session["active_q_index"] = index
    session["active_correct"] = new_correct
    session["active_started_at"] = time.time()

    msg = await send_poll_until_ok(
        chat_id=chat_id,
        question=poll_question,
        options=new_options,
        correct_option_id=new_correct,
        deadline=session["deadline"],
        retries=10,
        timeout=10
    )

    if not msg:
        session["paused"] = True
        await bot.send_message(
            chat_id,
            "❌ Poll yuborilmadi (Telegram javob qaytarmadi).\n\n"
            "▶️ Resume bosing yoki keyinroq urinib ko‘ring.",
            reply_markup=resume_group_keyboard()
        )
        return

    poll_id = msg.poll.id
    poll_chat_map[poll_id] = chat_id
    poll_correct_map[poll_id] = new_correct

    deadline_tasks[chat_id] = asyncio.create_task(
        question_deadline(chat_id, session["deadline"])
    )

    session["index"] += 1


async def send_poll_until_ok(
    chat_id: int,
    question: str,
    options: list[str],
    correct_option_id: int,
    deadline: int,
    retries: int = 10,
    timeout: int = 10
):
    for attempt in range(1, retries + 1):
        try:
            question_safe = html_module.escape(question)
            options_safe = [html_module.escape(o) for o in options]
            msg = await asyncio.wait_for(
                bot.send_poll(
                    chat_id=chat_id,
                    question=question_safe,
                    options=options_safe,
                    type="quiz",
                    correct_option_id=correct_option_id,
                    is_anonymous=False,
                    open_period=deadline
                ),
                timeout=timeout
            )

            if msg and msg.poll and msg.poll.id:
                return msg

        except asyncio.TimeoutError:
            print(f"[SEND_POLL TIMEOUT] chat={chat_id} attempt={attempt}")
        except Exception as e:
            print(f"[SEND_POLL ERROR] chat={chat_id} attempt={attempt} err={e}")

        await asyncio.sleep(1)  # kichkina pause (flood bo'lmasin)

    return None


async def question_deadline(chat_id, seconds):
    await asyncio.sleep(seconds)

    session = quiz_sessions.get(chat_id)
    if not session:
        return

    if session.get("paused"):
        return
    

    
    if not session.get("active_answered", False):
        session["no_answer_streak"] = session.get("no_answer_streak", 0) + 1
    else:
        session["no_answer_streak"] = 0
    if session["no_answer_streak"] >= 2:
        session["paused"] = True
        await bot.send_message(
            chat_id,
            "⏸ Quiz pauza qilindi.\n\n",
            reply_markup=resume_private_keyboard()
        )
        return
    await send_question_bg(chat_id)

@dp.callback_query(F.data == "quiz_resume_private")
async def quiz_resume_callback(callback):
    chat_id = callback.message.chat.id
    session = quiz_sessions.get(chat_id)

    if not session:
        await callback.answer("Quiz topilmadi", show_alert=True)
        return

    session["paused"] = False
    session["no_answer_streak"] = 0

    await callback.message.edit_text("▶️ Quiz davom ettirildi!")

    await send_question_bg(chat_id)



@dp.poll_answer()
async def poll_answer_handler(poll_answer):
    poll_id = poll_answer.poll_id
    user_id = poll_answer.user.id
    

    chat_id = poll_chat_map.get(poll_id)
    if not chat_id:
        return
    if chat_id < 0:
        chat_bucket = user_info.setdefault(chat_id, {})
        chat_bucket[user_id] = {
                "username": poll_answer.user.username,
            }

    session = quiz_sessions.get(chat_id)
    if not session or session.get("paused"):
        return
    
    session["active_answered"] = True
    if not poll_answer.option_ids:
        return
    selected = poll_answer.option_ids[0]
    correct = poll_correct_map.get(poll_id)
    if correct is None:
        return
    

    quiz_correct.setdefault(chat_id, {})
    quiz_answered.setdefault(chat_id, {})

    quiz_correct[chat_id].setdefault(user_id, 0)
    quiz_answered[chat_id].setdefault(user_id, 0)

    quiz_answered[chat_id][user_id] += 1
    quiz_scores.setdefault(chat_id, {})
    quiz_scores[chat_id].setdefault(user_id, 0)

    

    if selected == correct:
        quiz_correct[chat_id][user_id] += 1
        quiz_scores[chat_id][user_id] += 1
    if chat_id > 0:
        old = deadline_tasks.pop(chat_id, None)
        if old:
                old.cancel()
        await send_question_bg(chat_id)
        



async def finish_quiz_private(chat_id):
    session = quiz_sessions.get(chat_id)
    if not session:
        return

    share_code = session.get("share_code")
    quiz = Quizes.objects.filter(share_code=share_code).first()
    if not quiz:
        await bot.send_message(chat_id, "❌ Quiz topilmadi.")
        return

    quiz_title = quiz.title
    total_questions = quiz.questions.count()

    # private chatda 1 user bo'ladi
    user_id = chat_id
    user = CustomUser.objects.filter(tg_id=user_id).first()
    if not user:
        await bot.send_message(chat_id, "❌ Siz ro'yxatdan o'tmagansiz. Ro'yxatdan o'tish uchun /start buyrug'ini yuboring.")
        return
    correct = quiz_correct.get(chat_id, {}).get(user_id, 0)
    answered = quiz_answered.get(chat_id, {}).get(user_id, 0)

    wrong = max(0, answered - correct)
    not_answered = max(0, total_questions - answered)

    started = quiz_start_time.get(chat_id)
    spent = (time.time() - started) if started else 0.0
    
    

    def format_time(sec: float):
        sec = max(0, float(sec))
        m = int(sec // 60)
        s = int(sec % 60)
        return f"{m} daqiqa {s} soniya" if m else f"{round(sec,1)} soniya"

    # --- leader stats (DB best)
    leader_row = QuizAnswers.objects.filter(quiz=quiz,user=user).order_by("-correct_answers", "total_time").first()

    # --- ranking hisoblash
    leaderboard = list(
        QuizAnswers.objects.filter(quiz=quiz).order_by("-correct_answers", "total_time")
    )
    total_people = len(leaderboard)

    rank = None
    for i, row in enumerate(leaderboard, start=1):
        if row.user_id == user.id:
            rank = i
            break

    if total_people > 0 and rank:
        percent_higher = int(round(((total_people - rank) / total_people) * 100))
    else:
        percent_higher = 0

    

    rank_text = ""
    if rank:
        rank_text = (
            f"{total_people} tadan {rank}-oʻrin. "
            f"Siz ushbu testda ishtirok etgan {percent_higher}% odamlardan yuqoriroq ball toʻpladingiz.\n\n"
        )

    text = (
        f"🎲 “{quiz_title} (1-{total_questions})” testi\n\n"
            f"Siz {answered} ta savolga javob berdingiz:\n\n"
            f"✅ Toʻgʻri – {correct}\n"
            f"❌ Xato – {wrong}\n"
            f"⌛️ Tashlab ketilgan – {not_answered}\n"
            f"⏱ {format_time(spent)}\n\n"
            f"{rank_text}"
            "Bu testda yana qatnashishingiz mumkin, lekin bu yetakchilardagi oʻrningizni oʻzgartirmaydi."
        )

    await bot.send_message(chat_id, text,reply_markup=restart_quiz_keyboard(quiz.share_code))

    should_update = False
    if not leader_row:
        should_update = True
    elif correct > leader_row.correct_answers:
        should_update = True
    elif correct == leader_row.correct_answers and spent < leader_row.total_time:
        should_update = True

    if should_update:
        QuizAnswers.objects.update_or_create(
            user=user,
            quiz=quiz,
            defaults={
                "correct_answers": correct,
                "wrong_answers": wrong,
                "not_answered": not_answered,
                "total_time": spent
            }
        )
    cleanup_chat(chat_id)

    
 

def cleanup_chat(chat_id):
    active_quiz.pop(chat_id, None)
    quiz_sessions.pop(chat_id, None)
    quiz_answered.pop(chat_id, None)
    quiz_correct.pop(chat_id, None)
    quiz_start_time.pop(chat_id, None)
    ready_users.pop(chat_id, None)
    quiz_scores.pop(chat_id, None)
    user_info.pop(chat_id, None)
    poll_chat_map_copy = poll_chat_map.copy()
    
    for poll_id, c_id in poll_chat_map_copy.items():
        if c_id == chat_id:
            poll_chat_map.pop(poll_id, None)
            poll_correct_map.pop(poll_id, None)
    
    
    

    task = deadline_tasks.pop(chat_id, None)
    if task:
        task.cancel()

    # optional: maplarni ham tozalash
    to_delete = [pid for pid, cid in poll_chat_map.items() if cid == chat_id]
    for pid in to_delete:
        poll_chat_map.pop(pid, None)
        poll_correct_map.pop(pid, None)

    
