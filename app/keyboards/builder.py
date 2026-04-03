from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

def get_main_menu_kb(is_admin: bool) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="🏢 Каталог ЖК")
    builder.button(text="🔍 Поиск по названию")
    builder.button(text="📝 Запрос на обзор")
    if is_admin:
        builder.button(text="➕ Добавить ЖК")
        builder.button(text="⚙️ Управление ЖК")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def get_complex_actions_kb(complex_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Редактировать", callback_data=f"action_edit_{complex_id}")
    builder.button(text="Удалить", callback_data=f"action_del_{complex_id}")
    builder.adjust(2)
    return builder.as_markup()

def get_floor_plans_kb(complex_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📐 Смотреть планировки", callback_data=f"plans_{complex_id}")
    return builder.as_markup()

def get_districts_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    districts = [
        "Алмазарский", "Бектемирский", "Мирабадский", "Мирзо-Улугбекский",
        "Сергелийский", "Учтепинский", "Чиланзарский", "Шайхантахурский",
        "Юнусабадский", "Яккасарайский", "Янгихаётский", "Яшнободский"
    ]
    for d in districts:
        builder.button(text=d, callback_data=f"dist_{d}")
    builder.adjust(2)
    return builder.as_markup()

def get_classes_kb(district: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    classes = ["Comfort", "Business", "Premium"]
    for c in classes:
        builder.button(text=c, callback_data=f"class_{district}_{c}")
    builder.adjust(1)
    return builder.as_markup()

def get_complexes_kb(complexes: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for c in complexes:
        builder.button(text=c.name, callback_data=f"complex_{c.id}")
    builder.adjust(1)
    return builder.as_markup()

def get_edit_districts_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    districts = [
        "Алмазарский", "Бектемирский", "Мирабадский", "Мирзо-Улугбекский",
        "Сергелийский", "Учтепинский", "Чиланзарский", "Шайхантахурский",
        "Юнусабадский", "Яккасарайский", "Янгихаётский", "Яшнободский"
    ]
    for d in districts:
        builder.button(text=d, callback_data=f"editdist_{d}")
    builder.adjust(2)
    return builder.as_markup()

def get_edit_classes_kb(district: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    classes = ["Comfort", "Business", "Premium"]
    for c in classes:
        builder.button(text=c, callback_data=f"editclass_{district}_{c}")
    builder.adjust(1)
    return builder.as_markup()

def get_edit_complexes_kb(complexes: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for c in complexes:
        builder.button(text=c.name, callback_data=f"editcomp_{c.id}")
    builder.adjust(1)
    return builder.as_markup()

def get_fields_to_edit_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    fields = {
        "name": "Название",
        "price": "Цена",
        "current_stage": "Этап",
        "deadline": "Срок сдачи",
        "finish_type": "Отделка",
        "amenities": "Благоустройство",
        "floors": "Этажность",
        "location_link": "Локация (ссылка)"
    }
    for col, txt in fields.items():
        builder.button(text=txt, callback_data=f"field_{col}")
    builder.adjust(2)
    return builder.as_markup()

def get_admin_districts_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    districts = [
        "Алмазарский", "Бектемирский", "Мирабадский", "Мирзо-Улугбекский",
        "Сергелийский", "Учтепинский", "Чиланзарский", "Шайхантахурский",
        "Юнусабадский", "Яккасарайский", "Янгихаётский", "Яшнободский"
    ]
    for d in districts:
        builder.button(text=d)
    return builder.adjust(2).as_markup(resize_keyboard=True, one_time_keyboard=True)

def get_admin_classes_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    classes = ["Comfort", "Business", "Premium"]
    for c in classes:
        builder.button(text=c)
    return builder.adjust(3).as_markup(resize_keyboard=True, one_time_keyboard=True)

def get_admin_finish_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    finishes = ["White-Box", "С ремонтом от застройщика", "Черновая отделка"]
    for f in finishes:
        builder.button(text=f)
    return builder.adjust(1).as_markup(resize_keyboard=True, one_time_keyboard=True)

def get_admin_stage_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    stages = ["Котлован", "Возведение каркаса", "СМР", "Внутренние отделочные работы"]
    for s in stages:
        builder.button(text=s)
    return builder.adjust(1).as_markup(resize_keyboard=True, one_time_keyboard=True)