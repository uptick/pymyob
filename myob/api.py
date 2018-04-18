from .endpoints import ENDPOINTS
from .managers import Manager

class CompanyFiles:
    def __init__(self, credentials):
        self.credentials = credentials
        for k, v in ENDPOINTS.items():
            if k == '':
                setattr(self, 'api', Manager(k, credentials))
                
    
    def get(self, id):
        self.endpoints = self.api.get(id=id, company_id=id)
        return Company(id, self.credentials) 

    def all(self):
        return self.api.all()


class Company:
    def __init__(self, id, credentials):
        self.id = id
        self.credentials = credentials
        for k, v in ENDPOINTS.items():
            if k != '':
                setattr(self, v['plural'], Manager(k, credentials, company_id=self.id))
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
        self.companyfiles = CompanyFiles(self.credentials)

        

    def __repr__(self):
        return '%s:\n    %s' % (self.__class__.__name__, '\n    '.join(
            sorted(v['plural'] for v in ENDPOINTS.values())
        ))