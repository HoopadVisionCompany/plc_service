from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from src.task.model import TaskSchema,TaskUpdateSchema

from src.task.service import TaskCollectionCreator

task_factory = TaskCollectionCreator()
task_collection = task_factory.create_collection()

router = APIRouter()


@router.get("/task/list")
def list_task():
    data = task_collection.retrieve()
    return JSONResponse(status_code=status.HTTP_200_OK, content=data)


@router.get("/task/detail/{id}")
def detail_task(id: str):
    data = task_collection.detail(id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=data)


@router.post("/task/insert")
def insert_task(task_data: TaskSchema):
    data = task_data.model_dump()
    task_collection.insert(data)
    return JSONResponse(status_code=status.HTTP_200_OK, content="inserted successfully")


@router.patch("/task/update/{id}")
def update_task(task_data: TaskUpdateSchema, id: str):
    update_data = task_data.model_dump(exclude_none=True)
    task_collection.update(update_data, id)
    return JSONResponse(status_code=status.HTTP_200_OK, content="updated successfully")


@router.delete("/task/delete/{id}")
def delete_task(id: str):
    task_collection.delete(id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content="deleted successfully")
