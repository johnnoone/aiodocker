import pytest
from aiodocker import Docker
from conftest import async_test


@async_test
def test_info():
    client = Docker.local_client()
    info = yield from client.info()
    assert 'containers' in info, 'must have containers key'


@async_test
def test_version():
    client = Docker.local_client()
    version = yield from client.version()
    assert client.api_version <= version['api_version'], 'api versions should be equals'


@async_test
def test_ping():
    client = Docker.local_client()
    assert (yield from client.ping())
