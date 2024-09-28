from fastapi.responses import JSONResponse
from typing import List, Type
from src.utils.handlers.exception_handlers import ExceptionHandlerInterface


class ExceptionHandler:
    def __init__(self):
        self._handlers: List[Type[ExceptionHandlerInterface]] = []

    def set_handler(self, handler: Type[ExceptionHandlerInterface]) -> "ExceptionHandler":
        self._handlers.append(handler)
        return self

    def handle_exception(self, exception: Exception) -> JSONResponse:
        for handler in self._handlers:
            response = handler.handle_exception(exception)
            if isinstance(response, JSONResponse):
                return response
