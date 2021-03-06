import pytest
from aiodocker import Docker
from aiodocker import ConflictError, NotFound
from conftest import async_test


@async_test
def test_conflict():
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

    data_1 = yield from client.containers.get('aio-1')
    data_2 = yield from client.containers.get(container_id)

    assert data_1 == data_2, 'Fetch by name or id must returns same data'
    assert data_1['id'] == container_id

    # Cannot create container with the same name
    with pytest.raises(ConflictError):
        yield from client.containers.create(**conf)

    c1 = containers = yield from client.containers.items(status='all')
    assert {'id': container_id} in containers, 'Must match by id'

    c2 = containers = yield from client.containers.items(status='running')
    assert {'id': container_id} not in containers, 'Must not be running'

    c3 = containers = yield from client.containers.items(status='exited')
    assert {'id': container_id} in containers, 'Must be exited'

    started = yield from client.containers.start(container_id)
    assert started

    started = yield from client.containers.start(container_id)
    assert not started

    # Cannot delete running container
    with pytest.raises(ConflictError):
        yield from client.containers.delete(container_id)

    stoped = yield from client.containers.stop(container_id)
    assert stoped, 'Should be stoped'

    stoped = yield from client.containers.stop(container_id)
    assert not stoped, 'Should be already stoped'

    deleted = yield from client.containers.delete(container_id)
    assert deleted, 'Should be deleted'

    deleted = yield from client.containers.delete(container_id)
    assert not deleted, 'Should be already deleted'
