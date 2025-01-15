import unittest
import sys
import os

from dotenv import load_dotenv
from pymongo.errors import DuplicateKeyError

sys.path.append("..")
from src.controller_backend.service import PLCCollectionCreator, PlcCollection
from src.database.db import DbBuilder
from src.utils.patterns.builders import PLCDataBuilder
from src.utils.exceptions.custom_exceptions import CustomException404

load_dotenv()


class Initialize:
    def setUp(self):
        self.db = DbBuilder().db
        self.db_client = DbBuilder().db_client
        self.obj = PLCCollectionCreator().create_collection()
        self.collection = self.db["plc_collection"]


class TestPLCCollectionCreator(unittest.TestCase):
    def setUp(self) -> None:
        self.db = DbBuilder().db
        self.db_client = DbBuilder().db_client

    def tearDown(self) -> None:
        self.db_client.drop_database(os.getenv("TEST_DB_NAME"))

    def test_create_plc_collection(self):
        plc_factory = PLCCollectionCreator()
        plc_collection = plc_factory.create_collection()

        collections = self.db.list_collection_names()
        self.assertIn("plc_collection", collections)
        self.assertIsInstance(plc_collection, PlcCollection)


class TestPLCCollection(Initialize, unittest.TestCase):
    def setUp(self) -> None:
        Initialize.setUp(self)

    def tearDown(self) -> None:
        self.db_client.drop_database(os.getenv("TEST_DB_NAME"))

    def test_create_collection(self):
        self.obj.create_collection()
        collections = self.db.list_collection_names()
        self.assertIn("plc_collection", collections)

    def test_insert(self):
        data = PLCDataBuilder().add_type("Delta").add_protocol("TCP").add_ip("0.0.0.0").add_port(8080).add_count_pin_in(
            10).add_count_pin_out(10).add_count_total_pin(20).data
        self.obj.insert(data)
        find_data = self.collection.find_one(data)
        self.assertEqual(find_data, data)


class TestPLCCollectionInsert(Initialize, unittest.TestCase):
    def setUp(self) -> None:
        Initialize.setUp(self)
        self.data1 = PLCDataBuilder().add_type("PLC!!!!").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            8080).add_count_pin_in(
            10).add_count_pin_out(10).add_count_total_pin(20).data
        self.data2 = PLCDataBuilder().add_type("PLC!!!!").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            8081).add_count_pin_in(
            11).add_count_pin_out(10).add_count_total_pin(20).data
        self.data3 = PLCDataBuilder().add_type("PLC!!!!").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            8081).add_count_pin_in(
            10).add_count_pin_out(11).add_count_total_pin(20).data
        self.data4 = PLCDataBuilder().add_type("PLC!!!!").add_protocol("TCP").add_ip("11111111111111111111").add_port(
            8081).add_count_pin_in(
            10).add_count_pin_out(10).add_count_total_pin(20).data
        self.data5_1 = PLCDataBuilder().add_type("PLC!!!!").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            8080).add_count_pin_in(
            10).add_count_pin_out(10).add_count_total_pin(20).data

    def tearDown(self) -> None:
        print("in tear down")
        self.db_client.drop_database(os.getenv("TEST_DB_NAME"))

    def test_insert_valid_data(self):
        self.obj.insert(self.data1)
        find_data = self.collection.find_one(self.data1)
        self.assertEqual(find_data, self.data1)

    def test_insert_invalid_data_add_count_pin_in(self):
        self.obj.insert(self.data2)
        find_data = self.collection.find_one(self.data2)
        self.assertEqual(find_data, self.data2)

    def test_insert_invalid_data_add_count_pin_out(self):
        self.obj.insert(self.data3)
        find_data = self.collection.find_one(self.data3)
        self.assertEqual(find_data, self.data3)

    def test_insert_invalid_data_ip(self):
        self.obj.insert(self.data4)
        find_data = self.collection.find_one(self.data4)
        self.assertEqual(find_data, self.data4)

    def test_insert_duplicate(self):
        self.obj.insert(self.data1)
        try:
            self.obj.insert(self.data5_1)
        except Exception as e:
            self.assertIsInstance(e, DuplicateKeyError)


