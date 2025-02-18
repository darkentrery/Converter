import fastapi

from app import entity
from app.api import deps

router = fastapi.APIRouter(prefix="/feedbacks", tags=["Feedbacks"])


@router.post("/", status_code=201)
async def create_feedback(service: deps.FeedbackServiceDep, body: entity.AddFeedback) -> entity.Feedback:
    return await service.create(body)
