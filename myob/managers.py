import re
import requests

from .constants import MYOB_BASE_URL
from .endpoints import ENDPOINTS, METHOD_ORDER
from .exceptions import MyobExceptionUnknown, MyobUnauthorized


class Manager():
    def __init__(self, name, credentials):
        self.credentials = credentials
        self.name = name
        self.base_url = '%s/%s' % (MYOB_BASE_URL, name.lower())
        self.method_signatures = {}

        # Build ORM methods from given url endpoints.
        # Sort them first, to determine duplicate disambiguation order.
        endpoints = sorted(ENDPOINTS[name]['methods'], key=lambda x: METHOD_ORDER.index(x[0]))
        for method, endpoint in endpoints:
            self.build_method(method, endpoint)

    def build_method(self, method, endpoint):
        required_args = re.findall('\[([^\]]*)\]', endpoint)
        template = endpoint.replace('[', '{').replace(']', '}')

        def inner(*args, **kwargs):
            if args:
                raise AttributeError("Unnamed args provided. Only keyword args accepted.")

            # Build url.
            try:
                url = self.base_url + template.format(**kwargs)
            except KeyError as e:
                raise KeyError("Missing arg '%s' while building url. Endpoint requires %s." % (
                    str(e), required_args
                ))

            # Build headers.
            headers = {
                'Authorization': 'Bearer %s' % self.credentials.oauth_token,
                'x-myobapi-cftoken': self.credentials.userpass,
                'x-myobapi-key': self.credentials.consumer_key,
                'x-myobapi-version': 'v2',
            }

            # Build query.
            params = dict((k, v) for k, v in kwargs.items() if k not in required_args)
            request_method = 'GET' if method == 'ALL' else method
            response = requests.request(request_method, url, headers=headers, params=params)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise MyobUnauthorized(response)
            else:
                raise MyobExceptionUnknown(response)

        # Build method name
        method_name = '_'.join(p for p in endpoint.split('/') if '[' not in p)
        # If it has no name, use method.
        if not method_name:
            method_name = method.lower()
        # If it already exists, prepend with method to disambiguate.
        elif hasattr(self, method_name):
            method_name = '%s_%s' % (method.lower(), method_name)
        self.method_signatures[method_name] = required_args
        setattr(self, method_name, inner)

    def __repr__(self):
        return '%s%s:\n    %s' % (self.name, self.__class__.__name__, '\n    '.join(
            '%s(%s)' % (k, ', '.join(v)) for k, v in sorted(self.method_signatures.items())
        ))
