from functools import partial, wraps
import asyncio
import inspect


def task(func=None, *, loop=None):
    """Transforms func into an asyncio task."""

    if not func:
        if not loop:
            raise ValueError('loop is required')
        return partial(task, loop=loop)

    if getattr(func, '_is_task', False):
        return func

    coro = asyncio.coroutine(func)

    if inspect.ismethod(func):
        @wraps(func)
        def wrapper(self, *arg, **kwargs):
            l = loop or self.loop
            return asyncio.async(coro(self, *arg, **kwargs), loop=l)
    else:
        @wraps(func)
        def wrapper(*arg, **kwargs):
            return asyncio.async(coro(*arg, **kwargs), loop=loop)
    wrapper._is_task = True
    return wrapper


def mark_task(func):
    """Mark function as a defacto task (for documenting purpose)"""
    func._is_task = True
    return func
