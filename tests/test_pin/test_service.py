import time
import unittest
import sys
import os
import uuid

from dotenv import load_dotenv

sys.path.append("..")
from src.pin.service import PinCollectionCreator, PinCollection
from src.database.db import DbBuilder
from src.utils.patterns.builders import PLCDataBuilder, PinDataBuilder
from src.plc.service import PlcCollection, PLCCollectionCreator
from src.utils.exceptions.custom_exceptions import CustomException404
from pymongo.errors import DuplicateKeyError

load_dotenv()


class Initialize:
    def setUp(self):
        self.db = DbBuilder().db
        self.db_client = DbBuilder().db_client
        self.obj_plc = PLCCollectionCreator().create_collection()
        self.obj_pin = PinCollectionCreator().create_collection()
        self.collection = self.db["pin_collection"]
        self.plc_collection = self.db["plc_collection"]


class TestPinCollectionCreator(unittest.TestCase):
    def setUp(self) -> None:
        self.db = DbBuilder().db
        self.db_client = DbBuilder().db_client

    def tearDown(self) -> None:
        self.db_client.drop_database(os.getenv("TEST_DB_NAME"))

    def test_create_pin_collection(self):
        pin_factory = PinCollectionCreator()
        pin_collection = pin_factory.create_collection()

        collections = self.db.list_collection_names()
        self.assertIn("pin_collection", collections)
        self.assertIsInstance(pin_collection, PinCollection)


class TestPinCollection(unittest.TestCase, Initialize):
    def setUp(self) -> None:
        Initialize.setUp(self)

    def tearDown(self) -> None:
        self.db_client.drop_database(os.getenv("TEST_DB_NAME"))

    def test_create_collection(self):
        self.obj_pin.create_collection()
        collections = self.db.list_collection_names()
        self.assertIn("pin_collection", collections)

    def test_plc_exists(self):
        try:
            _ = self.obj_pin.plc_exists("1")
        except Exception as e:
            self.assertEquals(str(e), "plc not found")

        test_data2 = PLCDataBuilder().add_uuid().add_type("Delta").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            5000).add_count_pin_out(10).add_count_pin_in(10).add_count_total_pin(20).data

        self.plc_collection.insert_one(test_data2)

        test_result2 = self.obj_pin.plc_exists(test_data2["_id"])

        self.assertIsNotNone(test_result2)


class TestPinCollectionInsert(unittest.TestCase, Initialize):
    def setUp(self):
        Initialize.setUp(self)
        self.plc1 = PLCDataBuilder().add_type("PLC!!!!").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            8080).add_count_pin_in(
            10).add_count_pin_out(10).add_count_total_pin(20).add_uuid().data
        self.plc1_id = self.plc1["_id"]
        self.plc_collection.insert_one(self.plc1)

        self.data1 = PinDataBuilder().add_type("in").add_id(1).add_plc_id(self.plc1_id).data  # 200
        self.data2 = PinDataBuilder().add_type("aaaaaa").add_id(2).add_plc_id(self.plc1_id).data  # 422
        self.data3 = PinDataBuilder().add_type("in").add_id(200000000).add_plc_id(self.plc1_id).data  # 422
        self.data4 = PinDataBuilder().add_type("in").add_id(3).add_plc_id("1").data  # 404
        self.data5_1 = PinDataBuilder().add_type("in").add_id(1).add_plc_id(self.plc1_id).data  # 500

    def tearDown(self) -> None:
        self.db_client.drop_database(os.getenv("TEST_DB_NAME"))

    def test_insert_valid_date(self):
        self.obj_pin.insert(self.data1)
        find_data = self.collection.find_one(self.data1)
        self.assertEqual(find_data, self.data1)

    def test_insert_invalid_type(self):
        self.obj_pin.insert(self.data2)
        find_data = self.collection.find_one(self.data2)
        self.assertEqual(find_data, self.data2)

    def test_insert_invalid_id(self):
        self.obj_pin.insert(self.data3)
        find_data = self.collection.find_one(self.data3)
        self.assertEqual(find_data, self.data3)

    def test_insert_invalid_plc_id(self):
        try:
            self.obj_pin.insert(self.data4)
        except Exception as e:
            self.assertEquals(str(e), "plc not found")
            self.assertIsInstance(e, CustomException404)

    def test_insert_duplicate_data(self):

        self.obj_pin.insert(self.data1)
        try:
            self.obj_pin.insert(self.data5_1)
        except Exception as e:
            self.assertIsInstance(e, DuplicateKeyError)


