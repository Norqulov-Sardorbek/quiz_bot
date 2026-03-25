from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats

from quiz_bot.dispatcher import bot


async def set_bot_commands():
    commands = [
        BotCommand(command="start", description="🚀 Botni ishga tushirish"),
        BotCommand(command="stop", description="🛑 Testni to'xtatish"),
    ]
    group_commands = [
        BotCommand(command="stop", description="🛑 Testni to'xtatish"),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(group_commands, scope=BotCommandScopeAllGroupChats())
    
    

