from src.database.db import DbBuilder
from src.utils.exceptions.custom_exceptions import CustomException404

from src.database.collection_interface import CollectionInterface
from src.controller_backend.service import ControllerCollectionCreator
from src.pin.service import PinCollectionCreator
from src.scenario.service import ScenarioCollectionCreator

from src.database.collection_factory import CollectionFactoryInterface
from typing import List, Dict, Any

controller_factory = ControllerCollectionCreator()
controller_collection = controller_factory.create_collection()

pin_factory = PinCollectionCreator()
pin_collection = pin_factory.create_collection()

scenario_factory = ScenarioCollectionCreator()
scenario_collection = scenario_factory.create_collection()


class TaskCollection(DbBuilder, CollectionInterface):
    def __init__(self) -> None:
        super().__init__()

    def create_collection(self) -> None:
        print("Creating TaskCollection...")
        self.task_collection = self.db['task_collection']
        self.task_collection.create_index([("controller_id", 1), ("pin_numbers", 1)], unique=True)

        print("TaskCollection created with unique index on 'controller_id' and 'pin_numbers'")

    def get_collection(self) -> Any:
        return self.task_collection

    def insert(self, data: Dict[str, Any]) -> None:
        _ = self.controller_exists(data["controller_id"])
        for id in data["pin_numbers"]:
            _ = self.pin_exists(id, data["controller_id"])
        _ = self.scenario_exists(data["scenario_id"])
        data = self.id_creator(data)
        self.task_collection.insert_one(data)
        print("inserted task")

    def update(self, update_data: Dict[str, Any], pk: str) -> None:
        _ = self.controller_exists(update_data["controller_id"])
        for id in update_data["pin_numbers"]:
            _ = self.pin_exists(id, update_data["controller_id"])
        _ = self.detail(pk)
        self.task_collection.update_one({"_id": pk}, {"$set": update_data})
        print("updated task")

    def delete(self, pk: str) -> None:
        _ = self.detail(pk)
        self.task_collection.delete_one({"_id": pk})
        print("deleted task")

    def filter(self, filter_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        pass

    def retrieve(self) -> List[Dict[str, Any]]:
        data = list(self.task_collection.find())
        if not data:
            raise CustomException404(message="task not found")
        print("list task")
        return data

    def detail(self, id: str) -> Dict[str, Any]:
        data = list(self.task_collection.find({"_id": id}))
        if not data:
            raise CustomException404(message="task not found")
        print("detail task")
        return data

    def controller_exists(self, controller_id: str) -> List[Dict[str, Any]]:
        # data = list(controller_collection.get_collection().find({"_id": controller_id}))
        data = list(controller_collection.detail(controller_id))
        return data

    def pin_exists(self, pin_number: int, controller_id: str) -> List[Dict[str, Any]]:
        data = list(pin_collection.get_collection().find({"controller_id": controller_id, "number": pin_number}))
        if not data:
            raise CustomException404(message=f"pin not found")
        return data

    def scenario_exists(self, scenario_id: str) -> List[Dict[str, Any]]:
        data = list(scenario_collection.detail(scenario_id))
        return data


class TaskCollectionCreator(CollectionFactoryInterface):
    def create_collection(self) -> TaskCollection:
        task_collection_obj = TaskCollection()
        task_collection_obj.create_collection()
        return task_collection_obj
