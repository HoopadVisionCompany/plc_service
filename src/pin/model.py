from pydantic import BaseModel, Field
from enum import Enum
from typing import Union


class PinType(str, Enum):
    pin_in = "in"
    pin_out = "out"


class PinSchema(BaseModel):
    type: PinType = Field(default=PinType.pin_in)
    controller_id: str
    number: int = Field(ge=0, le=100)


class PinUpdateSchema(BaseModel):
    type: Union[PinType, None] = Field(default=PinType.pin_in)
    controller_id: Union[str, None] = None
    number: Union[int, None] = Field(ge=0, le=100)
