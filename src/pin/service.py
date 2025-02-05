from src.database.db import DbBuilder
from src.utils.exceptions.custom_exceptions import CustomException404
from src.database.collection_interface import CollectionInterface

from src.database.collection_factory import CollectionFactoryInterface
from src.controller_backend.service import ControllerCollectionCreator
from typing import Dict, Any, List

controller_factory = ControllerCollectionCreator()
controller_collection = controller_factory.create_collection()


class PinCollection(DbBuilder, CollectionInterface):
    def __init__(self) -> None:
        super().__init__()

    def create_collection(self) -> None:
        print("Creating PinCollection...")
        self.pin_collection = self.db['pin_collection']
        self.pin_collection.create_index([("controller_id", 1), ("number", 1), ('type', 1)], unique=True)

        print("PinCollection created with unique index on 'controller_id' and 'number'")

    def get_collection(self) -> Any:
        return self.pin_collection

    def insert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        _ = self.controller_exists(data["controller_id"])
        data = self.id_creator(data)
        self.pin_collection.insert_one(data)
        print("inserted pin")
        return data

    def update(self, update_data: Dict[str, Any], pk: str) -> Dict[str, Any]:
        _ = self.detail(pk)
        _ = self.controller_exists(update_data["controller_id"])
        self.pin_collection.update_one({"_id": pk}, {"$set": update_data})
        print("updated pin")
        return self.detail(pk)

    def delete(self, pk: str) -> None:
        _ = self.detail(pk)
        self.pin_collection.delete_one({"_id": pk})
        print("deleted pin")

    def filter(self, filter_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        pass

    def retrieve(self) -> List[Dict[str, Any]]:
        data = list(self.pin_collection.find())
        # if not data:
        #     raise CustomException404(message="pin not found")
        print("list pin")
        return data

    def detail(self, id: str) -> List[Dict[str, Any]]:
        data = list(self.pin_collection.find({"_id": id}))
        if not data:
            raise CustomException404(message="pin not found")
        print("detail pin")
        return data

    def controller_exists(self, controller_id: str) -> Dict[str, Any]:
        # data = list(controller_collection.get_collection().find({"_id": controller_id}))
        data = list(controller_collection.detail(controller_id))
        return data

    def update_badge(self, update_data: Dict[str, Any], pk: str) -> Dict[str, Any]:
        _ = self.detail(pk)
        self.pin_collection.update_one({"_id": pk}, {"$set": update_data})
        print("updated pin")
        return self.detail(pk)

class PinCollectionCreator(CollectionFactoryInterface):
    def create_collection(self) -> PinCollection:
        pin_collection_obj = PinCollection()
        pin_collection_obj.create_collection()
        return pin_collection_obj
