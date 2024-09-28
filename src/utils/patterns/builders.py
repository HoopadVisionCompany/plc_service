from uuid import uuid4
from typing import Dict, List, Any


class PLCDataBuilder:
    def __init__(self) -> None:
        self.data: Dict[str, Any] = {}

    def add_type(self, v: str) -> "PLCDataBuilder":
        self.data["type"] = v
        return self

    def add_protocol(self, v: str) -> "PLCDataBuilder":
        self.data["protocol"] = v
        return self

    def add_ip(self, v: str) -> "PLCDataBuilder":
        self.data["ip"] = v
        return self

    def add_port(self, v: int) -> "PLCDataBuilder":
        self.data["port"] = v
        return self

    def add_count_pin_out(self, v: int) -> "PLCDataBuilder":
        self.data["count_pin_out"] = v
        return self

    def add_count_pin_in(self, v: int) -> "PLCDataBuilder":
        self.data["count_pin_in"] = v
        return self

    def add_count_total_pin(self, v: int) -> "PLCDataBuilder":
        self.data["count_total_pin"] = v
        return self

    def add_uuid(self) -> "PLCDataBuilder":
        self.data["_id"] = str(uuid4())
        return self


class PinDataBuilder:
    def __init__(self) -> None:
        self.data: Dict[str, Any] = {}

    def add_type(self, v: str) -> "PinDataBuilder":
        self.data["type"] = v
        return self

    def add_plc_id(self, v: str) -> "PinDataBuilder":
        self.data["plc_id"] = v
        return self

    def add_id(self, v: str) -> "PinDataBuilder":
        self.data["id"] = v
        return self

    def add_uuid(self) -> "PinDataBuilder":
        self.data["_id"] = str(uuid4())
        return self


class TaskDataBuilder:
    def __init__(self) -> None:
        self.data: Dict[str, Any] = {}

    def add_name(self, v: str) -> "TaskDataBuilder":
        self.data["name"] = v
        return self

    def add_description(self, v: str) -> "TaskDataBuilder":
        self.data["description"] = v
        return self

    def add_plc_id(self, v: str) -> "TaskDataBuilder":
        self.data["plc_id"] = v
        return self

    def add_pin_ids(self, v: List[str]) -> "TaskDataBuilder":
        self.data["pin_ids"] = v
        return self

    def add_uuid(self) -> "TaskDataBuilder":
        self.data["_id"] = str(uuid4())
        return self
