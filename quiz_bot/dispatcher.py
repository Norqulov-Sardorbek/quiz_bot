from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from decouple import config
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from quiz_bot.middleware import DjangoDBMiddleware
TOKEN = config("BOT_TOKEN")

bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

print(TOKEN)

dp = Dispatcher(storage=MemoryStorage())
dp.update.middleware(DjangoDBMiddleware())