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

    async def get_statistic(self) -> entity.Statistic:
        async with self.uow:
            actions = await self.uow.user_action.get_statistic_actions()
            from_formats = await self.uow.user_action.get_from_formats()
            to_formats = await self.uow.user_action.get_to_formats()
            users_count, users = await self.uow.user.find_all({}, limit=5000)
            return entity.Statistic(
                users=users_count,
                actions=actions,
                from_formats=from_formats,
                to_formats=to_formats
            )
