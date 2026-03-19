import json
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

@dp.message(Command("upload"),StateFilter(None))
async def start(message: Message, state: FSMContext) -> None:
    user = CustomUser.objects.filter(tg_id=message.from_user.id ).first()
    if not user:
        await message.answer(text="Siz admin emassiz! Agar Botga savol joylamoqchi bolsangiz, admin bilan bog'laning.")
        return
    if user and user.role != 'admin':
        await message.answer(text="Siz admin emassiz! Agar Botga savol joylamoqchi bolsangiz, admin bilan bog'laning.")
        return
    await message.answer(text="Savol va javoblar uchun nom kiriting!",reply_markup=back_keyboard())
    await state.set_state(UploadQuestion.upload_1)
    
@dp.message(StateFilter(UploadQuestion.upload_1))
async def upload_quiz_title(message: Message, state: FSMContext) -> None:
    quiz_title = message.text.strip()
    quiz = Quizes.objects.create(title=quiz_title)
    await state.update_data(quiz_id=quiz.id)
    await message.answer("Endi savol va javoblar joylashgan JSON faylni yuboring.",reply_markup=back_keyboard())
    await state.set_state(UploadQuestion.upload_2)


@dp.message(StateFilter(UploadQuestion.upload_2))
async def upload_question(message: Message, state: FSMContext) -> None:
    if not message.document or not message.document.file_name.endswith(".json"):
        await message.answer("❌ JSON fayl yuboring")
        return

    file = await message.bot.download(message.document)
    data = await state.get_data()
    quiz_id = data.get("quiz_id")

    try:
        data = json.load(file)
    except Exception:
        await message.answer("❌ JSON fayl noto‘g‘ri formatda")
        return

    questions_created = 0
    for item in data:
        if (
            "question" not in item or
            "options" not in item or
            "correct_index" not in item
        ):
            print("Skipping invalid item:", item)
            continue

        if not isinstance(item["options"], list) :
            continue

        QuizQuestion.objects.create(
            quiz_id=quiz_id,
            question=item["question"],
            options=item["options"],
            correct_index=item["correct_index"]
        )
        questions_created += 1

    await message.answer(
        text=f"✅ {questions_created} ta savol va javob muvaffaqiyatli yuklandi!",
        reply_markup=back_keyboard()
    )
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