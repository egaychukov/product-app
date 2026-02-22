class NotFoundError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class ForbiddenError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class BadRequestError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
