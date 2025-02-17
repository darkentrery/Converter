from pydantic import BaseModel, ConfigDict

from app.entity import ActionType
from app.entity.mixins import IdMixin, DateTimeMixin


class UserAction(IdMixin, DateTimeMixin):
    user_id: int
    action_type: ActionType
    comment: str | None


class AddUserAction(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    user_id: int
    action_type: ActionType
    comment: str | None
