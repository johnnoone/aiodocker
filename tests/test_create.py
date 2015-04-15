import io
import pytest
from aiodocker import Docker
from aiodocker import BuildError
from conftest import async_test
from tempfile import NamedTemporaryFile


BUILD_ALPINE = """\
FROM gliderlabs/alpine:3.1
RUN echo "hello" > /tmp/foo
ENTRYPOINT ["cat", "/tmp/foo"]
"""


BUILD_ALPINE_FAIL = """\
FROM gliderlabs/alpine:3.1
RUN absolutelydummycommand
ENTRYPOINT ["areyouexperienced"]
"""


@async_test
def test_build_from_string_io():
    """build from StringIO"""
    client = Docker.local_client()
    src = io.StringIO(BUILD_ALPINE)
    image_id = yield from client.images.build('img-1:a', src=src)
    assert image_id is not None
    images = yield from client.images.items()
    assert {'id': image_id} in images
    yield from client.images.delete(image_id)


@async_test
def test_build_from_bytes_io():
    """build from BytesIO"""
    client = Docker.local_client()
    src = io.BytesIO(BUILD_ALPINE.encode('utf-8'))
    image_id = yield from client.images.build('img-1:b', src=src)
    assert image_id is not None
    images = yield from client.images.items()
    assert {'id': image_id} in images
    yield from client.images.delete(image_id)


@async_test
def test_dockerfile():
    client = Docker.local_client()
    file = NamedTemporaryFile()
    file.write(BUILD_ALPINE.encode('utf-8'))
    file.seek(0)
    src = file.name
    image_id = yield from client.images.build('img-1:c', src=src)
    assert image_id is not None
    images = yield from client.images.items()
    assert {'id': image_id} in images
    yield from client.images.delete(image_id)


@async_test
def test_failed_build():
    client = Docker.local_client()
    src = io.StringIO(BUILD_ALPINE_FAIL)
    with pytest.raises(BuildError):
        yield from client.images.build('img-1:d', src=src)
