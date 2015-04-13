import asyncio
import json
import logging
import os
import os.path
import pytest
import sys
from aioconsul import Consul
from functools import wraps
from subprocess import Popen, PIPE
from time import sleep

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

HERE = os.path.dirname(os.path.abspath(__file__))


def async_test(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)
        pending = asyncio.Task.all_tasks()
        if pending:
            loop.run_until_complete(asyncio.wait(pending))
    return wrapper
