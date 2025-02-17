import traceback
from typing import Callable, Dict, Any, Awaitable, Union

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from app import exc, entity
from app.logger import logger
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
        data["user"] = await self.get_or_create_user(event)
        return await handler(event, data)

    async def get_or_create_user(self, event: Union[Message, CallbackQuery]) -> entity.User:
        try:
            user = await self.api_service.get_user_by_tg_id(event.from_user.id)
        except exc.NotFoundError:
            user = await self.api_service.create_user(entity.AddUser(
                username=event.from_user.username,
                last_name=event.from_user.last_name,
                first_name=event.from_user.first_name,
                tg_id=event.from_user.id
            ))
        return user


class ErrorMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)
        except exc.NotFoundError as e:
            logger.error(f"Ошибка в хендлере: {e=} \n {traceback.format_exc()}")
            await self.send_error_message(event, e)
        except exc.AlreadyExists as e:
            logger.error(f"Ошибка в хендлере: {e=} \n {traceback.format_exc()}")
            await self.send_error_message(event, e)
        except exc.InvalidRequest as e:
            logger.error(f"Ошибка в хендлере: {e=} \n {traceback.format_exc()}")
            await self.send_error_message(event, e)
        except Exception as e:
            logger.error(f"Ошибка в хендлере: {e=} \n {traceback.format_exc()}")
            await self.send_error_message(event, e)

    async def send_error_message(self, event: Union[Message, CallbackQuery], error: Exception | None = None) -> None:
        text = "Произошла ошибка, попробуйте позже."
        if error:
            text += f" {error=}"
        if isinstance(event, Message):
            await event.answer("Произошла ошибка, попробуйте позже.")
        elif isinstance(event, CallbackQuery):
            await event.answer("Произошла ошибка, попробуйте позже.", show_alert=True)
