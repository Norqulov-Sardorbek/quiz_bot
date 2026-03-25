from aiogram import F
from quiz_bot.dispatcher import dp
from quiz_bot.state import QuizSearch
from quiz_bot.buttons.inline import *
from aiogram.fsm.context import FSMContext
from quiz_bot.models import CustomUser,Quizes
from aiogram.filters import Command,StateFilter
from aiogram.types import CallbackQuery, Message
from quiz_bot.handlers.private_quiz_handler import begin_quiz_in_private
from quiz_bot.handlers.group_quiz_handler import begin_quiz_in_group






@dp.message(Command("start"),StateFilter(None))
async def start(message: Message, state: FSMContext) -> None:
    tg_id = message.from_user.id
    user = CustomUser.objects.filter(tg_id=tg_id).first()
    if not user:
        user = CustomUser.objects.create(
            tg_id=tg_id,
            username=message.from_user.username,
            role='user'
        )
    if message.chat.type != "private" and message.chat.type in ["group","supergroup"]:
        message_text = message.text
        if " " in message_text:
            args = message.text.split(" ")[1]
            chat_id = message.chat.id
            await begin_quiz_in_group(chat_id=chat_id, share_code=args,user_id=user.id)
            return
        else:
            await message.answer(
                text="👥 Guruhlarda quizni boshlash uchun botga kiring va o'zingizga kerakli quizni tanlang"
            )
            return
    elif message.chat.type == "private" and " "  in message.text:
        args = message.text.split(" ")[1]
        await begin_quiz_in_private(chat_id=message.chat.id, share_code=args)
        return
            
    if user.role == 'admin':
        await message.answer(text="Admin bosh menyu",reply_markup=admin_keyboard())
    else:
        await message.answer(text=
f"""🎯 Quiz Avto Botga xush kelibsiz, {message.from_user.first_name}

━━━━━━━━━━━━━━━━━━━━

🚀 Imkoniyatlar:
├ 📝 Fayldan avtomatik test yaratish (DOCX, TXT, PDF)
├ ✏️ Qo'lda test yaratish
├ 👥 Guruhda test o'tkazish
├ 📊 Natijalar va statistika
└ 🏆 Reyting tizimi

━━━━━━━━━━━━━━━━━━━━

📌 Boshlash uchun:
• Avtomatik quiz tuzish — DOCX, TXT, PDF fayldan
• Quiz tuzish — qo'lda yaratish
• Mening quizlarim — yaratilgan testlar""",
reply_markup=main_menu_keyboard())
        

   


@dp.callback_query(F.data == "all_quizzes")
async def all_quizzes_callback(callback_query, state: FSMContext):
    await callback_query.answer()
    user = CustomUser.objects.filter(tg_id=callback_query.from_user.id).first()
        
    page = 1
    limit = 5
    offset = (page - 1) * limit
    if user.role == 'admin':
        total = Quizes.objects.all().count()
    else:
        total = Quizes.objects.filter(user_id=user.id).count()
    if total == 0:
        await callback_query.message.edit_text(
            text="Hozircha mavjud bo'lgan viktorinalar yo'q.",
            reply_markup=main_menu_keyboard()
        )
        return

    if user.role == 'admin':
        quizzes = Quizes.objects.all()[offset:offset + limit]
    else:
        quizzes = Quizes.objects.filter(user_id=user.id)[offset:offset + limit]
    total_pages = (total + limit - 1) // limit

    quiz_list = "\n\n".join([
        f"{offset + i + 1}. 📚 {quiz.title}\n{quiz.description or 'Tavsif mavjud emas'}"
        for i, quiz in enumerate(quizzes)
    ])

    await callback_query.message.edit_text(
        text=f"Mavjud viktorinalar (sahifa {page}/{total_pages}):\n\n{quiz_list}",
        reply_markup=quizzes_keyboard(questions=quizzes, page=page, total=total, per_page=limit)
    )


@dp.callback_query(F.data.startswith("quiz_page:"))
async def quizzes_page_callback(callback_query, state: FSMContext):
    await callback_query.answer()
    page = int(callback_query.data.split(":")[1])
    limit = 5
    offset = (page - 1) * limit
    user = CustomUser.objects.filter(tg_id=callback_query.from_user.id).first()
    if user.role == 'admin':
        total = Quizes.objects.all().count()
    else:
        total = Quizes.objects.filter(user_id=user.id).count()
    total_pages = (total + limit - 1) // limit
    if user.role == 'admin':
        quizzes = Quizes.objects.all()[offset:offset + limit]
    else:
        quizzes = Quizes.objects.filter(user_id=user.id)[offset:offset + limit]

    quiz_list = "\n\n".join([
        f"{offset + i + 1}. 📚 {quiz.title}\n{quiz.description or 'Tavsif mavjud emas'}"
        for i, quiz in enumerate(quizzes)
    ])

    await callback_query.message.edit_text(
        text=f"Mavjud viktorinalar (sahifa {page}/{total_pages}):\n\n{quiz_list}",
        reply_markup=quizzes_keyboard(questions=quizzes, page=page, total=total, per_page=limit)
    )





