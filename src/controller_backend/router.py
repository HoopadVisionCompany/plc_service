from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.responses import JSONResponse
from src.controller_backend.model import ControllerSchema, ControllerUpdateSchema
from src.controller_backend.service import ControllerCollectionCreator
from src.utils.auth.authorization import retrieve_user

controller_factory = ControllerCollectionCreator()
controller_collection = controller_factory.create_collection()
from src.controller.controller import Controller
from src.utils.controller_dict_creator import update_controllers_info_dict

router = APIRouter(
    # dependencies=[Depends(retrieve_user),]
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
    controller_collection.insert(data)
    # update controller info
    print("befroe : ",Controller({}).controller_info)
    controller_info=update_controllers_info_dict(data)
    Controller({}).update_controller_info(controller_info)
    print("after : ", Controller({}).controller_info)
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
