from aiodocker.util import task
from aiodocker.exceptions import ServerError, UnexpectedError
from aiodocker.exceptions import NotFound, ConflictError, ValidationError
from aiodocker.formatters import from_images, from_history
import json
import logging

log = logging.getLogger(__name__)


class ImagesEndpoint:

    def __init__(self, client):
        self.client = client

    @task
    def items(self, *, status=None):
        path = '/images/json'
        params = {
            'all': False
        }
        if status == 'dangling':
            params['filters'] = json.dumps({'dangling': True})

        response = yield from self.client.get(path, params=params)
        if response.status == 200:
            data = yield from response.json()
            return from_images(data)

        data = yield from response.text()
        raise UnexpectedError(response.status, data)

    @task
    def build(self):
        path = '/build'
        raise NotImplementedError()

    @task
    def create(self):
        path = '/images/create'
        raise NotImplementedError()

    @task
    def inspect(self, ref):
        path = '/images/%s/json' % ref

        response = yield from self.client.get(path)
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

        response = yield from self.client.get(path)
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
    def tag(self, ref, *, tag, repository, force=False):
        path = '/images/%s/tag' % ref
        params = {
            'tag': tag,
            'repo': repository,
            'force': force
        }

        response = yield from self.client.post(path, params=params)
        if response.status == 201:
            return True

        data = yield from response.text()
        if response.status == 400:
            raise ValidationError(data)
        if response.status == 404:
            raise NotFound(data)
        if response.status == 409:
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

        response = yield from self.client.delete(path, params=params)
        if response.status == 200:
            return True
        elif response.status == 404:
            return False

        data = yield from response.text()
        if response.status == 500:
            raise ServerError(data)
        raise UnexpectedError(response.status, data)

    @task
    def search(self, ref, *, term):
        path = '/images/search'
        params = {
            'term': term
        }

        response = yield from self.client.get(path, params=params)
        if response.status == 200:
            data = yield from response.json()
            return data

        data = yield from response.text()
        if response.status == 500:
            raise ServerError(data)
        raise UnexpectedError(response.status, data)
