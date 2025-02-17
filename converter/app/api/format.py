import fastapi

from app import entity
from app.api import deps

router = fastapi.APIRouter(prefix="/formats", tags=["Formats"])


@router.get("/")
async def get_formats(service: deps.FormatServiceDep) -> list[entity.Format]:
    return await service.get_all()


@router.get("/with-pair/")
async def get_formats_with_pair(service: deps.FormatServiceDep) -> list[entity.Format]:
    return await service.get_formats_with_pair()


@router.get("/{format_name}/cross/")
async def get_cross_formats(service: deps.FormatServiceDep, format_name: str) -> list[entity.FormatCrossWithName]:
    return await service.get_cross_formats_by_format_name(format_name)
