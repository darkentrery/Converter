from pydantic import BaseModel

from app.entity import ActionType
from app.entity.mixins import IdMixin, DateTimeMixin


class Feedback(IdMixin, DateTimeMixin):
    user_id: int
    text: str


class AddFeedback(BaseModel):
    user_id: int
    text: str
