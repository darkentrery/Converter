from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import DateTime, ARRAY, String
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

from app.repository.sqlalchemy.mixins import IdMixin, TimestampMixin


class BaseModel(DeclarativeBase):
    pass


class OutboxModel(IdMixin, TimestampMixin, BaseModel):
    __tablename__ = 'outbox'

    ack: Mapped[bool] = mapped_column(nullable=False, default=False)
    key: Mapped[str] = mapped_column(nullable=True)
    payload: Mapped[str] = mapped_column(nullable=False)
