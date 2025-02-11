import asyncio
import logging

from aiogram import Bot, Dispatcher

import redis.asyncio as redis
from aiogram.fsm.storage.redis import RedisStorage

from app.config import config
from app.routers import router
from app.routers.middleware import ServiceMiddleware
from app.services.converter import ConverterService


async def main():
    redis_client = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=0)
    storage = RedisStorage(redis_client)
    bot = Bot(token=config.TG_TOKEN)
    convert_service = ConverterService(bot)
    dp = Dispatcher(storage=storage)
    dp.message.middleware(ServiceMiddleware(convert_service))
    logging.basicConfig(level=logging.INFO)
    dp.include_routers(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
