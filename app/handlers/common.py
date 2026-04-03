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

@router.message(CommandStart(), StateFilter(any_state))
async def cmd_start(message: Message, state: FSMContext, command: CommandObject):
    await state.clear()
    await register_user(message.from_user.id, message.from_user.username)

    args = command.args
    if args and args.startswith("complex_"):
        try:
            complex_id = int(args.split("_")[1])
            c = await get_complex_by_id(complex_id)
            if c:
                async with async_session() as session:
                    result = await session.execute(select(Photo).where(Photo.complex_id == complex_id))
                    photos = result.scalars().all()

                text = format_complex_info(c)
                plans = await get_floor_plans(complex_id)
                kb = get_floor_plans_kb(complex_id) if plans else None

                if photos:
                    media_group = [InputMediaPhoto(media=p.telegram_file_id) for p in photos[:10]]
                    if len(text) <= 1024:
                        media_group[0].caption = text
                        media_group[0].parse_mode = "HTML"
                        await message.answer_media_group(media_group)
                        if kb:
                            await message.answer("Дополнительная информация:", reply_markup=kb)
                    else:
                        await message.answer_media_group(media_group)
                        await message.answer(text, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True)
                else:
                    await message.answer(text, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True)
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