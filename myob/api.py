from .credentials import PartnerCredentials
from .endpoints import ALL, ENDPOINTS, GET
from .managers import Manager


class Myob:
    """ An ORM-like interface to the MYOB API. """
    def __init__(self, credentials):
        if not isinstance(credentials, PartnerCredentials):
            raise TypeError(
                'Expected a Credentials instance, got %s.' % (
                    type(credentials).__name__,
                )
            )
        self.credentials = credentials
        self.companyfiles = CompanyFiles(credentials)
        self._manager = Manager('', credentials, raw_endpoints=[
            (GET, 'Info/', 'Return API build information for each individual endpoint.'),
        ])

    def info(self):
        return self._manager.info()

    def __repr__(self):
        return 'Myob:\n    %s' % '\n    '.join(['companyfiles', 'info'])


class CompanyFiles:
    def __init__(self, credentials):
        self.credentials = credentials
        self._manager = Manager('', self.credentials, raw_endpoints=[
            (ALL, '', 'Return a list of company files.'),
            (GET, '[id]/', 'List endpoints available for a company file.'),
        ])
        self._manager.name = 'CompanyFile'

    def all(self):
        raw_companyfiles = self._manager.all()
        return [CompanyFile(raw_companyfile, self.credentials) for raw_companyfile in raw_companyfiles]

    def get(self, id, call=True):
        if call:
            raw_companyfile = self._manager.get(id=id)['CompanyFile']
        else:
            raw_companyfile = {'Id': id}
        return CompanyFile(raw_companyfile, self.credentials)

    def __repr__(self):
        return self._manager.__repr__()


class CompanyFile:
    def __init__(self, raw, credentials):
        self.id = raw['Id']
        self.name = raw.get('Name')
        self.data = raw  # Dump remaining raw data here.
        self.credentials = credentials
        for k, v in ENDPOINTS.items():
            setattr(self, v['name'], Manager(k, credentials, endpoints=v['methods'], company_id=self.id))

    def __repr__(self):
        return 'CompanyFile:\n    %s' % '\n    '.join(sorted(v['name'] for v in ENDPOINTS.values()))
