from fastapi import APIRouter, status,Depends
from fastapi.responses import JSONResponse
from src.setting.model import SettingSchema, SettingUpdateSchema
from src.setting.service import SettingCollectionCreator
from src.utils.auth.authorization import retrieve_user
from src.utils.part_package_validators import package_checker
setting_factory = SettingCollectionCreator()
setting_collection = setting_factory.create_collection()

router = APIRouter()


@router.get("/setting/list")
def list_setting(_=Depends(retrieve_user)):
    data = setting_collection.retrieve()
    return JSONResponse(status_code=status.HTTP_200_OK, content=data)


@router.get("/setting/detail/{id}")
def detail_setting(id: str,_=Depends(retrieve_user)):
    data = setting_collection.detail(id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=data)


@router.post("/setting/insert")
def insert_setting(setting_data: SettingSchema,user=Depends(retrieve_user)):
    data = setting_data.model_dump()
    _ = package_checker(user['key_auth'], data, user)
    setting_collection.insert(data)
    return JSONResponse(status_code=status.HTTP_200_OK, content="inserted successfully")


@router.patch("/setting/update/{id}")
def update_setting(setting_data: SettingUpdateSchema, id: str,user=Depends(retrieve_user)):
    update_data = setting_data.model_dump(exclude_none=True)
    if "package_id" in update_data.keys():
        _ = package_checker(user['key_auth'], update_data, user)
    setting_collection.update(update_data, id)
    return JSONResponse(status_code=status.HTTP_200_OK, content="updated successfully")


@router.delete("/setting/delete/{id}")
def delete_setting(id: str,_=Depends(retrieve_user)):
    setting_collection.delete(id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content="deleted successfully")
