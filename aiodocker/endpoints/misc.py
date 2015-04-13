from aiodocker.util import task
from aiodocker.exceptions import UnexpectedError
from aiodocker.formatters import from_info, from_version
import logging

log = logging.getLogger(__name__)


class MiscEndpoint:

    def __init__(self, client):
        self.client = client

    @task
    def info(self):
        response = yield from self.client.get('info')
        if response.status == 200:
            data = yield from response.json()
            return from_info(data)
        data = yield from response.text()
        raise UnexpectedError(response.status, data)

    @task
    def version(self):
        response = yield from self.client.get('version')
        if response.status == 200:
            data = yield from response.json()
            return from_version(data)
        data = yield from response.text()
        raise UnexpectedError(response.status, data)

    @task
    def ping(self):
        response = yield from self.client.get('_ping')
        if response.status == 200:
            return True
        data = yield from response.text()
        raise UnexpectedError(response.status, data)
