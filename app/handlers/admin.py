from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from app.states.states import AddComplex, EditComplex
from app.database.requests import (
    add_complex, add_photo, add_floor_plan, get_complexes_by_filter,
    update_complex_field, delete_complex, get_complex_by_id
)
from app.utils.broadcaster import broadcast_new_complex
from app.middlewares.role_check import AdminMiddleware
from app.keyboards.builder import (
    get_admin_districts_kb, get_admin_classes_kb, get_admin_finish_kb, get_admin_stage_kb,
    get_edit_districts_kb, get_edit_classes_kb, get_edit_complexes_kb, get_fields_to_edit_kb,
    get_complex_actions_kb, get_main_menu_kb
)
from aiogram.fsm.state import any_state
from app.config import settings
from app.database.requests import get_analytics_data

router = Router()
router.message.middleware(AdminMiddleware())
router.callback_query.middleware(AdminMiddleware())


@router.message(F.text == "➕ Добавить ЖК", StateFilter(any_state))
async def admin_add_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(AddComplex.name)
    await message.answer("Введите название ЖК:", reply_markup=ReplyKeyboardRemove())


@router.message(AddComplex.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddComplex.developer)
    await message.answer("Введите застройщика:", reply_markup=ReplyKeyboardRemove())

@router.message(AddComplex.developer)
async def process_developer(message: Message, state: FSMContext):
    await state.update_data(developer=message.text)
    await state.set_state(AddComplex.district)
    await message.answer("Выберите район:", reply_markup=get_admin_districts_kb())

@router.message(AddComplex.district)
async def process_district(message: Message, state: FSMContext):
    await state.update_data(district=message.text)
    await state.set_state(AddComplex.estate_class)
    await message.answer("Выберите класс:", reply_markup=get_admin_classes_kb())


@router.message(AddComplex.estate_class)
async def process_class(message: Message, state: FSMContext):
    await state.update_data(estate_class=message.text)
    await state.set_state(AddComplex.finish_type)
    await message.answer("Выберите тип отделки:", reply_markup=get_admin_finish_kb())


@router.message(AddComplex.finish_type)
async def process_finish(message: Message, state: FSMContext):
    await state.update_data(finish_type=message.text)
    await state.set_state(AddComplex.price)
    await message.answer("Введите цену (только цифры):", reply_markup=ReplyKeyboardRemove())


@router.message(AddComplex.price)
async def process_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.set_state(AddComplex.price_numeric)
    await message.answer("Введите числовую цену (для аналитики, только цифры):")

