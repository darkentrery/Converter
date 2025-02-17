from app import entity
from app.repository.sqlalchemy import SAUnitOfWork


class UserActionService:
    def __init__(self, uow: SAUnitOfWork):
        self.uow = uow

    async def create(self, body: entity.AddUserAction) -> entity.UserAction:
        async with self.uow:
            user_action = await self.uow.user_action.add(body.model_dump())
            await self.uow.commit()
            return user_action
