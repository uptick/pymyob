from .api import Myob  # noqa

VERSION = (1, 2, 10)

__version__ = '.'.join(str(x) for x in VERSION[:(2 if VERSION[2] == 0 else 3)])  # noqa
