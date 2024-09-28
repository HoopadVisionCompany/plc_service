from pydantic import BaseModel, Field
from typing import List


class TaskSchema(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    description: str = Field(min_length=2, max_length=50)
    plc_id: str
    pin_ids: List[int]
