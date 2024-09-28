from src.database.db import DbBuilder
from src.utils.exceptions.custom_exceptions import CustomException404
from src.database.collection_interface import CollectionInterface
from src.database.collection_factory import CollectionFactoryInterface
from typing import Dict, List, Any


class PlcCollection(DbBuilder, CollectionInterface):
    def __init__(self) -> None:
        super().__init__()

    def create_collection(self) -> None:
        print("Creating PlcCollection...")
        self.plc_collection = self.db['plc_collection']
        self.plc_collection.create_index("port", unique=True)
        print("PlcCollection created with unique index on 'port'")

    def get_collection(self) -> Any:
        return self.plc_collection

    def insert(self, data: Dict[str, Any]) -> None:
        data = self.id_creator(data)
        self.plc_collection.insert_one(data)
        print("inserted plc")

    def update(self, update_data: Dict[str, Any], pk: str) -> None:
        data = self.detail(pk)
        if update_data["count_pin_out"] + update_data["count_pin_in"] > data["count_total_pin"]:
            raise ValueError("exceeded the total number of pins")
        self.plc_collection.update_one({"_id": pk}, {"$set": update_data})
        print("updated plc")

    def delete(self, pk: str) -> None:
        _ = self.detail(pk)
        self.plc_collection.delete_one({"_id": pk})
        print("deleted plc")

    def filter(self, filter_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        pass

    def retrieve(self) -> List[Dict[str, Any]]:
        data = list(self.plc_collection.find())
        if not data:
            raise CustomException404(message="plc not found")
        print("list plc")
        return data

    def detail(self, id: str) -> Dict[str, Any]:
        data = self.plc_collection.find_one({"_id": id})
        if not data:
            raise CustomException404(message="plc not found")
        print("detail plc")
        return data


class PLCCollectionCreator(CollectionFactoryInterface):
    def create_collection(self) -> PlcCollection:
        plc_collection_obj = PlcCollection()
        plc_collection_obj.create_collection()
        return plc_collection_obj
