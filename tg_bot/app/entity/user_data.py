import base64
from typing import Literal, Any

from pydantic import BaseModel, Field, field_validator
from pydantic.main import IncEx


class UserData(BaseModel):
    from_format: str = ""
    to_format: str = ""
    images: list[bytes | str] = Field(default_factory=list)
    orientation: str = ""

    @field_validator("images", mode="before")
    @classmethod
    def parse_images(cls, values: list[str]) -> list[bytes]:
        data = [base64.b64decode(v) for v in values]
        return data

    def model_dump(
        self,
        *,
        mode: Literal['json', 'python'] | str = 'python',
        include: IncEx | None = None,
        exclude: IncEx | None = None,
        context: Any | None = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool | Literal['none', 'warn', 'error'] = True,
        serialize_as_any: bool = False,
    ) -> dict[str, Any]:
        data = super().model_dump(include=include, exclude=exclude)
        data["images"] = [base64.b64encode(image).decode("utf-8") for image in data["images"]]
        return data
