import asyncio
import pytest
from aiodocker import Docker
from aiodocker import ConflictError, NotFound
from conftest import async_test


@async_test
def test_execute():
    client = Docker.local_client()
    conf = {
        'name': 'aio-1',
        'image': 'gliderlabs/alpine:3.1',
        'command': ['sleep', '60']
    }

    with pytest.raises(NotFound):
        yield from client.containers.get('aio-1')

    container_id = yield from client.containers.create(**conf)
    assert container_id

    started = yield from client.containers.start(container_id)
    assert started

    # the real test starts now

    exec_id = yield from client.executors.create(container_id, cmd=[
        'echo', 'FOOBAR'
    ])

    yield from client.executors.start(exec_id)

    results = yield from client.executors.inspect(exec_id)
    print(started, results)

    # end of the test

    stoped = yield from client.containers.stop(container_id)
    assert stoped, 'Should be stoped'

    deleted = yield from client.containers.delete(container_id)
    assert not deleted, 'Should be already deleted'
    assert False
