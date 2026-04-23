from aiogram import Router
from aiogram.filters import CommandStart, Command, CommandObject, StateFilter
from aiogram.types import Message, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import any_state
from sqlalchemy import select

from app.keyboards.builder import get_main_menu_kb, get_floor_plans_kb
from app.config import settings
from app.database.engine import async_session
from app.database.models import Photo
from app.database.requests import register_user, get_complex_by_id, get_floor_plans
from app.utils.formatters import format_complex_info

router = Router()

@router.message(Command("cancel"), StateFilter(any_state))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    is_admin = message.from_user.id in settings.admin_list
    await message.answer("Действие отменено.", reply_markup=get_main_menu_kb(is_admin))