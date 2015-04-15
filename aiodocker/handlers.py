from aiodocker.util import task
from urllib.parse import urlparse
import aiohttp
import json
import os.path
import ssl

__all__ = ['DockerHandler']


class DockerHandler:

    def __init__(self, host, version, cert_path=None, tls_verify=None):
        cert, cert_ca = None, None
        if cert_path:
            cert_path = os.path.expanduser(cert_path)
            cert = (
                os.path.join(cert_path, 'cert.pem'),
                os.path.join(cert_path, 'key.pem')
            )
            cert_ca = os.path.join(cert_path, 'ca.pem')

        host, socket, connector = connect(host, tls_verify, cert, cert_ca)

        self.host = host
        self.socket = socket
        self.connector = connector

        self.version = version
        self.cert_path = cert_path
        self.tls_verify = tls_verify
        self.cert = cert
        self.cert_ca = cert_ca

    def get(self, path, **kwargs):
        """
        Short-cut towards :meth:`request`
        """
        return self.request('GET', path, **kwargs)

    def post(self, path, **kwargs):
        """
        Short-cut towards :meth:`request`
        """
        return self.request('POST', path, **kwargs)

    def put(self, path, **kwargs):
        """
        Short-cut towards :meth:`request`
        """
        return self.request('PUT', path, **kwargs)

    def delete(self, path, **kwargs):
        """
        Short-cut towards :meth:`request`
        """
        return self.request('DELETE', path, **kwargs)

    @task
    def request(self, method, path, **kwargs):
        version = kwargs.pop('version', self.version)
        url = '%s/v%s/%s' % (self.host, version, path.lstrip('/'))
        params = kwargs.get('params', {}).copy()
        kwargs['params'] = parameters(params)
        kwargs.setdefault('connector', self.connector)
        response = yield from aiohttp.request(method, url, **kwargs)
        return response


def parameters(data):

    def prepare(obj):
        if obj is True:
            return '1'
        if obj is False:
            return '0'
        if isinstance(obj, dict):
            return clean(obj)
        if isinstance(obj, (list, set, tuple)):
            return [prepare(elt) for elt in obj]
        return obj

    def clean(data):
        return {k: prepare(v) for k, v in data.items() if v is not None}

    response = clean(data)
    for k, v in response.items():
        if isinstance(v, (dict, list, set, tuple)):
            response[k] = json.dumps(v)
    return response


def connect(host, tls_verify, cert, cert_ca):
    parsed = urlparse(host)
    if parsed.scheme == 'unix':
        return connect_unix(parsed.path)
    else:
        return connect_tcp(host, tls_verify, cert, cert_ca)


def connect_unix(path):
    socket = path
    connector = aiohttp.TCPConnector(path=path)
    return 'http://127.0.0.1', socket, connector


def connect_tcp(host, tls_verify, cert, cert_ca):
    parsed = urlparse(host)
    scheme, hostname, port = parsed.scheme, parsed.hostname, parsed.port

    if scheme == 'tcp':
        scheme = 'https' if tls_verify else 'http'

    connector = None
    if scheme == 'https':
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        context.verify_mode = ssl.CERT_NONE
        if cert:
            context.load_cert_chain(*cert)
        connector = aiohttp.TCPConnector(verify_ssl=True,
                                         ssl_context=context)

    host = '%s://%s%s' % (scheme, hostname, (':%s' % port if port else ''))
    return host, None, connector
