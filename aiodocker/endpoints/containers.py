from aiodocker.formatters import from_containers
from aiodocker.formatters import from_container_inspect
from aiodocker.formatters import from_container_top
from aiodocker.formatters import to_container_config
from aiodocker.exceptions import ServerError, UnexpectedError, ConflictError
from aiodocker.exceptions import NotFound, NotRunning, ValidationError
from aiodocker.util import task
from aiodocker.util import read_stream
from copy import copy
import asyncio
import json
import logging

log = logging.getLogger(__name__)


class ContainersEndpoint:

    def __init__(self, api):
        self.api = api

    @task
    def items(self, *, status=None):
        """List containers.
        Parameters:
            status (int, str): a status. one of restarting, running, paused or
                               exited. if int, it is the exit code
        """
        path = '/containers/json'
        params = {
            'all': False,
            'size': True
        }
        if status == 'all':
            params['all'] = True
        elif status in ('restarting', 'running', 'paused', 'exited'):
            params['all'] = False
            params['filters'] = {'status': [status]}
        elif isinstance(status, int):
            params['all'] = False
            params['filters'] = {'exited': [status]}
        else:
            params['all'] = False

        response = yield from self.api.get(path, params=params)
        if response.status == 200:
            data = yield from response.json()
            return from_containers(data)

        data = yield from response.text()
        if response.status == 400:
            raise ValidationError(data)
        elif response.status == 500:
            raise ServerError(data)
        raise UnexpectedError(response.status, data)

    @task
    def create(self, name, **config):
        """Create a container
        """
        path = '/containers/create'
        params = {
            'name': name
        }
        data = to_container_config(config)
        data.setdefault('AttachStdin', True)
        data.setdefault('AttachStdout', True)
        data.setdefault('AttachStderr', True)
        data.setdefault('Tty', False)
        data.setdefault('OpenStdin', True)
        data.setdefault('Cmd', '/bin/bash')
        headers = {
            'Content-Type': 'application/json'
        }
        response = yield from self.api.post(path,
                                            params=params,
                                            data=json.dumps(data),
                                            headers=headers)
        if response.status == 201:
            data = yield from response.json()
            for warn in (data.get('Warnings') or []):
                log.warn(warn)
            return data['Id']

        data = yield from response.text()
        if response.status == 404:
            raise NotFound(data)
        elif response.status == 406:
            raise NotRunning(data)
        elif response.status == 409:
            raise ConflictError(data)
        elif response.status == 500:
            raise ServerError(data)
        raise UnexpectedError(response.status, data)

    @task
    def inspect(self, ref):
        path = '/containers/%s/json' % ref

        response = yield from self.api.get(path)
        if response.status == 200:
            data = yield from response.json()
            return from_container_inspect(data)

        data = yield from response.text()
        if response.status == 404:
            raise NotFound(data)
        elif response.status == 500:
            raise ServerError(data)
        raise UnexpectedError(response.status, data)

    get = inspect

    @task
    def top(self, ref, *, ps_args=None):
        path = '/containers/%s/top' % ref
        params = {
            'ps_args': ps_args
        }

        response = yield from self.api.get(path, params=params)
        if response.status == 200:
            data = yield from response.json()
            return from_container_top(data)

        data = yield from response.text()
        if response.status == 404:
            raise NotFound(data)
        elif response.status == 500:
            raise ServerError(data)
        raise UnexpectedError(response.status, data)

    def log(self, ref, *, stdout=None, stderr=None):
        """
        Returns:
            ContainerLog: iterable through latest logs
        """
        return ContainerLog(self.api, ref, stdout=stdout, stderr=stderr)

    @task
    def changes(self, ref):
        path = '/containers/%s/changes' % ref

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
    def export(self, ref):
        path = '/containers/%s/export' % ref
        # response = yield from self.api.get(path)
        raise NotImplementedError()

    @task
    def stats(self, ref):
        path = '/containers/%s/stats' % ref

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
    def resize_tty(self, ref, *, height, width):
        path = '/containers/%s/resize' % ref
        params = {
            'h': height,
            'w': width,
        }

        response = yield from self.api.post(path, params=params)
        if response.status == 200:
            return True

        data = yield from response.text()
        if response.status == 404:
            raise NotFound(data)
        elif response.status == 500:
            raise ServerError(data)
        raise UnexpectedError(response.status, data)

    @task
    def start(self, ref):
        """
        Returns
            bool: True if started, false if already started
        """
        path = '/containers/%s/start' % ref
        response = yield from self.api.post(path)
        if response.status == 204:
            return True
        elif response.status == 304:
            return False

        data = yield from response.text()
        if response.status == 404:
            raise NotFound(data)
        elif response.status == 500:
            raise ServerError(data)
        raise UnexpectedError(response.status, data)

    @task
    def stop(self, ref, *, wait=None):
        """
        Returns
            bool: True if stoped, false if already stoped
        """
        path = '/containers/%s/stop' % ref
        params = {
            't': wait,
        }
        response = yield from self.api.post(path, params=params)
        if response.status == 204:
            return True
        elif response.status == 304:
            return False

        data = yield from response.text()
        if response.status == 404:
            raise NotFound(data)
        elif response.status == 500:
            raise ServerError(data)
        raise UnexpectedError(response.status, data)

    @task
    def restart(self, ref, *, wait=None):
        path = '/containers/%s/restart' % ref
        params = {
            't': wait,
        }
        response = yield from self.api.post(path, params=params)
        if response.status == 204:
            return True

        data = yield from response.text()
        if response.status == 404:
            raise NotFound(data)
        elif response.status == 500:
            raise ServerError(data)
        raise UnexpectedError(response.status, data)

    @task
    def kill(self, ref, *, signal=None):
        path = '/containers/%s/kill' % ref
        params = {
            'signal': signal,
        }
        response = yield from self.api.post(path, params=params)
        if response.status == 204:
            return True

        data = yield from response.text()
        if response.status == 404:
            raise NotFound(data)
        elif response.status == 500:
            raise ServerError(data)
        raise UnexpectedError(response.status, data)

    @task
    def rename(self, ref, *, name):
        path = '/containers/%s/rename' % ref
        params = {
            'name': name,
        }
        response = yield from self.api.post(path, params=params)
        if response.status == 204:
            return True

        data = yield from response.text()
        if response.status == 404:
            raise NotFound(data)
        elif response.status == 409:
            raise ValidationError(data)
        elif response.status == 500:
            raise ServerError(data)
        raise UnexpectedError(response.status, data)

    @task
    def pause(self, ref):
        path = '/containers/%s/pause' % ref
        response = yield from self.api.post(path)
        if response.status == 204:
            return True

        data = yield from response.text()
        if response.status == 404:
            raise NotFound(data)
        elif response.status == 500:
            raise ServerError(data)
        raise UnexpectedError(response.status, data)

    @task
    def unpause(self, ref):
        path = '/containers/%s/unpause' % ref
        response = yield from self.api.post(path)
        if response.status == 204:
            return True

        data = yield from response.text()
        if response.status == 404:
            raise NotFound(data)
        elif response.status == 500:
            raise ServerError(data)
        raise UnexpectedError(response.status, data)

    @task
    def attach(self, ref):
        path = '/containers/%s/attach' % ref
        # response = yield from self.api.post(path)
        raise NotImplementedError()

    @task
    def wait(self, ref):
        path = '/containers/%s/wait' % ref
        response = yield from self.api.post(path)
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
    def remove(self, ref, *, also_volumes=False, force=False):
        path = '/containers/%s' % ref
        params = {
            'v': also_volumes,
            'force': force
        }
        response = yield from self.api.delete(path, params=params)
        if response.status == 204:
            return True
        elif response.status == 404:
            return False

        data = yield from response.text()
        if response.status == 400:
            raise ValidationError(data)
        elif response.status == 409:
            raise ConflictError(data)
        elif response.status == 500:
            raise ServerError(data)
        raise UnexpectedError(response.status, data)

    delete = remove

    @task
    def copy(self, ref, *, resource):
        path = '/containers/%s' % ref
        data = {
            'Resource': resource
        }
        # response = yield from self.api.delete(path, data=json.dumps(data))
        raise NotImplementedError()