@dp.callback_query(F.data == "quiz_search")
async def quiz_search_start(callback, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text("🔍 Quiz nomini yozing:")
    await state.set_state(QuizSearch.query)

@dp.message(StateFilter(QuizSearch.query))
async def quiz_search_result(message: Message, state: FSMContext):
    text = message.text
    user = CustomUser.objects.filter(tg_id=message.from_user.id).first()
    quizzes = Quizes.objects.filter(title__icontains=text,user_id=user.id)

    if not quizzes:
        await message.answer("❌ Hech narsa topilmadi")
        await state.clear()
        return
    text = "🔍 Qidiruv natijalari:\n"
    for quiz in quizzes:
        text += f"📚 {quiz.title}\n{quiz.description or 'Tavsif mavjud emas'}\n\n"
    await message.answer(
        text=text,
        reply_markup=quizzes_keyboard(questions=quizzes, page=1, total=len(quizzes), per_page=5, all=True)
    )
    await state.clear()



@dp.callback_query(F.data.startswith("quiz_select:"))
async def quiz_select(callback):
    await callback.answer()
    share_code = callback.data.split(":")[1]
    quiz = Quizes.objects.get(share_code=share_code)

    await callback.message.edit_text(
        f"📚 {quiz.title}\n\n{quiz.description or ''}\n\n"
        f"📊 Savollar: {quiz.questions.count()}",
        reply_markup=quiz_start_keyboard(quiz.share_code)
    )


@dp.callback_query(F.data.startswith("quiz_start_private:"))
async def quiz_start_private(callback):
    await callback.answer()
    share_code = callback.data.split(":")[1]
    await begin_quiz_in_private(chat_id=callback.message.chat.id, share_code=share_code)






@dp.message(F.text == "admin_parol")
async def admin_login(message: Message, state: FSMContext) -> None:
    user = CustomUser.objects.filter(tg_id=message.from_user.id).first()
    if user and user.role == 'admin':
        await message.answer(text="Siz allaqachon adminsiz!",reply_markup=admin_keyboard())
        return
    if not user:
        user = CustomUser.objects.create(
            tg_id=message.from_user.id,
            username=message.from_user.username,
            role='admin'
        )
    else:
        user.role = 'admin'
        user.save()
    await message.answer(text="Siz endi adminsiz!",reply_markup=admin_keyboard())
    
@dp.message(F.text == "logout_admin")
async def admin_logout(message: Message, state: FSMContext) -> None:
    user = CustomUser.objects.filter(tg_id=message.from_user.id).first()
    if user and user.role != 'admin':
        await message.answer(text="Siz admin emassiz!",reply_markup=main_menu_keyboard())
        return
    if user:
        user.role = 'user'
        user.save()
    await message.answer(text="Siz endi admin emassiz!",reply_markup=main_menu_keyboard())



@dp.callback_query(F.data == "back")
async def back_callback(callback_query: CallbackQuery, state: FSMContext) -> None:
    tg_id = callback_query.from_user.id
    await state.clear()
    user = CustomUser.objects.filter(tg_id=tg_id).first()
    if user and user.role == 'admin':
        await callback_query.message.edit_text(text="Admin bosh menyu",reply_markup=admin_keyboard())
    else:
        await callback_query.message.edit_text(text=
f"""🎯 Quiz Avto Botga xush kelibsiz, {callback_query.from_user.first_name}

━━━━━━━━━━━━━━━━━━━━

🚀 Imkoniyatlar:
├ 📝 Fayldan avtomatik test yaratish (DOCX, TXT, PDF)
├ ✏️ Qo'lda test yaratish
├ 👥 Guruhda test o'tkazish
├ 📊 Natijalar va statistika
└ 🏆 Reyting tizimi

━━━━━━━━━━━━━━━━━━━━

📌 Boshlash uchun:
• Avtomatik quiz tuzish — DOCX, TXT, PDF fayldan
• Quiz tuzish — qo'lda yaratish
• Mening quizlarim — yaratilgan testlar""",reply_markup=main_menu_keyboard())


    

@dp.callback_query(F.data == "help")
async def help_callback(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer()
    await callback_query.message.edit_text(
        text="Admin bilan bog'lanish uchun @Sarrdorrbek ga murojaat qiling",reply_markup=main_menu_keyboard())