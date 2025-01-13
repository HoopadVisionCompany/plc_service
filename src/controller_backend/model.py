from pydantic import BaseModel, Field, model_validator
from typing import Union, List


class ControllerSchema(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    type: str = Field(min_length=1, max_length=100, default="1")
    protocol: str = Field(min_length=1, max_length=100, default="TCP")
    ip: str = Field(min_length=7, max_length=15, default="0.0.0.0")
    port: int = Field(ge=1, le=50000, default=4000)
    driver:Union[str, None] = Field(min_length=1, max_length=100, default=None)
    controller_unit: int = Field(ge=1, default=None)
    count_pin_out: int = Field(ge=1, le=100, default=100)
    count_pin_in: int = Field(ge=1, le=100, default=100)
    count_total_pin: int = Field(ge=1, le=200, default=200)

    @model_validator(mode="before")
    @classmethod
    def validate_pins(cls, data):
        if data["count_pin_out"] + data["count_pin_in"] > data["count_total_pin"]:
            raise ValueError("Pin count cannot be greater than total pin count")
        return data


class ControllerUpdateSchema(BaseModel):
    name: Union[str, None] = Field(min_length=1, max_length=100)
    type: Union[str, None] = Field(min_length=1, max_length=100, default="1")
    protocol: Union[str, None] = Field(min_length=1, max_length=100, default="TCP")
    ip: Union[str, None] = Field(min_length=7, max_length=15, default="0.0.0.0")
    port: Union[int, None] = Field(ge=1, le=50000, default=4000)
    driver: Union[str, None] = Field(min_length=1, max_length=100, default=None)
    controller_unit_id: Union[int, None] = Field(ge=1, default=None)
    count_pin_out: Union[int, None] = Field(ge=1, le=100, default=100)
    count_pin_in: Union[int, None] = Field(ge=1, le=100, default=100)
