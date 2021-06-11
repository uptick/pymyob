import re
import requests
from datetime import date

from .constants import DEFAULT_PAGE_SIZE, MYOB_BASE_URL
from .endpoints import CRUD, METHOD_MAPPING, METHOD_ORDER
from .exceptions import (
    MyobBadRequest,
    MyobExceptionUnknown,
    MyobForbidden,
    MyobGatewayTimeout,
    MyobNotFound,
    MyobRateLimitExceeded,
    MyobUnauthorized,
)


class Manager:
    def __init__(self, name, credentials, company_id=None, endpoints=[], raw_endpoints=[]):
        self.credentials = credentials
        self.name = '_'.join(p for p in name.rstrip('/').split('/') if '[' not in p)
        self.base_url = MYOB_BASE_URL
        if company_id is not None:
            self.base_url += company_id + '/'
        if name:
            self.base_url += name
        self.method_details = {}
        self.company_id = company_id

        # Build ORM methods from given url endpoints.
        for method, base, name in endpoints:
            if method == CRUD:
                for m in METHOD_ORDER:
                    self.build_method(
                        m,
                        METHOD_MAPPING[m]['endpoint'](base),
                        METHOD_MAPPING[m]['hint'](name),
                    )
            else:
                self.build_method(
                    method,
                    METHOD_MAPPING[method]['endpoint'](base),
                    METHOD_MAPPING[method]['hint'](name),
                )
        # Build raw methods (ones where we don't want to tinker with the endpoint or hint)
        for method, endpoint, hint in raw_endpoints:
            self.build_method(method, endpoint, hint)

    def build_method(self, method, endpoint, hint):
        full_endpoint = self.base_url + endpoint
        url_keys = re.findall(r'\[([^\]]*)\]', full_endpoint)
        template = full_endpoint.replace('[', '{').replace(']', '}')

        required_kwargs = url_keys.copy()
        if method in ('PUT', 'POST'):
            required_kwargs.append('data')

        def inner(*args, timeout=None, **kwargs):
            if args:
                raise AttributeError("Unnamed args provided. Only keyword args accepted.")

            # Ensure all required url kwargs have been provided.
            missing_kwargs = set(required_kwargs) - set(kwargs.keys())
            if missing_kwargs:
                raise KeyError("Missing kwargs %s. Endpoint requires %s." % (
                    list(missing_kwargs), required_kwargs
                ))

            # Parse kwargs.
            url_kwargs = {}
            request_kwargs_raw = {}
            for k, v in kwargs.items():
                if k in url_keys:
                    url_kwargs[k] = v
                elif k != 'data':
                    request_kwargs_raw[k] = v

            # Determine request method.
            request_method = 'GET' if method == 'ALL' else method

            # Build url.
            url = template.format(**url_kwargs)

            # Build request kwargs (header/query/body)
            request_kwargs = self.build_request_kwargs(request_method, data=kwargs.get('data'), **request_kwargs_raw)
            response = requests.request(request_method, url, timeout=timeout, **request_kwargs)

            if response.status_code == 200:
                # We don't want to be deserialising binary responses..
                if not response.headers.get('content-type', '').startswith('application/json'):
                    return response.content

                try:
                    return response.json()
                except ValueError:
                    # Handle possible empty string response to DELETE request
                    if method == 'DELETE' and response.content == b'':
                        return {}
                    raise
            elif response.status_code == 201:
                return response.json()
            elif response.status_code == 400:
                raise MyobBadRequest(response)
            elif response.status_code == 401:
                raise MyobUnauthorized(response)
            elif response.status_code == 403:
                if response.json()['Errors'][0]['Name'] == 'RateLimitError':
                    raise MyobRateLimitExceeded(response)
                raise MyobForbidden(response)
            elif response.status_code == 404:
                raise MyobNotFound(response)
            elif response.status_code == 504:
                raise MyobGatewayTimeout(response)
            else:
                raise MyobExceptionUnknown(response)

        # Build method name
        method_name = '_'.join(p for p in endpoint.rstrip('/').split('/') if '[' not in p).lower()
        # If it has no name, use method.
        if not method_name:
            method_name = method.lower()
        # If it already exists, prepend with method to disambiguate.
        elif hasattr(self, method_name):
            method_name = '%s_%s' % (method.lower(), method_name)
        self.method_details[method_name] = {
            'kwargs': required_kwargs,
            'hint': hint,
        }
        setattr(self, method_name, inner)

    def build_request_kwargs(self, method, data=None, **kwargs):
        request_kwargs = {}

        # Build headers.
        if self.company_id:
            try:
                companyfile_credentials = self.credentials.companyfile_credentials[self.company_id]
            except KeyError:
                raise KeyError('There are no stored username-password credentials for this company id.')
        else:
            companyfile_credentials = ''

        request_kwargs['headers'] = {
            'Authorization': 'Bearer %s' % self.credentials.oauth_token,
            'x-myobapi-cftoken': companyfile_credentials,
            'x-myobapi-key': self.credentials.consumer_key,
            'x-myobapi-version': 'v2',
        }
        if 'headers' in kwargs:
            request_kwargs['headers'].update(kwargs['headers'])

        # Build query.
        request_kwargs['params'] = {}
        filters = []

        def build_value(value):
            if issubclass(type(value), date):
                return "datetime'%s'" % value
            if isinstance(value, bool):
                return str(value).lower()
            return "'%s'" % value

        if 'raw_filter' in kwargs:
            filters.append(kwargs['raw_filter'])

        for k, v in kwargs.items():
            if k not in ['orderby', 'format', 'headers', 'page', 'limit', 'templatename', 'timeout', 'raw_filter']:
                operator = 'eq'
                for op in ['lt', 'gt']:
                    if k.endswith('__%s' % op):
                        k = k[:-4]
                        operator = op
                if not isinstance(v, (list, tuple)):
                    v = [v]
                filters.append(' or '.join("%s %s %s" % (k, operator, build_value(v_)) for v_ in v))

        if filters:
            request_kwargs['params']['$filter'] = ' and '.join('(%s)' % f for f in filters)

        if 'orderby' in kwargs:
            request_kwargs['params']['$orderby'] = kwargs['orderby']

        page_size = DEFAULT_PAGE_SIZE
        if 'limit' in kwargs:
            page_size = int(kwargs['limit'])
            request_kwargs['params']['$top'] = page_size

        if 'page' in kwargs:
            request_kwargs['params']['$skip'] = (int(kwargs['page']) - 1) * page_size

        if 'format' in kwargs:
            request_kwargs['params']['format'] = kwargs['format']

        if 'templatename' in kwargs:
            request_kwargs['params']['templatename'] = kwargs['templatename']

        if method in ('PUT', 'POST'):
            request_kwargs['params']['returnBody'] = 'true'

        # Build body.
        if data is not None:
            request_kwargs['json'] = data

        return request_kwargs

    def __repr__(self):
        def print_method(name, args):
            return '%s(%s)' % (name, ', '.join(args))

        formatstr = '%%%is - %%s' % max(
            len(print_method(k, v['kwargs']))
            for k, v in self.method_details.items()
        )
        return '%s%s:\n    %s' % (self.name, self.__class__.__name__, '\n    '.join(
            formatstr % (
                print_method(k, v['kwargs']),
                v['hint'],
            ) for k, v in sorted(self.method_details.items())
        ))
