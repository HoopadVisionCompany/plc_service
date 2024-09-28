from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from src.pin.model import PinSchema

from src.pin.service import PinCollectionCreator

pin_factory = PinCollectionCreator()
pin_collection = pin_factory.create_collection()
router = APIRouter()


@router.get("/pin/list")
def list_pin():
    data = pin_collection.retrieve()
    return JSONResponse(status_code=status.HTTP_200_OK, content=data)


@router.get("/pin/detail/{id}")
def detail_pin(id: str):
    data = pin_collection.detail(id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=data)


@router.post("/pin/insert")
def insert_pin(pin_data: PinSchema):
    data = pin_data.model_dump()
    pin_collection.insert(data)
    return JSONResponse(status_code=status.HTTP_200_OK, content="inserted successfully")


@router.patch("/pin/update/{id}")
def update_pin(pin_data: PinSchema, id: str):
    update_data = pin_data.model_dump()
    pin_collection.update(update_data, id)
    return JSONResponse(status_code=status.HTTP_200_OK, content="updated successfully")


@router.delete("/pin/delete/{id}")
def delete_pin(id: str):
    pin_collection.delete(id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content="deleted successfully")
