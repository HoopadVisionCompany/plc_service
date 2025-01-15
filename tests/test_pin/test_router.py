import time
import unittest
import sys
import os
import uuid
from fastapi.testclient import TestClient
from dotenv import load_dotenv
from main import app_gate

sys.path.append("..")
from src.pin.service import PinCollectionCreator, PinCollection
from src.database.db import DbBuilder
from src.utils.patterns.builders import PLCDataBuilder, PinDataBuilder
from src.controller_backend.service import PlcCollection, PLCCollectionCreator
from src.utils.exceptions.custom_exceptions import CustomException404
from pymongo.errors import DuplicateKeyError

load_dotenv()

client = TestClient(app_gate)


class Initialize:
    def setUp(self):
        self.db = DbBuilder().db
        self.db_client = DbBuilder().db_client
        self.obj_plc = PLCCollectionCreator().create_collection()
        self.obj_pin = PinCollectionCreator().create_collection()
        self.collection = self.db["pin_collection"]
        self.plc_collection = self.db["plc_collection"]


class TestInsertPin(unittest.TestCase, Initialize):
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
        response = client.post('/pin/insert', json=self.data1)
        self.assertEqual(response.status_code, 200)

    def test_insert_invalid_type(self):
        response = client.post('/pin/insert', json=self.data2)
        self.assertEqual(response.status_code, 422)

    def test_insert_invalid_id(self):
        response = client.post('/pin/insert', json=self.data3)
        self.assertEqual(response.status_code, 422)

    def test_insert_invalid_plc_id(self):
        response = client.post('/pin/insert', json=self.data4)
        self.assertEqual(response.status_code, 404)

    def test_insert_duplicate_data(self):
        self.obj_pin.insert(self.data1)
        response = client.post('/pin/insert', json=self.data5_1)
        self.assertEqual(response.status_code, 500)


class TestUpdatePin(unittest.TestCase, Initialize):
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
        response = client.patch(f"/pin/update/{self.data1_id}", json=self.data2)
        self.assertEqual(response.status_code, 200)

    def test_update_invalid_type(self):
        response = client.patch(f"/pin/update/{self.data1_id}", json=self.data3)
        self.assertEqual(response.status_code, 422)

    def test_update_invalid_id(self):
        response = client.patch(f"/pin/update/{self.data1_id}", json=self.data4)
        self.assertEqual(response.status_code, 422)

    def test_update_invalid_plc_id(self):
        response = client.patch(f"/pin/update/{self.data1_id}", json=self.data5)
        self.assertEqual(response.status_code, 404)

    def test_update_duplicate_data(self):
        self.data6["_id"] = str(uuid.uuid4())
        self.obj_pin.insert(self.data6)

        response = client.patch(f"/pin/update/{self.data1_id}", json=self.data6_1)
        self.assertEqual(response.status_code, 500)


class TestDeletePin(unittest.TestCase, Initialize):
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
        response = client.delete(f'/pin/delete/{self.data1_id}')
        self.assertEqual(response.status_code, 204)

    def test_delete_not_found(self):
        response = client.delete('/pin/delete/1')
        self.assertEqual(response.status_code, 404)


class TestRetrievePin(unittest.TestCase, Initialize):
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
        response = client.get("/pin/list")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(response.json(), [self.data1, self.data2])

    def test_retrieve_not_found(self):
        response = client.get("/pin/list")
        self.assertEqual(response.status_code, 404)


class TestDetailPin(unittest.TestCase, Initialize):
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
        response = client.get(f"/pin/detail/{self.data1_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json())

    def test_detail_not_found(self):
        response = client.get("/pin/detail/1")
        self.assertEqual(response.status_code, 404)