class ContainerLog:

    def __init__(self, api, ref, *, stdout=None, stderr=None):
        self.api = api
        self.ref = ref
        self.stdout = stdout
        self.stderr = stderr
        self._tail = 'all'

    @asyncio.coroutine
    def __iter__(self):

        path = '/containers/%s/logs' % self.ref
        params = {
            'stdout': self.stdout,
            'stderr': self.stderr,
            'timestamps': True,
            'tail': self._tail
        }

        response = yield from self.api.get(path, params=params)
        if response.status == 200:
            data = yield from response.text()
            return read_stream(response)
            # return iter(data.split('\n'))

        data = yield from response.text()
        if response.status == 404:
            raise NotFound(data)
        elif response.status == 500:
            raise ServerError(data)
        raise UnexpectedError(response.status, data)

    def __getitem__(self, item):
        if isinstance(item, slice):
            start, stop, step = item.start, item.stop, item.stop
            if start > 0:
                raise ValidationError('start must be negative')
            if stop is not None:
                raise ValidationError('stop cannot be set')
            if step is not None:
                raise ValidationError('step cannot be set')
            return self.tail(abs(start))
        raise ValidationError('cannot get an item')

    def tail(self, count):
        instance = copy(self)
        instance._tail = count
        return instance

    def follow(self):
        # TODO finish logs, with log follows
        raise NotImplementedError()


class ContainerExec:

    def __init__(self, api, ref, *, stdout=None, stderr=None):
        self.api = api
        self.ref = ref

    def start(self):
        """docstring for start"""
        pass
