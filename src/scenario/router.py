from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from .service import ScenarioCollectionCreator
from src.utils.auth.authorization import retrieve_user

scenario_factory = ScenarioCollectionCreator()
scenario_collection = scenario_factory.create_collection()
router = APIRouter(dependencies=[Depends(retrieve_user), ])


@router.get("/scenario/list")
def list_scenario():
    data = scenario_collection.retrieve()
    return JSONResponse(status_code=status.HTTP_200_OK, content=data)