class TestPinCollectionUpdate(unittest.TestCase, Initialize):
    def setUp(self):
        Initialize.setUp(self)
        self.plc1 = PLCDataBuilder().add_type("PLC!!!!").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            8080).add_count_pin_in(
            10).add_count_pin_out(10).add_count_total_pin(20).add_uuid().data
        self.plc1_id = self.plc1["_id"]
        self.plc_collection.insert_one(self.plc1)

        self.data1 = PinDataBuilder().add_type("in").add_id(1).add_plc_id(self.plc1_id).add_uuid().data  # 200
        self.collection.insert_one(self.data1)
        self.data1_id = self.data1["_id"]
        self.data2 = PinDataBuilder().add_type("out").add_id(1).add_plc_id(self.plc1_id).data
        self.data3 = PinDataBuilder().add_type("aaaaaa").add_id(2).add_plc_id(self.plc1_id).data  # 422
        self.data4 = PinDataBuilder().add_type("in").add_id(200000000).add_plc_id(self.plc1_id).data  # 422
        self.data5 = PinDataBuilder().add_type("in").add_id(3).add_plc_id("1").data  # 404
        self.data6 = PinDataBuilder().add_type("out").add_id(2).add_plc_id(self.plc1_id).data  # 500
        self.data6_1 = PinDataBuilder().add_type("out").add_id(2).add_plc_id(self.plc1_id).data  # 500

    def tearDown(self) -> None:
        self.db_client.drop_database(os.getenv("TEST_DB_NAME"))

    def test_update_valid_data(self):
        self.obj_pin.update(self.data2, pk=self.data1_id)
        find_data = self.collection.find_one(self.data2, {"_id": 0})
        self.assertEqual(find_data, self.data2)

    def test_update_invalid_type(self):
        self.obj_pin.update(self.data3, pk=self.data1_id)
        find_data = self.collection.find_one(self.data3, {"_id": 0})
        self.assertEqual(find_data, self.data3)

    def test_update_invalid_id(self):
        self.obj_pin.update(self.data4, pk=self.data1_id)
        find_data = self.collection.find_one(self.data4, {"_id": 0})
        self.assertEqual(find_data, self.data4)

    def test_update_invalid_plc_id(self):
        try:
            self.obj_pin.update(self.data5, pk=self.data1_id)
        except Exception as e:
            self.assertEquals(str(e), "plc not found")
            self.assertIsInstance(e, CustomException404)

    def test_update_duplicate_data(self):
        self.data6["_id"] = str(uuid.uuid4())
        self.obj_pin.insert(self.data6)

        try:
            self.obj_pin.update(self.data6_1, pk=self.data1_id)
        except Exception as e:
            self.assertIsInstance(e, DuplicateKeyError)


class TestPinCollectionDelete(unittest.TestCase, Initialize):
    def setUp(self):
        Initialize.setUp(self)
        self.plc1 = PLCDataBuilder().add_type("PLC!!!!").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            8080).add_count_pin_in(
            10).add_count_pin_out(10).add_count_total_pin(20).add_uuid().data
        self.plc1_id = self.plc1["_id"]
        self.plc_collection.insert_one(self.plc1)

        self.data1 = PinDataBuilder().add_type("in").add_id(1).add_plc_id(self.plc1_id).add_uuid().data  # 200
        self.collection.insert_one(self.data1)
        self.data1_id = self.data1["_id"]

    def tearDown(self):
        self.db_client.drop_database(os.getenv("TEST_DB_NAME"))

    def test_delete_valid_data(self):
        self.obj_pin.delete(pk=self.data1_id)
        find_data = self.collection.find_one({"_id": self.data1_id})
        self.assertIsNone(find_data)

    def test_delete_not_found(self):
        try:
            self.obj_pin.delete(pk="1")
        except Exception as e:
            self.assertIsInstance(e, CustomException404)


class TestPinCollectionRetrieve(unittest.TestCase, Initialize):
    def setUp(self):
        Initialize.setUp(self)

    def tearDown(self):
        self.db_client.drop_database(os.getenv("TEST_DB_NAME"))

    def test_retrieve_valid_data(self):
        self.plc1 = PLCDataBuilder().add_type("PLC!!!!").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            8080).add_count_pin_in(
            10).add_count_pin_out(10).add_count_total_pin(20).add_uuid().data
        self.plc1_id = self.plc1["_id"]
        self.plc_collection.insert_one(self.plc1)

        self.data1 = PinDataBuilder().add_type("in").add_id(1).add_plc_id(self.plc1_id).add_uuid().data  # 200
        self.data2 = PinDataBuilder().add_type("out").add_id(2).add_plc_id(self.plc1_id).add_uuid().data
        self.collection.insert_one(self.data1)
        self.collection.insert_one(self.data2)
        data = self.obj_pin.retrieve()
        self.assertEqual(data, [self.data1, self.data2])

    def test_retrieve_not_found(self):
        try:
            _ = self.obj_pin.retrieve()
        except Exception as e:
            self.assertIsInstance(e, CustomException404)


class TestPinCollectionDetail(unittest.TestCase, Initialize):
    def setUp(self):
        Initialize.setUp(self)
        self.plc1 = PLCDataBuilder().add_type("PLC!!!!").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            8080).add_count_pin_in(
            10).add_count_pin_out(10).add_count_total_pin(20).add_uuid().data
        self.plc1_id = self.plc1["_id"]
        self.plc_collection.insert_one(self.plc1)
        self.data1 = PinDataBuilder().add_type("in").add_id(1).add_plc_id(self.plc1_id).add_uuid().data  # 200
        self.collection.insert_one(self.data1)
        self.data1_id = self.data1["_id"]

    def tearDown(self):
        self.db_client.drop_database(os.getenv("TEST_DB_NAME"))

    def test_detail_valid_data(self):

        data = self.obj_pin.detail(id=self.data1_id)
        self.assertIsNotNone(data)

    def test_detail_not_found(self):
        try:
            _ = self.obj_pin.detail("1")
        except Exception as e:
            self.assertIsInstance(e, CustomException404)
