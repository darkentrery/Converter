import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

from app.entity import ActionType
from app.repository.sqlalchemy.mixins import IdMixin, TimestampMixin


class BaseModel(DeclarativeBase):
    pass


class User(IdMixin, TimestampMixin, BaseModel):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(nullable=False)
    first_name: Mapped[str] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=True)
    tg_id: Mapped[int] = mapped_column(nullable=True, unique=True)

    __table_args__ = (
        sa.UniqueConstraint("username", "tg_id", name="users_unique_key"),
    )


class UserAction(IdMixin, TimestampMixin, BaseModel):
    __tablename__ = "user_actions"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    action_type: Mapped[ActionType] = mapped_column(default=ActionType.START, server_default="START", nullable=False)
    comment: Mapped[str] = mapped_column(nullable=True)


class Format(IdMixin, TimestampMixin, BaseModel):
    __tablename__ = "formats"

    name: Mapped[str] = mapped_column(nullable=False, unique=True)


class FormatCross(IdMixin, TimestampMixin, BaseModel):
    __tablename__ = "formats_cross"

    format_from_id: Mapped[int] = mapped_column(ForeignKey("formats.id"), nullable=False)
    format_to_id: Mapped[int] = mapped_column(ForeignKey("formats.id"), nullable=False)

    __table_args__ = (
        sa.UniqueConstraint("format_from_id", "format_to_id", name="formats_cross_unique_key"),
    )
