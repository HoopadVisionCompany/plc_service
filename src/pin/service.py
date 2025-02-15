from src.database.db import DbBuilder
from src.utils.exceptions.custom_exceptions import CustomException404, CustomException400
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
        controller_data = self.controller_exists(data["controller_id"])
        self.validate_total_pin_count(controller_data)
        self.validate_input_pin_count(controller_data)
        self.validate_output_pin_count(controller_data)

        data = self.id_creator(data)
        self.pin_collection.insert_one(data)
        print("inserted pin")
        return data

    def update(self, update_data: Dict[str, Any], pk: str) -> Dict[str, Any]:
        _ = self.detail(pk)
        controller_data = self.controller_exists(update_data["controller_id"])
        if "type" in update_data and update_data["type"] == "in":
            self.validate_input_pin_count(controller_data)
        if "type" in update_data and update_data["type"] == "out":
            self.validate_output_pin_count(controller_data)
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
        data = controller_collection.detail(controller_id)
        return data

    def update_badge(self, update_data: Dict[str, Any], pk: str) -> Dict[str, Any]:
        _ = self.detail(pk)
        self.pin_collection.update_one({"_id": pk}, {"$set": update_data})
        print("updated pin")
        return self.detail(pk)

    def validate_total_pin_count(self, controller_data: Dict[str, Any]) -> None:
        all_pins = self.pin_collection.count_documents({"controller_id": controller_data["_id"]})

        if controller_data["count_total_pin"] <= all_pins:
            raise CustomException400(
                f'this controller has {controller_data["count_total_pin"]} pins which you added previously')

    def validate_input_pin_count(self, controller_data: Dict[str, Any]) -> None:

        in_pins = self.pin_collection.count_documents({"controller_id": controller_data["_id"], "type": "in"})

        if controller_data["count_pin_in"] <= in_pins:
            raise CustomException400(
                f'this controller has {controller_data["count_pin_in"]} input pins which you added previously')

    def validate_output_pin_count(self, controller_data: Dict[str, Any]) -> None:

        out_pins = self.pin_collection.count_documents(
            {"controller_id": controller_data["_id"], "type": "out"})

        if controller_data["count_pin_out"] <= out_pins:
            raise CustomException400(
                f'this controller has {controller_data["count_pin_out"]} output pins which you added previously')


class PinCollectionCreator(CollectionFactoryInterface):
    def create_collection(self) -> PinCollection:
        pin_collection_obj = PinCollection()
        pin_collection_obj.create_collection()
        return pin_collection_obj
