from src.database.db import DbBuilder
from src.utils.exceptions.custom_exceptions import CustomException404
from src.database.collection_interface import CollectionInterface
from src.database.collection_factory import CollectionFactoryInterface
from typing import Dict, List, Any


class ControllerCollection(DbBuilder, CollectionInterface):
    def __init__(self) -> None:
        super().__init__()

    def create_collection(self) -> None:
        print("Creating ControllerCollection...")
        self.controller_collection = self.db['controller_collection']
        self.controller_collection.create_index("name", unique=True)
        # self.controller_collection.create_index("controller_unit", unique=True)
        # self.controller_collection.create_index("port", unique=True)
        # print("controllerCollection created with unique index on 'name','controller_unit','port'")
        print("controllerCollection created with unique index on 'name'")

    def get_collection(self) -> Any:
        return self.controller_collection

    def insert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        data = self.id_creator(data)
        self.controller_collection.insert_one(data)
        print("inserted controller_backend")
        return data

    def update(self, update_data: Dict[str, Any], pk: str) -> Dict[str, Any]:
        data = self.detail(pk)
        if "count_pin_in" in update_data.keys() and "count_pin_out" in update_data.keys() and update_data[
            "count_pin_out"] + update_data["count_pin_in"] > data["count_total_pin"]:
            raise ValueError("exceeded the total number of pins")
        self.controller_collection.update_one({"_id": pk}, {"$set": update_data})
        print("updated controller_backend")
        return self.detail(pk)

    def delete(self, pk: str) -> None:
        _ = self.detail(pk)
        self.controller_collection.delete_one({"_id": pk})
        print("deleted controller_backend")

    def filter(self, filter_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        pass

    def retrieve(self) -> List[Dict[str, Any]]:
        data = list(self.controller_collection.find())
        # if not data:
        #     raise CustomException404(message="controller_backend not found")
        print("list controller_backend")
        return data

    def detail(self, id: str) -> Dict[str, Any]:
        data = self.controller_collection.find_one({"_id": id})
        if not data:
            raise CustomException404(message="controller_backend not found")
        print("detail controller_backend")
        return data


class ControllerCollectionCreator(CollectionFactoryInterface):
    def create_collection(self) -> ControllerCollection:
        controller_collection_obj = ControllerCollection()
        controller_collection_obj.create_collection()
        return controller_collection_obj
