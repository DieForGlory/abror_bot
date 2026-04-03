from app.database.models import ResidentialComplex


def format_complex_info(c: ResidentialComplex) -> str:
    updated = c.updated_at.strftime("%d.%m.%Y %H:%M") if c.updated_at else "Нет данных"
    link_text = f"<a href='{c.location_link}'>Открыть на карте</a>" if c.location_link and c.location_link != "-" else "Не указана"

    return (
        f"🏢 <b>{c.name}</b>\n\n"
        f"📍 <b>Район:</b> {c.district}\n"
        f"💎 <b>Класс:</b> {c.estate_class}\n"
        f"🏗 <b>Этажность:</b> {c.floors}\n"
        f"🛠 <b>Отделка:</b> {c.finish_type}\n"
        f"💰 <b>Цена:</b> {c.price}\n"
        f"📅 <b>Срок сдачи:</b> {c.deadline}\n"
        f"🗺 <b>Локация:</b> {link_text}\n\n"
        f"🌳 <b>Благоустройство:</b>\n{c.amenities}\n\n"
        f"🚧 <b>Текущий этап:</b>\n{c.current_stage}\n\n"
        f"🔄 <i>Обновлено: {updated}</i>"
    )