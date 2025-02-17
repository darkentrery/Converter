from pydantic import BaseModel

from app.entity import ActionType
from app.entity.mixins import IdMixin, DateTimeMixin


class UserAction(IdMixin, DateTimeMixin):
    user_id: int
    action_type: ActionType
    comment: str | None


class AddUserAction(BaseModel):
    user_id: int
    action_type: ActionType
    comment: str | None
