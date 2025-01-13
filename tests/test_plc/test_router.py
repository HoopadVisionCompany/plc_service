import unittest
import sys
import os
import time
from fastapi.testclient import TestClient

sys.path.append('..')

from main import app_gate

from src.controller_backend.service import PLCCollectionCreator
from src.database.db import DbBuilder
from src.utils.patterns.builders import PLCDataBuilder

client = TestClient(app_gate)


class Initialize:
    def setUp(self):
        self.db = DbBuilder().db
        self.db_client = DbBuilder().db_client
        self.obj = PLCCollectionCreator().create_collection()
        self.collection = self.db["plc_collection"]


class TestListPLC(unittest.TestCase, Initialize):
    def setUp(self) -> None:
        Initialize.setUp(self)
        self.data1 = PLCDataBuilder().add_type("DELTA").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            3030).add_count_pin_out(10).add_count_pin_in(10).add_count_total_pin(20).data
        self.data2 = PLCDataBuilder().add_type("DELTA").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            3031).add_count_pin_out(10).add_count_pin_in(10).add_count_total_pin(20).data

    def tearDown(self) -> None:
        print("in tear down")
        self.db_client.drop_database(os.getenv("TEST_DB_NAME"))

    def test_list_plc_valid(self):
        self.obj.insert(self.data1)
        self.obj.insert(self.data2)

        response = client.get('/controller_backend/list')
        self.assertEqual(response.status_code, 200)

    def test_list_plc_empty(self):
        response = client.get('/controller_backend/list')
        self.assertEqual(response.status_code, 404)


class TestDetailPLC(unittest.TestCase, Initialize):
    def setUp(self) -> None:
        Initialize.setUp(self)
        self.data1 = PLCDataBuilder().add_type("DELTA").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            3030).add_count_pin_out(10).add_count_pin_in(10).add_count_total_pin(20).add_uuid().data
        self.collection.insert_one(self.data1)
        self.id1 = self.data1["_id"]

    def tearDown(self) -> None:
        print("in tear down")
        self.db_client.drop_database(os.getenv("TEST_DB_NAME"))

    def test_detail_plc_valid(self):
        response = client.get(f'/controller_backend/detail/{self.id1}')
        self.assertEqual(response.status_code, 200)

    def test_detail_plc_invalid_id(self):
        response = client.get('/controller_backend/detail/1')
        self.assertEqual(response.status_code, 404)


class TestInsertPLC(unittest.TestCase, Initialize):
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

    def test_insert_plc_valid_data(self):
        response = client.post('/controller_backend/insert', json=self.data1)
        self.assertEqual(response.status_code, 200)

    def test_insert_plc_invalid_data_add_count_pin_in(self):
        response = client.post('/controller_backend/insert', json=self.data2)
        self.assertEqual(response.status_code, 422)

    def test_insert_plc_invalid_data_add_count_pin_out(self):
        response = client.post('/controller_backend/insert', json=self.data3)
        self.assertEqual(response.status_code, 422)

    def test_insert_plc_invalid_data_ip(self):
        response = client.post('/controller_backend/insert', json=self.data4)
        self.assertEqual(response.status_code, 422)

    def test_insert_plc_duplicate(self):
        self.obj.insert(self.data1)
        response = client.post('/controller_backend/insert', json=self.data5_1)
        self.assertEqual(response.status_code, 500)


class TestUpdatePLC(unittest.TestCase, Initialize):
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

    def test_update_plc_valid_data(self):
        self.collection.insert_one(self.data1)
        response = client.patch(f'/controller_backend/update/{self.data1_id}', json=self.data2)
        self.assertEqual(response.status_code, 200)

    def test_update_plc_invalid_data_add_count_pin_in(self):
        self.collection.insert_one(self.data1)
        response = client.patch(f'/controller_backend/update/{self.data1_id}', json=self.data3)
        self.assertEqual(response.status_code, 422)

    def test_update_plc_invalid_data_add_count_pin_out(self):
        self.collection.insert_one(self.data1)
        response = client.patch(f'/controller_backend/update/{self.data1_id}', json=self.data4)
        self.assertEqual(response.status_code, 422)

    def test_update_plc_duplicate(self):
        self.collection.insert_one(self.data1)
        self.collection.insert_one(self.data5)
        response = client.patch(f'/controller_backend/update/{self.data5_id}', json=self.data5_1)
        self.assertEqual(response.status_code, 500)


class TestDeletePLC(unittest.TestCase, Initialize):
    def setUp(self) -> None:
        Initialize.setUp(self)
        self.data1 = PLCDataBuilder().add_type("PLC!!!!").add_protocol("TCP").add_ip("0.0.0.0").add_port(
            8080).add_count_pin_in(
            10).add_count_pin_out(10).add_count_total_pin(20).add_uuid().data
        self.data1_id = self.data1["_id"]

    def tearDown(self) -> None:
        print("in tear down")
        self.db_client.drop_database(os.getenv("TEST_DB_NAME"))

    def test_delete_plc_valid_data(self):
        self.collection.insert_one(self.data1)
        response = client.delete(f'/controller_backend/delete/{self.data1_id}')
        self.assertEqual(response.status_code, 204)

    def test_delete_plc_notfound_data(self):
        self.collection.insert_one(self.data1)
        response = client.delete('/controller_backend/delete/1')
        self.assertEqual(response.status_code, 404)
