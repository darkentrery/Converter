import enum

from pydantic import BaseModel


class Button(enum.Enum):
    LPG_TO_PDF: str = "Конвертация JPG to PDF"
    READY: str = "Готово"
    PORTRAIT: str = "Книжный"
    LANDSCAPE: str = "Альбомный"
    MIX: str = "Формат в зависимости от размера изображений"


class Orientation(enum.Enum):
    PORTRAIT: str = "Книжный"
    LANDSCAPE: str = "Альбомный"
    MIX: str = "Формат в зависимости от размера изображений"
