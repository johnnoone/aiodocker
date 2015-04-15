from . import endpoints
from .handlers import DockerHandler
from .util import lazy_property
import os

__all__ = ['Docker']


class Docker:

    def __init__(self, host=None, *, cert_path=None, tls_verify=None):
        version = '1.17'
        self.api = DockerHandler(host, version, cert_path, tls_verify)

    @classmethod
    def local_client(cls):
        """
        Scaffold a local client.
        """
        host = os.environ.get('DOCKER_HOST')
        cert_path = os.environ.get('DOCKER_CERT_PATH', '~/.docker')
        tls_verify = os.environ.get('DOCKER_TLS_VERIFY') in ('1', 'true', 'on')
        return cls(host, cert_path=cert_path, tls_verify=tls_verify)

    @property
    def host(self):
        return self.api.host

    @property
    def api_version(self):
        return self.api.version

    @lazy_property
    def containers(self):
        return endpoints.ContainersEndpoint(self.api)

    @lazy_property
    def images(self):
        return endpoints.ImagesEndpoint(self.api)

    @lazy_property
    def misc(self):
        return endpoints.MiscEndpoint(self.api)

    @lazy_property
    def docker_hub(self):
        """Connect to DockerHub"""
        return endpoints.DockerHubEndpoint(self.api)

    def __getattr__(self, name):
        if hasattr(self.misc, name):
            return getattr(self.misc, name)
        raise AttributeError('attribute not found %r' % name)

    def __repr__(self):
        return '<Docker(host=%r)>' % self.host
