import datetime

import pytest
import pytest_asyncio
from aiogram import Dispatcher, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message, Chat, User, Update
from aiogram.fsm.storage.memory import MemoryStorage
from unittest.mock import AsyncMock

from app import entity
from main import get_dispatcher


@pytest_asyncio.fixture(scope="session")
async def bot():
    """Создаем мок-бота"""
    bot_mock = AsyncMock(spec=Bot)
    bot_mock.token = "TEST_TOKEN"
    yield bot_mock
    bot_mock.reset_mock()


@pytest_asyncio.fixture(scope="session")
async def storage():
    storage = MemoryStorage()
    yield storage
    await storage.close()


@pytest_asyncio.fixture(scope="session")
async def dispatcher(bot: Bot, storage: MemoryStorage):
    """Создаем тестовый Dispatcher с MemoryStorage"""
    dp = get_dispatcher(bot, storage)
    await dp.emit_startup()
    yield dp
    await dp.emit_shutdown()


@pytest_asyncio.fixture(scope="session")
async def state(bot: Bot, storage: MemoryStorage):
    state = FSMContext(
        storage,
        StorageKey(
            bot_id=bot.id,
            chat_id=123,
            user_id=123,
        )
    )
    yield state
    await state.clear()


@pytest.mark.asyncio(loop_scope="class")
class TestContract:

    @pytest.mark.regular
    async def test_start_handler(self, dispatcher: Dispatcher, bot: Bot, storage: MemoryStorage, state: FSMContext):
        message = Message.model_construct(
            message_id=1,
            date=datetime.datetime.now(),
            chat=Chat.model_construct(id=123, type="private"),
            from_user=User.model_construct(id=123, is_bot=False, first_name="Test User"),
            text="/start"
        )
        update = Update(update_id=1, message=message)
        await dispatcher.feed_update(bot, update)
        current_state = await state.get_state()
        assert current_state == entity.UserState.START

        # bot.send_message = AsyncMock()
        #
        # # Запускаем обработчик
        # await dispatcher.message.handlers[0].callback(message)
        #
        # # Проверяем, что бот отправил правильное сообщение
        # bot.send_message.assert_called_once_with("Привет! Введи свое имя:")