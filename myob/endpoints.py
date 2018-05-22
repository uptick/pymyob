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
            (GET, '[id]/', 'List endpoints available for a company file.'),
            (GET, 'Info/', 'Return API build information for each individual endpoint.'),
        ],
    },
    '[company_id]/Contact/': {
        'plural': 'contacts',
        'methods': [
            (ALL, '', 'Return all contact types for an AccountRight company file.'),
            (ALL, 'Customer/', 'Return all customer contacts for an AccountRight company file.'),
            (GET, 'Customer/[uid]/', 'Return selected customer contact.'),
            (PUT, 'Customer/[uid]/', 'Update selected customer contact.'),
            (POST, 'Customer/', 'Create new customer contact.'),
            (DELETE, 'Customer/[uid]/', 'Delete selected customer contact.'),
            (ALL, 'Supplier/', 'Return all supplier contacts for an AccountRight company file.'),
            (GET, 'Supplier/[uid]/', 'Return selected supplier contact.'),
            (PUT, 'Supplier/[uid]/', 'Update selected supplier contact.'),
            (POST, 'Supplier/', 'Create new supplier contact.'),
            (DELETE, 'Supplier/[uid]/', 'Delete selected supplier contact.'),
        ],
    },
    '[company_id]/Sale/Invoice/': {
        'plural': 'invoices',
        'methods': [
            (ALL, '', 'Return all sale invoice types for an AccountRight company file.'),
            (ALL, 'Item/', 'Return item type sale invoices for an AccountRight company file.'),
            (GET, 'Item/[uid]/', 'Return selected item type sale invoice.'),
            (PUT, 'Item/[uid]/', 'Update selected item type sale invoice.'),
            (POST, 'Item/', 'Create new item type sale invoice.'),
            (DELETE, 'Item/[uid]/', 'Delete selected item type sale invoice.'),
            (ALL, 'Service/', 'Return service type sale invoices for an AccountRight company file.'),
            (GET, 'Service/[uid]/', 'Return selected service type sale invoice.'),
            (PUT, 'Service/[uid]/', 'Update selected service type sale invoice.'),
            (POST, 'Service/', 'Create new service type sale invoice.'),
            (DELETE, 'Service/[uid]/', 'Delete selected service type sale invoice.'),
        ]
    },
    '[company_id]/GeneralLedger/': {
        'plural': 'general_ledger',
        'methods': [
            (ALL, 'TaxCode/', 'Return tax codes set up with an AccountRight company file.'),
            (GET, 'TaxCode/[uid]/', 'Return selected tax code.'),
            (PUT, 'TaxCode/[uid]/', 'Update selected tax codes.'),
            (POST, 'TaxCode/', 'Create new tax code.'),
            (DELETE, 'TaxCode/[uid]/', 'Delete selected tax code.'),
            (ALL, 'Account/', 'Return accounts set up with an AccountRight company file.'),
            (GET, 'Account/[uid]/', 'Return selected account.'),
            (PUT, 'Account/[uid]/', 'Update selected accounts.'),
            (POST, 'Account/', 'Create new account.'),
            (DELETE, 'Account/[uid]/', 'Delete selected account.'),
        ]
    },
    '[company_id]/Inventory/': {
        'plural': 'inventory',
        'methods': [
            (ALL, 'Item/', 'Return inventory items for an AccountRight company file.'),
            (GET, 'Item/[uid]/', 'Return selected inventory item.'),
            (PUT, 'Item/[uid]/', 'Update selected inventory items.'),
            (POST, 'Item/', 'Create new inventory item.'),
            (DELETE, 'Item/[uid]/', 'Delete selected inventory item.'),
        ]
    },
    '[company_id]/Purchase/Order/': {
        'plural': 'purchase_orders',
        'methods': [
            (ALL, '', 'Return all purchase order types for an AccountRight company file.'),
            (ALL, 'Item/', 'Return item type purchase orders for an AccountRight company file.'),
            (GET, 'Item/[uid]/', 'Return selected item type purchase order.'),
            (PUT, 'Item/[uid]/', 'Update selected item type purchase order.'),
            (POST, 'Item/', 'Create new item type purchase order.'),
            (DELETE, 'Item/[uid]/', 'Delete selected item type purchase order.'),
        ]
    },
    '[company_id]/Purchase/Bill/': {
        'plural': 'purchase_bills',
        'methods': [
            (ALL, '', 'Return all purchase bill types for an AccountRight company file.'),
            (ALL, 'Item/', 'Return item type purchase bills for an AccountRight company file.'),
            (GET, 'Item/[uid]/', 'Return selected item type purchase bill.'),
            (PUT, 'Item/[uid]/', 'Update selected item type purchase bill.'),
            (POST, 'Item/', 'Create new item type purchase bill.'),
            (DELETE, 'Item/[uid]/', 'Delete selected item type purchase bill.'),
            (ALL, 'Service/', 'Return service type purchase bills for an AccountRight company file.'),
            (GET, 'Service/[uid]/', 'Return selected service type purchase bill.'),
            (PUT, 'Service/[uid]/', 'Update selected service type purchase bill.'),
            (POST, 'Service/', 'Create new service type purchase bill.'),
            (DELETE, 'Service/[uid]/', 'Delete selected service type purchase bill.'),
        ]
    },
}