class TestPLCCollectionUpdate(Initialize, unittest.TestCase):
    def setUp(self) -> None:
        Initialize.setUp(self)
        self.data1 = PLCDataBuilder().add_type("PLC!!!!").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            8080).add_count_pin_in(
            10).add_count_pin_out(10).add_count_total_pin(20).add_uuid().data
        self.data1_id = self.data1["_id"]
        self.data2 = PLCDataBuilder().add_type("PLC!!!!").add_protocol("UDp").add_ip("0.0.0.0").add_port(
            8081).add_count_pin_in(
            10).add_count_pin_out(10).add_count_total_pin(20).data
        self.data3 = PLCDataBuilder().add_type("PLC!!!!").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            8081).add_count_pin_in(
            11).add_count_pin_out(10).add_count_total_pin(20).data
        self.data4 = PLCDataBuilder().add_type("PLC!!!!").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            8081).add_count_pin_in(
            10).add_count_pin_out(11).add_count_total_pin(20).data
        self.data5 = PLCDataBuilder().add_type("PLC!!!!").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            8989).add_count_pin_in(
            10).add_count_pin_out(10).add_count_total_pin(20).add_uuid().data
        self.data5_id = self.data5["_id"]
        self.data5_1 = PLCDataBuilder().add_type("PLC!!!!").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            8080).add_count_pin_in(
            10).add_count_pin_out(10).add_count_total_pin(20).data

    def tearDown(self) -> None:
        print("in tear down")
        self.db_client.drop_database(os.getenv("TEST_DB_NAME"))

    def test_update_valid_data(self):
        self.collection.insert_one(self.data1)
        self.obj.update(update_data=self.data2, pk=self.data1_id)
        find_data = self.collection.find_one({"_id": self.data1_id}, {"_id": 0})
        self.assertEqual(find_data, self.data2)

    def test_update_invalid_data_add_count_pin_in(self):
        self.collection.insert_one(self.data1)
        try:
            self.obj.update(update_data=self.data3, pk=self.data1_id)
        except Exception as e:
            self.assertIsInstance(e, ValueError)

    def test_update_invalid_data_add_count_pin_out(self):
        self.collection.insert_one(self.data1)
        try:
            self.obj.update(update_data=self.data4, pk=self.data1_id)
        except Exception as e:
            self.assertIsInstance(e, ValueError)

    def test_update_duplicate(self):
        self.collection.insert_one(self.data1)
        self.collection.insert_one(self.data5)
        try:
            self.obj.update(update_data=self.data5_1, pk=self.data5_id)
        except Exception as e:
            self.assertIsInstance(e, DuplicateKeyError)


class TestPLCCollectionDelete(Initialize, unittest.TestCase):
    def setUp(self) -> None:
        Initialize.setUp(self)
        self.data1 = PLCDataBuilder().add_type("PLC!!!!").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            8080).add_count_pin_in(
            10).add_count_pin_out(10).add_count_total_pin(20).add_uuid().data
        self.data1_id = self.data1["_id"]

    def tearDown(self) -> None:
        print("in tear down")
        self.db_client.drop_database(os.getenv("TEST_DB_NAME"))

    def test_delete_valid_data(self):
        self.collection.insert_one(self.data1)
        self.obj.delete(pk=self.data1_id)
        find_data = self.collection.find_one({"_id": self.data1_id}, {"_id": 0})
        self.assertIsNone(find_data)

    def test_delete_notfound_data(self):
        self.collection.insert_one(self.data1)
        try:
            self.obj.delete(pk="1")
        except Exception as e:
            self.assertIsInstance(e, CustomException404)


class TestPLCCollectionRetrieve(Initialize, unittest.TestCase):
    def setUp(self) -> None:
        Initialize.setUp(self)
        self.data1 = PLCDataBuilder().add_type("PLC!!!!").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            8080).add_count_pin_in(
            10).add_count_pin_out(10).add_count_total_pin(20).add_uuid().data
        self.data1_id = self.data1["_id"]
        self.data2 = PLCDataBuilder().add_type("PLC!!!!").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            8081).add_count_pin_in(
            10).add_count_pin_out(10).add_count_total_pin(20).add_uuid().data
        self.data2_id = self.data2["_id"]

    def tearDown(self) -> None:
        print("in tear down")
        self.db_client.drop_database(os.getenv("TEST_DB_NAME"))

    def test_retrieve_valid_data(self):
        self.collection.insert_one(self.data1)
        self.collection.insert_one(self.data2)

        find_data = self.obj.retrieve()
        self.assertIsNotNone(find_data)
        self.assertEqual(len(find_data), 2)

    def test_retrieve_notfound_data(self):
        try:
            self.obj.retrieve()
        except Exception as e:
            self.assertIsInstance(e, CustomException404)


class TestPLCCollectionDetail(Initialize, unittest.TestCase):
    def setUp(self) -> None:
        Initialize.setUp(self)
        self.data1 = PLCDataBuilder().add_type("PLC!!!!").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            8080).add_count_pin_in(
            10).add_count_pin_out(10).add_count_total_pin(20).add_uuid().data
        self.data1_id = self.data1["_id"]

    def tearDown(self) -> None:
        print("in tear down")
        self.db_client.drop_database(os.getenv("TEST_DB_NAME"))

    def test_detail_valid_data(self):
        self.collection.insert_one(self.data1)

        find_data = self.obj.detail(id=self.data1_id)
        self.assertIsNotNone(find_data)
        self.assertEqual(find_data, self.data1)

    def test_detail_notfound_data(self):
        self.collection.insert_one(self.data1)
        try:
            self.obj.detail(id="1")
        except Exception as e:
            self.assertIsInstance(e, CustomException404)
