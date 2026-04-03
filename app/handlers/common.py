from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.keyboards.builder import get_main_menu_kb
from app.config import settings
from aiogram.filters import StateFilter
from aiogram.fsm.state import any_state
from aiogram.filters import CommandObject
from app.database.requests import register_user, get_complex_by_id
from app.utils.formatters import format_complex_info

router = Router()


@router.message(CommandStart(), StateFilter(any_state))
async def cmd_start(message: Message, state: FSMContext, command: CommandObject):
    await state.clear()
    await register_user(message.from_user.id, message.from_user.username)

    # Обработка глубокой ссылки start=complex_ID
    args = command.args
    if args and args.startswith("complex_"):
        try:
            complex_id = int(args.split("_")[1])
            c = await get_complex_by_id(complex_id)
            if c:
                text = format_complex_info(c)
                await message.answer(text, parse_mode="HTML")
                return
        except (ValueError, IndexError):
            pass

    is_admin = message.from_user.id in settings.admin_list
    await message.answer("Главное меню:", reply_markup=get_main_menu_kb(is_admin))

@router.message(Command("cancel"), StateFilter(any_state))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    is_admin = message.from_user.id in settings.admin_list
    await message.answer("Действие отменено.", reply_markup=get_main_menu_kb(is_admin))