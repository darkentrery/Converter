import enum


class Orientation(enum.Enum):
    PORTRAIT: str = "Книжный"
    LANDSCAPE: str = "Альбомный"
    MIX: str = "Mix"#"Формат в зависимости от размера изображений"
