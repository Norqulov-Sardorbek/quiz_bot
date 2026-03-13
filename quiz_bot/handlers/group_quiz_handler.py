import time
import random
import asyncio
import html as html_module
from aiogram import F
from quiz_bot.dispatcher import dp
from quiz_bot.dispatcher import bot
from aiogram.filters import Command
from quiz_bot.buttons.inline import *
from aiogram.types import InlineQuery,Message
from quiz_bot.models import CustomUser,Quizes,ReadyCount
from quiz_bot.handlers.private_quiz_handler import finish_quiz_private,cleanup_chat
from quiz_bot.state import active_quiz, quiz_sessions, deadline_tasks, poll_chat_map, poll_correct_map, quiz_scores, ready_users,user_info  





@dp.message(Command("stop"))
async def stop_quiz_message_handler(message: Message):
    await stop_quiz(message.chat.id, message.chat.type, message.from_user.id)


@dp.callback_query(F.data == "quiz_stop")
async def stop_quiz_callback_handler(callback):
    await callback.message.edit_reply_markup(None)
    await stop_quiz(callback.message.chat.id, callback.message.chat.type, callback.from_user.id)
    


async def stop_quiz(chat_id: int, chat_type: str,user_id: int = None):
    if chat_id not in quiz_sessions:
        await bot.send_message(
            chat_id,
            "❗ Bu chatda hozircha hech qanday test o'tkazilmayapti."
        )

    if chat_type in ("group", "supergroup"):
        ready = ReadyCount.objects.filter(chat_id=chat_id, is_ended=True).first()
        if ready and ready.quiz_starter_id:
            starter_tg_id = ready.quiz_starter.tg_id  # CustomUser.tg_id
            if starter_tg_id != user_id:
                await bot.send_message(
                    chat_id,
                    "❗ Faqat testni boshlagan foydalanuvchi uni to'xtatishi mumkin."
                )
                return

        await finish_quiz(chat_id)
    else:
        await finish_quiz_private(chat_id)

    



async def begin_quiz_in_group(chat_id: int, share_code,user_id: int):
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
        "📰 Ovozlar guruh aʼzolari va test egasiga koʻrinadigan boʻladi\n\n"
        "🏁 Test kamida 2 kishi ishlashga tayyor boʻlganida boshlanadi. Uni toʻxtatish uchun /stop buyrugʻini yuboring.")
    msg =await bot.send_message(chat_id=chat_id, text=text,reply_markup=quiz_ready_group_button(quiz.share_code))
    ReadyCount.objects.create(
        chat_id=chat_id,
        message_id=msg.message_id,
        quiz_id=quiz.id,
        is_ended=False,
        count=0,
        quiz_starter_id=user_id
    )
     
     
@dp.callback_query(F.data.startswith("quiz_ready_group:"))
async def quiz_ready_callback(callback_query):
    user = CustomUser.objects.filter(tg_id=callback_query.from_user.id).first()
    if not user:
        user = CustomUser.objects.create(
            tg_id=callback_query.from_user.id,
            username=callback_query.from_user.username,
            role='user'
        )

    share_code = callback_query.data.split(":")[1]
    chat_id = callback_query.message.chat.id
    key = (chat_id, share_code)
    quiz = Quizes.objects.filter(share_code=share_code).first()
    if not quiz:
        await callback_query.answer("❌ Bunday quiz topilmadi.")
        return

    ready_people = ReadyCount.objects.filter(
        chat_id=chat_id,
        quiz_id=quiz.id,
        is_ended=False
    ).first()

    if not ready_people:
        ready_people = ReadyCount.objects.create(
            chat_id=chat_id,
            message_id=callback_query.message.message_id,
            quiz_id=quiz.id,
            count=0,
            is_ended=False,
            quiz_starter_id=user.id
        )

    users = ready_users.get(key, set())

    await callback_query.answer(
            "Qoyilmaqom! Test tez orada boshlanadi!"
        )
    if user.tg_id in users:
        return

    users.add(user.tg_id)
    ready_users[key] = users

    ready_count = len(users)
    ready_people.count = ready_count
    ready_people.save(update_fields=["count"])

    quiz = Quizes.objects.filter(share_code=share_code).first()
    quiz_count = quiz.questions.count()

    text = (
        f"🎲 “{quiz.title} (1-{quiz_count})”\n\n"
        f"🖊 {quiz_count} ta savol\n"
        f"⏱ Har bir savol uchun {quiz.deadline} soniya\n"
        "📰 Ovozlar guruh aʼzolari va test egasiga koʻrinadigan boʻladi\n\n"
        "🏁 Test kamida 2 kishi ishlashga tayyor boʻlganida boshlanadi.\n"
        "Uni toʻxtatish uchun /stop buyrugʻini yuboring.\n\n"
        f"👥 Tayyor: {ready_count} ta"
    )

    

    await callback_query.message.edit_text(
        text=text,
        reply_markup=quiz_ready_group_button(share_code)
    )

    if ready_count >= 2:
        ready_users.pop(key, None)
        await asyncio.sleep(2)
        await bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=ready_people.message_id,
            reply_markup=None
        )
        ready_people.is_ended = True
        ready_people.save(update_fields=["is_ended"])
        await counter_handler(chat_id, share_code)

