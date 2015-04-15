import asyncio
import json
import struct


@asyncio.coroutine
def stream_json(response):
    # TODO find a way to do this better, because results can became really huge
    results = []
    if response.headers['Transfer-Encoding'] == 'chunked':
        # this is a stream
        stream = response.content
        buff = ''
        while not stream.at_eof():
            buff += (yield from stream.read(1)).decode('utf-8')
            try:
                data = json.loads(buff)
                results.append(data)
            except ValueError:
                continue
            else:
                buff = ''
    else:
        data = yield from response.json()
        results.append(data)
    return results


@asyncio.coroutine
def stream_raw(response):
    # TODO find a way to do this better, because results can became really huge
    results = []
    content_type = response.headers['Content-Type']
    content = response.content
    while not content.at_eof():
        header = yield from content.read(8)
        type, length = struct.unpack('>BxxxL', header)
        data = yield from content.read(length)

        name = {0: 'stdin', 1: 'stdout', 2: 'stderr'}.get(type, 'N/A')
        if content_type == 'application/vnd.docker.raw-stream':
            results.append({
                'type': name,
                'msg': str(data, 'utf-8')
            })
        elif content_type == 'application/json':
            results.append({
                'type': name,
                'payload': json.loads(str(data, 'utf-8'))
            })
        else:
            results.append({
                'type': name,
                'raw': str(data, 'utf-8')
            })
    return results


@asyncio.coroutine
def stream_raw_json(response):
    # TODO find a way to do this better, because results can became really huge
    results = []
    if response.headers['Transfer-Encoding'] == 'chunked':
        # this is a stream
        stream = response.content
        buff = ''
        while not stream.at_eof():
            buff += (yield from stream.read(1)).decode('utf-8')
            try:
                data = json.loads(buff)
                results.append(data)
            except ValueError:
                continue
            else:
                buff = ''
    else:
        data = yield from response.json()
        results.append(data)
    return results
