import base64

from pydantic import BaseModel


class ConvertRequest(BaseModel):
    files: list[str]
    orientation: str

    @property
    def files_bytes(self) -> list[bytes]:
        return [base64.b64decode(v) for v in self.files]
