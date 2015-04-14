import asyncio
import json


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
