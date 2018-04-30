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

    def test_companyfiles(self):
        self.assertEndpointReached(self.myob.companyfiles.all, {}, 'GET', '/')
        self.assertEndpointReached(self.myob.companyfiles.get, {'id': CID}, 'GET', f'/{CID}/')
        self.assertEndpointReached(self.myob.companyfiles.info, {}, 'GET', '/Info/')

    def test_contacts(self):
        self.assertEndpointReached(self.myob.contacts.all, {'company_id': CID}, 'GET', f'/{CID}/Contact/')
        self.assertEndpointReached(self.myob.contacts.customer, {'company_id': CID}, 'GET', f'/{CID}/Contact/Customer/')
        self.assertEndpointReached(self.myob.contacts.get_customer, {'company_id': CID, 'uid': UID}, 'GET', f'/{CID}/Contact/Customer/{UID}/')
        self.assertEndpointReached(self.myob.contacts.put_customer, {'company_id': CID, 'uid': UID, 'data': DATA}, 'PUT', f'/{CID}/Contact/Customer/{UID}/')
        self.assertEndpointReached(self.myob.contacts.post_customer, {'company_id': CID, 'data': DATA}, 'POST', f'/{CID}/Contact/Customer/')
        self.assertEndpointReached(self.myob.contacts.delete_customer, {'company_id': CID, 'uid': UID}, 'DELETE', f'/{CID}/Contact/Customer/{UID}/')

    def test_invoices(self):
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
        self.assertEndpointReached(self.myob.inventory.item, {'company_id': CID}, 'GET', f'/{CID}/Inventory/Item/')
        self.assertEndpointReached(self.myob.inventory.get_item, {'company_id': CID, 'uid': UID}, 'GET', f'/{CID}/Inventory/Item/{UID}/')
        self.assertEndpointReached(self.myob.inventory.put_item, {'company_id': CID, 'uid': UID, 'data': DATA}, 'PUT', f'/{CID}/Inventory/Item/{UID}/')
        self.assertEndpointReached(self.myob.inventory.post_item, {'company_id': CID, 'data': DATA}, 'POST', f'/{CID}/Inventory/Item/')
        self.assertEndpointReached(self.myob.inventory.delete_item, {'company_id': CID, 'uid': UID}, 'DELETE', f'/{CID}/Inventory/Item/{UID}/')

    def test_purchase_orders(self):
        self.assertEndpointReached(self.myob.purchase_orders.all, {'company_id': CID}, 'GET', f'/{CID}/Purchase/Order/')
        self.assertEndpointReached(self.myob.purchase_orders.item, {'company_id': CID}, 'GET', f'/{CID}/Purchase/Order/Item/')
        self.assertEndpointReached(self.myob.purchase_orders.get_item, {'company_id': CID, 'uid': UID}, 'GET', f'/{CID}/Purchase/Order/Item/{UID}/')
        self.assertEndpointReached(self.myob.purchase_orders.put_item, {'company_id': CID, 'uid': UID, 'data': DATA}, 'PUT', f'/{CID}/Purchase/Order/Item/{UID}/')
        self.assertEndpointReached(self.myob.purchase_orders.post_item, {'company_id': CID, 'data': DATA}, 'POST', f'/{CID}/Purchase/Order/Item/')
        self.assertEndpointReached(self.myob.purchase_orders.delete_item, {'company_id': CID, 'uid': UID}, 'DELETE', f'/{CID}/Purchase/Order/Item/{UID}/')

    def test_purchase_bills(self):
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
