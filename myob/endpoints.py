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
            (GET, 'Item/[uid]', 'Return selected item type sale invoice.'),
            (PUT, 'Item/[uid]', 'Update selected item type sale invoice.'),
            (POST, 'Item', 'Create new item type sale invoice.'),
            (DELETE, 'Item/[uid]', 'Delete selected item type sale invoice.')
        ]
    },
    '[company_id]/GeneralLedger': {
        'plural': 'general_ledger',
        'methods': [
            (ALL, 'TaxCode', 'Return tax codes set up with an AccountRight company file.'),
            (GET, 'TaxCode/[uid]', 'Return selected tax code.'),
            (PUT, 'TaxCode/[uid]', 'Update selected tax codes.'),
            (POST, 'TaxCode', 'Create new tax code.'),
            (DELETE, 'TaxCode/[uid]', 'Delete selected tax code.')
        ]
    },
    '[company_id]/Inventory': {
        'plural': 'inventory',
        'methods': [
            (ALL, 'Item', 'Return inventory items for an AccountRight company file'),
            (GET, 'Item/[uid]', 'Return selected inventory item.'),
            (PUT, 'Item/[uid]', 'Update selected inventory items.'),
            (POST, 'Item', 'Create new inventory item.'),
            (DELETE, 'Item/[uid]', 'Delete selected inventory item.')
        ]
    },
}
