import unittest
import sys
import os

from dotenv import load_dotenv

sys.path.append("..")
from src.task.service import TaskCollectionCreator, TaskCollection

from src.database.db import DbBuilder
from src.utils.patterns.builders import PLCDataBuilder, PinDataBuilder, TaskDataBuilder

from src.utils.exceptions.custom_exceptions import CustomException404
from pymongo.errors import DuplicateKeyError

load_dotenv()


class Initialize:
    def setUp(self):
        self.db = DbBuilder().db
        self.db_client = DbBuilder().db_client
        self.obj_task = TaskCollectionCreator().create_collection()
        self.collection = self.db["task_collection"]
        self.pin_collection = self.db["pin_collection"]
        self.plc_collection = self.db["plc_collection"]


class TestTaskCollectionCreator(unittest.TestCase):
    def setUp(self) -> None:
        self.db = DbBuilder().db
        self.db_client = DbBuilder().db_client

    def tearDown(self) -> None:
        self.db_client.drop_database(os.getenv("TEST_DB_NAME"))

    def test_create_task_collection(self):
        task_factory = TaskCollectionCreator()
        task_collection = task_factory.create_collection()

        collections = self.db.list_collection_names()
        self.assertIn("task_collection", collections)
        self.assertIsInstance(task_collection, TaskCollection)


class TestTaskCollection(unittest.TestCase, Initialize):
    def setUp(self) -> None:
        Initialize.setUp(self)

    def tearDown(self) -> None:
        self.db_client.drop_database(os.getenv("TEST_DB_NAME"))

    def test_create_collection(self):
        self.obj_task.create_collection()
        collections = self.db.list_collection_names()
        self.assertIn("task_collection", collections)

    def test_plc_exists(self):
        try:
            _ = self.obj_task.plc_exists("1")
        except Exception as e:
            self.assertEqual(str(e), "controller_backend not found")

        test_data2 = PLCDataBuilder().add_uuid().add_type("Delta").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            5000).add_count_pin_out(10).add_count_pin_in(10).add_count_total_pin(20).data

        self.plc_collection.insert_one(test_data2)

        test_result2 = self.obj_task.plc_exists(test_data2["_id"])

        self.assertIsNotNone(test_result2)

    def test_pin_exists(self):
        try:
            _ = self.obj_task.pin_exists("1", "1")
        except Exception as e:
            self.assertIsInstance(e, CustomException404)

        plc = PLCDataBuilder().add_uuid().add_type("Delta").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            5000).add_count_pin_out(10).add_count_pin_in(10).add_count_total_pin(20).data
        plc_id = plc["_id"]
        pin = PinDataBuilder().add_plc_id(plc_id).add_type("in").add_id(1).add_uuid().data

        self.plc_collection.insert_one(plc)
        self.pin_collection.insert_one(pin)

        test_result2 = self.obj_task.pin_exists(pin["id"], plc_id)

        self.assertIsNotNone(test_result2)


class TestTaskCollectionInsert(unittest.TestCase, Initialize):
    def setUp(self):
        Initialize.setUp(self)
        self.plc1 = PLCDataBuilder().add_type("PLC!!!!").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            8080).add_count_pin_in(
            10).add_count_pin_out(10).add_count_total_pin(20).add_uuid().data
        self.plc1_id = self.plc1["_id"]
        self.plc_collection.insert_one(self.plc1)
        self.pin1 = PinDataBuilder().add_uuid().add_plc_id(self.plc1_id).add_type("in").add_id(1).data
        self.pin2 = PinDataBuilder().add_uuid().add_plc_id(self.plc1_id).add_type("in").add_id(2).data
        self.pin3 = PinDataBuilder().add_uuid().add_plc_id(self.plc1_id).add_type("out").add_id(3).data
        self.pin_collection.insert_one(self.pin1)
        self.pin_collection.insert_one(self.pin2)
        self.pin_collection.insert_one(self.pin3)

        self.task1 = TaskDataBuilder().add_name("task1").add_description("task1").add_plc_id(self.plc1_id).add_pin_ids(
            [1, 2, 3]).data  # 200
        self.task2 = TaskDataBuilder().add_name("task1" * 51).add_description("task1").add_plc_id(
            self.plc1_id).add_pin_ids([1, 2, 3]).data  # 422
        self.task3 = TaskDataBuilder().add_name("task1").add_description("task1" * 51).add_plc_id(
            self.plc1_id).add_pin_ids([1, 2, 3]).data  # 422
        self.task4 = TaskDataBuilder().add_name("task1").add_description("task1").add_plc_id("1").add_pin_ids(
            [1, 2, 3]).data  # 404
        self.task5 = TaskDataBuilder().add_name("task1").add_description("task1").add_plc_id(self.plc1_id).add_pin_ids(
            [10, 20, 30]).data  # 404
        self.task6_1 = TaskDataBuilder().add_name("task1").add_description("task1").add_plc_id(
            self.plc1_id).add_pin_ids([1, 2, 3]).data  # 500

    def tearDown(self) -> None:
        self.db_client.drop_database(os.getenv("TEST_DB_NAME"))

    def test_insert_valid_date(self):
        self.obj_task.insert(self.task1)
        find_data = self.collection.find_one(self.task1)
        self.assertIsNotNone(find_data)

    def test_insert_invalid_name(self):
        self.obj_task.insert(self.task2)
        find_data = self.collection.find_one(self.task2)
        self.assertIsNotNone(find_data)

    def test_insert_invalid_description(self):
        self.obj_task.insert(self.task3)
        find_data = self.collection.find_one(self.task3)
        self.assertIsNotNone(find_data)

    def test_insert_invalid_plc_id(self):
        try:
            self.obj_task.insert(self.task4)
        except Exception as e:
            self.assertEqual(str(e), "controller_backend not found")
            self.assertIsInstance(e, CustomException404)

    def test_insert_invalid_pin_ids(self):
        try:
            self.obj_task.insert(self.task5)
        except Exception as e:
            self.assertEqual(str(e), "pin not found")
            self.assertIsInstance(e, CustomException404)

    def test_insert_duplicate_data(self):

        self.obj_task.insert(self.task1)
        try:
            self.obj_task.insert(self.task6_1)
        except Exception as e:
            self.assertIsInstance(e, DuplicateKeyError)


