from aiogram import BaseMiddleware
from django.db import close_old_connections

class DjangoDBMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        close_old_connections()
        try:
            return await handler(event, data)
        finally:
            close_old_connections()
