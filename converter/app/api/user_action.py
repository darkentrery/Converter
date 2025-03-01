import fastapi

from app import entity
from app.api import deps

router = fastapi.APIRouter(prefix="/user-actions", tags=["User Actions"])


@router.post("/", status_code=201)
async def create_user_action(service: deps.UserActionServiceDep, body: entity.AddUserAction) -> entity.UserAction:
    return await service.create(body)


@router.get("/statistic")
async def get_statistic(service: deps.UserActionServiceDep) -> entity.Statistic:
    return await service.get_statistic()
