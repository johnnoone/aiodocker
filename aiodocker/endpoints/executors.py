from aiodocker.util import task
from aiodocker.exceptions import NotFound
from aiodocker.exceptions import ServerError, UnexpectedError
from aiodocker.formatters import from_exec_inspect
from aiodocker.helpers import stream_raw
import json
import logging

log = logging.getLogger(__name__)


class ExecEndpoint:

    def __init__(self, api):
        self.api = api

    @task
    def create(self, ref, *, cmd):
        path = '/containers/%s/exec' % ref
        data = {
            'AttachStdin': False,
            'AttachStdout': True,
            'AttachStderr': True,
            'Tty': False,
            'Cmd': cmd
        }
        headers = {
            'Content-Type': 'application/json'
        }

        response = yield from self.api.post(path,
                                            headers=headers,
                                            data=json.dumps(data))
        if response.status == 201:
            data = yield from response.json()
            executor = data['Id']
            return executor

        data = yield from response.text()
        if response.status == 404:
            raise NotFound(data)
        elif response.status == 500:
            raise ServerError(data)
        raise UnexpectedError(response.status, data)

    @task
    def start(self, exec_id):
        path = '/exec/%s/start' % exec_id
        data = {
            'Detach': False,
            'Tty': False
        }
        headers = {
            'Content-Type': 'application/json'
        }

        response = yield from self.api.post(path,
                                            headers=headers,
                                            data=json.dumps(data))

        if response.status in (200, 201):
            for data in (yield from stream_raw(response)):
                log.info(data)
            return
        data = yield from response.text()
        if response.status == 404:
            raise NotFound(data)
        elif response.status == 500:
            raise ServerError(data)
        raise UnexpectedError(response.status, data)

    @task
    def start_detached(self, exec_id):
        path = '/exec/%s/start' % exec_id
        data = {
            'Detach': True,
            'Tty': False
        }
        headers = {
            'Content-Type': 'application/json'
        }

        response = yield from self.api.post(path,
                                            headers=headers,
                                            data=json.dumps(data))

        if response.status == 204:
            return True
        data = yield from response.text()
        if response.status == 404:
            raise NotFound(data)
        elif response.status == 500:
            raise ServerError(data)
        raise UnexpectedError(response.status, data)

    @task
    def inspect(self, exec_id):
        path = '/exec/%s/json' % exec_id

        response = yield from self.api.get(path)
        if response.status == 200:
            data = yield from response.json()
            return from_exec_inspect(data)

        data = yield from response.text()
        if response.status == 404:
            raise NotFound(data)
        elif response.status == 500:
            raise ServerError(data)
        raise UnexpectedError(response.status, data)
