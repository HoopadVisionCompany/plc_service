from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse
from src.controller_backend.model import ControllerSchema, ControllerUpdateSchema
from src.controller_backend.service import ControllerCollectionCreator

controller_factory = ControllerCollectionCreator()
controller_collection = controller_factory.create_collection()

router = APIRouter()


@router.get("/controller/list")
def list_controller():
    data = controller_collection.retrieve()
    return JSONResponse(status_code=status.HTTP_200_OK, content=data)


@router.get("/controller/detail/{id}")
def detail_controller(id: str):
    data = controller_collection.detail(id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=data)


@router.post("/controller/insert")
def insert_controller(controller_data: ControllerSchema):
    data = controller_data.model_dump()
    controller_collection.insert(data)
    return JSONResponse(status_code=status.HTTP_200_OK, content="inserted successfully")


@router.patch("/controller/update/{id}")
def update_controller(controller_data: ControllerUpdateSchema, id: str):
    update_data = controller_data.model_dump(exclude_none=True)
    controller_collection.update(update_data, id)
    return JSONResponse(status_code=status.HTTP_200_OK, content="updated successfully")


@router.delete("/controller/delete/{id}")
def delete_controller(id: str):
    controller_collection.delete(id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content="deleted successfully")
