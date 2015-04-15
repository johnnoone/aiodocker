import pytest
from aiodocker import Docker
from aiodocker import ConflictError
from conftest import async_test


@async_test
def test_search():
    # TODO mock result
    client = Docker()
    info = yield from client.docker_hub.search('ubuntu')
    assert info[0].name == 'ubuntu'


@async_test
def test_pull():
    client = Docker()

    ref = 'gliderlabs/alpine:2.6'

    pulled = yield from client.docker_hub.pull(ref)
    assert pulled, 'Should download gliderlabs/alpine:2.6'

    # is it present locally?
    image = yield from client.images.inspect(ref)
    assert image

    # start a new container with this image
    container_id = yield from client.containers.create(**{
        'name': 'aio-2',
        'image': 'gliderlabs/alpine:2.6',
        'command': ['echo', 'bar']
    })
    assert container_id

    started = yield from client.containers.start(container_id)
    assert started

    pulled = yield from client.docker_hub.pull(ref)
    assert pulled, 'Should still download gliderlabs/alpine:2.6'

    with pytest.raises(ConflictError):
        destroyed = yield from client.images.delete(ref)
        assert not destroyed, 'Should not allow destroy'

    removed = yield from client.containers.remove(container_id)
    assert removed, 'Should remove container'

    images = yield from client.images.items()
    assert {'repo_tags': [ref]} in images, 'Should be present'

    destroyed = yield from client.images.delete(ref)
    assert destroyed, 'Should be destroyed'

    images = yield from client.images.items()
    assert {'repo_tags': [ref]} not in images, 'Should be absent'
