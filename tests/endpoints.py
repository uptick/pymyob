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
            companyfile_credentials={CID: '!encoded-userpass='}
        )
        self.myob = Myob(cred)
        self.companyfile = self.myob.companyfiles.get(CID, call=False)
        self.expected_request_headers = {
            'Authorization': 'Bearer None',
            'x-myobapi-cftoken': '!encoded-userpass=',
            'x-myobapi-key': 'KeyToTheKingdom',
            'x-myobapi-version': 'v2'
        }

    @patch('myob.managers.requests.request')
    def assertEndpointReached(self, func, params, method, endpoint, mock_request, timeout=None):
        mock_request.return_value.status_code = 200
        print(endpoint)
        if endpoint == '/%s/' % CID:
            mock_request.return_value.json.return_value = {'CompanyFile': {'Id': CID}}
        func(**params)
        full_endpoint = 'https://api.myob.com/accountright' + endpoint
        mock_request.assert_called_once_with(
            method,
            full_endpoint,
            headers=self.expected_request_headers,
            params={'returnBody': 'true'} if method in ['PUT', 'POST'] else {},
            **({'json': DATA} if method in ['PUT', 'POST'] else {}),
            timeout=timeout,
        )

    def test_base(self):
        self.assertEqual(repr(self.myob), (
            "Myob:\n"
            "    companyfiles\n"
            "    info"
        ))
        # Don't expect companyfile credentials here as this endpoint is not companyfile specific.
        self.expected_request_headers['x-myobapi-cftoken'] = ''
        self.assertEndpointReached(self.myob.info, {}, 'GET', '/Info/')

    def test_companyfiles(self):
        self.assertEqual(repr(self.myob.companyfiles), (
            "CompanyFileManager:\n"
            "      all() - Return a list of company files.\n"
            "    get(id) - List endpoints available for a company file."
        ))
        # Don't expect companyfile credentials here as this endpoint is not companyfile specific.
        self.expected_request_headers['x-myobapi-cftoken'] = ''
        self.assertEndpointReached(self.myob.companyfiles.all, {}, 'GET', '/')
        self.assertEndpointReached(self.myob.companyfiles.get, {'id': CID}, 'GET', f'/{CID}/')

    def test_companyfile(self):
        self.assertEqual(repr(self.companyfile), (
            "CompanyFile:\n"
            "    banking\n"
            "    company\n"
            "    contacts\n"
            "    general_ledger\n"
            "    inventory\n"
            "    invoices\n"
            "    purchase_bills\n"
            "    purchase_orders"
        ))

    def test_banking(self):
        self.assertEqual(repr(self.companyfile.banking), (
            "BankingManager:\n"
            "                             all() - Return all banking types for an AccountRight company file.\n"
            "       delete_receivemoneytxn(uid) - Delete selected receivemoneytxn.\n"
            "         delete_spendmoneytxn(uid) - Delete selected spendmoneytxn.\n"
            "          get_receivemoneytxn(uid) - Return selected receivemoneytxn.\n"
            "            get_spendmoneytxn(uid) - Return selected spendmoneytxn.\n"
            "        post_receivemoneytxn(data) - Create new receivemoneytxn.\n"
            "          post_spendmoneytxn(data) - Create new spendmoneytxn.\n"
            "    put_receivemoneytxn(uid, data) - Update selected receivemoneytxn.\n"
            "      put_spendmoneytxn(uid, data) - Update selected spendmoneytxn.\n"
            "                 receivemoneytxn() - Return all receivemoneytxns for an AccountRight company file.\n"
            "                   spendmoneytxn() - Return all spendmoneytxns for an AccountRight company file."
        ))
        self.assertEndpointReached(self.companyfile.banking.all, {}, 'GET', f'/{CID}/Banking/')
        self.assertEndpointReached(self.companyfile.banking.spendmoneytxn, {}, 'GET', f'/{CID}/Banking/SpendMoneyTxn/')
        self.assertEndpointReached(self.companyfile.banking.get_spendmoneytxn, {'uid': UID}, 'GET', f'/{CID}/Banking/SpendMoneyTxn/{UID}/')
        self.assertEndpointReached(self.companyfile.banking.put_spendmoneytxn, {'uid': UID, 'data': DATA}, 'PUT', f'/{CID}/Banking/SpendMoneyTxn/{UID}/')
        self.assertEndpointReached(self.companyfile.banking.post_spendmoneytxn, {'data': DATA}, 'POST', f'/{CID}/Banking/SpendMoneyTxn/')
        self.assertEndpointReached(self.companyfile.banking.delete_spendmoneytxn, {'uid': UID}, 'DELETE', f'/{CID}/Banking/SpendMoneyTxn/{UID}/')
        self.assertEndpointReached(self.companyfile.banking.receivemoneytxn, {}, 'GET', f'/{CID}/Banking/ReceiveMoneyTxn/')
        self.assertEndpointReached(self.companyfile.banking.get_receivemoneytxn, {'uid': UID}, 'GET', f'/{CID}/Banking/ReceiveMoneyTxn/{UID}/')
        self.assertEndpointReached(self.companyfile.banking.put_receivemoneytxn, {'uid': UID, 'data': DATA}, 'PUT', f'/{CID}/Banking/ReceiveMoneyTxn/{UID}/')
        self.assertEndpointReached(self.companyfile.banking.post_receivemoneytxn, {'data': DATA}, 'POST', f'/{CID}/Banking/ReceiveMoneyTxn/')
        self.assertEndpointReached(self.companyfile.banking.delete_receivemoneytxn, {'uid': UID}, 'DELETE', f'/{CID}/Banking/ReceiveMoneyTxn/{UID}/')

    def test_contacts(self):
        self.assertEqual(repr(self.companyfile.contacts), (
            "ContactManager:\n"
            "                      all() - Return all contact types for an AccountRight company file.\n"
            "                 customer() - Return all customer contacts for an AccountRight company file.\n"
            "       delete_customer(uid) - Delete selected customer contact.\n"
            "       delete_supplier(uid) - Delete selected supplier contact.\n"
            "          get_customer(uid) - Return selected customer contact.\n"
            "          get_supplier(uid) - Return selected supplier contact.\n"
            "        post_customer(data) - Create new customer contact.\n"
            "        post_supplier(data) - Create new supplier contact.\n"
            "    put_customer(uid, data) - Update selected customer contact.\n"
            "    put_supplier(uid, data) - Update selected supplier contact.\n"
            "                 supplier() - Return all supplier contacts for an AccountRight company file."
        ))
        self.assertEndpointReached(self.companyfile.contacts.all, {}, 'GET', f'/{CID}/Contact/')
        self.assertEndpointReached(self.companyfile.contacts.customer, {}, 'GET', f'/{CID}/Contact/Customer/')
        self.assertEndpointReached(self.companyfile.contacts.get_customer, {'uid': UID}, 'GET', f'/{CID}/Contact/Customer/{UID}/')
        self.assertEndpointReached(self.companyfile.contacts.put_customer, {'uid': UID, 'data': DATA}, 'PUT', f'/{CID}/Contact/Customer/{UID}/')
        self.assertEndpointReached(self.companyfile.contacts.post_customer, {'data': DATA}, 'POST', f'/{CID}/Contact/Customer/')
        self.assertEndpointReached(self.companyfile.contacts.delete_customer, {'uid': UID}, 'DELETE', f'/{CID}/Contact/Customer/{UID}/')
        self.assertEndpointReached(self.companyfile.contacts.supplier, {}, 'GET', f'/{CID}/Contact/Supplier/')
        self.assertEndpointReached(self.companyfile.contacts.get_supplier, {'uid': UID}, 'GET', f'/{CID}/Contact/Supplier/{UID}/')
        self.assertEndpointReached(self.companyfile.contacts.put_supplier, {'uid': UID, 'data': DATA}, 'PUT', f'/{CID}/Contact/Supplier/{UID}/')
        self.assertEndpointReached(self.companyfile.contacts.post_supplier, {'data': DATA}, 'POST', f'/{CID}/Contact/Supplier/')
        self.assertEndpointReached(self.companyfile.contacts.delete_supplier, {'uid': UID}, 'DELETE', f'/{CID}/Contact/Supplier/{UID}/')

    def test_invoices(self):
        self.assertEqual(repr(self.companyfile.invoices), (
            "Sale_InvoiceManager:\n"
            "                     all() - Return all sale invoice types for an AccountRight company file.\n"
            "          delete_item(uid) - Delete selected item type sale invoice.\n"
            "       delete_service(uid) - Delete selected service type sale invoice.\n"
            "             get_item(uid) - Return selected item type sale invoice.\n"
            "          get_service(uid) - Return selected service type sale invoice.\n"
            "                    item() - Return item type sale invoices for an AccountRight company file.\n"
            "           post_item(data) - Create new item type sale invoice.\n"
            "        post_service(data) - Create new service type sale invoice.\n"
            "       put_item(uid, data) - Update selected item type sale invoice.\n"
            "    put_service(uid, data) - Update selected service type sale invoice.\n"
            "                 service() - Return service type sale invoices for an AccountRight company file."
        ))
        self.assertEndpointReached(self.companyfile.invoices.all, {}, 'GET', f'/{CID}/Sale/Invoice/')
        self.assertEndpointReached(self.companyfile.invoices.item, {}, 'GET', f'/{CID}/Sale/Invoice/Item/')
        self.assertEndpointReached(self.companyfile.invoices.get_item, {'uid': UID}, 'GET', f'/{CID}/Sale/Invoice/Item/{UID}/')
        self.assertEndpointReached(self.companyfile.invoices.put_item, {'uid': UID, 'data': DATA}, 'PUT', f'/{CID}/Sale/Invoice/Item/{UID}/')
        self.assertEndpointReached(self.companyfile.invoices.post_item, {'data': DATA}, 'POST', f'/{CID}/Sale/Invoice/Item/')
        self.assertEndpointReached(self.companyfile.invoices.delete_item, {'uid': UID}, 'DELETE', f'/{CID}/Sale/Invoice/Item/{UID}/')
        self.assertEndpointReached(self.companyfile.invoices.service, {}, 'GET', f'/{CID}/Sale/Invoice/Service/')
        self.assertEndpointReached(self.companyfile.invoices.get_service, {'uid': UID}, 'GET', f'/{CID}/Sale/Invoice/Service/{UID}/')
        self.assertEndpointReached(self.companyfile.invoices.put_service, {'uid': UID, 'data': DATA}, 'PUT', f'/{CID}/Sale/Invoice/Service/{UID}/')
        self.assertEndpointReached(self.companyfile.invoices.post_service, {'data': DATA}, 'POST', f'/{CID}/Sale/Invoice/Service/')
        self.assertEndpointReached(self.companyfile.invoices.delete_service, {'uid': UID}, 'DELETE', f'/{CID}/Sale/Invoice/Service/{UID}/')

    def test_general_ledger(self):
        self.assertEqual(repr(self.companyfile.general_ledger), (
            "GeneralLedgerManager:\n"
            "                 account() - Return accounts set up with an AccountRight company file.\n"
            "       delete_account(uid) - Delete selected account.\n"
            "       delete_taxcode(uid) - Delete selected tax code.\n"
            "          get_account(uid) - Return selected account.\n"
            "          get_taxcode(uid) - Return selected tax code.\n"
            "        post_account(data) - Create new account.\n"
            "        post_taxcode(data) - Create new tax code.\n"
            "    put_account(uid, data) - Update selected accounts.\n"
            "    put_taxcode(uid, data) - Update selected tax codes.\n"
            "                 taxcode() - Return tax codes set up with an AccountRight company file."
        ))
        self.assertEndpointReached(self.companyfile.general_ledger.taxcode, {}, 'GET', f'/{CID}/GeneralLedger/TaxCode/')
        self.assertEndpointReached(self.companyfile.general_ledger.get_taxcode, {'uid': UID}, 'GET', f'/{CID}/GeneralLedger/TaxCode/{UID}/')
        self.assertEndpointReached(self.companyfile.general_ledger.put_taxcode, {'uid': UID, 'data': DATA}, 'PUT', f'/{CID}/GeneralLedger/TaxCode/{UID}/')
        self.assertEndpointReached(self.companyfile.general_ledger.post_taxcode, {'data': DATA}, 'POST', f'/{CID}/GeneralLedger/TaxCode/')
        self.assertEndpointReached(self.companyfile.general_ledger.delete_taxcode, {'uid': UID}, 'DELETE', f'/{CID}/GeneralLedger/TaxCode/{UID}/')
        self.assertEndpointReached(self.companyfile.general_ledger.account, {}, 'GET', f'/{CID}/GeneralLedger/Account/')
        self.assertEndpointReached(self.companyfile.general_ledger.get_account, {'uid': UID}, 'GET', f'/{CID}/GeneralLedger/Account/{UID}/')
        self.assertEndpointReached(self.companyfile.general_ledger.put_account, {'uid': UID, 'data': DATA}, 'PUT', f'/{CID}/GeneralLedger/Account/{UID}/')
        self.assertEndpointReached(self.companyfile.general_ledger.post_account, {'data': DATA}, 'POST', f'/{CID}/GeneralLedger/Account/')
        self.assertEndpointReached(self.companyfile.general_ledger.delete_account, {'uid': UID}, 'DELETE', f'/{CID}/GeneralLedger/Account/{UID}/')

    def test_inventory(self):
        self.assertEqual(repr(self.companyfile.inventory), (
            "InventoryManager:\n"
            "       delete_item(uid) - Delete selected inventory item.\n"
            "          get_item(uid) - Return selected inventory item.\n"
            "                 item() - Return inventory items for an AccountRight company file.\n"
            "        post_item(data) - Create new inventory item.\n"
            "    put_item(uid, data) - Update selected inventory items."
        ))
        self.assertEndpointReached(self.companyfile.inventory.item, {}, 'GET', f'/{CID}/Inventory/Item/')
        self.assertEndpointReached(self.companyfile.inventory.get_item, {'uid': UID}, 'GET', f'/{CID}/Inventory/Item/{UID}/')
        self.assertEndpointReached(self.companyfile.inventory.put_item, {'uid': UID, 'data': DATA}, 'PUT', f'/{CID}/Inventory/Item/{UID}/')
        self.assertEndpointReached(self.companyfile.inventory.post_item, {'data': DATA}, 'POST', f'/{CID}/Inventory/Item/')
        self.assertEndpointReached(self.companyfile.inventory.delete_item, {'uid': UID}, 'DELETE', f'/{CID}/Inventory/Item/{UID}/')

    def test_purchase_orders(self):
        self.assertEqual(repr(self.companyfile.purchase_orders), (
            "Purchase_OrderManager:\n"
            "                  all() - Return all purchase order types for an AccountRight company file.\n"
            "       delete_item(uid) - Delete selected item type purchase order.\n"
            "          get_item(uid) - Return selected item type purchase order.\n"
            "                 item() - Return item type purchase orders for an AccountRight company file.\n"
            "        post_item(data) - Create new item type purchase order.\n"
            "    put_item(uid, data) - Update selected item type purchase order."
        ))
        self.assertEndpointReached(self.companyfile.purchase_orders.all, {}, 'GET', f'/{CID}/Purchase/Order/')
        self.assertEndpointReached(self.companyfile.purchase_orders.item, {}, 'GET', f'/{CID}/Purchase/Order/Item/')
        self.assertEndpointReached(self.companyfile.purchase_orders.get_item, {'uid': UID}, 'GET', f'/{CID}/Purchase/Order/Item/{UID}/')
        self.assertEndpointReached(self.companyfile.purchase_orders.put_item, {'uid': UID, 'data': DATA}, 'PUT', f'/{CID}/Purchase/Order/Item/{UID}/')
        self.assertEndpointReached(self.companyfile.purchase_orders.post_item, {'data': DATA}, 'POST', f'/{CID}/Purchase/Order/Item/')
        self.assertEndpointReached(self.companyfile.purchase_orders.delete_item, {'uid': UID}, 'DELETE', f'/{CID}/Purchase/Order/Item/{UID}/')

    def test_purchase_bills(self):
        self.assertEqual(repr(self.companyfile.purchase_bills), (
            "Purchase_BillManager:\n"
            "                     all() - Return all purchase bill types for an AccountRight company file.\n"
            "          delete_item(uid) - Delete selected item type purchase bill.\n"
            "       delete_service(uid) - Delete selected service type purchase bill.\n"
            "             get_item(uid) - Return selected item type purchase bill.\n"
            "          get_service(uid) - Return selected service type purchase bill.\n"
            "                    item() - Return item type purchase bills for an AccountRight company file.\n"
            "           post_item(data) - Create new item type purchase bill.\n"
            "        post_service(data) - Create new service type purchase bill.\n"
            "       put_item(uid, data) - Update selected item type purchase bill.\n"
            "    put_service(uid, data) - Update selected service type purchase bill.\n"
            "                 service() - Return service type purchase bills for an AccountRight company file."
        ))
        self.assertEndpointReached(self.companyfile.purchase_bills.all, {}, 'GET', f'/{CID}/Purchase/Bill/')
        self.assertEndpointReached(self.companyfile.purchase_bills.item, {}, 'GET', f'/{CID}/Purchase/Bill/Item/')
        self.assertEndpointReached(self.companyfile.purchase_bills.get_item, {'uid': UID}, 'GET', f'/{CID}/Purchase/Bill/Item/{UID}/')
        self.assertEndpointReached(self.companyfile.purchase_bills.put_item, {'uid': UID, 'data': DATA}, 'PUT', f'/{CID}/Purchase/Bill/Item/{UID}/')
        self.assertEndpointReached(self.companyfile.purchase_bills.post_item, {'data': DATA}, 'POST', f'/{CID}/Purchase/Bill/Item/')
        self.assertEndpointReached(self.companyfile.purchase_bills.delete_item, {'uid': UID}, 'DELETE', f'/{CID}/Purchase/Bill/Item/{UID}/')
        self.assertEndpointReached(self.companyfile.purchase_bills.service, {}, 'GET', f'/{CID}/Purchase/Bill/Service/')
        self.assertEndpointReached(self.companyfile.purchase_bills.get_service, {'uid': UID}, 'GET', f'/{CID}/Purchase/Bill/Service/{UID}/')
        self.assertEndpointReached(self.companyfile.purchase_bills.put_service, {'uid': UID, 'data': DATA}, 'PUT', f'/{CID}/Purchase/Bill/Service/{UID}/')
        self.assertEndpointReached(self.companyfile.purchase_bills.post_service, {'data': DATA}, 'POST', f'/{CID}/Purchase/Bill/Service/')
        self.assertEndpointReached(self.companyfile.purchase_bills.delete_service, {'uid': UID}, 'DELETE', f'/{CID}/Purchase/Bill/Service/{UID}/')

    def test_company(self):
        self.assertEqual(repr(self.companyfile.company), (
            "CompanyManager:\n"
            "    preferences() - Return company data file preferences for an AccountRight company file."
        ))
        self.assertEndpointReached(self.companyfile.company.preferences, {}, 'GET', f'/{CID}/Company/Preferences/')

    def test_timeout(self):
        self.assertEndpointReached(self.companyfile.contacts.all, {'timeout': 5}, 'GET', f'/{CID}/Contact/', timeout=5)
