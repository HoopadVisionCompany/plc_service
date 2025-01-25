from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from src.plc.model import PLCSchema, PLCUpdateSchema
from src.plc.service import PLCCollectionCreator
from src.utils.auth.authorization import retrieve_user
plc_factory = PLCCollectionCreator()
plc_collection = plc_factory.create_collection()

router = APIRouter(dependencies=[Depends(retrieve_user)])


@router.get("/plc/list")
def list_plc():
    data = plc_collection.retrieve()
    return JSONResponse(status_code=status.HTTP_200_OK, content=data)


@router.get("/plc/detail/{id}")
def detail_plc(id: str):
    data = plc_collection.detail(id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=data)


@router.post("/plc/insert")
def insert_plc(plc_data: PLCSchema):
    data = plc_data.model_dump()
    plc_collection.insert(data)
    return JSONResponse(status_code=status.HTTP_200_OK, content="inserted successfully")


@router.patch("/plc/update/{id}")
def update_plc(plc_data: PLCUpdateSchema, id: str):
    update_data = plc_data.model_dump()
    plc_collection.update(update_data, id)
    return JSONResponse(status_code=status.HTTP_200_OK, content="updated successfully")


@router.delete("/plc/delete/{id}")
def delete_plc(id: str):
    plc_collection.delete(id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content="deleted successfully")
