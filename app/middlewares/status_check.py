from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from app.database.requests import get_user_by_id


class StatusMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = event.from_user
        user_data = await get_user_by_id(user.id)

        if not user_data:
            return await handler(event, data)

        if user_data.role == 'admin' or user_data.status == 'approved':
            return await handler(event, data)

        if isinstance(event, Message):
            if event.text == "/start" or event.contact or (event.text and not event.text.startswith('/')):
                return await handler(event, data)
            await event.answer("Доступ ограничен. Завершите регистрацию или ожидайте подтверждения.")
        elif isinstance(event, CallbackQuery):
            await event.answer("Доступ ограничен.", show_alert=True)
        return