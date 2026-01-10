from aiogram.types import KeyboardButton, ReplyKeyboardMarkup



def back():
    keyboard1 = KeyboardButton(text = "🔙 Orqaga")
    design = [[keyboard1]]
    return ReplyKeyboardMarkup(keyboard=design , resize_keyboard=True)

def phone_number_btn():
    keyboard1=KeyboardButton(text = "Raqamni yuborish 📞",request_contact=True)
    keyboard2=KeyboardButton(text="🔙 Orqaga")
    design=[[keyboard1],[keyboard2]]
    return ReplyKeyboardMarkup(keyboard=design ,one_time_keyboard=True,
                               resize_keyboard=True)
    
    
def get_location_keyboard():
    
    contact_button = KeyboardButton(text="📍 Lokatsiyamni yuborish", request_location=True)
    design = [[contact_button]]
    return ReplyKeyboardMarkup(keyboard=design, resize_keyboard=True)