from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

from starlette.requests import Request

from src.utils.patterns.exception_chain_handler import ExceptionHandler
from src.utils.handlers.exception_handlers import (
    ValidationErrorException,
    ValueErrorException,
    CustomException400Exception,
    CustomException404Exception,
    CustomException401Exception,
    CustomException500Exception
)


class ExceptionMiddleware(BaseHTTPMiddleware):
    def create_exception_chain(self) -> ExceptionHandler:
        exception_chain = ExceptionHandler()
        exception_chain.set_handler(ValidationErrorException()).set_handler(ValueErrorException()).set_handler(
            CustomException404Exception()).set_handler(CustomException401Exception()).set_handler(CustomException400Exception()).set_handler(CustomException500Exception())
        return exception_chain

    async def dispatch(self, request: Request, call_next) -> StreamingResponse:
        exception_chain = self.create_exception_chain()

        try:
            response = await call_next(request)

        except Exception as e:
            response = exception_chain.handle_exception(e)

        return response
