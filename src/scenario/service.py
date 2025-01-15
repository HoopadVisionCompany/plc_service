import uuid

from src.database.db import DbBuilder
from src.utils.exceptions.custom_exceptions import CustomException404
# from src.database.collection_interface import CollectionInterface
from src.database.collection_factory import CollectionFactoryInterface
from typing import Dict, List, Any


class ScenarioCollection(DbBuilder):
    def __init__(self) -> None:
        super().__init__()

    def create_collection(self) -> None:
        print("Creating ScenarioCollection...")
        self.scenario_collection = self.db['scenario_collection']
        self.scenario_collection.create_index("name", unique=True)
        print("scenarioCollection created with unique index on 'name' ")

    def get_collection(self) -> Any:
        return self.scenario_collection

    def retrieve(self) -> List[Dict[str, Any]]:
        data = list(self.scenario_collection.find())
        # if not data:
        #     raise CustomException404(message="scenario_backend not found")
        print("list scenario")
        return data

    def insert(self, data: Dict[str, Any]) -> None:
        data["_id"] = str(uuid.uuid4())
        self.scenario_collection.insert_one(data)
        print("inserted scenario")

    def detail(self, id: str) -> Dict[str, Any]:
        data = self.scenario_collection.find_one({"_id": id})
        if not data:
            raise CustomException404(message="scenario not found")
        print("detail scenario")
        return data
    # 
    # def update(self, update_data: Dict[str, Any], pk: str) -> None:
    #     data = self.detail(pk)
    #     if update_data["count_pin_out"] + update_data["count_pin_in"] > data["count_total_pin"]:
    #         raise ValueError("exceeded the total number of pins")
    #     self.scenario_collection.update_one({"_id": pk}, {"$set": update_data})
    #     print("updated scenario_backend")
    # 
    # def delete(self, pk: str) -> None:
    #     _ = self.detail(pk)
    #     self.scenario_collection.delete_one({"_id": pk})
    #     print("deleted scenario_backend")
    # 
    # def filter(self, filter_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    #     pass
    # 




class ScenarioCollectionCreator(CollectionFactoryInterface):
    def create_collection(self) -> ScenarioCollection:
        scenario_collection_obj = ScenarioCollection()
        scenario_collection_obj.create_collection()
        return scenario_collection_obj
