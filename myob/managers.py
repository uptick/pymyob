import re
import requests

from .constants import MYOB_BASE_URL
from .endpoints import ENDPOINTS, METHOD_ORDER
from .exceptions import MyobBadRequest, MyobExceptionUnknown, MyobNotFound, MyobUnauthorized


class Manager():
    def __init__(self, name, credentials):
        self.credentials = credentials
        self.name = '_'.join(p for p in name.split('/') if '[' not in p)
        self.base_url = MYOB_BASE_URL
        if name:
            self.base_url += '/' + name.lower()
        self.method_details = {}

        # Build ORM methods from given url endpoints.
        # Sort them first, to determine duplicate disambiguation order.
        endpoints = sorted(ENDPOINTS[name]['methods'], key=lambda x: METHOD_ORDER.index(x[0]))
        for method, endpoint, hint in endpoints:
            self.build_method(method, endpoint, hint)

    def build_method(self, method, endpoint, hint):
        full_endpoint = self.base_url + '/' + endpoint
        required_args = re.findall('\[([^\]]*)\]', full_endpoint)
        if method in ('PUT', 'POST'):
            required_args.append('data')
        template = full_endpoint.replace('[', '{').replace(']', '}')

        def inner(*args, **kwargs):
            if args:
                raise AttributeError("Unnamed args provided. Only keyword args accepted.")

            # Ensure all required args have been provided.
            missing_args = set(required_args) - set(kwargs.keys())
            if missing_args:
                raise KeyError("Missing args %s. Endpoint requires %s." % (
                    list(missing_args), required_args
                ))

            # Determine request method.
            request_method = 'GET' if method == 'ALL' else method

            # Build url.
            url = template.format(**kwargs)

            request_kwargs = {}

            # Build headers.
            request_kwargs['headers'] = {
                'Authorization': 'Bearer %s' % self.credentials.oauth_token,
                'x-myobapi-cftoken': self.credentials.userpass,
                'x-myobapi-key': self.credentials.consumer_key,
                'x-myobapi-version': 'v2',
            }

            # Build query.
            request_kwargs['params'] = {}
            filters = []
            for k, v in kwargs.items():
                if k not in required_args + ['orderby', 'format', 'headers']:
                    if isinstance(v, str):
                        v = [v]
                    filters.append(' or '.join("%s eq '%s'" % (k, v_) for v_ in v))
            if filters:
                request_kwargs['params']['$filter'] = '&'.join(filters)
            if 'orderby' in kwargs:
                request_kwargs['params']['$orderby'] = kwargs['orderby']
            if 'format' in kwargs:
                request_kwargs['params']['format'] = kwargs['format']
            if 'headers' in kwargs:
                request_kwargs['headers'].update(kwargs['headers'])

            # Build body.
            if 'data' in kwargs:
                request_kwargs['json'] = kwargs['data']

            response = requests.request(request_method, url, **request_kwargs)

            if response.status_code == 200:
                # We don't want to be deserialising binary responses..
                if not response.headers['content-type'].startswith('application/json'):
                    return response.content

                return response.json()
            elif response.status_code == 201:
                return {'status': 'OK'},
            elif response.status_code == 400:
                raise MyobBadRequest(response)
            elif response.status_code == 401:
                raise MyobUnauthorized(response)
            elif response.status_code == 404:
                raise MyobNotFound(response)
            else:
                raise MyobExceptionUnknown(response)

        # Build method name
        method_name = '_'.join(p for p in endpoint.split('/') if '[' not in p).lower()
        # If it has no name, use method.
        if not method_name:
            method_name = method.lower()
        # If it already exists, prepend with method to disambiguate.
        elif hasattr(self, method_name):
            method_name = '%s_%s' % (method.lower(), method_name)
        self.method_details[method_name] = {
            'args': required_args,
            'hint': hint,
        }
        setattr(self, method_name, inner)

    def __repr__(self):
        def print_method(name, args):
            return '%s(%s)' % (name, ', '.join(args))

        formatstr = '%%%is - %%s' % max(
            len(print_method(k, v['args']))
            for k, v in self.method_details.items()
        )
        return '%s%s:\n    %s' % (self.name, self.__class__.__name__, '\n    '.join(
            formatstr % (
                print_method(k, v['args']),
                v['hint'],
            ) for k, v in sorted(self.method_details.items())
        ))
