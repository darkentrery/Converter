from app import entity
from app.repository.sqlalchemy import SAUnitOfWork


class UserService:
    def __init__(self, uow: SAUnitOfWork):
        self.uow = uow

    async def create(self, body: entity.AddUser) -> entity.User:
        async with self.uow:
            user = await self.uow.user.add(body.model_dump())
            await self.uow.commit()
            return user

    async def get_by_id(self, user_id: int) -> entity.User:
        async with self.uow:
            user = await self.uow.user.find({"id": user_id})
            return user
