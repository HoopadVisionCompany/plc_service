import sys
import unittest
import json
from pydantic import ValidationError

sys.path.append("..")
from src.plc.model import PLCSchema, PLCUpdateSchema
from src.utils.patterns.builders import PLCDataBuilder


class TestPLCSchema(unittest.TestCase):
    def test_valid_data(self):
        self.valid_data = PLCDataBuilder().add_type("DELTA").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            3030).add_count_pin_out(10).add_count_pin_in(10).add_count_total_pin(20).data
        PLCSchema(**self.valid_data)

    def test_invalid_type(self):
        self.data = PLCDataBuilder().add_type("D" * 200).add_protocol("TCP").add_ip("0.0.0.0").add_port(
            3030).add_count_pin_in(10).add_count_pin_out(10).add_count_total_pin(20).data
        try:
            PLCSchema(**self.data)
        except Exception as e:
            self.assertIsInstance(e, ValidationError)

    def test_invalid_protocol(self):
        self.data = PLCDataBuilder().add_type("DELTA").add_protocol("T" * 200).add_ip("0.0.0.0").add_port(
            3030).add_count_pin_in(10).add_count_pin_out(10).add_count_total_pin(20).data
        try:
            PLCSchema(**self.data)
        except Exception as e:
            self.assertIsInstance(e, ValidationError)

    def test_invalid_ip(self):
        self.data = PLCDataBuilder().add_type("DELTA").add_protocol("TCP").add_ip("0" * 20).add_port(
            3030).add_count_pin_in(10).add_count_pin_out(10).add_count_total_pin(20).data
        try:
            PLCSchema(**self.data)
        except Exception as e:
            self.assertIsInstance(e, ValidationError)

    def test_invalid_port(self):
        self.data = PLCDataBuilder().add_type("DELTA").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            8080).add_count_pin_in(10).add_count_pin_out(10).add_count_total_pin(20).data
        try:
            PLCSchema(**self.data)
        except Exception as e:
            self.assertIsInstance(e, ValidationError)

    def test_invalid_pin_in(self):
        self.data = PLCDataBuilder().add_type("DELTA").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            3030).add_count_pin_in(200).add_count_pin_out(10).add_count_total_pin(20).data
        try:
            PLCSchema(**self.data)
        except Exception as e:
            self.assertIsInstance(e, ValidationError)

    def test_invalid_pin_out(self):
        self.data = PLCDataBuilder().add_type("DELTA").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            3030).add_count_pin_in(10).add_count_pin_out(200).add_count_total_pin(20).data
        try:
            PLCSchema(**self.data)
        except Exception as e:
            self.assertIsInstance(e, ValidationError)

    def test_invalid_pin_total(self):
        self.data = PLCDataBuilder().add_type("DELTA").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            3030).add_count_pin_in(10).add_count_pin_out(10).add_count_total_pin(200).data
        try:
            PLCSchema(**self.data)
        except Exception as e:
            self.assertIsInstance(e, ValidationError)


class TestPLCUpdateSchema(unittest.TestCase):
    def test_valid_data(self):
        self.valid_data = PLCDataBuilder().add_type("DELTA").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            3030).add_count_pin_out(10).add_count_pin_in(10).data
        PLCUpdateSchema(**self.valid_data)

    def test_invalid_type(self):
        self.data = PLCDataBuilder().add_type("D" * 200).add_protocol("TCP").add_ip("0.0.0.0").add_port(
            3030).add_count_pin_in(10).add_count_pin_out(10).data
        with self.assertRaises(ValidationError):
            PLCUpdateSchema(**self.data)

    def test_invalid_protocol(self):
        self.data = PLCDataBuilder().add_type("DELTA").add_protocol("T" * 200).add_ip("0.0.0.0").add_port(
            3030).add_count_pin_in(10).add_count_pin_out(10).data
        with self.assertRaises(ValidationError):
            PLCUpdateSchema(**self.data)

    def test_invalid_ip(self):
        self.data = PLCDataBuilder().add_type("DELTA").add_protocol("TCP").add_ip("0" * 20).add_port(
            3030).add_count_pin_in(10).add_count_pin_out(10).data
        with self.assertRaises(ValidationError):
            PLCUpdateSchema(**self.data)

    def test_invalid_port(self):
        self.data = PLCDataBuilder().add_type("DELTA").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            60000).add_count_pin_in(10).add_count_pin_out(10).data  # Invalid port
        with self.assertRaises(ValidationError):
            PLCUpdateSchema(**self.data)

    def test_invalid_pin_in(self):
        self.data = PLCDataBuilder().add_type("DELTA").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            3030).add_count_pin_in(200).add_count_pin_out(10).data  # Exceeds maximum
        with self.assertRaises(ValidationError):
            PLCUpdateSchema(**self.data)

    def test_invalid_pin_out(self):
        self.data = PLCDataBuilder().add_type("DELTA").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            3030).add_count_pin_in(10).add_count_pin_out(200).data  # Exceeds maximum
        with self.assertRaises(ValidationError):
            PLCUpdateSchema(**self.data)

    def test_partial_update(self):
        data = {
            "type": None,
            "protocol": "UDP",
            "ip": "192.168.1.1",
            "port": 8080,
            "count_pin_out": None,
            "count_pin_in": 5
        }
        PLCUpdateSchema(**data)
