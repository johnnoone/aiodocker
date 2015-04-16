AIO Docker
==========

::

    from aiodocker import Docker
    client = Docker.local_client()

    # pull some images from dockerhub
    tasks = [
        client.docker_hub.pull('alpine:latest'),
        client.docker_hub.pull('ubuntu:latest'),
        client.docker_hub.pull('debian:latest')
    ]
    yield from asyncio.wait(tasks)

    # are they here ?
    for image in (yield from client.images.items()):
        print(image['names'])
