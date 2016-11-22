from .endpoints import ENDPOINTS
from .managers import Manager


class Myob:
    """An ORM-like interface to the MYOB API"""
    def __init__(self, credentials):
        from .credentials import PartnerCredentials
        if not isinstance(credentials, PartnerCredentials):
            raise TypeError(
                'Expected a Credentials instance, got %s.' % (
                    type(credentials).__name__,
                )
            )
        self.credentials = credentials

        for k, v in ENDPOINTS.items():
            setattr(self, v['plural'], Manager(k, credentials))

    def __repr__(self):
        return '%s:\n    %s' % (self.__class__.__name__, '\n    '.join(
            sorted(v['plural'] for v in ENDPOINTS.values())
        ))
