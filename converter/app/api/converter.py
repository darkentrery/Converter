import fastapi
from starlette.responses import StreamingResponse

from app import entity
from app.api import deps

router = fastapi.APIRouter(prefix="/converters", tags=["Converters"])


@router.post("/from-jpg-to-pdf")
async def from_jpg_to_pdf(service: deps.ConverterServiceDep, body: entity.ConvertRequest):
    file = await service.from_jpg_to_pdf(body.orientation, body.files_bytes)
    return StreamingResponse(
        file,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=converted.pdf"}
    )


@router.post("/from-word-to-pdf")
async def from_word_to_pdf(service: deps.ConverterServiceDep, body: entity.ConvertRequest):
    file = service.from_word_to_pdf(body.files_bytes)
    return StreamingResponse(
        file,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=converted.pdf"}
    )


@router.post("/from-excel-to-pdf")
async def from_excel_to_pdf(service: deps.ConverterServiceDep, body: entity.ConvertRequest):
    file = service.from_excel_to_pdf(body.files_bytes)
    return StreamingResponse(
        file,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=converted.pdf"}
    )
