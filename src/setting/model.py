from pydantic import BaseModel, Field
from typing import Union


class SettingSchema(BaseModel):
    package_id: int
    name: str


class SettingUpdateSchema(BaseModel):
    package_id: Union[int, None] = Field(default=None)
    name: Union[str, None] = Field(default=None)
