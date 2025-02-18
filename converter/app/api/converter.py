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


@router.post("/from-powerpoint-to-pdf")
async def from_powerpoint_to_pdf(service: deps.ConverterServiceDep, body: entity.ConvertRequest):
    file = service.from_powerpoint_to_pdf(body.files_bytes)
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


@router.post("/from-csv-to-pdf")
async def from_csv_to_pdf(service: deps.ConverterServiceDep, body: entity.ConvertRequest):
    file = service.from_csv_to_pdf(body.files_bytes)
    return StreamingResponse(
        file,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=converted.pdf"}
    )


@router.post("/from-html-to-pdf")
async def from_html_to_pdf(service: deps.ConverterServiceDep, body: entity.ConvertRequest):
    file = service.from_html_to_pdf(body.files_bytes)
    return StreamingResponse(
        file,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=converted.pdf"}
    )


@router.post("/from-txt-to-pdf")
async def from_txt_to_pdf(service: deps.ConverterServiceDep, body: entity.ConvertRequest):
    file = service.from_txt_to_pdf(body.files_bytes)
    return StreamingResponse(
        file,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=converted.pdf"}
    )


@router.post("/from-jpg-to-word")
async def from_jpg_to_word(service: deps.ConverterServiceDep, body: entity.ConvertRequest):
    file = service.from_jpg_to_word(body.files_bytes)
    return StreamingResponse(
        file,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=converted.docx"}
    )


@router.post("/from-excel-to-csv")
async def from_excel_to_csv(service: deps.ConverterServiceDep, body: entity.ConvertRequest):
    file = service.from_excel_to_csv(body.files_bytes)
    return StreamingResponse(
        file,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=converted.csv"}
    )


@router.post("/from-csv-to-excel")
async def from_csv_to_excel(service: deps.ConverterServiceDep, body: entity.ConvertRequest):
    file = service.from_csv_to_excel(body.files_bytes)
    return StreamingResponse(
        file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=converted.csv"}
    )
