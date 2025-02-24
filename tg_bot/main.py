import asyncio
import logging

from aiogram import Bot, Dispatcher

import redis.asyncio as redis
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.redis import RedisStorage
from httpx import AsyncClient, Timeout

from app.config import config
from app.routers import router
from app.routers.middleware import ServiceMiddleware, ErrorMiddleware
from app.service import ApiService, ConverterService, StateService
from app.utils.command import get_bot_commands


def get_dispatcher(bot: Bot, storage: BaseStorage) -> Dispatcher:
    convert_service = ConverterService(bot)
    timeout = Timeout(
        connect=60.0,
        read=60.0,
        write=60.0,
        pool=60.0
    )
    api_servie = ApiService(AsyncClient(timeout=timeout))
    state_service = StateService()
    dp = Dispatcher(storage=storage)
    dp.message.middleware(ServiceMiddleware(convert_service, api_servie, state_service))
    dp.callback_query.middleware(ServiceMiddleware(convert_service, api_servie, state_service))
    dp.message.middleware(ErrorMiddleware())
    dp.callback_query.middleware(ErrorMiddleware())
    logging.basicConfig(level=logging.INFO)
    dp.include_routers(router)
    return dp


async def main():
    redis_client = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=0)
    storage = RedisStorage(redis_client)
    bot = Bot(token=config.TG_TOKEN)
    await bot.set_my_commands(get_bot_commands())
    dp = get_dispatcher(bot, storage)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
