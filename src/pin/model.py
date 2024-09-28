from pydantic import BaseModel, Field
from enum import Enum


class PinType(str, Enum):
    pin_in = "in"
    pin_out = "out"


class PinSchema(BaseModel):
    type: PinType = Field(default=PinType.pin_in)
    plc_id: str
    id: int = Field(ge=0, le=100)
