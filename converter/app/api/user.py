import fastapi

from app import entity
from app.api import deps

router = fastapi.APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=201)
async def create_user(service: deps.UserServiceDep, body: entity.AddUser) -> entity.User:
    return await service.create(body)


@router.get("/{user_id}")
async def get_user_by_id(service: deps.UserServiceDep, user_id: int) -> entity.User:
    return await service.get_by_id(user_id)


@router.get("/by-tg/{tg_id}")
async def get_user_by_tg_id(service: deps.UserServiceDep, tg_id: int) -> entity.User:
    return await service.get_by_tg_id(tg_id)
