from pydantic import BaseModel

from app.entity.mixins import IdMixin, DateTimeMixin


class User(IdMixin, DateTimeMixin):
    username: str
    first_name: str | None
    last_name: str | None
    tg_id: int | None


class AddUser(BaseModel):
    username: str
    first_name: str
    last_name: str
    tg_id: int
