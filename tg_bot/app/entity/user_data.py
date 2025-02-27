from aiogram.types import Message
from pydantic import BaseModel, Field


class UserData(BaseModel):
    from_format: str = ""
    to_format: str = ""
    orientation: str = ""
    files: list[str] = Field(default_factory=list)
    last_message: Message | None = None
