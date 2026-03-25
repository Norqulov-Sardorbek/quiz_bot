import asyncio
from aiogram import F
from quiz_bot.buttons.inline import *
from quiz_bot.dispatcher import dp,bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message,CallbackQuery
from aiogram.filters import Command,StateFilter
from quiz_bot.state import UploadQuestion,Register
from quiz_bot.models import CustomUser, QuizQuestion,Quizes
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter

@dp.callback_query(F.data == "autocreate")
async def quiz_autocreate(callback_query: CallbackQuery, state: FSMContext) -> None:
    print("quiz_autocreate")
    await callback_query.message.edit_text(text="📝 Savol va javoblar uchun nom kiriting!",reply_markup=back_keyboard())
    await state.set_state(UploadQuestion.upload_1)
    
@dp.message(StateFilter(UploadQuestion.upload_1))
async def upload_quiz_title(message: Message, state: FSMContext) -> None:
    quiz_title = message.text.strip()
    await state.update_data(quiz_title=quiz_title)
    await message.answer("📄 Endi savol va javoblar joylashgan DOCX faylni yuboring.",reply_markup=back_keyboard())
    await state.set_state(UploadQuestion.upload_2)



from docx import Document
import re

def clean(t):
    return re.sub(r"\s+", " ", t).strip()


def parse_docx(file):
    doc = Document(file)
    text = "\n".join(p.text for p in doc.paragraphs)

    question_blocks = re.split(r"\n\+{4,}\n", text)

    questions = []
    errors = []

    for idx, block in enumerate(question_blocks, start=1):
        block = block.strip()

        if "====" not in block:
            continue

        parts = re.split(r"\n\s*=+\s*\n", block)

        if len(parts) < 2:
            errors.append(f"{idx}-savol: variantlar topilmadi")
            continue

        question = clean(parts[0])
        options = []
        correct_index = None

        for i, opt in enumerate(parts[1:]):
            opt = clean(opt)

            if not opt:
                continue

            if "#" in opt:
                correct_index = i

            opt = opt.replace("#", "").replace("=====", "").strip()
            options.append(opt)

        # VALIDATION
        if not question:
            errors.append(f"{idx}-savol: savol matni bo'sh")
            continue

        if len(options) < 2:
            errors.append(f"{idx}-savol: kamida 2 ta variant bo‘lishi kerak")
            continue

        if correct_index is None:
            errors.append(f"{idx}-savol: to‘g‘ri javob (#) belgilanmagan")
            continue

        questions.append({
            "question": question,
            "options": options,
            "correct_index": correct_index
        })

    return questions, errors


@dp.message(StateFilter(UploadQuestion.upload_2))
async def upload_docx(message: Message, state: FSMContext):
    if not message.document or not message.document.file_name.endswith(".docx"):
        await message.answer("❌ Faqat .docx fayl yuboring",reply_markup=back_keyboard())
        return

    file = await message.bot.download(message.document)

    questions, errors = parse_docx(file)

    if errors:
        text = "❌ Xatoliklar topildi:\n\n" + "\n".join(errors[:10])
        await message.answer(text,reply_markup=back_keyboard())
        return

    if not questions:
        await message.answer("❌ Umuman savol topilmadi",reply_markup=back_keyboard())
        return

    # vaqtinchalik saqlaymiz
    await state.update_data(
        parsed_questions=questions
    )

    await message.answer(
        f"✅ {len(questions)} ta savol topildi!\n\nSavollar nechtadan guruhlashini xohlaysiz?",
        reply_markup=back_keyboard()

    )

    await state.set_state(UploadQuestion.upload_3)
    
    
@dp.message(StateFilter(UploadQuestion.upload_3))
async def get_limit(message: Message, state: FSMContext):
    try:
        limit = int(message.text)
    except:
        await message.answer("❌ Raqam kiriting",reply_markup=back_keyboard())
        return

    data = await state.get_data()
    await state.update_data(limit=limit)

    await message.answer("Har bir savol uchun vaqt kiriting (sekundda)?",reply_markup=back_keyboard())
    await state.set_state(UploadQuestion.upload_4)
    
    
@dp.message(StateFilter(UploadQuestion.upload_4))
async def save_questions(message: Message, state: FSMContext):
    try:
        deadline = int(message.text)
    except:
        await message.answer("❌ Raqam kiriting",reply_markup=back_keyboard())
        return

    data = await state.get_data()

    questions = data["parsed_questions"]
    limit = data["limit"]
    quiz_title = data["quiz_title"]

    chunks = [
        questions[i:i + limit]
        for i in range(0, len(questions), limit)
    ]

    count = 0
    user = CustomUser.objects.filter(tg_id=message.from_user.id).first()
    for idx, chunk in enumerate(chunks, start=1):
        quiz = Quizes.objects.create(
            user_id=user.id,
            title=f"{quiz_title} {idx}-qism",
            deadline=deadline
        )

        for q in chunk:
            QuizQuestion.objects.create(
                quiz=quiz,
                question=q["question"],
                options=q["options"],
                correct_index=q["correct_index"],
            )
            count += 1

    await message.answer(f"✅ {count} ta savol saqlandi!",reply_markup=main_menu_keyboard())
    await state.clear()





























async def send_safe_message(chat_id: int, text: str, **kwargs) -> Message | None:
    kwargs['parse_mode'] = kwargs.get('parse_mode', 'HTML')
    try:
        return await bot.send_message(chat_id=chat_id, text=text, **kwargs)
    except Exception:
        return None
    

    
@dp.callback_query(F.data == "broadcast_message")
async def broadcast_message(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer()
    await callback_query.message.answer("📢 Iltimos, bot foydalanuvchilariga jo'natiladigan xabar matnini kiriting:",reply_markup=back_keyboard())
    await state.set_state(Register.every_one)
    
BATCH_SIZE = 25
DELAY = 0.03

@dp.message(StateFilter(Register.every_one))
async def process_broadcast_message(message: Message, state: FSMContext):
    text = message.text.strip() if message.text else None
    if not text:
        await message.answer("❗️ Iltimos, xabar matnini kiriting.")
        return

    await message.answer("⏳ Xabar yuborilmoqda...")

    await state.clear()
    success = 0
    fail = 0

    users = CustomUser.objects.all().values_list("tg_id", flat=True)

    batch = []
    for tg_id in users.iterator():
        batch.append(tg_id)

        if len(batch) >= BATCH_SIZE:
            for uid in batch:
                try:
                    await bot.send_message(uid, f"📢 Botdan umumiy xabar:\n\n{text}")
                    success += 1
                    await asyncio.sleep(DELAY)
                except TelegramForbiddenError:
                    fail += 1
                except TelegramRetryAfter as e:
                    await asyncio.sleep(e.retry_after)
                except:
                    fail += 1
            batch.clear()

    for uid in batch:
        try:
            await send_safe_message(uid, f"📢 Botdan umumiy xabar:\n\n{text}")
            success += 1
            await asyncio.sleep(DELAY)
        except:
            fail += 1

    await message.answer(
        f"📢 Xabar yuborildi.\n\n✅ Muvaffaqiyatli: {success}\n❌ Muvaffaqiyatsiz: {fail}",
        reply_markup=admin_keyboard()
    )