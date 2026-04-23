from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, InputMediaPhoto, Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import any_state

from app.database.requests import (
    register_user, get_user_by_id, update_user_registration, get_admins,
    get_complexes_by_filter, get_complex_by_id, search_complexes_by_name,
    get_floor_plans, get_photos
)
from app.states.states import Registration, UserSearch, RequestReview
from app.keyboards.builder import (
    get_contact_kb, get_admin_approve_kb, get_main_menu_kb,
    get_districts_kb, get_classes_kb, get_complexes_kb, get_floor_plans_kb
)
from app.utils.formatters import format_complex_info

router = Router()


# --- БЛОК АВТОРИЗАЦИИ И РЕГИСТРАЦИИ ---

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await register_user(message.from_user.id, message.from_user.username)
    user = await get_user_by_id(message.from_user.id)

    if user.role == 'admin' or user.status == 'approved':
        await message.answer("Доступ разрешен.", reply_markup=get_main_menu_kb(user.role == 'admin'))
        return

    if user.status == 'rejected':
        await message.answer("Доступ запрещен.", reply_markup=ReplyKeyboardRemove())
        return

    if user.status == 'pending_approval':
        await message.answer("Заявка находится на рассмотрении.", reply_markup=ReplyKeyboardRemove())
        return

    await state.set_state(Registration.full_name)
    await message.answer("Регистрация. Введите ваше ФИО:", reply_markup=ReplyKeyboardRemove())


@router.message(Registration.full_name)
async def process_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(Registration.phone)
    await message.answer("Отправьте номер телефона:", reply_markup=get_contact_kb())


@router.message(Registration.phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext):
    await process_phone(message, state, message.contact.phone_number)


@router.message(Registration.phone, F.text)
async def process_phone_text(message: Message, state: FSMContext):
    await process_phone(message, state, message.text)


async def process_phone(message: Message, state: FSMContext, phone: str):
    data = await state.get_data()
    full_name = data.get("full_name")
    tg_id = message.from_user.id

    await update_user_registration(tg_id, full_name, phone)
    await state.clear()
    await message.answer("Данные отправлены. Ожидайте подтверждения администратором.",
                         reply_markup=ReplyKeyboardRemove())

    admins = await get_admins()
    admin_text = f"Заявка на доступ:\nФИО: {full_name}\nТелефон: {phone}\nID: {tg_id}\nUsername: @{message.from_user.username}"
    for admin_id in admins:
        try:
            await message.bot.send_message(admin_id, admin_text, reply_markup=get_admin_approve_kb(tg_id))
        except Exception:
            pass


# --- БЛОК КАТАЛОГА ЖК ---

@router.message(F.text == "🏢 Каталог ЖК", StateFilter(any_state))
async def catalog_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Выберите район:", reply_markup=get_districts_kb())


@router.callback_query(F.data.startswith("dist_"))
async def select_class(callback: CallbackQuery):
    district = callback.data.split("_")[1]
    await callback.message.edit_text(f"Район: {district}. Выберите класс:", reply_markup=get_classes_kb(district))


@router.callback_query(F.data.startswith("class_"))
async def select_complex(callback: CallbackQuery):
    parts = callback.data.split("_")
    district, estate_class = parts[1], parts[2]
    complexes = await get_complexes_by_filter(district, estate_class)
    if not complexes:
        await callback.answer("В этом разделе нет объектов", show_alert=True)
        return
    await callback.message.edit_text("Выберите ЖК:", reply_markup=get_complexes_kb(complexes))


@router.callback_query(F.data.startswith("complex_"))
async def show_complex(callback: CallbackQuery):
    complex_id = int(callback.data.split("_")[1])
    c = await get_complex_by_id(complex_id)
    if not c:
        await callback.answer("ЖК не найден", show_alert=True)
        return

    photos = await get_photos(complex_id)
    plans = await get_floor_plans(complex_id)
    text = format_complex_info(c)
    kb = get_floor_plans_kb(complex_id) if plans else None

    await callback.message.delete()
    if photos:
        if len(photos) == 1:
            await callback.message.answer_photo(photos[0].telegram_file_id, caption=text, parse_mode="HTML",
                                                reply_markup=kb)
        else:
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

    await callback.message.delete()
    if len(plans) == 1:
        await callback.message.answer_photo(plans[0].telegram_file_id)
    else:
        media_group = [InputMediaPhoto(media=p.telegram_file_id) for p in plans[:10]]
        await callback.message.answer_media_group(media_group)


# --- БЛОК ПОИСКА И ОБЗОРОВ ---

@router.message(F.text == "🔍 Поиск по названию", StateFilter(any_state))
async def search_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(UserSearch.query)
    await message.answer("Введите название ЖК (или часть названия) для поиска:", reply_markup=ReplyKeyboardRemove())


@router.message(UserSearch.query)
async def process_search(message: Message, state: FSMContext):
    query = message.text
    complexes = await search_complexes_by_name(query)
    if not complexes:
        await message.answer("По вашему запросу ничего не найдено.")
        user = await get_user_by_id(message.from_user.id)
        await message.answer("Попробуйте еще раз или вернитесь в меню.",
                             reply_markup=get_main_menu_kb(user.role == 'admin'))
        return

    await message.answer("Найденные ЖК:", reply_markup=get_complexes_kb(complexes))
    await state.clear()


@router.message(F.text == "📝 Запрос на обзор", StateFilter(any_state))
async def review_request_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(RequestReview.name)
    await message.answer("Введите название ЖК, который нужно проверить:", reply_markup=ReplyKeyboardRemove())


@router.message(RequestReview.name)
async def process_review_request(message: Message, state: FSMContext):
    complex_name = message.text
    admins = await get_admins()
    user_name = message.from_user.username or message.from_user.full_name

    for admin_id in admins:
        try:
            await message.bot.send_message(
                admin_id,
                f"🔔 <b>Новый запрос на обзор ЖК!</b>\n\nОт пользователя: @{user_name}\nНазвание ЖК: <b>{complex_name}</b>",
                parse_mode="HTML"
            )
        except Exception:
            pass

    user = await get_user_by_id(message.from_user.id)
    await message.answer("Ваш запрос отправлен администраторам. Спасибо!",
                         reply_markup=get_main_menu_kb(user.role == 'admin'))
    await state.clear()