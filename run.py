import asyncio
import aiohttp
from aiogram import Bot, Dispatcher
import logging

logging.basicConfig(level=logging.INFO)
_orig_connector_init = aiohttp.TCPConnector.__init__

def _patched_connector_init(self, *args, **kwargs):
    kwargs['ssl'] = False
    _orig_connector_init(self, *args, **kwargs)

aiohttp.TCPConnector.__init__ = _patched_connector_init

from app.config import settings
from app.handlers.common import router as common_router
from app.handlers.admin import router as admin_router
from app.handlers.user import router as user_router

async def main():
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(common_router)
    dp.include_router(admin_router)
    dp.include_router(user_router)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())