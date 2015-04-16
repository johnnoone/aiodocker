

class ValidationError(Exception):
    pass


class ServerError(Exception):
    pass


class UnexpectedError(Exception):
    pass


class NotFound(Exception):
    """Raised when image or container was not found"""
    pass


class CreateError(Exception):
    """Raised when image was not created"""
    pass


class NotRunning(Exception):
    """Raised when image or container was not running"""
    pass


class ConflictError(Exception):
    """Raised when image conflicts with another"""
    pass


class BuildError(Exception):
    """Raised when image failed to build"""
    pass


class CompareError(ValueError):
    """Raised when comparing objects"""
    pass


class SparseError(ValueError):
    """Raised when comparing sparse objects"""
    pass
