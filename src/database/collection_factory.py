from src.database.collection_interface import CollectionInterface
from abc import ABC


class CollectionFactoryInterface(ABC):
    def create_collection(self) -> CollectionInterface:
        pass
