from aiodocker.util import task
from aiodocker.exceptions import UnexpectedError
from aiodocker.formatters import from_info, from_version
import logging

log = logging.getLogger(__name__)


class MiscEndpoint:

    def __init__(self, client):
        self.api = client

    @task
    def info(self):
        response = yield from self.api.get('info')
        if response.status == 200:
            data = yield from response.json()
            return from_info(data)
        data = yield from response.text()
        raise UnexpectedError(response.status, data)

    @task
    def version(self):
        response = yield from self.api.get('version')
        if response.status == 200:
            data = yield from response.json()
            return from_version(data)
        data = yield from response.text()
        raise UnexpectedError(response.status, data)

    @task
    def ping(self):
        """
        Ping server.

        Returns
            bool: True if it's ok
        """
        response = yield from self.api.get('_ping')
        return response.status == 200