@router.message(AddComplex.price)
async def process_price(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Требуется число. Введите цену (только цифры):")
        return
    await state.update_data(price=int(message.text))
    await state.set_state(AddComplex.floors)
    await message.answer("Введите этажность (число или диапазон, например 14-16):")


@router.message(EditComplex.input_value)
async def edit_stage_final(message: Message, state: FSMContext):
    data = await state.get_data()
    complex_id = data['complex_id']
    field_to_update = data['field_to_update']

    new_value = message.text
    if field_to_update == "price":
        if not new_value.isdigit():
            await message.answer("Требуется число. Введите заново:")
            return
        new_value = int(new_value)

    await update_complex_field(complex_id, field_to_update, new_value)

    c = await get_complex_by_id(complex_id)
    await broadcast_new_complex(message.bot, complex_id, c.name, is_update=True)

    await state.clear()
    await message.answer("Данные обновлены.", reply_markup=get_main_menu_kb(True))

@router.message(AddComplex.floors)
async def process_floors(message: Message, state: FSMContext):
    await state.update_data(floors=message.text)
    await state.set_state(AddComplex.amenities)
    await message.answer("Введите описание благоустройства:")


@router.message(AddComplex.amenities)
async def process_amenities(message: Message, state: FSMContext):
    await state.update_data(amenities=message.text)
    await state.set_state(AddComplex.deadline)
    await message.answer("Введите срок сдачи:")


@router.message(AddComplex.deadline)
async def process_deadline(message: Message, state: FSMContext):
    await state.update_data(deadline=message.text)
    await state.set_state(AddComplex.current_stage)
    await message.answer("Выберите текущий этап строительства:", reply_markup=get_admin_stage_kb())


@router.message(AddComplex.current_stage)
async def process_stage(message: Message, state: FSMContext):
    await state.update_data(current_stage=message.text)
    await state.set_state(AddComplex.location_link)
    await message.answer("Отправьте ссылку на локацию (Яндекс/Google) или - для пропуска:",
                         reply_markup=ReplyKeyboardRemove())


@router.message(AddComplex.location_link)
async def process_location(message: Message, state: FSMContext):
    await state.update_data(location_link=message.text)
    await state.set_state(AddComplex.photos)
    await message.answer("Отправьте фото объекта по одному. По завершении введите /next:")


@router.message(AddComplex.photos, F.photo)
async def process_photos(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)


@router.message(AddComplex.photos, Command("next"))
async def process_next_plans(message: Message, state: FSMContext):
    await state.set_state(AddComplex.floor_plans)
    await message.answer("Отправьте фото планировок по одному. По завершении введите /done:")


@router.message(AddComplex.floor_plans, F.photo)
async def process_floor_plans(message: Message, state: FSMContext):
    data = await state.get_data()
    plans = data.get("plans", [])
    plans.append(message.photo[-1].file_id)
    await state.update_data(plans=plans)


@router.message(AddComplex.floor_plans, Command("done"))
async def process_done(message: Message, state: FSMContext):
    data = await state.get_data()
    photo_ids = data.pop("photos", [])
    plan_ids = data.pop("plans", [])

    complex_id = await add_complex(data)
    for file_id in photo_ids:
        await add_photo(complex_id, file_id)
    for file_id in plan_ids:
        await add_floor_plan(complex_id, file_id)

    # Вызов рассылки
    await broadcast_new_complex(message.bot, complex_id, data['name'], is_update=False)

    await state.clear()
    await message.answer(f"Запись сохранена.", reply_markup=get_main_menu_kb(True))


@router.message(F.text == "⚙️ Управление ЖК", StateFilter(any_state))
async def admin_edit_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(EditComplex.choice_district)
    await message.answer("Управление: Выберите район ЖК:", reply_markup=get_edit_districts_kb())


@router.callback_query(EditComplex.choice_district, F.data.startswith("editdist_"))
async def edit_stage_district(callback: CallbackQuery, state: FSMContext):
    district = callback.data.split("_")[1]
    await state.update_data(district=district)
    await state.set_state(EditComplex.choice_class)
    await callback.message.edit_text(f"Район: {district}. Выберите класс:", reply_markup=get_edit_classes_kb(district))


@router.callback_query(EditComplex.choice_class, F.data.startswith("editclass_"))
async def edit_stage_class(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    district, estate_class = parts[1], parts[2]
    complexes = await get_complexes_by_filter(district, estate_class)
    if not complexes:
        await callback.answer("В этом разделе нет объектов", show_alert=True)
        return
    await state.set_state(EditComplex.choice_complex)
    await callback.message.edit_text("Выберите ЖК:", reply_markup=get_edit_complexes_kb(complexes))


@router.callback_query(EditComplex.choice_complex, F.data.startswith("editcomp_"))
async def edit_stage_complex(callback: CallbackQuery, state: FSMContext):
    complex_id = int(callback.data.split("_")[1])
    await state.update_data(complex_id=complex_id)
    await state.set_state(EditComplex.action_select)
    await callback.message.edit_text("Выберите действие:", reply_markup=get_complex_actions_kb(complex_id))


@router.callback_query(EditComplex.action_select, F.data.startswith("action_del_"))
async def process_delete(callback: CallbackQuery, state: FSMContext):
    complex_id = int(callback.data.split("_")[2])
    await delete_complex(complex_id)
    await state.clear()
    await callback.message.edit_text("ЖК удален.")


@router.callback_query(EditComplex.action_select, F.data.startswith("action_edit_"))
async def process_edit_field(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EditComplex.choice_field)
    await callback.message.edit_text("Что именно нужно изменить?", reply_markup=get_fields_to_edit_kb())


@router.callback_query(EditComplex.choice_field, F.data.startswith("field_"))
async def edit_stage_field(callback: CallbackQuery, state: FSMContext):
    field_name = callback.data.split("_")[1]
    await state.update_data(field_to_update=field_name)
    await state.set_state(EditComplex.input_value)
    await callback.message.delete()
    if field_name == "current_stage":
        await callback.message.answer("Выберите новый этап:", reply_markup=get_admin_stage_kb())
    elif field_name == "finish_type":
        await callback.message.answer("Выберите тип отделки:", reply_markup=get_admin_finish_kb())
    else:
        await callback.message.answer("Введите новое значение для этого поля:", reply_markup=ReplyKeyboardRemove())


@router.message(F.text == "📊 Аналитика рынка", StateFilter(any_state))
async def admin_analytics(message: Message, state: FSMContext):
    await state.clear()
    districts, classes, developers = await get_analytics_data()

    text = "📊 <b>Аналитика рынка недвижимости</b>\n\n"

    text += "📍 <b>Средняя цена по районам:</b>\n"
    if not districts:
        text += "Нет данных\n"
    for dist, avg_price in districts:
        text += f"— {dist}: {avg_price}\n"

    text += "\n💎 <b>Средняя цена по классам:</b>\n"
    if not classes:
        text += "Нет данных\n"
    for cls, avg_price in classes:
        text += f"— {cls}: {avg_price}\n"

    text += "\n🏗 <b>Средняя цена по застройщикам (Район | Класс):</b>\n"
    if not developers:
        text += "Нет данных\n"
    for dev, dist, cls, avg_price in developers:
        text += f"— <b>{dev}</b> ({dist}, {cls}): {avg_price}\n"

    await message.answer(text, parse_mode="HTML")