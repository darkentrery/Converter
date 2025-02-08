from pydantic import BaseModel, Field

from converter.entity import Step, Orientation


class UserData(BaseModel):
    step: Step = Step.START
    images: list[bytes] = Field(default_factory=list)
    orientation: Orientation = Orientation.PORTRAIT
