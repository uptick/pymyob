ALL = 'ALL'
GET = 'GET'
POST = 'POST'
PUT = 'PUT'
DELETE = 'DELETE'

METHOD_ORDER = [ALL, GET, POST, PUT, DELETE]

ENDPOINTS = {
    '': {
        'plural': 'companyfiles',
        'methods': [
            (ALL, ''),
            (GET, '[id]'),
            (GET, 'info'),
        ],
    },
    'Contact': {
        'plural': 'contacts',
        'methods': [
            (GET, ''),
            (GET, 'customer'),
            (PUT, 'customer'),
            (POST, 'customer'),
            (DELETE, 'customer'),
        ],
    },
}
