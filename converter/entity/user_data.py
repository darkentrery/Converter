from pydantic import BaseModel, Field

from converter.entity import Orientation


class UserData(BaseModel):
    from_format: str = ""
    to_format: str = ""
    images: list[bytes] = Field(default_factory=list)
    orientation: Orientation = Orientation.PORTRAIT
