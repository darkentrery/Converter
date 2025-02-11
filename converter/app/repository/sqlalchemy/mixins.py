from datetime import datetime

from sqlalchemy.orm import declarative_mixin, Mapped, mapped_column


@declarative_mixin
class IdMixin:
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, sort_order=-99)


@declarative_mixin
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, sort_order=99)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow, sort_order=99, nullable=True
    )
