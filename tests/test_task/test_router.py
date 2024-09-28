import unittest
import sys
import os
from fastapi.testclient import TestClient
from dotenv import load_dotenv

sys.path.append("..")
from src.task.service import TaskCollectionCreator, TaskCollection

from src.database.db import DbBuilder
from src.utils.patterns.builders import PLCDataBuilder, PinDataBuilder, TaskDataBuilder
from main import app_gate
from src.utils.exceptions.custom_exceptions import CustomException404
from pymongo.errors import DuplicateKeyError

load_dotenv()

client = TestClient(app_gate)


class Initialize:
    def setUp(self):
        self.db = DbBuilder().db
        self.db_client = DbBuilder().db_client
        self.obj_task = TaskCollectionCreator().create_collection()
        self.collection = self.db["task_collection"]
        self.pin_collection = self.db["pin_collection"]
        self.plc_collection = self.db["plc_collection"]


class TestTaskInsert(unittest.TestCase, Initialize):
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
        response = client.post('/task/insert', json=self.task1)
        self.assertEqual(response.status_code, 200)

    def test_insert_invalid_name(self):
        response = client.post('/task/insert', json=self.task2)
        self.assertEqual(response.status_code, 422)

    def test_insert_invalid_description(self):
        response = client.post('/task/insert', json=self.task3)
        self.assertEqual(response.status_code, 422)

    def test_insert_invalid_plc_id(self):
        response = client.post('/task/insert', json=self.task4)
        self.assertEqual(response.status_code, 404)

    def test_insert_invalid_pin_ids(self):
        response = client.post('/task/insert', json=self.task5)
        self.assertEqual(response.status_code, 404)

    def test_insert_duplicate_data(self):
        self.obj_task.insert(self.task1)
        response = client.post('/task/insert', json=self.task6_1)
        self.assertEqual(response.status_code, 500)


class TestTaskUpdate(unittest.TestCase, Initialize):
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
        response = client.patch(f'/task/update/{self.task1_id}', json=self.task0)
        self.assertEqual(response.status_code, 200)

    def test_update_invalid_name(self):
        response = client.patch(f'/task/update/{self.task1_id}', json=self.task2)
        self.assertEqual(response.status_code, 422)

    def test_update_invalid_description(self):
        response = client.patch(f'/task/update/{self.task1_id}', json=self.task3)
        self.assertEqual(response.status_code, 422)

    def test_update_invalid_plc_id(self):
        response = client.patch(f'/task/update/{self.task1_id}', json=self.task4)
        self.assertEqual(response.status_code, 404)

    def test_update_invalid_pin_ids(self):
        response = client.patch(f'/task/update/{self.task1_id}', json=self.task5)
        self.assertEqual(response.status_code, 404)

    def test_update_duplicate_data(self):
        self.obj_task.insert(self.task6)
        response = client.patch(f'/task/update/{self.task1_id}', json=self.task6)
        self.assertEqual(response.status_code, 500)


class TestTaskDelete(unittest.TestCase, Initialize):
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
        response = client.delete(f'/task/delete/{self.task1_id}')
        self.assertEqual(response.status_code, 204)

    def test_delete_not_found(self):
        response = client.delete('/task/delete/1')
        self.assertEqual(response.status_code, 404)


class TestTaskRetrieve(unittest.TestCase, Initialize):
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
        response = client.get('/task/list')
        self.assertEqual(response.status_code, 200)

    def test_retrieve_not_found(self):
        response = client.get('/task/list')
        self.assertEqual(response.status_code, 404)


class TestTaskDetail(unittest.TestCase, Initialize):
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
        response = client.get(f'/task/detail/{self.task1_id}')
        self.assertEqual(response.status_code, 200)

    def test_detail_not_found(self):
        response = client.get('/task/detail/1')
        self.assertEqual(response.status_code, 404)
