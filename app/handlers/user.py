from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from app.keyboards.builder import get_classes_kb, get_complexes_kb, get_districts_kb, get_floor_plans_kb
from app.database.requests import get_complexes_by_filter, get_complex_by_id, search_complexes_by_name, get_floor_plans
from app.database.engine import async_session
from app.database.models import Photo
from app.utils.formatters import format_complex_info
from app.states.states import UserSearch
from aiogram.filters import StateFilter
from aiogram.fsm.state import any_state

router = Router()


@router.message(F.text == "📝 Запрос на обзор", StateFilter(any_state))
async def review_request_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(RequestReview.name)
    await message.answer("Введите название ЖК, который нужно проверить:")


@router.message(RequestReview.name)
async def review_request_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(RequestReview.comment)
    await message.answer("Добавьте комментарий (что именно проверить) или отправьте '-':")


@router.message(RequestReview.comment)
async def review_request_final(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await state.clear()

    # Уведомление админов
    admin_text = (
        f"📩 <b>Новый запрос на обзор!</b>\n\n"
        f"От: {message.from_user.full_name} (@{message.from_user.username})\n"
        f"ЖК: {data['name']}\n"
        f"Комментарий: {message.text}"
    )

    for admin_id in settings.admin_list:
        try:
            await bot.send_message(admin_id, admin_text, parse_mode="HTML")
        except Exception:
            continue

    await message.answer("Ваш запрос отправлен специалистам. Спасибо!")

@router.message(F.text == "🏢 Каталог ЖК", StateFilter(any_state))
async def user_catalog(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Выберите район:", reply_markup=get_districts_kb())


@router.message(F.text == "🔍 Поиск по названию", StateFilter(any_state))
async def user_search_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(UserSearch.input_name)
    await message.answer("Введите название ЖК:")


@router.message(UserSearch.input_name)
async def user_search_process(message: Message, state: FSMContext):
    complexes = await search_complexes_by_name(message.text)
    await state.clear()
    if not complexes:
        await message.answer("Совпадений не найдено.")
        return
    await message.answer("Результаты поиска:", reply_markup=get_complexes_kb(complexes))


@router.callback_query(F.data.startswith("dist_"))
async def process_district(callback: CallbackQuery):
    district = callback.data.split("_")[1]
    await callback.message.edit_text(f"Район: {district}. Выберите класс:", reply_markup=get_classes_kb(district))


@router.callback_query(F.data.startswith("class_"))
async def process_class(callback: CallbackQuery):
    parts = callback.data.split("_")
    complexes = await get_complexes_by_filter(parts[1], parts[2])
    if not complexes:
        await callback.answer("Объекты не найдены", show_alert=True)
        return
    await callback.message.edit_text("Выберите объект:", reply_markup=get_complexes_kb(complexes))


@router.callback_query(F.data.startswith("complex_"))
async def process_complex(callback: CallbackQuery):
    complex_id = int(callback.data.split("_")[1])
    c = await get_complex_by_id(complex_id)
    if not c:
        await callback.answer("Запись удалена", show_alert=True)
        return

    await callback.message.delete()

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
            await callback.message.answer_media_group(media_group)
            if kb:
                await callback.message.answer("Дополнительная информация:", reply_markup=kb)
        else:
            await callback.message.answer_media_group(media_group)
            await callback.message.answer(text, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True)
    else:
        await callback.message.answer(text, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True)


@router.callback_query(F.data.startswith("plans_"))
async def process_plans(callback: CallbackQuery):
    complex_id = int(callback.data.split("_")[1])
    plans = await get_floor_plans(complex_id)
    if not plans:
        await callback.answer("Планировки отсутствуют", show_alert=True)
        return

    media_group = [InputMediaPhoto(media=p.telegram_file_id) for p in plans[:10]]
    await callback.message.answer_media_group(media_group)
    await callback.answer()