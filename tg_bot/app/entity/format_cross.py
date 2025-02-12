from app.entity.mixins import IdMixin, DateTimeMixin


class FormatCross(IdMixin, DateTimeMixin):
    format_from_id: int
    format_to_id: int


class FormatCrossWithName(FormatCross):
    format_from_name: str
    format_to_name: str
