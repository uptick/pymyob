GET = 'GET'
POST = 'POST'
PUT = 'PUT'
DELETE = 'DELETE'

METHOD_ORDER = [GET, POST, PUT, DELETE]

ENDPOINTS = {
    '': {
        'plural': 'companyfiles',
        'methods': [
            (GET, ''),
            (GET, 'info')
        ],
    },
}
