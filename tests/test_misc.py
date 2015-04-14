import pytest
from aiodocker import Docker
from conftest import async_test


@async_test
def test_info():
    client = Docker()
    info = yield from client.info()
    assert 'containers' in info, 'must have containers key'


@async_test
def test_version():
    client = Docker()
    version = yield from client.version()
    assert client.api_version == version['api_version'], 'api versions should be equals'


@async_test
def test_ping():
    client = Docker()
    assert (yield from client.ping())
