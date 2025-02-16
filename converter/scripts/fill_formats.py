import asyncio
import json
import os.path

from app.config import config
from app.repository.sqlalchemy import SAUnitOfWork
from app.repository.sqlalchemy.sauow import pg_async_session_maker


async def fill_formats(uow: SAUnitOfWork) -> None:
    """Need open uow!"""
    with open(os.path.join(config.base_dir, "configs", "formats.json"), "r") as f:
        data = json.load(f)

    await uow.format.bulk_add(data)


async def fill_cross_formats(uow: SAUnitOfWork) -> None:
    """Need open uow!"""
    with open(os.path.join(config.base_dir, "configs", "cross_formats.json"), "r") as f:
        data = json.load(f)
    cross_formats = []

    for row in data:
        format_from = await uow.format.find({"name": row["format_from_name"]})
        format_to = await uow.format.find({"name": row["format_to_name"]})
        cross_formats.append({
            "format_from_id": format_from.id,
            "format_to_id": format_to.id
        })
    await uow.format_cross.bulk_add(cross_formats)


async def main() -> None:
    uow = SAUnitOfWork(pg_async_session_maker)
    async with uow:
        await uow.format_cross.delete({})
        await uow.format.delete({})
        await fill_formats(uow)
        await fill_cross_formats(uow)
        await uow.commit()


if __name__ == "__main__":
    asyncio.run(main())
