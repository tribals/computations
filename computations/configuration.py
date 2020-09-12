import os


class EnvConfig(object):
    _PREFIX = 'COMPUTATIONS'

    def __getattr__(self, name):
        return os.environ[f'{self._PREFIX}_{name}']
