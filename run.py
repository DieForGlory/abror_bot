import asyncio
import aiohttp
from aiogram import Bot, Dispatcher

# Глобальное отключение проверки SSL-сертификатов для aiohttp (обход блокировок)
_orig_connector_init = aiohttp.TCPConnector.__init__


def _patched_connector_init(self, *args, **kwargs):
    kwargs['ssl'] = False
    _orig_connector_init(self, *args, **kwargs)


aiohttp.TCPConnector.__init__ = _patched_connector_init

from app.config import settings
from app.database.engine import engine
from app.database.models import Base

from app.handlers.common import router as common_router
from app.handlers.admin import router as admin_router
from app.handlers.user import router as user_router


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def main():
    await init_models()

    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(common_router)
    dp.include_router(admin_router)
    dp.include_router(user_router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())