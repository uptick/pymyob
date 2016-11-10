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
            (ALL, '', 'Returns a list of company files.'),
            (GET, '[id]', 'Lists endpoints available for a company file.'),
            (GET, 'Info', 'Returns API build information for each individual endpoint'),
        ],
    },
    '[company_id]/Contact': {
        'plural': 'contacts',
        'methods': [
            (ALL, '', 'Return all contact types for an AccountRight company file'),
            (ALL, 'Customer', 'Returns all customer contacts for an AccountRight company file.'),
            (GET, 'Customer/[uid]', 'Returns selected customer contact.'),
            (PUT, 'Customer/[uid]', 'Updates selected customer contact.'),
            (POST, 'Customer', 'Creates new customer contact.'),
            (DELETE, 'Customer/[uid]', 'Deletes selected customer contact.'),
        ],
    },
}
