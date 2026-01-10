from decouple import config
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import  InlineQueryResultArticle, InputTextMessageContent

BOT_USERNAME = config("BOT_USERNAME")


def main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Barcha viktorinalar", callback_data="all_quizzes"),
        ],
        
    ])
    return keyboard

def admin_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📋 Buyurtma raqami bo'yicha qidirish", callback_data="check_order_number"),
        ],
        [
            InlineKeyboardButton(text="📲 Kanalga rasm yuborish", callback_data="send_image_to_channel"),
        ]
    ])
    return keyboard

def back_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="back"),
        ],
    ])
    return keyboard

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def quizzes_keyboard(questions, page: int, total: int, per_page: int, all=False) :
    builder = InlineKeyboardBuilder()
    start_index = (page - 1) * per_page

    for i, q in enumerate(questions, start=start_index + 1):
        builder.button(
            text=str(i),
            callback_data=f"quiz_select:{q.share_code}"
        )

    builder.adjust(5)
    nav_buttons = []
    total_pages = (total + per_page - 1) // per_page

    if page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Oldingi",
                callback_data=f"quiz_page:{page - 1}"
            )
        )
    if page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text="Keyingi ➡️",
                callback_data=f"quiz_page:{page + 1}"
            )
        )

    if nav_buttons:
        builder.row(*nav_buttons)

    # Orqaga tugmasi
    builder.row(
        InlineKeyboardButton(
            text=" 🔍 Qidirish",
            callback_data="quiz_search"
        ),
        InlineKeyboardButton(
            text="🔙 Orqaga",
            callback_data=f"{'all_quizzes' if all else 'back'}"
        ),
    )

    return builder.as_markup()




def quiz_start_keyboard(share_code):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="👤 Botda ishlash",
                callback_data=f"quiz_start_private:{share_code}"
            ),
            InlineKeyboardButton(
                text="👥 Guruhda ishlash",
                url=f"https://t.me/{BOT_USERNAME}?startgroup={share_code}")
        ],
        [
            InlineKeyboardButton(
                text="📤 Testni ulashish",
                switch_inline_query=f"quiz:{share_code}"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 Ortga",
                callback_data="all_quizzes"
            )
        ]
    ])
    

def quiz_start_group_keyboard(share_code):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Bu quizni boshlash",
                url=f"https://t.me/{BOT_USERNAME}?start={share_code}")
        ],
            [
                InlineKeyboardButton(text="Guruhda testni boshlash", url=f"https://t.me/{BOT_USERNAME}?startgroup={share_code}")
            ],
            [
                InlineKeyboardButton(
                    text="📤 Testni ulashish",
                    switch_inline_query=f"quiz:{share_code}"
                )
            ]
    ])    
    return keyboard

def share_quiz_keyboard(share_code):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📤 Testni ulashish",
                switch_inline_query=f"quiz:{share_code}"
            )
        ],
    ])    

def quiz_ready_group_button(share_code):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Men tayyorman!",
                callback_data=f"quiz_ready_group:{share_code}"
            )
        ]
    ])
    
def quiz_ready_private_button(share_code):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Men tayyorman!",
                callback_data=f"quiz_ready_private:{share_code}"
            )
        ]
    ])
    
def inline_query_btn(quiz, code):
    keyboard = InlineQueryResultArticle(
        id=code,
        title=quiz.title,
        description=f"{quiz.questions.count()} ta savol · {quiz.deadline} soniya",
        input_message_content=InputTextMessageContent(
            message_text=f"🏁 {quiz.title}\n\nQuiz boshlandi!"
        ),
        reply_markup=quiz_start_group_keyboard(code)
    )
    return keyboard

def resume_group_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="▶️ Davom etish!", callback_data="quiz_resume_group")],
            [InlineKeyboardButton(text="Testni to'xtatish", callback_data="quiz_stop")]
        ]
    )
    
def resume_private_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="▶️ Davom etish!", callback_data="quiz_resume_private")],
            [InlineKeyboardButton(text="Testni to'xtatish", callback_data="quiz_stop")]
        ]
    )
    
def restart_quiz_keyboard(share_code):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Qaytadan urinish",
                callback_data=f"quiz_restart_private:{share_code}"
            )
        ],
            [
                InlineKeyboardButton(text="Guruhda testni boshlash", url=f"https://t.me/{BOT_USERNAME}?startgroup={share_code}")
            ],
            [
                InlineKeyboardButton(
                    text="📤 Testni ulashish",
                    switch_inline_query=f"quiz:{share_code}"
                )
            ]
    ])    
    return keyboard