class TestTaskCollectionUpdate(unittest.TestCase, Initialize):
    def setUp(self):
        Initialize.setUp(self)
        self.plc1 = PLCDataBuilder().add_type("PLC!!!!").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            8080).add_count_pin_in(
            10).add_count_pin_out(10).add_count_total_pin(20).add_uuid().data
        self.plc1_id = self.plc1["_id"]
        self.plc_collection.insert_one(self.plc1)
        self.pin1 = PinDataBuilder().add_uuid().add_plc_id(self.plc1_id).add_type("in").add_id(1).data
        self.pin2 = PinDataBuilder().add_uuid().add_plc_id(self.plc1_id).add_type("in").add_id(2).data
        self.pin3 = PinDataBuilder().add_uuid().add_plc_id(self.plc1_id).add_type("out").add_id(3).data
        self.pin4 = PinDataBuilder().add_uuid().add_plc_id(self.plc1_id).add_type("out").add_id(4).data
        self.pin_collection.insert_one(self.pin1)
        self.pin_collection.insert_one(self.pin2)
        self.pin_collection.insert_one(self.pin3)
        self.pin_collection.insert_one(self.pin4)

        self.task1 = TaskDataBuilder().add_name("task1").add_description("task1").add_plc_id(self.plc1_id).add_pin_ids(
            [1, 2, 3]).add_uuid().data  # 200
        self.task1_id = self.task1["_id"]
        self.collection.insert_one(self.task1)
        self.task0 = TaskDataBuilder().add_name("task1").add_description("task1").add_plc_id(self.plc1_id).add_pin_ids(
            [1]).data  # 200
        self.task2 = TaskDataBuilder().add_name("task1" * 51).add_description("task1").add_plc_id(
            self.plc1_id).add_pin_ids([1, 2, 3]).data  # 422
        self.task3 = TaskDataBuilder().add_name("task1").add_description("task1" * 51).add_plc_id(
            self.plc1_id).add_pin_ids([1, 2, 3]).data  # 422
        self.task4 = TaskDataBuilder().add_name("task1").add_description("task1").add_plc_id("1").add_pin_ids(
            [1, 2, 3]).data  # 404
        self.task5 = TaskDataBuilder().add_name("task1").add_description("task1").add_plc_id(self.plc1_id).add_pin_ids(
            [10, 20, 30]).data  # 404
        self.task6 = TaskDataBuilder().add_name("task1").add_description("task1").add_plc_id(
            self.plc1_id).add_pin_ids([4]).add_uuid().data  # 500
        self.task6_id = self.task6["_id"]

    def tearDown(self) -> None:
        self.db_client.drop_database(os.getenv("TEST_DB_NAME"))

    def test_update_valid_date(self):
        self.obj_task.update(self.task0, pk=self.task1_id)
        find_data = self.collection.find_one({"_id": self.task1_id}, {"_id": 0})
        self.assertEqual(find_data, self.task0)

    def test_update_invalid_name(self):
        self.obj_task.update(self.task2, pk=self.task1_id)
        find_data = self.collection.find_one({"_id": self.task1_id}, {"_id": 0})
        self.assertEqual(find_data, self.task2)

    def test_update_invalid_description(self):
        self.obj_task.update(self.task3, pk=self.task1_id)
        find_data = self.collection.find_one({"_id": self.task1_id}, {"_id": 0})
        self.assertEqual(find_data, self.task3)

    def test_update_invalid_plc_id(self):
        try:
            self.obj_task.update(self.task4, pk=self.task1_id)
        except Exception as e:
            self.assertEqual(str(e), "controller_backend not found")
            self.assertIsInstance(e, CustomException404)

    def test_update_invalid_pin_ids(self):
        try:
            self.obj_task.update(self.task5, pk=self.task1_id)
        except Exception as e:
            self.assertEqual(str(e), "pin not found")
            self.assertIsInstance(e, CustomException404)

    def test_update_duplicate_data(self):

        self.obj_task.insert(self.task6)
        try:
            self.obj_task.update(self.task0, pk=self.task1_id)
        except Exception as e:
            self.assertIsInstance(e, DuplicateKeyError)


