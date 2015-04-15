from . import endpoints
from .handlers import DockerHandler
from .util import lazy_property
import os

__all__ = ['Docker']


class Docker:

    def __init__(self, host=None, *, cert_path=None, tls_verify=None):
        version = '1.14'

        if host is None:
            # load local settings with love and magic
            host = os.environ.get('DOCKER_HOST')
            cert_path = os.environ.get('DOCKER_CERT_PATH', '~/.docker')
            tls_verify = os.environ.get('DOCKER_TLS_VERIFY') in ('1', 'true', 'on')

        self.docker_handler = DockerHandler(host, version, cert_path, tls_verify)

    @property
    def host(self):
        return self.docker_handler.host

    @property
    def api_version(self):
        return self.docker_handler.version

    @lazy_property
    def containers(self):
        return endpoints.ContainersEndpoint(self.docker_handler)

    @lazy_property
    def images(self):
        return endpoints.ImagesEndpoint(self.docker_handler)

    @lazy_property
    def misc(self):
        return endpoints.MiscEndpoint(self.docker_handler)

    @lazy_property
    def docker_hub(self):
        """Connect to DockerHub"""
        return endpoints.DockerHubEndpoint(self.docker_handler)

    def __getattr__(self, name):
        if hasattr(self.misc, name):
            return getattr(self.misc, name)
        raise AttributeError('attribute not found %r' % name)

    def __repr__(self):
        return '<Docker(host=%r)>' % self.host
