from abc import ABC, abstractmethod
from pydantic import ValidationError
from fastapi.responses import JSONResponse
from fastapi import status
from src.utils.exceptions.custom_exceptions import CustomException404
from typing import Union


class ExceptionHandlerInterface(ABC):
    @abstractmethod
    def handle_exception(self, exception: Exception) -> Union[JSONResponse, None]:
        pass


class ValidationErrorException(ExceptionHandlerInterface):
    def handle_exception(self, exception: Exception) -> Union[JSONResponse, None]:
        if isinstance(exception, ValidationError):
            response = JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": exception.errors()}
            )
            return response
        return None


class ValueErrorException(ExceptionHandlerInterface):
    def handle_exception(self, exception: Exception) -> Union[JSONResponse, None]:
        if isinstance(exception, ValueError):
            response = JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={"detail": [{"msg": str(exception), "loc": ["Unknown"], "type": str(type(exception))}]},
            )
            return response
        return None


class CustomException404Exception(ExceptionHandlerInterface):
    def handle_exception(self, exception: Exception) -> Union[JSONResponse, None]:
        if isinstance(exception, CustomException404):
            response = JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": [{"msg": str(exception), "loc": ["Unknown"], "type": "Not Found Custom Exception"}]},
            )
            return response
        return None


class CustomException500Exception(ExceptionHandlerInterface):
    def handle_exception(self, exception: Exception) -> JSONResponse:
        response = JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": [{"msg": str(exception), "loc": ["Unknown"], "type": str(type(exception))}]},
        )
        return response
