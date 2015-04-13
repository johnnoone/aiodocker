

class ValidationError(Exception):
    pass


class ServerError(Exception):
    pass


class UnexpectedError(Exception):
    pass


class NotFound(Exception):
    """Raised when image or container was not found"""
    pass


class NotRunning(Exception):
    """Raised when image or container was not running"""
    pass


class ConflictError(Exception):
    """Raised when image conflicts with another"""
    pass
