from pydantic import BaseModel, ConfigDict

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


class StatisticAction(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    action: ActionType
    count: int


class StatisticFormat(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    format: str
    count: int


class Statistic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    users: int
    actions: list[StatisticAction]
    from_formats: list[StatisticFormat]
    to_formats: list[StatisticFormat]