async def counter_handler(chat_id, share_code):
    msg = await bot.send_message(chat_id, f"3️⃣ ...")
    await asyncio.sleep(1)
    await msg.edit_text(f"2️⃣ TAYYORMISIZ!")

    await asyncio.sleep(1)
    await msg.edit_text("1️⃣ SOZLANMOQDA!")
    
    await asyncio.sleep(1)
    await msg.edit_text("🏁 START!")

    await msg.delete()
    # quizni boshlash
    await start_quiz(chat_id, share_code)



async def start_quiz(chat_id, share_code):
    if chat_id in active_quiz:
        await bot.send_message(
            chat_id,
            "❗ Bu chatda allaqachon test ketmoqda. Avval tugashini kuting."
        )
        return
    cleanup_chat(chat_id)

    quiz = Quizes.objects.get(share_code=share_code)
    questions = list(quiz.questions.all().order_by("id"))
    questions = list(quiz.questions.all())
    random.shuffle(questions)
    active_quiz[chat_id] = share_code
    quiz_sessions[chat_id] = {
        "share_code": share_code,
        "questions": questions,
        "index": 0,
        "deadline": quiz.deadline
    }
    quiz_scores[chat_id] = {}

    await send_question_bg(chat_id)

async def send_question_bg(chat_id):
    session = quiz_sessions.get(chat_id)
    if not session:
        return

    if session.get("paused"):
        return

    index = session["index"]
    questions = session["questions"]
    total = len(questions)

    if index >= len(questions):
        await finish_quiz(chat_id)
        return

    q = questions[index]

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

    correct_text = (q.options[q.correct_index] or "").strip()[:100]

    new_correct = None
    for i, (old_i, opt) in enumerate(paired):
        if old_i == q.correct_index:
            new_correct = i
            break

    if new_correct is None:
        for i, opt in enumerate(new_options):
            if opt == correct_text:
                new_correct = i
                break

    if new_correct is None:
        new_correct = 0

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
    print(f"[POLL ID] chat_id={chat_id} poll_id={poll_id}")

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
                open_period=deadline,
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
        print("entered group")
        await bot.send_message(
            chat_id,
            ("⏸ Quiz pauza qilindi.\n\n"
            "❗ Chunki hech kim javob bermayapti."),
            reply_markup=resume_group_keyboard()
        )
        return

    # davom etadi
    await send_question_bg(chat_id)

@dp.callback_query(F.data == "quiz_resume_group")
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



async def finish_quiz(chat_id):
    scores = quiz_scores.get(chat_id, {})
    session = quiz_sessions.get(chat_id)
    share_code = session["share_code"] if session else None
    quiz = Quizes.objects.filter(share_code=share_code).first() if share_code else None
    quiz_title = quiz.title if quiz else "Test"
    total_questions = quiz.questions.count() if quiz else 0

    text = (
        f"🏁 “{quiz_title}” testi yakunlandi!\n\n"
        f"{total_questions} ta savolga javob berildi\n\n"
    )

    if not scores:
        text += "❌ Hech kim testda qatnashmadi\n"
        await bot.send_message(chat_id, text)
        return

    sorted_users = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    medals = ["🥇", "🥈", "🥉"]

    uids = [uid for uid, _ in sorted_users]

    existing_users = CustomUser.objects.filter(tg_id__in=uids)
    existing_map = {u.tg_id: u for u in existing_users}

    new_users = []
    for uid in uids:
        if uid in existing_map:
            continue

        data = user_info.get(chat_id, {}).get(uid, {})
        new_users.append(
            CustomUser(
                tg_id=uid,
                username=data.get("username", "") if data else "",
                role="user",
            )
        )

    if new_users:
        CustomUser.objects.bulk_create(new_users, ignore_conflicts=True)

        existing_users = CustomUser.objects.filter(tg_id__in=uids)
        existing_map = {u.tg_id: u for u in existing_users}

    for i, (uid, score) in enumerate(sorted_users):
        user = existing_map.get(uid)

        name = f"@{user.username}" if user and user.username else str(uid)

        prefix = medals[i] if i < 3 else f"{i+1}."
        text += f"{prefix} {name} – {score}\n"

    text += "\n🏆 Gʻoliblarni tabriklaymiz!"

    await bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=share_quiz_keyboard(share_code),
    )

    if quiz:
        ReadyCount.objects.filter(
            chat_id=chat_id,
            quiz_id=quiz.id,
            is_ended=True
        ).delete()

    cleanup_chat(chat_id)





@dp.inline_query()
async def inline_quiz_handler(inline_query: InlineQuery):
    query = inline_query.query

    # faqat quiz: bilan boshlanganlarini ushlaymiz
    if not query.startswith("quiz:"):
        return

    code = query.replace("quiz:", "").strip()

    quiz = Quizes.objects.filter(share_code=code).first()
    if not quiz:
        return


    await inline_query.answer(
        results=[inline_query_btn(quiz, code)],
        cache_time=0
    )