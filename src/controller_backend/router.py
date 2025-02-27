from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.responses import JSONResponse, Response
from src.controller_backend.model import ControllerSchema, ControllerUpdateSchema
from src.controller_backend.service import ControllerCollectionCreator
from src.controller_backend.controller_utils import update_controller_info_insert, update_controller_info_update, \
    update_controller_info_delete
from src.utils.auth.authorization import retrieve_user

controller_factory = ControllerCollectionCreator()
controller_collection = controller_factory.create_collection()

router = APIRouter(
    dependencies=[Depends(retrieve_user),]
)


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
    result = controller_collection.insert(data)
    # update controller info
    update_controller_info_insert(data)
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)


@router.patch("/controller/update/{id}")
def update_controller(controller_data: ControllerUpdateSchema, id: str):
    update_data = controller_data.model_dump(exclude_none=True)
    data_before_update = controller_collection.detail(id)
    result = controller_collection.update(update_data, id)
    data_after_update = controller_collection.detail(id)
    update_controller_info_update(data_before_update, data_after_update)
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)


@router.delete("/controller/delete/{id}")
def delete_controller(id: str):
    data = controller_collection.detail(id)
    update_controller_info_delete(data)
    controller_collection.delete(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT, content="deleted successfully")
