from abc import ABC, abstractmethod
from uuid import uuid4
from src.utils.patterns.singletons import SingletonMeta
from typing import List, Any, Dict, Union


class CollectionInterface(ABC, metaclass=SingletonMeta):
    def id_creator(self, data: Dict[str, Any]) -> Dict[str, Any]:
        print(5)
        data["_id"] = str(uuid4())
        return data

    @abstractmethod
    def create_collection(self):
        pass

    @abstractmethod
    def insert(self, data: Dict[str, Any]):
        pass

    @abstractmethod
    def update(self, update_data: Dict[str, Any], pk: Union[str, int]):
        pass

    @abstractmethod
    def delete(self, data: Dict[str, Any]):
        pass

    @abstractmethod
    def filter(self, filter_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def retrieve(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def detail(self, id: str) -> Dict[str, Any]:
        pass
