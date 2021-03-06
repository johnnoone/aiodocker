from . import endpoints
from .handlers import DockerHandler
from .util import lazy_property, get_config_from_env
import os
import logging

__all__ = ['Docker']

log = logging.getLogger(__name__)


class Docker:

    def __init__(self, host=None, *, cert_path=None, tls_verify=None, **opts):
        """

        .. note::
            arguments must follow the DOCKER_VARS
        """

        version = '1.17'
        self.api = DockerHandler(host, version, cert_path, tls_verify)
        if opts:
            log.warn('Don\'t know how to handle %s' % opts)

    @classmethod
    def local_client(cls):
        """
        Scaffold a local client with env variables.
        """

        opts = get_config_from_env()
        opts.setdefault('host', 'http://127.0.0.1:3000')
        opts.setdefault('tls_verify', False)
        opts.setdefault('cert_path', '~/.docker')
        return cls(**opts)

    @lazy_property
    def containers(self):
        return endpoints.ContainersEndpoint(self.api)

    @lazy_property
    def images(self):
        return endpoints.ImagesEndpoint(self.api)

    @lazy_property
    def executors(self):
        return endpoints.ExecEndpoint(self.api)

    @lazy_property
    def misc(self):
        return endpoints.MiscEndpoint(self.api)

    @lazy_property
    def dockerhub(self):
        """Connect to DockerHub"""
        return endpoints.DockerHubEndpoint(self.api)

    def __getattr__(self, name):
        if hasattr(self.misc, name):
            return getattr(self.misc, name)
        raise AttributeError('attribute not found %r' % name)

    def __repr__(self):
        return '<Docker(host=%r)>' % self.api.host
