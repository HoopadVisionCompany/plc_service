from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from src.pin.model import PinSchema, PinUpdateSchema
from typing import Union
from src.pin.service import PinCollectionCreator
from src.utils.auth.authorization import retrieve_user

pin_factory = PinCollectionCreator()
pin_collection = pin_factory.create_collection()
router = APIRouter()


@router.get("/pin/list")
def list_pin(controller_id: Union[str, None] = None):
    if controller_id is None:
        data = pin_collection.retrieve()
    else:
        filter_data = {"controller_id": controller_id}
        data = pin_collection.filter(filter_data)

    return JSONResponse(status_code=status.HTTP_200_OK, content=data)


@router.get("/pin/detail/{id}")
def detail_pin(id: str):
    data = pin_collection.detail(id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=data)


@router.post("/pin/insert")
def insert_pin(pin_data: PinSchema):
    data = pin_data.model_dump()
    result = pin_collection.insert(data)
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)


@router.patch("/pin/update/{id}")
def update_pin(pin_data: PinUpdateSchema, id: str):
    update_data = pin_data.model_dump(exclude_none=True)
    result = pin_collection.update(update_data, id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)


@router.delete("/pin/delete/{id}")
def delete_pin(id: str):
    pin_collection.delete(id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content="deleted successfully")
