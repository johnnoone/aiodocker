import os

__all__ = ['get_config_from_env']

def get_config_from_env():
    opts = {}
    for key, value in os.environ.items():
        if key.startswith('DOCKER_'):
            key = key[7:].lower()
            if key == 'tls_verify':
                value = value in ('1', 'true', 'on')
            opts[key] = value
    return opts
