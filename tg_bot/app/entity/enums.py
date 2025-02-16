import enum


class Button(enum.Enum):
    READY: str = "Готово"


class Orientation(enum.Enum):
    PORTRAIT: str = "Книжный"
    LANDSCAPE: str = "Альбомный"
    MIX: str = "Mix"#"Формат в зависимости от размера изображений"
