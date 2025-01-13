import sys
import unittest
from pydantic import ValidationError, BaseModel, Field
from fastapi import status, testclient
from fastapi.responses import JSONResponse

sys.path.append("..")
from src.utils.handlers.exception_handlers import (
    ValidationErrorException,
    ValueErrorException,
    CustomException404Exception
)
from src.utils.exceptions.custom_exceptions import CustomException404
from main import app_gate

client = testclient.TestClient(app_gate)


class MockBaseModel(BaseModel):
    id: int = Field(ge=1, le=2)


class TestValidationErrorException(unittest.TestCase):

    def test_exception_handler_validation_error(self):
        handler = ValidationErrorException()

        try:
            MockBaseModel(id="hello")
        except ValidationError as ve:
            response = handler.handle_exception(ve)
            self.assertIsInstance(response, JSONResponse)
            self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)


class TestValueErrorException(unittest.TestCase):
    def test_exception_handler_value_error(self):
        handler = ValueErrorException()
        try:
            MockBaseModel(id=10)
        except ValueError as ve:
            response = handler.handle_exception(ve)
            self.assertIsInstance(response, JSONResponse)
            self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)


class TestCustomException404Exception(unittest.TestCase):
    def test_exception_handler_custom_exception404(self):
        handler = CustomException404Exception()
        try:
            client.get("/controller_backend/detail/1")
        except CustomException404 as ce404:
            response = handler.handle_exception(ce404)
            self.assertIsInstance(response, JSONResponse)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestCustomException500Exception(unittest.TestCase):
    def setUp(self) -> None:
        self.data = {"type": "a",
                     "protocol": "b",
                     "ip": "0.0.0.0",
                     "port": 5000,
                     "count_pin_out": 10,
                     "count_pin_in": 10,
                     "count_total_pin": 20
                     }

        client.post("/controller_backend/insert", json=self.data)

    def tearDown(self):

        plcs = client.get("/controller_backend/list").json()
        for plc in plcs:
            client.delete(f"/controller_backend/delete/{plc['_id']}")

    def test_exception_handler_custom_exception500(self):
        handler = CustomException404Exception()
        try:

            client.post("/controller_backend/insert", json=self.data)
        except Exception as ce500:
            response = handler.handle_exception(ce500)
            self.assertIsInstance(response, JSONResponse)
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
