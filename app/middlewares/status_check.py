from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from app.database.requests import get_user_by_id
from app.config import settings
from app.states.states import Registration


class StatusMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = event.from_user

        if user.id in settings.admin_list:
            return await handler(event, data)

        user_data = await get_user_by_id(user.id)

        if user_data and (user_data.role == 'admin' or user_data.status == 'approved'):
            return await handler(event, data)

        state: FSMContext = data.get('state')
        current_state = await state.get_state() if state else None
        registration_states = [Registration.full_name.state, Registration.phone.state]

        if isinstance(event, Message):
            # Пропуск команды /start при любых условиях
            if event.text and event.text.startswith("/start"):
                return await handler(event, data)

            if current_state in registration_states:
                menu_buttons = ["🏢 Каталог ЖК", "🔍 Поиск по названию", "📝 Запрос на обзор", "➕ Добавить ЖК",
                                "⚙️ Управление ЖК", "📊 Аналитика рынка"]
                if event.text in menu_buttons:
                    await event.answer("Для продолжения завершите регистрацию. Введите запрашиваемые данные.",
                                       reply_markup=ReplyKeyboardRemove())
                    return
                return await handler(event, data)

            # Принудительное удаление зависшей клавиатуры
            await event.answer("Доступ ограничен. Введите /start для регистрации.", reply_markup=ReplyKeyboardRemove())
            return

        elif isinstance(event, CallbackQuery):
            await event.answer("Доступ ограничен.", show_alert=True)
            return