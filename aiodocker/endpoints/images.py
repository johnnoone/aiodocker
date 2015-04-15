from aiodocker.util import task
from aiodocker.exceptions import NotFound, ConflictError, BuildError
from aiodocker.exceptions import ServerError, UnexpectedError
from aiodocker.exceptions import ValidationError
from aiodocker.formatters import from_images, from_history
from aiodocker.helpers import stream_raw_json
from aiodocker.util import parse_name, make_dockerfile
import json
import logging
import re

log = logging.getLogger(__name__)


class ImagesEndpoint:

    def __init__(self, client):
        self.api = client

    @task
    def items(self, *, status=None):
        path = '/images/json'
        params = {
            'all': False
        }
        if status == 'dangling':
            params['filters'] = json.dumps({'dangling': True})

        response = yield from self.api.get(path, params=params)
        if response.status == 200:
            data = yield from response.json()
            return from_images(data)

        data = yield from response.text()
        raise UnexpectedError(response.status, data)

    @task
    def build(self, name, *, src, quiet=False):
        """
        Returns:
            str: the new image id
        Raises:
            BuildError: the error
        """
        path = '/build'
        headers = {}
        params = {
            't': name,
            'q': quiet
        }

        reader = yield from make_dockerfile(src)
        data = reader.content
        if reader.encoding:
            headers['Encoding'] = reader.encoding

        if reader.content_type:
            headers['Content-Type'] = reader.content_type

        response = yield from self.api.post('/build',
                                            params=params,
                                            headers=headers,
                                            data=data)
        if response.status == 200:
            image_id = None
            PATTERN = re.compile('Successfully built (?P<image_id>[0-9a-f]+)')
            for data in (yield from stream_raw_json(response)):
                log.info(data)
                if 'error' in data:
                    raise BuildError(data)
                if 'stream' in data:
                    data = data['stream']
                    match = PATTERN.search(data)
                    if match:
                        image_id = match.group('image_id')
            return image_id

            raise NotImplementedError()

        data = yield from response.text()
        if response.status == 500:
            raise ServerError(data)
        raise UnexpectedError(response.status, data)

    @task
    def create(self):
        path = '/images/create'
        raise NotImplementedError()

    @task
    def inspect(self, ref):
        path = '/images/%s/json' % ref

        response = yield from self.api.get(path)
        if response.status == 200:
            data = yield from response.json()
            return data

        data = yield from response.text()
        if response.status == 404:
            raise NotFound(data)
        elif response.status == 500:
            raise ServerError(data)
        raise UnexpectedError(response.status, data)

    @task
    def history(self, ref):
        path = '/images/%s/history' % ref

        response = yield from self.api.get(path)
        if response.status == 200:
            data = yield from response.json()
            return from_history(data)

        data = yield from response.text()
        if response.status == 404:
            raise NotFound(data)
        elif response.status == 500:
            raise ServerError(data)
        raise UnexpectedError(response.status, data)

    @task
    def push(self, ref):
        path = '/images/%s/push' % ref
        raise NotImplementedError()

    @task
    def tag(self, ref, *, repository, tag=None, force=False):
        if tag and ':' in ref:
            raise ValidationError('tag cannot be declared '
                                  'into image and tag parameters')
        elif tag is None:
            ref, tag = parse_name(ref)
        if not tag:
            raise ValidationError('tag is required')

        path = '/images/%s/tag' % ref
        params = {
            'tag': tag,
            'repo': repository,
            'force': force
        }

        response = yield from self.api.post(path, params=params)
        if response.status == 201:
            return True

        data = yield from response.text()
        if response.status == 400:
            raise ValidationError(data)
        if response.status == 404:
            raise NotFound(data)
        elif response.status == 409:
            raise ConflictError(data)
        elif response.status == 500:
            raise ServerError(data)
        raise UnexpectedError(response.status, data)

    @task
    def delete(self, ref, *, noprune=False, force=False):
        """
        Returns:
            bool: True if deleted, False if not found
        """
        path = '/images/%s' % ref
        params = {
            'noprune': noprune,
            'force': force
        }

        response = yield from self.api.delete(path, params=params)
        if response.status == 200:
            return True
        elif response.status == 404:
            return False

        data = yield from response.text()
        if response.status == 409:
            raise ConflictError(data)
        elif response.status == 500:
            raise ServerError(data)
        raise UnexpectedError(response.status, data)
