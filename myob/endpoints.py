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
    '[company_id]/Sale/Invoice': {
        'plural': 'invoices',
        'methods': [
            (ALL, '', 'Return all sale invoice types for an AccountRight company file'),
            (GET, 'Item', 'Return item type sale invoices for an AccountRight company file'),
            (POST, 'Item', 'Create item type sale invoices for an AccountRight company file'),
            (PUT, 'Item', 'Update item type sale invoices for an AccountRight company file'),
            (DELETE, 'Item', 'Delete item type sale invoices for an AccountRight company file')
        ]
    }
}
