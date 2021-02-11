from unittest import TestCase
from unittest.mock import patch

from myob import Myob
from myob.credentials import PartnerCredentials
from myob.exceptions import (
    MyobBadRequest,
    MyobExceptionUnknown,
    MyobForbidden,
    MyobGatewayTimeout,
    MyobNotFound,
    MyobRateLimitExceeded,
    MyobUnauthorized,
)

# Reusable dummy data
CID = 'DummyCompanyId'
UID = 'DummyResourceUid'
DATA = {'dummy': 'data'}


class EndpointTests(TestCase):
    maxDiff = None

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

    @patch('myob.managers.requests.request')
    def assertExceptionHandled(self, status_code, response_json, exception, mock_request):
        mock_request.return_value.status_code = status_code
        mock_request.return_value.json.return_value = response_json
        with self.assertRaises(exception):
            self.myob.info()

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
        self.assertEndpointReached(self.myob.companyfiles.get, {'id': CID}, 'GET', f'/{CID}/')
        # Don't expect companyfile credentials here as the next endpoint is not companyfile specific.
        self.expected_request_headers['x-myobapi-cftoken'] = ''
        self.assertEndpointReached(self.myob.companyfiles.all, {}, 'GET', '/')

    def test_companyfile(self):
        self.assertEqual(repr(self.companyfile), (
            "CompanyFile:\n"
            "    banking\n"
            "    company\n"
            "    contacts\n"
            "    general_ledger\n"
            "    inventory\n"
            "    invoices\n"
            "    orders\n"
            "    purchase_bills\n"
            "    purchase_orders\n"
            "    quotes"
        ))

    def test_banking(self):
        self.assertEqual(repr(self.companyfile.banking), (
            "BankingManager:\n"
            "                             all() - Return all banking types for an AccountRight company file.\n"
            "       delete_receivemoneytxn(uid) - Delete selected receive money transaction.\n"
            "         delete_spendmoneytxn(uid) - Delete selected spend money transaction.\n"
            "          get_receivemoneytxn(uid) - Return selected receive money transaction.\n"
            "            get_spendmoneytxn(uid) - Return selected spend money transaction.\n"
            "        post_receivemoneytxn(data) - Create new receive money transaction.\n"
            "          post_spendmoneytxn(data) - Create new spend money transaction.\n"
            "    put_receivemoneytxn(uid, data) - Update selected receive money transaction.\n"
            "      put_spendmoneytxn(uid, data) - Update selected spend money transaction.\n"
            "                 receivemoneytxn() - Return all receive money transactions for an AccountRight company file.\n"
            "                   spendmoneytxn() - Return all spend money transactions for an AccountRight company file."
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
            "       delete_employee(uid) - Delete selected employee card.\n"
            "       delete_supplier(uid) - Delete selected supplier contact.\n"
            "                 employee() - Return all employee cards for an AccountRight company file.\n"
            "          get_customer(uid) - Return selected customer contact.\n"
            "          get_employee(uid) - Return selected employee card.\n"
            "          get_supplier(uid) - Return selected supplier contact.\n"
            "        post_customer(data) - Create new customer contact.\n"
            "        post_employee(data) - Create new employee card.\n"
            "        post_supplier(data) - Create new supplier contact.\n"
            "    put_customer(uid, data) - Update selected customer contact.\n"
            "    put_employee(uid, data) - Update selected employee card.\n"
            "    put_supplier(uid, data) - Update selected supplier contact.\n"
            "                 supplier() - Return all supplier contacts for an AccountRight company file."
        ))
        self.assertEndpointReached(self.companyfile.contacts.all, {}, 'GET', f'/{CID}/Contact/')
        self.assertEndpointReached(self.companyfile.contacts.customer, {}, 'GET', f'/{CID}/Contact/Customer/')
        self.assertEndpointReached(self.companyfile.contacts.get_customer, {'uid': UID}, 'GET', f'/{CID}/Contact/Customer/{UID}/')
        self.assertEndpointReached(self.companyfile.contacts.put_customer, {'uid': UID, 'data': DATA}, 'PUT', f'/{CID}/Contact/Customer/{UID}/')
        self.assertEndpointReached(self.companyfile.contacts.post_customer, {'data': DATA}, 'POST', f'/{CID}/Contact/Customer/')
        self.assertEndpointReached(self.companyfile.contacts.delete_customer, {'uid': UID}, 'DELETE', f'/{CID}/Contact/Customer/{UID}/')
        self.assertEndpointReached(self.companyfile.contacts.employee, {}, 'GET', f'/{CID}/Contact/Employee/')
        self.assertEndpointReached(self.companyfile.contacts.get_employee, {'uid': UID}, 'GET', f'/{CID}/Contact/Employee/{UID}/')
        self.assertEndpointReached(self.companyfile.contacts.put_employee, {'uid': UID, 'data': DATA}, 'PUT', f'/{CID}/Contact/Employee/{UID}/')
        self.assertEndpointReached(self.companyfile.contacts.post_employee, {'data': DATA}, 'POST', f'/{CID}/Contact/Employee/')
        self.assertEndpointReached(self.companyfile.contacts.delete_employee, {'uid': UID}, 'DELETE', f'/{CID}/Contact/Employee/{UID}/')
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
            "                    item() - Return all item type sale invoices for an AccountRight company file.\n"
            "           post_item(data) - Create new item type sale invoice.\n"
            "        post_service(data) - Create new service type sale invoice.\n"
            "       put_item(uid, data) - Update selected item type sale invoice.\n"
            "    put_service(uid, data) - Update selected service type sale invoice.\n"
            "                 service() - Return all service type sale invoices for an AccountRight company file."
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

    def test_quotes(self):
        self.assertEqual(repr(self.companyfile.quotes), (
            "Sale_QuoteManager:\n"
            "                     all() - Return all sale quote types for an AccountRight company file.\n"
            "          delete_item(uid) - Delete selected item type sale quote.\n"
            "       delete_service(uid) - Delete selected service type sale quote.\n"
            "             get_item(uid) - Return selected item type sale quote.\n"
            "          get_service(uid) - Return selected service type sale quote.\n"
            "                    item() - Return all item type sale quotes for an AccountRight company file.\n"
            "           post_item(data) - Create new item type sale quote.\n"
            "        post_service(data) - Create new service type sale quote.\n"
            "       put_item(uid, data) - Update selected item type sale quote.\n"
            "    put_service(uid, data) - Update selected service type sale quote.\n"
            "                 service() - Return all service type sale quotes for an AccountRight company file."
        ))
        self.assertEndpointReached(self.companyfile.quotes.all, {}, 'GET', f'/{CID}/Sale/Quote/')
        self.assertEndpointReached(self.companyfile.quotes.item, {}, 'GET', f'/{CID}/Sale/Quote/Item/')
        self.assertEndpointReached(self.companyfile.quotes.get_item, {'uid': UID}, 'GET', f'/{CID}/Sale/Quote/Item/{UID}/')
        self.assertEndpointReached(self.companyfile.quotes.put_item, {'uid': UID, 'data': DATA}, 'PUT', f'/{CID}/Sale/Quote/Item/{UID}/')
        self.assertEndpointReached(self.companyfile.quotes.post_item, {'data': DATA}, 'POST', f'/{CID}/Sale/Quote/Item/')
        self.assertEndpointReached(self.companyfile.quotes.delete_item, {'uid': UID}, 'DELETE', f'/{CID}/Sale/Quote/Item/{UID}/')
        self.assertEndpointReached(self.companyfile.quotes.service, {}, 'GET', f'/{CID}/Sale/Quote/Service/')
        self.assertEndpointReached(self.companyfile.quotes.get_service, {'uid': UID}, 'GET', f'/{CID}/Sale/Quote/Service/{UID}/')
        self.assertEndpointReached(self.companyfile.quotes.put_service, {'uid': UID, 'data': DATA}, 'PUT', f'/{CID}/Sale/Quote/Service/{UID}/')
        self.assertEndpointReached(self.companyfile.quotes.post_service, {'data': DATA}, 'POST', f'/{CID}/Sale/Quote/Service/')
        self.assertEndpointReached(self.companyfile.quotes.delete_service, {'uid': UID}, 'DELETE', f'/{CID}/Sale/Quote/Service/{UID}/')

    def test_orders(self):
        self.assertEqual(repr(self.companyfile.orders), (
            "Sale_OrderManager:\n"
            "                     all() - Return all sale order types for an AccountRight company file.\n"
            "          delete_item(uid) - Delete selected item type sale order.\n"
            "       delete_service(uid) - Delete selected service type sale order.\n"
            "             get_item(uid) - Return selected item type sale order.\n"
            "          get_service(uid) - Return selected service type sale order.\n"
            "                    item() - Return all item type sale orders for an AccountRight company file.\n"
            "           post_item(data) - Create new item type sale order.\n"
            "        post_service(data) - Create new service type sale order.\n"
            "       put_item(uid, data) - Update selected item type sale order.\n"
            "    put_service(uid, data) - Update selected service type sale order.\n"
            "                 service() - Return all service type sale orders for an AccountRight company file."
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
            "                  account() - Return all accounts for an AccountRight company file.\n"
            "                 category() - Return all cost center tracking categories for an AccountRight company file.\n"
            "        delete_account(uid) - Delete selected account.\n"
            "       delete_category(uid) - Delete selected cost center tracking category.\n"
            "            delete_job(uid) - Delete selected job.\n"
            "        delete_taxcode(uid) - Delete selected tax code.\n"
            "           get_account(uid) - Return selected account.\n"
            "          get_category(uid) - Return selected cost center tracking category.\n"
            "               get_job(uid) - Return selected job.\n"
            "           get_taxcode(uid) - Return selected tax code.\n"
            "                      job() - Return all jobs for an AccountRight company file.\n"
            "         post_account(data) - Create new account.\n"
            "        post_category(data) - Create new cost center tracking category.\n"
            "             post_job(data) - Create new job.\n"
            "         post_taxcode(data) - Create new tax code.\n"
            "     put_account(uid, data) - Update selected account.\n"
            "    put_category(uid, data) - Update selected cost center tracking category.\n"
            "         put_job(uid, data) - Update selected job.\n"
            "     put_taxcode(uid, data) - Update selected tax code.\n"
            "                  taxcode() - Return all tax codes for an AccountRight company file."
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
        self.assertEndpointReached(self.companyfile.general_ledger.category, {}, 'GET', f'/{CID}/GeneralLedger/Category/')
        self.assertEndpointReached(self.companyfile.general_ledger.get_category, {'uid': UID}, 'GET', f'/{CID}/GeneralLedger/Category/{UID}/')
        self.assertEndpointReached(self.companyfile.general_ledger.put_category, {'uid': UID, 'data': DATA}, 'PUT', f'/{CID}/GeneralLedger/Category/{UID}/')
        self.assertEndpointReached(self.companyfile.general_ledger.post_category, {'data': DATA}, 'POST', f'/{CID}/GeneralLedger/Category/')
        self.assertEndpointReached(self.companyfile.general_ledger.delete_category, {'uid': UID}, 'DELETE', f'/{CID}/GeneralLedger/Category/{UID}/')

    def test_inventory(self):
        self.assertEqual(repr(self.companyfile.inventory), (
            "InventoryManager:\n"
            "           delete_item(uid) - Delete selected inventory item.\n"
            "       delete_location(uid) - Delete selected inventory location.\n"
            "              get_item(uid) - Return selected inventory item.\n"
            "          get_location(uid) - Return selected inventory location.\n"
            "                     item() - Return all inventory items for an AccountRight company file.\n"
            "                 location() - Return all inventory locations for an AccountRight company file.\n"
            "            post_item(data) - Create new inventory item.\n"
            "        post_location(data) - Create new inventory location.\n"
            "        put_item(uid, data) - Update selected inventory item.\n"
            "    put_location(uid, data) - Update selected inventory location."
        ))
        self.assertEndpointReached(self.companyfile.inventory.item, {}, 'GET', f'/{CID}/Inventory/Item/')
        self.assertEndpointReached(self.companyfile.inventory.get_item, {'uid': UID}, 'GET', f'/{CID}/Inventory/Item/{UID}/')
        self.assertEndpointReached(self.companyfile.inventory.put_item, {'uid': UID, 'data': DATA}, 'PUT', f'/{CID}/Inventory/Item/{UID}/')
        self.assertEndpointReached(self.companyfile.inventory.post_item, {'data': DATA}, 'POST', f'/{CID}/Inventory/Item/')
        self.assertEndpointReached(self.companyfile.inventory.delete_item, {'uid': UID}, 'DELETE', f'/{CID}/Inventory/Item/{UID}/')
        self.assertEndpointReached(self.companyfile.inventory.location, {}, 'GET', f'/{CID}/Inventory/Location/')
        self.assertEndpointReached(self.companyfile.inventory.get_location, {'uid': UID}, 'GET', f'/{CID}/Inventory/Location/{UID}/')
        self.assertEndpointReached(self.companyfile.inventory.put_location, {'uid': UID, 'data': DATA}, 'PUT', f'/{CID}/Inventory/Location/{UID}/')
        self.assertEndpointReached(self.companyfile.inventory.post_location, {'data': DATA}, 'POST', f'/{CID}/Inventory/Location/')
        self.assertEndpointReached(self.companyfile.inventory.delete_location, {'uid': UID}, 'DELETE', f'/{CID}/Inventory/Location/{UID}/')

    def test_purchase_orders(self):
        self.assertEqual(repr(self.companyfile.purchase_orders), (
            "Purchase_OrderManager:\n"
            "                  all() - Return all purchase order types for an AccountRight company file.\n"
            "       delete_item(uid) - Delete selected item type purchase order.\n"
            "          get_item(uid) - Return selected item type purchase order.\n"
            "                 item() - Return all item type purchase orders for an AccountRight company file.\n"
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
            "                           all() - Return all purchase bill types for an AccountRight company file.\n"
            "                delete_item(uid) - Delete selected item type purchase bill.\n"
            "       delete_miscellaneous(uid) - Delete selected miscellaneous type purchase bill.\n"
            "             delete_service(uid) - Delete selected service type purchase bill.\n"
            "                   get_item(uid) - Return selected item type purchase bill.\n"
            "          get_miscellaneous(uid) - Return selected miscellaneous type purchase bill.\n"
            "                get_service(uid) - Return selected service type purchase bill.\n"
            "                          item() - Return all item type purchase bills for an AccountRight company file.\n"
            "                 miscellaneous() - Return all miscellaneous type purchase bills for an AccountRight company file.\n"
            "                 post_item(data) - Create new item type purchase bill.\n"
            "        post_miscellaneous(data) - Create new miscellaneous type purchase bill.\n"
            "              post_service(data) - Create new service type purchase bill.\n"
            "             put_item(uid, data) - Update selected item type purchase bill.\n"
            "    put_miscellaneous(uid, data) - Update selected miscellaneous type purchase bill.\n"
            "          put_service(uid, data) - Update selected service type purchase bill.\n"
            "                       service() - Return all service type purchase bills for an AccountRight company file."
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
        self.assertEndpointReached(self.companyfile.purchase_bills.miscellaneous, {}, 'GET', f'/{CID}/Purchase/Bill/Miscellaneous/')
        self.assertEndpointReached(self.companyfile.purchase_bills.get_miscellaneous, {'uid': UID}, 'GET', f'/{CID}/Purchase/Bill/Miscellaneous/{UID}/')
        self.assertEndpointReached(self.companyfile.purchase_bills.put_miscellaneous, {'uid': UID, 'data': DATA}, 'PUT', f'/{CID}/Purchase/Bill/Miscellaneous/{UID}/')
        self.assertEndpointReached(self.companyfile.purchase_bills.post_miscellaneous, {'data': DATA}, 'POST', f'/{CID}/Purchase/Bill/Miscellaneous/')
        self.assertEndpointReached(self.companyfile.purchase_bills.delete_miscellaneous, {'uid': UID}, 'DELETE', f'/{CID}/Purchase/Bill/Miscellaneous/{UID}/')

    def test_company(self):
        self.assertEqual(repr(self.companyfile.company), (
            "CompanyManager:\n"
            "    preferences() - Return all company data file preferences for an AccountRight company file."
        ))
        self.assertEndpointReached(self.companyfile.company.preferences, {}, 'GET', f'/{CID}/Company/Preferences/')

    def test_timeout(self):
        self.assertEndpointReached(self.companyfile.contacts.all, {'timeout': 5}, 'GET', f'/{CID}/Contact/', timeout=5)

    def test_exceptions(self):
        self.assertExceptionHandled(400, {}, MyobBadRequest)
        self.assertExceptionHandled(401, {}, MyobUnauthorized)
        self.assertExceptionHandled(403, {'Errors': [{'Name': 'Something'}]}, MyobForbidden)
        self.assertExceptionHandled(403, {'Errors': [{'Name': 'RateLimitError'}]}, MyobRateLimitExceeded)
        self.assertExceptionHandled(404, {}, MyobNotFound)
        self.assertExceptionHandled(504, {}, MyobGatewayTimeout)
        self.assertExceptionHandled(418, {}, MyobExceptionUnknown)
