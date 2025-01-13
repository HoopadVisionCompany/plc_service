from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from .service import ScenarioCollectionCreator

scenario_factory = ScenarioCollectionCreator()
scenario_collection = scenario_factory.create_collection()
router = APIRouter()


@router.get("/scenario/list")
def list_scenario():
    data = scenario_collection.retrieve()
    return JSONResponse(status_code=status.HTTP_200_OK, content=data)
