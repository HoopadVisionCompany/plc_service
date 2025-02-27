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
    delay: int = Field(ge=0, default=0)
    timer: int = Field(ge=0, le=4095, default=None)


class PinUpdateSchema(BaseModel):
    type: Union[PinType, None] = Field(default=PinType.pin_in)
    controller_id: Union[str, None] = None
    number: Union[int, None] = Field(ge=0, le=100)
    delay: Union[int, None] = Field(ge=0, default=0)
    timer: Union[int, None] = Field(ge=0, le=4095, default=None)
