from pydantic import BaseModel, Field
from typing import List, Union


class TaskSchema(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    description: str = Field(min_length=2, max_length=50)
    controller_id: str
    pin_numbers: List[int]
    scenario_id: str


class TaskUpdateSchema(BaseModel):
    name: Union[str, None] = Field(min_length=2, max_length=50)
    description: Union[str, None] = Field(min_length=2, max_length=50)
    controller_id: Union[str, None]
    pin_numbers: Union[List[int], None]
    scenario_id: Union[str, None]
