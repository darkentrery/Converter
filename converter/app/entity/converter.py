import base64

from pydantic import BaseModel


class FromJpgToPdf(BaseModel):
    images: list[str]
    orientation: str

    @property
    def images_bytes(self) -> list[bytes]:
        return [base64.b64decode(v) for v in self.images]
