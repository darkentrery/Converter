import fastapi

from app import entity
from app.api import deps

router = fastapi.APIRouter(prefix="/formats", tags=["Formats"])


@router.get('/')
async def get_formats(
    # service: deps.CableServiceDep, pagination: deps.PaginationDep
):
    # count, rows = await service.find_all(pagination.offset, pagination.limit)
    return None
