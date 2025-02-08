from pydantic import BaseModel


class Config(BaseModel):
    A4_PORTRAIT: tuple[int, int] = (595, 842)  # Размер A4 в пикселях (72 DPI)
    A4_LANDSCAPE: tuple[int, int] = (842, 595)
    TOKEN: str = ""


config = Config()
