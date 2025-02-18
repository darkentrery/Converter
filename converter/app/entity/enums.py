import enum


class Orientation(enum.Enum):
    PORTRAIT: str = "Книжный"
    LANDSCAPE: str = "Альбомный"
    MIX: str = "Mix"#"Формат в зависимости от размера изображений"


class ActionType(enum.Enum):
    START = "start"
    CHOOSE_FROM = "choose_from"
    CHOOSE_TO = "choose_to"
    UPLOADING = "uploading"
    GOT_RESULT = "got_result"
    CONVERT = "convert"
    FEEDBACK = "feedback"
