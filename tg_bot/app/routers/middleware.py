from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from tg_bot.app.services.converter import ConverterService


class ServiceMiddleware(BaseMiddleware):
    def __init__(self, convert_service: ConverterService):
        super().__init__()
        self.convert_service = convert_service

    async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message, data: Dict[str, Any]) -> Any:
        data["convert_service"] = self.convert_service
        return await handler(event, data)
