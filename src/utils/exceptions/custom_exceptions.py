class CustomException404(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class CustomException401(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class CustomException400(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
