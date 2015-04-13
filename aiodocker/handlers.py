from aiodocker.util import task
from urllib.parse import urlparse
import aiohttp
import json
import os.path
import ssl

__all__ = ['DockerHandler']


class DockerHandler:

    def __init__(self, host, version, cert_path=None, tls=None):
        cert, cert_ca = None, None
        if cert_path:
            cert = (
                os.path.join(cert_path, 'cert.pem'),
                os.path.join(cert_path, 'key.pem')
            )
            cert_ca = os.path.join(cert_path, 'ca.pem')

        parsed = urlparse(host)
        scheme, hostname, port = parsed.scheme, parsed.hostname, parsed.port
        scheme = 'https' if scheme == 'tcp' else scheme

        connector = None
        if scheme == 'https':
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            context.verify_mode = ssl.CERT_NONE
            context.load_cert_chain(*cert)
            connector = aiohttp.TCPConnector(verify_ssl=True,
                                             ssl_context=context)

        host = '%s://%s%s' % (scheme, hostname, (':%s' % port if port else ''))
        self.host = host
        self.connector = connector

        self.version = version
        self.cert_path = cert_path
        self.tls = tls
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
        print(url)
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
