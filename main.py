import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from converter.config import config
from converter.routers import router
from converter.routers.middleware import ConvertMiddleware
from converter.services.converter import ConverterService


async def main():
    bot = Bot(token=config.TOKEN)
    storage = MemoryStorage()
    convert_service = ConverterService(bot)
    dp = Dispatcher(storage=storage)
    dp.message.middleware(ConvertMiddleware(convert_service))
    logging.basicConfig(level=logging.INFO)
    dp.include_routers(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
