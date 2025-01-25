from typing import Dict, List, Any
from src.database.db import DbBuilder
from src.utils.exceptions.custom_exceptions import CustomException404
from src.database.collection_interface import CollectionInterface
from src.database.collection_factory import CollectionFactoryInterface


class SettingCollection(DbBuilder, CollectionInterface):
    def __init__(self) -> None:
        super().__init__()

    def create_collection(self) -> None:
        print("Creating settingCollection...")
        self.setting_collection = self.db['setting_collection']
        self.setting_collection.create_index("package_id", unique=True)
        print("settingCollection created with unique index on 'package_id'")

    def get_collection(self) -> Any:
        return self.setting_collection

    def insert(self, data: Dict[str, Any]) -> None:
        data = self.id_creator(data)
        self.setting_collection.insert_one(data)
        print("inserted setting")

    def update(self, update_data: Dict[str, Any], pk: str) -> None:
        data = self.detail(pk)
        # if "package_id" in data.keys():
        #     if not package_is_exist(data['package_id']):
        #         raise CustomException404("this package is not exist")
        self.setting_collection.update_one({"_id": pk}, {"$set": update_data})
        print("updated setting")

    def delete(self, pk: str) -> None:
        _ = self.detail(pk)
        self.setting_collection.delete_one({"_id": pk})
        print("deleted setting")

    def filter(self, filter_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        pass

    def retrieve(self) -> List[Dict[str, Any]]:
        data = list(self.setting_collection.find())
        print("list setting")
        return data

    def detail(self, id: str) -> Dict[str, Any]:
        data = self.setting_collection.find_one({"_id": id})
        if not data:
            raise CustomException404(message="setting not found")
        print("detail setting")
        return data


class SettingCollectionCreator(CollectionFactoryInterface):
    def create_collection(self) -> SettingCollection:
        setting_collection_obj = SettingCollection()
        setting_collection_obj.create_collection()
        return setting_collection_obj