class TestTaskCollectionDelete(unittest.TestCase, Initialize):
    def setUp(self):
        Initialize.setUp(self)
        self.plc1 = PLCDataBuilder().add_type("PLC!!!!").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            8080).add_count_pin_in(
            10).add_count_pin_out(10).add_count_total_pin(20).add_uuid().data
        self.plc1_id = self.plc1["_id"]
        self.plc_collection.insert_one(self.plc1)
        self.pin1 = PinDataBuilder().add_uuid().add_plc_id(self.plc1_id).add_type("in").add_id(1).data
        self.pin_collection.insert_one(self.pin1)

        self.task1 = TaskDataBuilder().add_name("task1").add_description("task1").add_plc_id(self.plc1_id).add_pin_ids(
            [1, 2, 3]).add_uuid().data  # 200
        self.task1_id = self.task1["_id"]
        self.collection.insert_one(self.task1)

    def tearDown(self) -> None:
        self.db_client.drop_database(os.getenv("TEST_DB_NAME"))

    def test_delete_valid_date(self):
        self.obj_task.delete(pk=self.task1_id)
        find_data = self.collection.find_one({"_id": self.task1_id}, {"_id": 0})
        self.assertIsNone(find_data)

    def test_delete_not_found(self):
        try:
            self.obj_task.delete(pk="1")
        except Exception as e:
            self.assertIsInstance(e, CustomException404)
            self.assertEqual(str(e), "task not found")


class TestTaskCollectionRetrieve(unittest.TestCase, Initialize):
    def setUp(self):
        Initialize.setUp(self)
        self.plc1 = PLCDataBuilder().add_type("PLC!!!!").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            8080).add_count_pin_in(
            10).add_count_pin_out(10).add_count_total_pin(20).add_uuid().data
        self.plc1_id = self.plc1["_id"]
        self.plc_collection.insert_one(self.plc1)
        self.pin1 = PinDataBuilder().add_uuid().add_plc_id(self.plc1_id).add_type("in").add_id(1).data
        self.pin_collection.insert_one(self.pin1)

        self.task1 = TaskDataBuilder().add_name("task1").add_description("task1").add_plc_id(self.plc1_id).add_pin_ids(
            [1, 2, 3]).add_uuid().data  # 200
        self.task1_id = self.task1["_id"]

    def tearDown(self) -> None:
        self.db_client.drop_database(os.getenv("TEST_DB_NAME"))

    def test_retrieve_valid_date(self):
        self.collection.insert_one(self.task1)
        self.obj_task.retrieve()
        find_data = self.collection.find_one({"_id": self.task1_id}, {"_id": 0})
        self.assertIsNotNone(find_data)

    def test_retrieve_not_found(self):
        try:
            self.obj_task.retrieve()
        except Exception as e:
            self.assertIsInstance(e, CustomException404)
            self.assertEqual(str(e), "task not found")


class TestTaskCollectionDetail(unittest.TestCase, Initialize):
    def setUp(self):
        Initialize.setUp(self)
        self.plc1 = PLCDataBuilder().add_type("PLC!!!!").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            8080).add_count_pin_in(
            10).add_count_pin_out(10).add_count_total_pin(20).add_uuid().data
        self.plc1_id = self.plc1["_id"]
        self.plc_collection.insert_one(self.plc1)
        self.pin1 = PinDataBuilder().add_uuid().add_plc_id(self.plc1_id).add_type("in").add_id(1).data
        self.pin_collection.insert_one(self.pin1)

        self.task1 = TaskDataBuilder().add_name("task1").add_description("task1").add_plc_id(self.plc1_id).add_pin_ids(
            [1, 2, 3]).add_uuid().data  # 200
        self.task1_id = self.task1["_id"]

    def tearDown(self) -> None:
        self.db_client.drop_database(os.getenv("TEST_DB_NAME"))

    def test_detail_valid_date(self):
        self.collection.insert_one(self.task1)
        self.obj_task.detail(id=self.task1_id)
        find_data = self.collection.find_one({"_id": self.task1_id}, {"_id": 0})
        self.assertIsNotNone(find_data)

    def test_detail_not_found(self):
        try:
            self.obj_task.detail(id="1")
        except Exception as e:
            self.assertIsInstance(e, CustomException404)
            self.assertEqual(str(e), "task not found")
