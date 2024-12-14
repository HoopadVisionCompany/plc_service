from src.database.db import DbBuilder
from src.utils.exceptions.custom_exceptions import CustomException404
from src.database.collection_interface import CollectionInterface

from src.database.collection_factory import CollectionFactoryInterface
from src.plc.service import PLCCollectionCreator
from typing import Dict, Any, List

plc_factory = PLCCollectionCreator()
plc_collection = plc_factory.create_collection()


class PinCollection(DbBuilder, CollectionInterface):
    def __init__(self) -> None:
        super().__init__()

    def create_collection(self) -> None:
        print("Creating PinCollection...")
        self.pin_collection = self.db['pin_collection']
        self.pin_collection.create_index([("plc_id", 1), ("id", 1)], unique=True)

        print("PinCollection created with unique index on 'plc_id' and 'id'")

    def get_collection(self) -> Any:
        return self.pin_collection

    def insert(self, data: Dict[str, Any]) -> None:
        _ = self.plc_exists(data["plc_id"])
        data = self.id_creator(data)
        self.pin_collection.insert_one(data)
        print("inserted pin")

    def update(self, update_data: Dict[str, Any], pk: str) -> None:
        _ = self.detail(pk)
        _ = self.plc_exists(update_data["plc_id"])
        self.pin_collection.update_one({"_id": pk}, {"$set": update_data})
        print("updated pin")

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

    def plc_exists(self, plc_id: str) -> Dict[str, Any]:
        # data = list(plc_collection.get_collection().find({"_id": plc_id}))
        data = list(plc_collection.detail(plc_id))
        return data


class PinCollectionCreator(CollectionFactoryInterface):
    def create_collection(self) -> PinCollection:
        pin_collection_obj = PinCollection()
        pin_collection_obj.create_collection()
        return pin_collection_obj
