import sys
import unittest
from pydantic import ValidationError

sys.path.append("..")
from src.task.model import TaskSchema
from src.utils.patterns.builders import TaskDataBuilder


class TestTaskSchema(unittest.TestCase):
    def test_valid_data(self):
        self.valid_data = TaskDataBuilder().add_name("task1").add_description("task1").add_plc_id("1").add_pin_ids(
            [1, 2, 3]).data
        TaskSchema(**self.valid_data)

    def test_invalid_name(self):
        self.data = TaskDataBuilder().add_name("task1" * 100).add_description("task1").add_plc_id("1").add_pin_ids(
            [1, 2, 3]).data
        try:
            TaskSchema(**self.data)
        except Exception as e:
            self.assertIsInstance(e, ValidationError)

    def test_invalid_description(self):
        self.data = TaskDataBuilder().add_name("task1").add_description("task1" * 100).add_plc_id("1").add_pin_ids(
            [1, 2, 3]).data
        try:
            TaskSchema(**self.data)
        except Exception as e:
            self.assertIsInstance(e, ValidationError)

    def test_invalid_plc_id(self):
        self.data = TaskDataBuilder().add_name("task1").add_description("task1").add_plc_id(10000000).add_pin_ids(
            [1, 2, 3]).data
        try:
            TaskSchema(**self.data)
        except Exception as e:
            self.assertIsInstance(e, ValidationError)

    def test_invalid_pln_ids(self):
        self.data = TaskDataBuilder().add_name("task1").add_description("task1").add_plc_id("1").add_pin_ids(
            "hellloooooooo").data
        try:
            TaskSchema(**self.data)
        except Exception as e:
            self.assertIsInstance(e, ValidationError)
