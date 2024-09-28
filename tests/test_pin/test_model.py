import sys
import unittest
from pydantic import ValidationError

sys.path.append("..")
from src.pin.model import PinSchema
from src.utils.patterns.builders import PinDataBuilder


class TestPinSchema(unittest.TestCase):
    def test_valid_data(self):
        self.valid_data = PinDataBuilder().add_type("in").add_plc_id("1").add_id(1).data
        PinSchema(**self.valid_data)

    def test_invalid_type(self):
        self.data = PinDataBuilder().add_type("aaaaa").add_plc_id("1").add_id(1).data
        try:
            PinSchema(**self.data)
        except Exception as e:
            self.assertIsInstance(e, ValidationError)

    def test_invalid_plc_id(self):
        self.data = PinDataBuilder().add_type("in").add_plc_id(1).add_id(1).data
        try:
            PinSchema(**self.data)
        except Exception as e:
            self.assertIsInstance(e, ValidationError)

    def test_invalid_id(self):
        self.data = PinDataBuilder().add_type("in").add_plc_id("1").add_id(100000).data
        try:
            PinSchema(**self.data)
        except Exception as e:
            self.assertIsInstance(e, ValidationError)
