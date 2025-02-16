from typing import Callable, Dict, Any, Awaitable, Union

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from app.service import ApiService, ConverterService, StateService


class ServiceMiddleware(BaseMiddleware):
    def __init__(self, convert_service: ConverterService, api_service: ApiService, state_service: StateService):
        super().__init__()
        self.convert_service = convert_service
        self.api_service = api_service
        self.state_service = state_service

    async def __call__(
            self,
            handler: Callable[[Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]],
            event: Union[Message, CallbackQuery],
            data: Dict[str, Any]
    ) -> Any:
        data["convert_service"] = self.convert_service
        data["api_service"] = self.api_service
        self.state_service.set_context(data.get("state"))
        data["state_service"] = self.state_service
        return await handler(event, data)
