import fastapi
from starlette.responses import StreamingResponse

from app import entity
from app.api import deps

router = fastapi.APIRouter(prefix="/converters", tags=["Converters"])


@router.post("/from_jpg_to_pdf")
async def convert_images_to_pdf(service: deps.ConverterServiceDep, body: entity.FromJpgToPdf):
    file = await service.from_jpg_to_pdf(body.orientation, body.images_bytes)
    return StreamingResponse(
        file,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=converted.pdf"}
    )
