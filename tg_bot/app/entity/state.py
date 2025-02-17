from aiogram.fsm.state import StatesGroup, State


class UserState(StatesGroup):
    START = State()
    CHOOSE_FROM = State()
    CHOOSE_TO = State()
    UPLOADING = State()
    ORIENTATION = State()
