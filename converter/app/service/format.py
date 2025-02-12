from app import entity
from app.repository.sqlalchemy import SAUnitOfWork


class FormatService:
    def __init__(self, uow: SAUnitOfWork):
        self.uow = uow

    async def get_all(self) -> list[entity.Format]:
        async with self.uow:
            count, items = await self.uow.format.find_all({})
            return items

    async def get_cross_formats_by_format_name(self, format_name: str) -> list[entity.FormatCrossWithName]:
        async with self.uow:
            items = await self.uow.format_cross.find_cross_by_format_name(format_name)
            return items
