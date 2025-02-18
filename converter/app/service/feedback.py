from app import entity
from app.repository.sqlalchemy import SAUnitOfWork


class FeedbackService:
    def __init__(self, uow: SAUnitOfWork):
        self.uow = uow

    async def create(self, body: entity.AddFeedback) -> entity.Feedback:
        async with self.uow:
            item = await self.uow.feedback.add(body.model_dump())
            await self.uow.commit()
            return item
