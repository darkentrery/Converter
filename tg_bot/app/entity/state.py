from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.base import BaseStorage, StorageKey
from pydantic import TypeAdapter

from app.entity import UserData


class UserState(StatesGroup):
    START = State()
    CHOOSE_FROM = State()
    CHOOSE_TO = State()
    UPLOADING = State()
    ORIENTATION = State()
