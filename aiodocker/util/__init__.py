from .async import *  # noqa
from .config import * # noqa
from .files import *  # noqa
from .names import *  # noqa


class lazy_property:
    """
    meant to be used for lazy evaluation of an object attribute.
    property should represent non-mutable data, as it replaces itself.
    """

    def __init__(self, fget):
        self.fget = fget
        self.func_name = fget.__name__
        self.__name__ = fget.__name__
        self.__doc__ = fget.__doc__

    def __get__(self, obj, cls):
        if obj:
            value = self.fget(obj)
            setattr(obj, self.func_name, value)
            return value
        return self


class StandardIn(str):
    pass


class StandardOut(str):
    pass


class StandardError(str):
    pass
