from abc import ABCMeta
from typing import Type, Dict, Any


def singleton(cls: Type) -> Type:
    instances: Dict[Type, Any] = {}

    def get_instance(*args: Any, **kwargs: Any) -> Any:
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


class SingletonMeta(ABCMeta):
    _instances: Dict[Type, Any] = {}

    def __call__(cls: Type, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

    def __init__(self,*args):
        if not hasattr(self, "_initialized"):
            self._initialized = True