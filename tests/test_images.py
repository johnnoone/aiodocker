import pytest
from aiodocker import Docker
from conftest import async_test


@async_test
def test_delete():
    client = Docker.local_client()
    images = yield from client.images.items()
    for image in images:
        if '<none>:<none>' in image['repo_tags']:
            deleted = yield from client.images.delete(image['id'], force=True)
            assert deleted, 'cannot remove image'


@async_test
def test_pull():
    client = Docker.local_client()
    images = yield from client.images.items()
