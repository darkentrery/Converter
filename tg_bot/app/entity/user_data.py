import base64
from typing import Literal, Any

from pydantic import BaseModel, Field, field_validator
from pydantic.main import IncEx


class UserData(BaseModel):
    from_format: str = ""
    to_format: str = ""
    # images: list[bytes | str] = Field(default_factory=list)
    orientation: str = ""
    # word_file: bytes | str = b''
    files: list[str] = Field(default_factory=list)

    # @field_validator("images", mode="before")
    # @classmethod
    # def parse_images(cls, values: list[str]) -> list[bytes]:
    #     data = [base64.b64decode(v) for v in values]
    #     return data
    #
    # @field_validator("word_file", mode="before")
    # @classmethod
    # def parse_word_file(cls, value: str) -> bytes:
    #     return base64.b64decode(value)

    # def model_dump(
    #     self,
    #     *,
    #     mode: Literal['json', 'python'] | str = 'python',
    #     include: IncEx | None = None,
    #     exclude: IncEx | None = None,
    #     context: Any | None = None,
    #     by_alias: bool = False,
    #     exclude_unset: bool = False,
    #     exclude_defaults: bool = False,
    #     exclude_none: bool = False,
    #     round_trip: bool = False,
    #     warnings: bool | Literal['none', 'warn', 'error'] = True,
    #     serialize_as_any: bool = False,
    # ) -> dict[str, Any]:
    #     data = super().model_dump(include=include, exclude=exclude)
    #     if include is None or "images" in include:
    #         data["images"] = [base64.b64encode(image).decode("utf-8") for image in data["images"]]
    #     if include is None or "word_file" in include:
    #         data["word_file"] = base64.b64encode(data["word_file"]).decode("utf-8")
    #     return data
