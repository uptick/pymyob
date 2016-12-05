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
            (ALL, '', 'Return a list of company files.'),
            (GET, '[id]', 'List endpoints available for a company file.'),
            (GET, 'Info', 'Return API build information for each individual endpoint.'),
        ],
    },
    '[company_id]/Contact': {
        'plural': 'contacts',
        'methods': [
            (ALL, '', 'Return all contact types for an AccountRight company file'),
            (ALL, 'Customer', 'Return all customer contacts for an AccountRight company file.'),
            (GET, 'Customer/[uid]', 'Return selected customer contact.'),
            (PUT, 'Customer/[uid]', 'Update selected customer contact.'),
            (POST, 'Customer', 'Create new customer contact.'),
            (DELETE, 'Customer/[uid]', 'Delete selected customer contact.'),
        ],
    },
    '[company_id]/Sale/Invoice': {
        'plural': 'invoices',
        'methods': [
            (ALL, '', 'Return all sale invoice types for an AccountRight company file.'),
            (ALL, 'Item', 'Return item type sale invoices for an AccountRight company file.'),
            (GET, 'Item/[uid]', 'Return item type sale invoices for an AccountRight company file.'),
            (PUT, 'Item/[uid]', 'Update item type sale invoices for an AccountRight company file.'),
            (POST, 'Item', 'Create item type sale invoices for an AccountRight company file.'),
            (DELETE, 'Item/[uid]', 'Delete item type sale invoices for an AccountRight company file.')
        ]
    }
}
