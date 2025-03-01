import fastapi
from starlette.responses import StreamingResponse

from app import entity
from app.api import deps
from app.utils.headers import media_type, file_headers

router = fastapi.APIRouter(prefix="/converters", tags=["Converters"])


@router.post("/from-jpg-to-pdf")
async def from_jpg_to_pdf(service: deps.ConverterServiceDep, body: entity.ConvertRequest):
    file = await service.from_jpg_to_pdf(body.orientation, body.files_bytes)
    return StreamingResponse(file, media_type=media_type("pdf"), headers=file_headers("pdf"))


@router.post("/from-word-to-pdf")
async def from_word_to_pdf(service: deps.ConverterServiceDep, body: entity.ConvertRequest):
    file = service.from_word_to_pdf(body.files_bytes)
    return StreamingResponse(file, media_type=media_type("pdf"), headers=file_headers("pdf"))


@router.post("/from-powerpoint-to-pdf")
async def from_powerpoint_to_pdf(service: deps.ConverterServiceDep, body: entity.ConvertRequest):
    file = service.from_powerpoint_to_pdf(body.files_bytes)
    return StreamingResponse(file, media_type=media_type("pdf"), headers=file_headers("pdf"))


@router.post("/from-excel-to-pdf")
async def from_excel_to_pdf(service: deps.ConverterServiceDep, body: entity.ConvertRequest):
    file = service.from_excel_to_pdf(body.files_bytes)
    return StreamingResponse(file, media_type=media_type("pdf"), headers=file_headers("pdf"))


@router.post("/from-csv-to-pdf")
async def from_csv_to_pdf(service: deps.ConverterServiceDep, body: entity.ConvertRequest):
    file = service.from_csv_to_pdf(body.files_bytes)
    return StreamingResponse(file, media_type=media_type("pdf"), headers=file_headers("pdf"))


@router.post("/from-html-to-pdf")
async def from_html_to_pdf(service: deps.ConverterServiceDep, body: entity.ConvertRequest):
    file = service.from_html_to_pdf(body.files_bytes)
    return StreamingResponse(file, media_type=media_type("pdf"), headers=file_headers("pdf"))


@router.post("/from-txt-to-pdf")
async def from_txt_to_pdf(service: deps.ConverterServiceDep, body: entity.ConvertRequest):
    file = service.from_txt_to_pdf(body.files_bytes)
    return StreamingResponse(file, media_type=media_type("pdf"), headers=file_headers("pdf"))


@router.post("/from-jpg-to-word")
async def from_jpg_to_word(service: deps.ConverterServiceDep, body: entity.ConvertRequest):
    file = service.from_jpg_to_word(body.files_bytes)
    return StreamingResponse(file, media_type=media_type("docx"), headers=file_headers("docx"))


@router.post("/from-excel-to-csv")
async def from_excel_to_csv(service: deps.ConverterServiceDep, body: entity.ConvertRequest):
    file = service.from_excel_to_csv(body.files_bytes)
    return StreamingResponse(file, media_type=media_type("csv"), headers=file_headers("csv"))


@router.post("/from-csv-to-excel")
async def from_csv_to_excel(service: deps.ConverterServiceDep, body: entity.ConvertRequest):
    file = service.from_csv_to_excel(body.files_bytes)
    return StreamingResponse(file, media_type=media_type("xlsx"), headers=file_headers("xlsx"))


@router.post("/from-pdf-to-word")
async def from_pdf_to_word(service: deps.ConverterServiceDep, body: entity.ConvertRequest):
    file = service.from_pdf_to_word(body.files_bytes)
    return StreamingResponse(file, media_type=media_type("docx"), headers=file_headers("docx"))


@router.post("/from-pdf-to-html")
async def from_pdf_to_html(service: deps.ConverterServiceDep, body: entity.ConvertRequest):
    file = service.from_pdf_to_html(body.files_bytes)
    return StreamingResponse(file, media_type=media_type("html"), headers=file_headers("html"))


@router.post("/from-word-to-fb2")
async def from_word_to_pdf(service: deps.ConverterServiceDep, body: entity.ConvertRequest):
    file = service.from_word_to_fb2(body.files_bytes)
    return StreamingResponse(file, media_type=media_type("fb2"), headers=file_headers("fb2"))
