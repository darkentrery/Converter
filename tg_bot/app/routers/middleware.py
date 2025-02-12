from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from app.service.api import ApiService
from app.service.converter import ConverterService


class ServiceMiddleware(BaseMiddleware):
    def __init__(self, convert_service: ConverterService, api_service: ApiService):
        super().__init__()
        self.convert_service = convert_service
        self.api_service = api_service

    async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message, data: Dict[str, Any]) -> Any:
        data["convert_service"] = self.convert_service
        data["api_service"] = self.api_service
        return await handler(event, data)
