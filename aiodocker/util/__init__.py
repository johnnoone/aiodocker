from .async import *  # noqa
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


def read_stream(response):
    content_type = response.headers['Content-Type']
    content = response.content
    while not content.at_eof():
        header = yield from content.read(8)
        type, length = struct.unpack('>BxxxL', header)
        data = yield from content.read(length)

        Class = {0: StandardIn, 1: StandardOut, 2: StandardError}.get(type)
        data = Class(data, 'utf-8')
        if content_type == 'application/vnd.docker.raw-stream':
            yield data
        elif content_type == 'application/json':
            yield data
        else:
            yield data


class StandardIn(str):
    pass


class StandardOut(str):
    pass


class StandardError(str):
    pass
