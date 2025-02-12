from app.entity.mixins import IdMixin, DateTimeMixin


class Format(IdMixin, DateTimeMixin):
    name: str
