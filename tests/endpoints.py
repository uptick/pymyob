from unittest import TestCase
from unittest.mock import patch

from myob import Myob
from myob.credentials import PartnerCredentials

# Reusable dummy data
CID = 'DummyCompanyId'
UID = 'DummyResourceUid'
DATA = {'dummy': 'data'}


class EndpointTests(TestCase):
    def setUp(self):
        cred = PartnerCredentials(
            consumer_key='KeyToTheKingdom',
            consumer_secret='TellNoOne',
            callback_uri='CallOnlyWhenCalledTo',
        )
        self.myob = Myob(cred)
        self.request_headers = {
            'Authorization': 'Bearer None',
            'x-myobapi-cftoken': None,
            'x-myobapi-key': 'KeyToTheKingdom',
            'x-myobapi-version': 'v2'
        }

    @patch('myob.managers.requests.request')
    def assertEndpointReached(self, func, params, method, endpoint, mock_request):
        mock_request.return_value.status_code = 200
        func(**params)
        full_endpoint = 'https://api.myob.com/accountright' + endpoint
        mock_request.assert_called_once_with(
            method,
            full_endpoint,
            headers=self.request_headers,
            params={'returnBody': 'true'} if method in ['PUT', 'POST'] else {},
            **({'json': DATA} if method in ['PUT', 'POST'] else {}),
        )

    def test_base(self):
        self.assertEqual(repr(self.myob), (
            "Myob:\n"
            "    companyfiles\n"
            "    contacts\n"
            "    general_ledger\n"
            "    inventory\n"
            "    invoices\n"
            "    purchase_bills\n"
            "    purchase_orders"
        ))

    def test_companyfiles(self):
        self.assertEqual(repr(self.myob.companyfiles), (
            "Manager:\n"
            "      all() - Return a list of company files.\n"
            "    get(id) - List endpoints available for a company file.\n"
            "     info() - Return API build information for each individual endpoint."
        ))
        self.assertEndpointReached(self.myob.companyfiles.all, {}, 'GET', '/')
        self.assertEndpointReached(self.myob.companyfiles.get, {'id': CID}, 'GET', f'/{CID}/')
        self.assertEndpointReached(self.myob.companyfiles.info, {}, 'GET', '/Info/')

    def test_contacts(self):
        self.assertEqual(repr(self.myob.contacts), (
            "ContactManager:\n"
            "                        all(company_id) - Return all contact types for an AccountRight company file.\n"
            "                   customer(company_id) - Return all customer contacts for an AccountRight company file.\n"
            "       delete_customer(company_id, uid) - Delete selected customer contact.\n"
            "       delete_supplier(company_id, uid) - Delete selected supplier contact.\n"
            "          get_customer(company_id, uid) - Return selected customer contact.\n"
            "          get_supplier(company_id, uid) - Return selected supplier contact.\n"
            "        post_customer(company_id, data) - Create new customer contact.\n"
            "        post_supplier(company_id, data) - Create new supplier contact.\n"
            "    put_customer(company_id, uid, data) - Update selected customer contact.\n"
            "    put_supplier(company_id, uid, data) - Update selected supplier contact.\n"
            "                   supplier(company_id) - Return all supplier contacts for an AccountRight company file."
        ))
        self.assertEndpointReached(self.myob.contacts.all, {'company_id': CID}, 'GET', f'/{CID}/Contact/')
        self.assertEndpointReached(self.myob.contacts.customer, {'company_id': CID}, 'GET', f'/{CID}/Contact/Customer/')
        self.assertEndpointReached(self.myob.contacts.get_customer, {'company_id': CID, 'uid': UID}, 'GET', f'/{CID}/Contact/Customer/{UID}/')
        self.assertEndpointReached(self.myob.contacts.put_customer, {'company_id': CID, 'uid': UID, 'data': DATA}, 'PUT', f'/{CID}/Contact/Customer/{UID}/')
        self.assertEndpointReached(self.myob.contacts.post_customer, {'company_id': CID, 'data': DATA}, 'POST', f'/{CID}/Contact/Customer/')
        self.assertEndpointReached(self.myob.contacts.delete_customer, {'company_id': CID, 'uid': UID}, 'DELETE', f'/{CID}/Contact/Customer/{UID}/')
        self.assertEndpointReached(self.myob.contacts.supplier, {'company_id': CID}, 'GET', f'/{CID}/Contact/Supplier/')
        self.assertEndpointReached(self.myob.contacts.get_supplier, {'company_id': CID, 'uid': UID}, 'GET', f'/{CID}/Contact/Supplier/{UID}/')
        self.assertEndpointReached(self.myob.contacts.put_supplier, {'company_id': CID, 'uid': UID, 'data': DATA}, 'PUT', f'/{CID}/Contact/Supplier/{UID}/')
        self.assertEndpointReached(self.myob.contacts.post_supplier, {'company_id': CID, 'data': DATA}, 'POST', f'/{CID}/Contact/Supplier/')
        self.assertEndpointReached(self.myob.contacts.delete_supplier, {'company_id': CID, 'uid': UID}, 'DELETE', f'/{CID}/Contact/Supplier/{UID}/')

    def test_invoices(self):
        self.assertEqual(repr(self.myob.invoices), (
            "Sale_InvoiceManager:\n"
            "                       all(company_id) - Return all sale invoice types for an AccountRight company file.\n"
            "          delete_item(company_id, uid) - Delete selected item type sale invoice.\n"
            "       delete_service(company_id, uid) - Delete selected service type sale invoice.\n"
            "             get_item(company_id, uid) - Return selected item type sale invoice.\n"
            "          get_service(company_id, uid) - Return selected service type sale invoice.\n"
            "                      item(company_id) - Return item type sale invoices for an AccountRight company file.\n"
            "           post_item(company_id, data) - Create new item type sale invoice.\n"
            "        post_service(company_id, data) - Create new service type sale invoice.\n"
            "       put_item(company_id, uid, data) - Update selected item type sale invoice.\n"
            "    put_service(company_id, uid, data) - Update selected service type sale invoice.\n"
            "                   service(company_id) - Return service type sale invoices for an AccountRight company file."
        ))
        self.assertEndpointReached(self.myob.invoices.all, {'company_id': CID}, 'GET', f'/{CID}/Sale/Invoice/')
        self.assertEndpointReached(self.myob.invoices.item, {'company_id': CID}, 'GET', f'/{CID}/Sale/Invoice/Item/')
        self.assertEndpointReached(self.myob.invoices.get_item, {'company_id': CID, 'uid': UID}, 'GET', f'/{CID}/Sale/Invoice/Item/{UID}/')
        self.assertEndpointReached(self.myob.invoices.put_item, {'company_id': CID, 'uid': UID, 'data': DATA}, 'PUT', f'/{CID}/Sale/Invoice/Item/{UID}/')
        self.assertEndpointReached(self.myob.invoices.post_item, {'company_id': CID, 'data': DATA}, 'POST', f'/{CID}/Sale/Invoice/Item/')
        self.assertEndpointReached(self.myob.invoices.delete_item, {'company_id': CID, 'uid': UID}, 'DELETE', f'/{CID}/Sale/Invoice/Item/{UID}/')
        self.assertEndpointReached(self.myob.invoices.service, {'company_id': CID}, 'GET', f'/{CID}/Sale/Invoice/Service/')
        self.assertEndpointReached(self.myob.invoices.get_service, {'company_id': CID, 'uid': UID}, 'GET', f'/{CID}/Sale/Invoice/Service/{UID}/')
        self.assertEndpointReached(self.myob.invoices.put_service, {'company_id': CID, 'uid': UID, 'data': DATA}, 'PUT', f'/{CID}/Sale/Invoice/Service/{UID}/')
        self.assertEndpointReached(self.myob.invoices.post_service, {'company_id': CID, 'data': DATA}, 'POST', f'/{CID}/Sale/Invoice/Service/')
        self.assertEndpointReached(self.myob.invoices.delete_service, {'company_id': CID, 'uid': UID}, 'DELETE', f'/{CID}/Sale/Invoice/Service/{UID}/')

    def test_general_ledger(self):
        self.assertEqual(repr(self.myob.general_ledger), (
            "GeneralLedgerManager:\n"
            "                   account(company_id) - Return accounts set up with an AccountRight company file.\n"
            "       delete_account(company_id, uid) - Delete selected account.\n"
            "       delete_taxcode(company_id, uid) - Delete selected tax code.\n"
            "          get_account(company_id, uid) - Return selected account.\n"
            "          get_taxcode(company_id, uid) - Return selected tax code.\n"
            "        post_account(company_id, data) - Create new account.\n"
            "        post_taxcode(company_id, data) - Create new tax code.\n"
            "    put_account(company_id, uid, data) - Update selected accounts.\n"
            "    put_taxcode(company_id, uid, data) - Update selected tax codes.\n"
            "                   taxcode(company_id) - Return tax codes set up with an AccountRight company file."
        ))
        self.assertEndpointReached(self.myob.general_ledger.taxcode, {'company_id': CID}, 'GET', f'/{CID}/GeneralLedger/TaxCode/')
        self.assertEndpointReached(self.myob.general_ledger.get_taxcode, {'company_id': CID, 'uid': UID}, 'GET', f'/{CID}/GeneralLedger/TaxCode/{UID}/')
        self.assertEndpointReached(self.myob.general_ledger.put_taxcode, {'company_id': CID, 'uid': UID, 'data': DATA}, 'PUT', f'/{CID}/GeneralLedger/TaxCode/{UID}/')
        self.assertEndpointReached(self.myob.general_ledger.post_taxcode, {'company_id': CID, 'data': DATA}, 'POST', f'/{CID}/GeneralLedger/TaxCode/')
        self.assertEndpointReached(self.myob.general_ledger.delete_taxcode, {'company_id': CID, 'uid': UID}, 'DELETE', f'/{CID}/GeneralLedger/TaxCode/{UID}/')
        self.assertEndpointReached(self.myob.general_ledger.account, {'company_id': CID}, 'GET', f'/{CID}/GeneralLedger/Account/')
        self.assertEndpointReached(self.myob.general_ledger.get_account, {'company_id': CID, 'uid': UID}, 'GET', f'/{CID}/GeneralLedger/Account/{UID}/')
        self.assertEndpointReached(self.myob.general_ledger.put_account, {'company_id': CID, 'uid': UID, 'data': DATA}, 'PUT', f'/{CID}/GeneralLedger/Account/{UID}/')
        self.assertEndpointReached(self.myob.general_ledger.post_account, {'company_id': CID, 'data': DATA}, 'POST', f'/{CID}/GeneralLedger/Account/')
        self.assertEndpointReached(self.myob.general_ledger.delete_account, {'company_id': CID, 'uid': UID}, 'DELETE', f'/{CID}/GeneralLedger/Account/{UID}/')

    def test_inventory(self):
        self.assertEqual(repr(self.myob.inventory), (
            "InventoryManager:\n"
            "       delete_item(company_id, uid) - Delete selected inventory item.\n"
            "          get_item(company_id, uid) - Return selected inventory item.\n"
            "                   item(company_id) - Return inventory items for an AccountRight company file.\n"
            "        post_item(company_id, data) - Create new inventory item.\n"
            "    put_item(company_id, uid, data) - Update selected inventory items."
        ))
        self.assertEndpointReached(self.myob.inventory.item, {'company_id': CID}, 'GET', f'/{CID}/Inventory/Item/')
        self.assertEndpointReached(self.myob.inventory.get_item, {'company_id': CID, 'uid': UID}, 'GET', f'/{CID}/Inventory/Item/{UID}/')
        self.assertEndpointReached(self.myob.inventory.put_item, {'company_id': CID, 'uid': UID, 'data': DATA}, 'PUT', f'/{CID}/Inventory/Item/{UID}/')
        self.assertEndpointReached(self.myob.inventory.post_item, {'company_id': CID, 'data': DATA}, 'POST', f'/{CID}/Inventory/Item/')
        self.assertEndpointReached(self.myob.inventory.delete_item, {'company_id': CID, 'uid': UID}, 'DELETE', f'/{CID}/Inventory/Item/{UID}/')

    def test_purchase_orders(self):
        self.assertEqual(repr(self.myob.purchase_orders), (
            "Purchase_OrderManager:\n"
            "                    all(company_id) - Return all purchase order types for an AccountRight company file.\n"
            "       delete_item(company_id, uid) - Delete selected item type purchase order.\n"
            "          get_item(company_id, uid) - Return selected item type purchase order.\n"
            "                   item(company_id) - Return item type purchase orders for an AccountRight company file.\n"
            "        post_item(company_id, data) - Create new item type purchase order.\n"
            "    put_item(company_id, uid, data) - Update selected item type purchase order."
        ))
        self.assertEndpointReached(self.myob.purchase_orders.all, {'company_id': CID}, 'GET', f'/{CID}/Purchase/Order/')
        self.assertEndpointReached(self.myob.purchase_orders.item, {'company_id': CID}, 'GET', f'/{CID}/Purchase/Order/Item/')
        self.assertEndpointReached(self.myob.purchase_orders.get_item, {'company_id': CID, 'uid': UID}, 'GET', f'/{CID}/Purchase/Order/Item/{UID}/')
        self.assertEndpointReached(self.myob.purchase_orders.put_item, {'company_id': CID, 'uid': UID, 'data': DATA}, 'PUT', f'/{CID}/Purchase/Order/Item/{UID}/')
        self.assertEndpointReached(self.myob.purchase_orders.post_item, {'company_id': CID, 'data': DATA}, 'POST', f'/{CID}/Purchase/Order/Item/')
        self.assertEndpointReached(self.myob.purchase_orders.delete_item, {'company_id': CID, 'uid': UID}, 'DELETE', f'/{CID}/Purchase/Order/Item/{UID}/')

    def test_purchase_bills(self):
        self.assertEqual(repr(self.myob.purchase_bills), (
            "Purchase_BillManager:\n"
            "                       all(company_id) - Return all purchase bill types for an AccountRight company file.\n"
            "          delete_item(company_id, uid) - Delete selected item type purchase bill.\n"
            "       delete_service(company_id, uid) - Delete selected service type purchase bill.\n"
            "             get_item(company_id, uid) - Return selected item type purchase bill.\n"
            "          get_service(company_id, uid) - Return selected service type purchase bill.\n"
            "                      item(company_id) - Return item type purchase bills for an AccountRight company file.\n"
            "           post_item(company_id, data) - Create new item type purchase bill.\n"
            "        post_service(company_id, data) - Create new service type purchase bill.\n"
            "       put_item(company_id, uid, data) - Update selected item type purchase bill.\n"
            "    put_service(company_id, uid, data) - Update selected service type purchase bill.\n"
            "                   service(company_id) - Return service type purchase bills for an AccountRight company file."
        ))
        self.assertEndpointReached(self.myob.purchase_bills.all, {'company_id': CID}, 'GET', f'/{CID}/Purchase/Bill/')
        self.assertEndpointReached(self.myob.purchase_bills.item, {'company_id': CID}, 'GET', f'/{CID}/Purchase/Bill/Item/')
        self.assertEndpointReached(self.myob.purchase_bills.get_item, {'company_id': CID, 'uid': UID}, 'GET', f'/{CID}/Purchase/Bill/Item/{UID}/')
        self.assertEndpointReached(self.myob.purchase_bills.put_item, {'company_id': CID, 'uid': UID, 'data': DATA}, 'PUT', f'/{CID}/Purchase/Bill/Item/{UID}/')
        self.assertEndpointReached(self.myob.purchase_bills.post_item, {'company_id': CID, 'data': DATA}, 'POST', f'/{CID}/Purchase/Bill/Item/')
        self.assertEndpointReached(self.myob.purchase_bills.delete_item, {'company_id': CID, 'uid': UID}, 'DELETE', f'/{CID}/Purchase/Bill/Item/{UID}/')
        self.assertEndpointReached(self.myob.purchase_bills.service, {'company_id': CID}, 'GET', f'/{CID}/Purchase/Bill/Service/')
        self.assertEndpointReached(self.myob.purchase_bills.get_service, {'company_id': CID, 'uid': UID}, 'GET', f'/{CID}/Purchase/Bill/Service/{UID}/')
        self.assertEndpointReached(self.myob.purchase_bills.put_service, {'company_id': CID, 'uid': UID, 'data': DATA}, 'PUT', f'/{CID}/Purchase/Bill/Service/{UID}/')
        self.assertEndpointReached(self.myob.purchase_bills.post_service, {'company_id': CID, 'data': DATA}, 'POST', f'/{CID}/Purchase/Bill/Service/')
        self.assertEndpointReached(self.myob.purchase_bills.delete_service, {'company_id': CID, 'uid': UID}, 'DELETE', f'/{CID}/Purchase/Bill/Service/{UID}/')
