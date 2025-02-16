from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StateType
from pydantic import TypeAdapter

from app import entity


class StateService:
    def __init__(self):
        self.state: FSMContext | None = None

    def set_context(self, state: FSMContext):
        self.state = state

    async def set_state(self, state: StateType = None) -> None:
        await self.state.set_state(state)

    async def get_user_state(self) -> entity.UserData:
        data = await self.state.get_data()
        return TypeAdapter(entity.UserData).validate_python(data)

    @property
    async def files(self) -> list[str]:
        _state = await self.get_user_state()
        return _state.files

    async def add_file(self, file: str) -> None:
        _state = await self.get_user_state()
        _state.files.append(file)
        await self.state.update_data(_state.model_dump())

    @property
    async def orientation(self) -> str:
        _state = await self.get_user_state()
        return _state.orientation

    async def set_orientation(self, value: str) -> None:
        _state = await self.get_user_state()
        _state.orientation = value
        await self.state.update_data(_state.model_dump())

    @property
    async def from_format(self) -> str:
        _state = await self.get_user_state()
        return _state.from_format

    async def set_from_format(self, value: str) -> None:
        _state = await self.get_user_state()
        _state.from_format = value
        await self.state.update_data(_state.model_dump())

    @property
    async def to_format(self) -> str:
        _state = await self.get_user_state()
        return _state.to_format

    async def set_to_format(self, value: str) -> None:
        _state = await self.get_user_state()
        _state.to_format = value
        await self.state.update_data(_state.model_dump())

    @property
    async def body(self) -> dict:
        _state = await self.get_user_state()
        return _state.model_dump()

    async def set_default(self) -> None:
        await self.state.clear()
        await self.state.set_data(entity.UserData().model_dump())
