import asyncio
from aiogram import Bot
from app.database.requests import get_all_user_ids

async def broadcast_new_complex(bot: Bot, complex_id: int, name: str, is_update: bool = False):
    user_ids = await get_all_user_ids()
    bot_info = await bot.get_me()
    link = f"https://t.me/{bot_info.username}?start=complex_{complex_id}"

    action = "обновлена информация по ЖК" if is_update else "в базу добавлен новый ЖК"
    text = (
        f"🔔 <b>Уведомление</b>\n\n"
        f"Внимание, {action}: <b>{name}</b>\n\n"
        f"👉 <a href='{link}'>Нажмите здесь, чтобы открыть карточку</a>"
    )

    for user_id in user_ids:
        try:
            await bot.send_message(user_id, text, parse_mode="HTML", disable_web_page_preview=True)
            await asyncio.sleep(0.05)  # Задержка 50 мс предотвращает Flood limit
        except Exception:
            continue