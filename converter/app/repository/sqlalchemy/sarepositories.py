from pydantic import TypeAdapter
from sqlalchemy import select
from sqlalchemy.orm import aliased

from app import entity
from app.repository.sqlalchemy import SARepository, models


class UserRepository(SARepository):
    name = "User"
    model = models.User
    schema = entity.User


class FormatRepository(SARepository):
    name = "Format"
    model = models.Format
    schema = entity.Format


class FormatCrossRepository(SARepository):
    name = "FormatCross"
    model = models.FormatCross
    schema = entity.FormatCross

    async def find_cross_by_format_id(self, format_id: int) -> list[entity.FormatCrossWithName]:
        from_format = aliased(models.Format)
        to_format = aliased(models.Format)
        stmt = select(
            self.model.id,
            self.model.format_to_id,
            self.model.format_from_id,
            self.model.created_at,
            self.model.updated_at,
            from_format.name.label("format_from_name"),
            to_format.name.label("format_to_name"),
        ).join(
            from_format, from_format.id == self.model.format_from_id
        ).join(
            to_format, to_format.id == self.model.format_to_id
        ).filter(
            self.model.format_from_id == format_id
        )
        rows = (await self.session.execute(stmt)).all()
        return TypeAdapter(list[entity.FormatCrossWithName]).validate_python(rows)
