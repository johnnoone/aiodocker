from aiodocker.util import task
from aiodocker.exceptions import NotFound, ConflictError, ValidationError
from aiodocker.exceptions import ServerError, UnexpectedError
from aiodocker.formatters import from_search_results
from aiodocker.helpers import stream_json
from aiodocker.util import parse_name
import logging


log = logging.getLogger(__name__)


class RegistryEndpoint:

    def __init__(self, api, *, registry):
        self.api = api
        self.registry = registry

    @task
    def pull(self, image, *, tag=None):
        """
        Pull image from registry.

        Parameters:
            image (str): in the form of {repo}:{tag}
            tag (str): optionnal. if not set,
                       it will use tag in image parameters
        """
        if tag and ':' in image:
            raise ValidationError('tag cannot be declared '
                                  'into image and tag parameters')
        elif tag is None:
            image, tag = parse_name(image)

        path = '/images/create'
        params = {
            'fromImage': image,
            'registry': self.registry,
        }
        if tag:
            params['tag'] = tag

        response = yield from self.api.post(path, params=params)
        if response.status == 200:
            for data in (yield from stream_json(response)):
                log.info(data)
            return True

        data = yield from response.text()
        if response.status == 500:
            raise ServerError(data)
        raise UnexpectedError(response.status, data)

    @task
    def push(self, image, *, tag=None):
        """
        Push image to registry.

        Parameters:
            image (str): in the form of {repo}:{tag}
            tag (str): optionnal. if not set,
                       it will use tag in image parameters
        """
        if tag and ':' in image:
            raise ValidationError('tag cannot be declared '
                                  'into image and tag parameters')
        elif tag is None:
            image, tag = parse_name(image)

        params = {}
        if tag:
            params['tag'] = tag

        if self.registry:
            path = '/images/%s/%s/push' % (self.registry, image)
        else:
            path = '/images/%s/push' % image

        response = yield from self.api.post(path, params=params)
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
    def tag(self, image, *, tag=None, force=False):
        """
        Tag image into registry.

        Parameters:
            image (str): in the form of {repo}:{tag}
            tag (str): optionnal. if not set,
                       it will use tag in image parameters
            force (bool): force tag even if conflicts?
        """
        if tag and ':' in image:
            raise ValidationError('tag cannot be declared '
                                  'into image and tag parameters')
        elif tag is None:
            image, tag = parse_name(image)

        path = '/images/%s/tag' % image
        params = {}
        if tag:
            params['tag'] = tag

        response = yield from self.api.post(path, params=params)
        if response.status == 201:
            return True

        data = yield from response.text()
        if response.status == 400:
            raise ValidationError(data)
        elif response.status == 404:
            raise NotFound(data)
        elif response.status == 409:
            raise ConflictError(data)
        elif response.status == 500:
            raise ServerError(data)
        raise UnexpectedError(response.status, data)


class DockerHubEndpoint(RegistryEndpoint):
    """
    https://hub.docker.com endpoint
    """

    def __init__(self, api):
        self.api = api
        self.registry = None

    @task
    def search(self, term):
        """Search for images"""
        path = '/images/search'
        params = {
            'term': term
        }

        response = yield from self.api.get(path, params=params)
        if response.status == 200:
            data = yield from response.json()
            return from_search_results(data)

        data = yield from response.text()
        if response.status == 500:
            raise ServerError(data)
        raise UnexpectedError(response.status, data)
