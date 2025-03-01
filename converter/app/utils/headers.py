

def media_type(extension: str) -> str:
    media_types = {
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "pdf": "application/pdf",
        "csv": "text/csv",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "html": "text/html",
        "fb2": "application/x-fictionbook+xml",
    }
    return media_types[extension]


def file_headers(extension: str) -> dict[str, str]:
    return {"Content-Disposition": f"attachment; filename=converted.{extension}"}
