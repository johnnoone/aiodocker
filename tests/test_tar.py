import asyncio
import os.path
import pytest
from aiodocker import Docker
from conftest import async_test

@async_test
def test_tar():
    client = Docker.local_client()
    here = os.path.abspath(os.path.dirname(__file__))
    src = os.path.join(here, 'images', 'aio.tar')
    dest = os.path.join(here, 'images', 'aio.tar.bk')

    for i in range(4):
        with open(src, 'rb') as file:
            yield from client.images.load(file)

        images = yield from client.images.items()
        assert {'id': '017a8c79268d'} in images
        assert {'repo_tag': 'aio:latest'} in images
        if i % 2 == 0:
            deleted = yield from client.images.delete('aio:latest')
            assert deleted

    with open(dest, 'w') as file:
        yield from client.images.export('aio:latest', into=file)


    for i in range(4):
        with open(dest, 'rb') as file:
            yield from client.images.load(file)

        images = yield from client.images.items()
        assert {'id': '017a8c79268d'} in images
        assert {'repo_tag': 'aio:latest'} in images
        if i % 2 == 0:
            deleted = yield from client.images.delete('aio:latest')
            assert deleted
