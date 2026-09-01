from json import JSONDecodeError
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
BID = "DummyBusinessId"
UID = "DummyResourceUid"
DATA = {"dummy": "data"}


class EndpointTests(TestCase):
    maxDiff = None

    def setUp(self):
        cred = PartnerCredentials(
            consumer_key="KeyToTheKingdom",
            consumer_secret="TellNoOne",  # noqa: S106
            callback_uri="CallOnlyWhenCalledTo",
            business_id=BID,
        )
        self.myob = Myob(cred)
        self.expected_request_headers = {
            "Authorization": "Bearer None",
            "x-myobapi-key": "KeyToTheKingdom",
            "x-myobapi-version": "v2",
        }

    @patch("myob.managers.requests.request")
    def assertEndpointReached(self, func, params, method, endpoint, mock_request, timeout=None):  # noqa: N802
        mock_request.return_value.status_code = 200
        if endpoint == f"/{BID}/":
            mock_request.return_value.json.return_value = {"CompanyFile": {"Id": BID}}
        func(**params)
        full_endpoint = "https://api.myob.com/accountright" + endpoint
        mock_request.assert_called_once_with(
            method,
            full_endpoint,
            headers=self.expected_request_headers,
            params={"returnBody": "true"} if method in ["PUT", "POST"] else {},
            **({"json": DATA} if method in ["PUT", "POST"] else {}),
            timeout=timeout,
        )

    @patch("myob.managers.requests.request")
    def assertExceptionHandled(self, status_code, response_json, exception, mock_request):  # noqa: N802
        mock_request.return_value.status_code = status_code
        mock_request.return_value.json.return_value = response_json
        with self.assertRaises(exception):
            self.myob.info()

    def test_base(self):
        self.assertEqual(
            repr(self.myob),
            (
                "Myob:\n"
                "    banking\n"
                "    business\n"
                "    company\n"
                "    contacts\n"
                "    credit_refunds\n"
                "    credit_settlements\n"
                "    customer_payments\n"
                "    debit_refunds\n"
                "    debit_settlements\n"
                "    general_ledger\n"
                "    info\n"
                "    inventory\n"
                "    invoices\n"
                "    orders\n"
                "    purchase_bills\n"
                "    purchase_orders\n"
                "    quotes\n"
                "    supplier_payments"
            ),
        )
        self.assertEndpointReached(self.myob.info, {}, "GET", "/Info/")

    @patch("myob.managers.requests.request")
    def test_json_error(self, mock_request):
        mock_request.return_value.status_code = 200

        def response_json():
            raise JSONDecodeError("Some error message", "", 0)

        mock_request.return_value.json = response_json

        # Empty response to DELETE returns empty dict
        mock_request.return_value.content = b""
        result = self.myob.banking.delete_transfermoneytxn(uid=UID)
        self.assertEqual(result, {})

        # JSON error from non-empty DELETE response gets raised
        mock_request.return_value.content = "{"
        with self.assertRaises(ValueError):
            self.myob.banking.delete_transfermoneytxn(uid=UID)

        # JSON error from non-DELETE request gets raised, regardless of content
        mock_request.return_value.content = b""
        with self.assertRaises(ValueError):
            self.myob.banking.all()

        with self.assertRaises(ValueError):
            self.myob.banking.post_spendmoneytxn(data=DATA)

        with self.assertRaises(ValueError):
            self.myob.banking.put_transfermoneytxn(uid=UID, data=DATA)

        mock_request.return_value.content = "{"
        with self.assertRaises(ValueError):
            self.myob.banking.all()

        with self.assertRaises(ValueError):
            self.myob.banking.post_spendmoneytxn(data=DATA)

        with self.assertRaises(ValueError):
            self.myob.banking.put_transfermoneytxn(uid=UID, data=DATA)

    def test_business(self):
        self.assertEndpointReached(self.myob.business, {}, "GET", f"/{BID}/")

    @patch("myob.managers.requests.request")
    def test_business_unwraps_the_response_envelope(self, mock_request):
        mock_request.return_value.status_code = 200
        mock_request.return_value.json.return_value = {"CompanyFile": {"Id": BID, "Name": "Acme"}}
        self.assertEqual(self.myob.business(), {"Id": BID, "Name": "Acme"})

    def test_credentials_without_a_business_are_rejected(self):
        cred = PartnerCredentials(
            consumer_key="KeyToTheKingdom",
            consumer_secret="TellNoOne",  # noqa: S106
            callback_uri="CallOnlyWhenCalledTo",
        )
        with self.assertRaises(ValueError):
            Myob(cred)

    def test_banking(self):
        self.assertEqual(
            repr(self.myob.banking),
            (
                "BankingManager:\n"
                "                              all() - Return all banking types for a business.\n"
                "        delete_receivemoneytxn(uid) - Delete selected receive money transaction.\n"
                "          delete_spendmoneytxn(uid) - Delete selected spend money transaction.\n"
                "       delete_transfermoneytxn(uid) - Delete selected transfer money transaction.\n"
                "           get_receivemoneytxn(uid) - Return selected receive money transaction.\n"
                "             get_spendmoneytxn(uid) - Return selected spend money transaction.\n"
                "          get_transfermoneytxn(uid) - Return selected transfer money transaction.\n"
                "         post_receivemoneytxn(data) - Create new receive money transaction.\n"
                "           post_spendmoneytxn(data) - Create new spend money transaction.\n"
                "        post_transfermoneytxn(data) - Create new transfer money transaction.\n"
                "     put_receivemoneytxn(uid, data) - Update selected receive money transaction.\n"
                "       put_spendmoneytxn(uid, data) - Update selected spend money transaction.\n"
                "    put_transfermoneytxn(uid, data) - Update selected transfer money transaction.\n"
                "                  receivemoneytxn() - Return all receive money transactions for a business.\n"
                "                    spendmoneytxn() - Return all spend money transactions for a business.\n"
                "                 transfermoneytxn() - Return all transfer money transactions for a business."
            ),
        )
        self.assertEndpointReached(self.myob.banking.all, {}, "GET", f"/{BID}/Banking/")
        self.assertEndpointReached(
            self.myob.banking.spendmoneytxn,
            {},
            "GET",
            f"/{BID}/Banking/SpendMoneyTxn/",
        )
        self.assertEndpointReached(
            self.myob.banking.get_spendmoneytxn,
            {"uid": UID},
            "GET",
            f"/{BID}/Banking/SpendMoneyTxn/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.banking.put_spendmoneytxn,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{BID}/Banking/SpendMoneyTxn/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.banking.post_spendmoneytxn,
            {"data": DATA},
            "POST",
            f"/{BID}/Banking/SpendMoneyTxn/",
        )
        self.assertEndpointReached(
            self.myob.banking.delete_spendmoneytxn,
            {"uid": UID},
            "DELETE",
            f"/{BID}/Banking/SpendMoneyTxn/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.banking.receivemoneytxn,
            {},
            "GET",
            f"/{BID}/Banking/ReceiveMoneyTxn/",
        )
        self.assertEndpointReached(
            self.myob.banking.get_receivemoneytxn,
            {"uid": UID},
            "GET",
            f"/{BID}/Banking/ReceiveMoneyTxn/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.banking.put_receivemoneytxn,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{BID}/Banking/ReceiveMoneyTxn/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.banking.post_receivemoneytxn,
            {"data": DATA},
            "POST",
            f"/{BID}/Banking/ReceiveMoneyTxn/",
        )
        self.assertEndpointReached(
            self.myob.banking.delete_receivemoneytxn,
            {"uid": UID},
            "DELETE",
            f"/{BID}/Banking/ReceiveMoneyTxn/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.banking.transfermoneytxn,
            {},
            "GET",
            f"/{BID}/Banking/TransferMoneyTxn/",
        )
        self.assertEndpointReached(
            self.myob.banking.get_transfermoneytxn,
            {"uid": UID},
            "GET",
            f"/{BID}/Banking/TransferMoneyTxn/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.banking.put_transfermoneytxn,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{BID}/Banking/TransferMoneyTxn/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.banking.post_transfermoneytxn,
            {"data": DATA},
            "POST",
            f"/{BID}/Banking/TransferMoneyTxn/",
        )
        self.assertEndpointReached(
            self.myob.banking.delete_transfermoneytxn,
            {"uid": UID},
            "DELETE",
            f"/{BID}/Banking/TransferMoneyTxn/{UID}/",
        )

    def test_contacts(self):
        self.assertEqual(
            repr(self.myob.contacts),
            (
                "ContactManager:\n"
                "                      all() - Return all contact types for a business.\n"
                "                 customer() - Return all customer contacts for a business.\n"
                "       delete_customer(uid) - Delete selected customer contact.\n"
                "       delete_employee(uid) - Delete selected employee card.\n"
                "       delete_supplier(uid) - Delete selected supplier contact.\n"
                "                 employee() - Return all employee cards for a business.\n"
                "          get_customer(uid) - Return selected customer contact.\n"
                "          get_employee(uid) - Return selected employee card.\n"
                "          get_supplier(uid) - Return selected supplier contact.\n"
                "        post_customer(data) - Create new customer contact.\n"
                "        post_employee(data) - Create new employee card.\n"
                "        post_supplier(data) - Create new supplier contact.\n"
                "    put_customer(uid, data) - Update selected customer contact.\n"
                "    put_employee(uid, data) - Update selected employee card.\n"
                "    put_supplier(uid, data) - Update selected supplier contact.\n"
                "                 supplier() - Return all supplier contacts for a business."
            ),
        )
        self.assertEndpointReached(self.myob.contacts.all, {}, "GET", f"/{BID}/Contact/")
        self.assertEndpointReached(
            self.myob.contacts.customer, {}, "GET", f"/{BID}/Contact/Customer/"
        )
        self.assertEndpointReached(
            self.myob.contacts.get_customer,
            {"uid": UID},
            "GET",
            f"/{BID}/Contact/Customer/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.contacts.put_customer,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{BID}/Contact/Customer/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.contacts.post_customer,
            {"data": DATA},
            "POST",
            f"/{BID}/Contact/Customer/",
        )
        self.assertEndpointReached(
            self.myob.contacts.delete_customer,
            {"uid": UID},
            "DELETE",
            f"/{BID}/Contact/Customer/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.contacts.employee, {}, "GET", f"/{BID}/Contact/Employee/"
        )
        self.assertEndpointReached(
            self.myob.contacts.get_employee,
            {"uid": UID},
            "GET",
            f"/{BID}/Contact/Employee/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.contacts.put_employee,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{BID}/Contact/Employee/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.contacts.post_employee,
            {"data": DATA},
            "POST",
            f"/{BID}/Contact/Employee/",
        )
        self.assertEndpointReached(
            self.myob.contacts.delete_employee,
            {"uid": UID},
            "DELETE",
            f"/{BID}/Contact/Employee/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.contacts.supplier, {}, "GET", f"/{BID}/Contact/Supplier/"
        )
        self.assertEndpointReached(
            self.myob.contacts.get_supplier,
            {"uid": UID},
            "GET",
            f"/{BID}/Contact/Supplier/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.contacts.put_supplier,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{BID}/Contact/Supplier/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.contacts.post_supplier,
            {"data": DATA},
            "POST",
            f"/{BID}/Contact/Supplier/",
        )
        self.assertEndpointReached(
            self.myob.contacts.delete_supplier,
            {"uid": UID},
            "DELETE",
            f"/{BID}/Contact/Supplier/{UID}/",
        )

    def test_invoices(self):
        self.assertEqual(
            repr(self.myob.invoices),
            (
                "Sale_InvoiceManager:\n"
                "                     all() - Return all sale invoice types for a business.\n"
                "          delete_item(uid) - Delete selected item type sale invoice.\n"
                "       delete_service(uid) - Delete selected service type sale invoice.\n"
                "             get_item(uid) - Return selected item type sale invoice.\n"
                "          get_service(uid) - Return selected service type sale invoice.\n"
                "                    item() - Return all item type sale invoices for a business.\n"
                "           post_item(data) - Create new item type sale invoice.\n"
                "        post_service(data) - Create new service type sale invoice.\n"
                "       put_item(uid, data) - Update selected item type sale invoice.\n"
                "    put_service(uid, data) - Update selected service type sale invoice.\n"
                "                 service() - Return all service type sale invoices for a business."
            ),
        )
        self.assertEndpointReached(
            self.myob.invoices.all, {}, "GET", f"/{BID}/Sale/Invoice/"
        )
        self.assertEndpointReached(
            self.myob.invoices.item, {}, "GET", f"/{BID}/Sale/Invoice/Item/"
        )
        self.assertEndpointReached(
            self.myob.invoices.get_item,
            {"uid": UID},
            "GET",
            f"/{BID}/Sale/Invoice/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.invoices.put_item,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{BID}/Sale/Invoice/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.invoices.post_item,
            {"data": DATA},
            "POST",
            f"/{BID}/Sale/Invoice/Item/",
        )
        self.assertEndpointReached(
            self.myob.invoices.delete_item,
            {"uid": UID},
            "DELETE",
            f"/{BID}/Sale/Invoice/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.invoices.service,
            {},
            "GET",
            f"/{BID}/Sale/Invoice/Service/",
        )
        self.assertEndpointReached(
            self.myob.invoices.get_service,
            {"uid": UID},
            "GET",
            f"/{BID}/Sale/Invoice/Service/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.invoices.put_service,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{BID}/Sale/Invoice/Service/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.invoices.post_service,
            {"data": DATA},
            "POST",
            f"/{BID}/Sale/Invoice/Service/",
        )
        self.assertEndpointReached(
            self.myob.invoices.delete_service,
            {"uid": UID},
            "DELETE",
            f"/{BID}/Sale/Invoice/Service/{UID}/",
        )

    def test_customer_payments(self):
        self.assertEqual(
            repr(self.myob.customer_payments),
            (
                "Sale_CustomerPaymentManager:\n"
                "          all() - Return all sale customer payments for a business.\n"
                "    delete(uid) - Delete selected sale customer payment.\n"
                "       get(uid) - Return selected sale customer payment.\n"
                "     post(data) - Create new sale customer payment."
            ),
        )
        self.assertEndpointReached(
            self.myob.customer_payments.all,
            {},
            "GET",
            f"/{BID}/Sale/CustomerPayment/",
        )
        self.assertEndpointReached(
            self.myob.customer_payments.get,
            {"uid": UID},
            "GET",
            f"/{BID}/Sale/CustomerPayment/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.customer_payments.delete,
            {"uid": UID},
            "DELETE",
            f"/{BID}/Sale/CustomerPayment/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.customer_payments.post,
            {"data": DATA},
            "POST",
            f"/{BID}/Sale/CustomerPayment/",
        )

    def test_credit_refunds(self):
        self.assertEqual(
            repr(self.myob.credit_refunds),
            (
                "Sale_CreditRefundManager:\n"
                "          all() - Return all sale credit refunds for a business.\n"
                "    delete(uid) - Delete selected sale credit refund.\n"
                "       get(uid) - Return selected sale credit refund.\n"
                "     post(data) - Create new sale credit refund."
            ),
        )
        self.assertEndpointReached(
            self.myob.credit_refunds.all, {}, "GET", f"/{BID}/Sale/CreditRefund/"
        )
        self.assertEndpointReached(
            self.myob.credit_refunds.get,
            {"uid": UID},
            "GET",
            f"/{BID}/Sale/CreditRefund/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.credit_refunds.delete,
            {"uid": UID},
            "DELETE",
            f"/{BID}/Sale/CreditRefund/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.credit_refunds.post,
            {"data": DATA},
            "POST",
            f"/{BID}/Sale/CreditRefund/",
        )

    def test_credit_settlements(self):
        self.assertEqual(
            repr(self.myob.credit_settlements),
            (
                "Sale_CreditSettlementManager:\n"
                "          all() - Return all sale credit settlements for a business.\n"
                "    delete(uid) - Delete selected sale credit settlement.\n"
                "       get(uid) - Return selected sale credit settlement.\n"
                "     post(data) - Create new sale credit settlement."
            ),
        )
        self.assertEndpointReached(
            self.myob.credit_settlements.all,
            {},
            "GET",
            f"/{BID}/Sale/CreditSettlement/",
        )
        self.assertEndpointReached(
            self.myob.credit_settlements.get,
            {"uid": UID},
            "GET",
            f"/{BID}/Sale/CreditSettlement/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.credit_settlements.delete,
            {"uid": UID},
            "DELETE",
            f"/{BID}/Sale/CreditSettlement/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.credit_settlements.post,
            {"data": DATA},
            "POST",
            f"/{BID}/Sale/CreditSettlement/",
        )

    def test_quotes(self):
        self.assertEqual(
            repr(self.myob.quotes),
            (
                "Sale_QuoteManager:\n"
                "                     all() - Return all sale quote types for a business.\n"
                "          delete_item(uid) - Delete selected item type sale quote.\n"
                "       delete_service(uid) - Delete selected service type sale quote.\n"
                "             get_item(uid) - Return selected item type sale quote.\n"
                "          get_service(uid) - Return selected service type sale quote.\n"
                "                    item() - Return all item type sale quotes for a business.\n"
                "           post_item(data) - Create new item type sale quote.\n"
                "        post_service(data) - Create new service type sale quote.\n"
                "       put_item(uid, data) - Update selected item type sale quote.\n"
                "    put_service(uid, data) - Update selected service type sale quote.\n"
                "                 service() - Return all service type sale quotes for a business."
            ),
        )
        self.assertEndpointReached(self.myob.quotes.all, {}, "GET", f"/{BID}/Sale/Quote/")
        self.assertEndpointReached(
            self.myob.quotes.item, {}, "GET", f"/{BID}/Sale/Quote/Item/"
        )
        self.assertEndpointReached(
            self.myob.quotes.get_item,
            {"uid": UID},
            "GET",
            f"/{BID}/Sale/Quote/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.quotes.put_item,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{BID}/Sale/Quote/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.quotes.post_item,
            {"data": DATA},
            "POST",
            f"/{BID}/Sale/Quote/Item/",
        )
        self.assertEndpointReached(
            self.myob.quotes.delete_item,
            {"uid": UID},
            "DELETE",
            f"/{BID}/Sale/Quote/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.quotes.service, {}, "GET", f"/{BID}/Sale/Quote/Service/"
        )
        self.assertEndpointReached(
            self.myob.quotes.get_service,
            {"uid": UID},
            "GET",
            f"/{BID}/Sale/Quote/Service/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.quotes.put_service,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{BID}/Sale/Quote/Service/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.quotes.post_service,
            {"data": DATA},
            "POST",
            f"/{BID}/Sale/Quote/Service/",
        )
        self.assertEndpointReached(
            self.myob.quotes.delete_service,
            {"uid": UID},
            "DELETE",
            f"/{BID}/Sale/Quote/Service/{UID}/",
        )

    def test_orders(self):
        self.assertEqual(
            repr(self.myob.orders),
            (
                "Sale_OrderManager:\n"
                "                     all() - Return all sale order types for a business.\n"
                "          delete_item(uid) - Delete selected item type sale order.\n"
                "       delete_service(uid) - Delete selected service type sale order.\n"
                "             get_item(uid) - Return selected item type sale order.\n"
                "          get_service(uid) - Return selected service type sale order.\n"
                "                    item() - Return all item type sale orders for a business.\n"
                "           post_item(data) - Create new item type sale order.\n"
                "        post_service(data) - Create new service type sale order.\n"
                "       put_item(uid, data) - Update selected item type sale order.\n"
                "    put_service(uid, data) - Update selected service type sale order.\n"
                "                 service() - Return all service type sale orders for a business."
            ),
        )
        self.assertEndpointReached(
            self.myob.invoices.all, {}, "GET", f"/{BID}/Sale/Invoice/"
        )
        self.assertEndpointReached(
            self.myob.invoices.item, {}, "GET", f"/{BID}/Sale/Invoice/Item/"
        )
        self.assertEndpointReached(
            self.myob.invoices.get_item,
            {"uid": UID},
            "GET",
            f"/{BID}/Sale/Invoice/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.invoices.put_item,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{BID}/Sale/Invoice/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.invoices.post_item,
            {"data": DATA},
            "POST",
            f"/{BID}/Sale/Invoice/Item/",
        )
        self.assertEndpointReached(
            self.myob.invoices.delete_item,
            {"uid": UID},
            "DELETE",
            f"/{BID}/Sale/Invoice/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.invoices.service,
            {},
            "GET",
            f"/{BID}/Sale/Invoice/Service/",
        )
        self.assertEndpointReached(
            self.myob.invoices.get_service,
            {"uid": UID},
            "GET",
            f"/{BID}/Sale/Invoice/Service/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.invoices.put_service,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{BID}/Sale/Invoice/Service/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.invoices.post_service,
            {"data": DATA},
            "POST",
            f"/{BID}/Sale/Invoice/Service/",
        )
        self.assertEndpointReached(
            self.myob.invoices.delete_service,
            {"uid": UID},
            "DELETE",
            f"/{BID}/Sale/Invoice/Service/{UID}/",
        )

    def test_general_ledger(self):
        self.assertEqual(
            repr(self.myob.general_ledger),
            (
                "GeneralLedgerManager:\n"
                "                        account() - Return all accounts for a business.\n"
                "           accountingproperties() - Return all accounting property settings for a business.\n"
                "                accountregister() - Return all account registers for a business.\n"
                "                       category() - Return all cost center tracking categories for a business.\n"
                "              delete_account(uid) - Delete selected account.\n"
                "             delete_category(uid) - Delete selected cost center tracking category.\n"
                "       delete_generaljournal(uid) - Delete selected general journal.\n"
                "                  delete_job(uid) - Delete selected job.\n"
                "              delete_taxcode(uid) - Delete selected tax code.\n"
                "                 generaljournal() - Return all general journals for a business.\n"
                "                 get_account(uid) - Return selected account.\n"
                "                get_category(uid) - Return selected cost center tracking category.\n"
                "          get_generaljournal(uid) - Return selected general journal.\n"
                "                     get_job(uid) - Return selected job.\n"
                "      get_journaltransaction(uid) - Return selected transaction journal.\n"
                "                 get_taxcode(uid) - Return selected tax code.\n"
                "                            job() - Return all jobs for a business.\n"
                "             journaltransaction() - Return all transaction journals for a business.\n"
                "               post_account(data) - Create new account.\n"
                "              post_category(data) - Create new cost center tracking category.\n"
                "        post_generaljournal(data) - Create new general journal.\n"
                "                   post_job(data) - Create new job.\n"
                "               post_taxcode(data) - Create new tax code.\n"
                "           put_account(uid, data) - Update selected account.\n"
                "          put_category(uid, data) - Update selected cost center tracking category.\n"
                "    put_generaljournal(uid, data) - Update selected general journal.\n"
                "               put_job(uid, data) - Update selected job.\n"
                "           put_taxcode(uid, data) - Update selected tax code.\n"
                "                        taxcode() - Return all tax codes for a business."
            ),
        )
        self.assertEndpointReached(
            self.myob.general_ledger.taxcode,
            {},
            "GET",
            f"/{BID}/GeneralLedger/TaxCode/",
        )
        self.assertEndpointReached(
            self.myob.general_ledger.get_taxcode,
            {"uid": UID},
            "GET",
            f"/{BID}/GeneralLedger/TaxCode/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.general_ledger.put_taxcode,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{BID}/GeneralLedger/TaxCode/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.general_ledger.post_taxcode,
            {"data": DATA},
            "POST",
            f"/{BID}/GeneralLedger/TaxCode/",
        )
        self.assertEndpointReached(
            self.myob.general_ledger.delete_taxcode,
            {"uid": UID},
            "DELETE",
            f"/{BID}/GeneralLedger/TaxCode/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.general_ledger.account,
            {},
            "GET",
            f"/{BID}/GeneralLedger/Account/",
        )
        self.assertEndpointReached(
            self.myob.general_ledger.get_account,
            {"uid": UID},
            "GET",
            f"/{BID}/GeneralLedger/Account/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.general_ledger.put_account,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{BID}/GeneralLedger/Account/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.general_ledger.post_account,
            {"data": DATA},
            "POST",
            f"/{BID}/GeneralLedger/Account/",
        )
        self.assertEndpointReached(
            self.myob.general_ledger.delete_account,
            {"uid": UID},
            "DELETE",
            f"/{BID}/GeneralLedger/Account/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.general_ledger.category,
            {},
            "GET",
            f"/{BID}/GeneralLedger/Category/",
        )
        self.assertEndpointReached(
            self.myob.general_ledger.get_category,
            {"uid": UID},
            "GET",
            f"/{BID}/GeneralLedger/Category/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.general_ledger.put_category,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{BID}/GeneralLedger/Category/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.general_ledger.post_category,
            {"data": DATA},
            "POST",
            f"/{BID}/GeneralLedger/Category/",
        )
        self.assertEndpointReached(
            self.myob.general_ledger.delete_category,
            {"uid": UID},
            "DELETE",
            f"/{BID}/GeneralLedger/Category/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.general_ledger.journaltransaction,
            {},
            "GET",
            f"/{BID}/GeneralLedger/JournalTransaction/",
        )
        self.assertEndpointReached(
            self.myob.general_ledger.accountregister,
            {},
            "GET",
            f"/{BID}/GeneralLedger/AccountRegister/",
        )
        self.assertEndpointReached(
            self.myob.general_ledger.accountingproperties,
            {},
            "GET",
            f"/{BID}/GeneralLedger/AccountingProperties/",
        )

    def test_inventory(self):
        self.assertEqual(
            repr(self.myob.inventory),
            (
                "InventoryManager:\n"
                "                      adjustment() - Return all inventory adjustments for a business.\n"
                "            delete_adjustment(uid) - Delete selected inventory adjustment.\n"
                "                  delete_item(uid) - Delete selected inventory item.\n"
                "              delete_location(uid) - Delete selected inventory location.\n"
                "               get_adjustment(uid) - Return selected inventory adjustment.\n"
                "                     get_item(uid) - Return selected inventory item.\n"
                "          get_itempricematrix(uid) - Return selected inventory item price matrix.\n"
                "                 get_location(uid) - Return selected inventory location.\n"
                "                            item() - Return all inventory items for a business.\n"
                "                 itempricematrix() - Return all inventory item price matrices for a business.\n"
                "                        location() - Return all inventory locations for a business.\n"
                "             post_adjustment(data) - Create new inventory adjustment.\n"
                "                   post_item(data) - Create new inventory item.\n"
                "               post_location(data) - Create new inventory location.\n"
                "         put_adjustment(uid, data) - Update selected inventory adjustment.\n"
                "               put_item(uid, data) - Update selected inventory item.\n"
                "    put_itempricematrix(uid, data) - Update selected inventory item price matrix.\n"
                "           put_location(uid, data) - Update selected inventory location."
            ),
        )
        self.assertEndpointReached(
            self.myob.inventory.item, {}, "GET", f"/{BID}/Inventory/Item/"
        )
        self.assertEndpointReached(
            self.myob.inventory.get_item,
            {"uid": UID},
            "GET",
            f"/{BID}/Inventory/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.inventory.put_item,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{BID}/Inventory/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.inventory.post_item,
            {"data": DATA},
            "POST",
            f"/{BID}/Inventory/Item/",
        )
        self.assertEndpointReached(
            self.myob.inventory.delete_item,
            {"uid": UID},
            "DELETE",
            f"/{BID}/Inventory/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.inventory.itempricematrix,
            {},
            "GET",
            f"/{BID}/Inventory/ItemPriceMatrix/",
        )
        self.assertEndpointReached(
            self.myob.inventory.get_itempricematrix,
            {"uid": UID},
            "GET",
            f"/{BID}/Inventory/ItemPriceMatrix/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.inventory.put_itempricematrix,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{BID}/Inventory/ItemPriceMatrix/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.inventory.location,
            {},
            "GET",
            f"/{BID}/Inventory/Location/",
        )
        self.assertEndpointReached(
            self.myob.inventory.get_location,
            {"uid": UID},
            "GET",
            f"/{BID}/Inventory/Location/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.inventory.put_location,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{BID}/Inventory/Location/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.inventory.post_location,
            {"data": DATA},
            "POST",
            f"/{BID}/Inventory/Location/",
        )
        self.assertEndpointReached(
            self.myob.inventory.delete_location,
            {"uid": UID},
            "DELETE",
            f"/{BID}/Inventory/Location/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.inventory.adjustment,
            {},
            "GET",
            f"/{BID}/Inventory/Adjustment/",
        )
        self.assertEndpointReached(
            self.myob.inventory.get_adjustment,
            {"uid": UID},
            "GET",
            f"/{BID}/Inventory/Adjustment/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.inventory.put_adjustment,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{BID}/Inventory/Adjustment/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.inventory.post_adjustment,
            {"data": DATA},
            "POST",
            f"/{BID}/Inventory/Adjustment/",
        )
        self.assertEndpointReached(
            self.myob.inventory.delete_adjustment,
            {"uid": UID},
            "DELETE",
            f"/{BID}/Inventory/Adjustment/{UID}/",
        )

    def test_purchase_orders(self):
        self.assertEqual(
            repr(self.myob.purchase_orders),
            (
                "Purchase_OrderManager:\n"
                "                  all() - Return all purchase order types for a business.\n"
                "       delete_item(uid) - Delete selected item type purchase order.\n"
                "          get_item(uid) - Return selected item type purchase order.\n"
                "                 item() - Return all item type purchase orders for a business.\n"
                "        post_item(data) - Create new item type purchase order.\n"
                "    put_item(uid, data) - Update selected item type purchase order."
            ),
        )
        self.assertEndpointReached(
            self.myob.purchase_orders.all, {}, "GET", f"/{BID}/Purchase/Order/"
        )
        self.assertEndpointReached(
            self.myob.purchase_orders.item,
            {},
            "GET",
            f"/{BID}/Purchase/Order/Item/",
        )
        self.assertEndpointReached(
            self.myob.purchase_orders.get_item,
            {"uid": UID},
            "GET",
            f"/{BID}/Purchase/Order/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.purchase_orders.put_item,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{BID}/Purchase/Order/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.purchase_orders.post_item,
            {"data": DATA},
            "POST",
            f"/{BID}/Purchase/Order/Item/",
        )
        self.assertEndpointReached(
            self.myob.purchase_orders.delete_item,
            {"uid": UID},
            "DELETE",
            f"/{BID}/Purchase/Order/Item/{UID}/",
        )

    def test_purchase_bills(self):
        self.assertEqual(
            repr(self.myob.purchase_bills),
            (
                "Purchase_BillManager:\n"
                "                           all() - Return all purchase bill types for a business.\n"
                "                delete_item(uid) - Delete selected item type purchase bill.\n"
                "       delete_miscellaneous(uid) - Delete selected miscellaneous type purchase bill.\n"
                "             delete_service(uid) - Delete selected service type purchase bill.\n"
                "                   get_item(uid) - Return selected item type purchase bill.\n"
                "          get_miscellaneous(uid) - Return selected miscellaneous type purchase bill.\n"
                "                get_service(uid) - Return selected service type purchase bill.\n"
                "                          item() - Return all item type purchase bills for a business.\n"
                "                 miscellaneous() - Return all miscellaneous type purchase bills for a business.\n"
                "                 post_item(data) - Create new item type purchase bill.\n"
                "        post_miscellaneous(data) - Create new miscellaneous type purchase bill.\n"
                "              post_service(data) - Create new service type purchase bill.\n"
                "             put_item(uid, data) - Update selected item type purchase bill.\n"
                "    put_miscellaneous(uid, data) - Update selected miscellaneous type purchase bill.\n"
                "          put_service(uid, data) - Update selected service type purchase bill.\n"
                "                       service() - Return all service type purchase bills for a business."
            ),
        )
        self.assertEndpointReached(
            self.myob.purchase_bills.all, {}, "GET", f"/{BID}/Purchase/Bill/"
        )
        self.assertEndpointReached(
            self.myob.purchase_bills.item,
            {},
            "GET",
            f"/{BID}/Purchase/Bill/Item/",
        )
        self.assertEndpointReached(
            self.myob.purchase_bills.get_item,
            {"uid": UID},
            "GET",
            f"/{BID}/Purchase/Bill/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.purchase_bills.put_item,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{BID}/Purchase/Bill/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.purchase_bills.post_item,
            {"data": DATA},
            "POST",
            f"/{BID}/Purchase/Bill/Item/",
        )
        self.assertEndpointReached(
            self.myob.purchase_bills.delete_item,
            {"uid": UID},
            "DELETE",
            f"/{BID}/Purchase/Bill/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.purchase_bills.service,
            {},
            "GET",
            f"/{BID}/Purchase/Bill/Service/",
        )
        self.assertEndpointReached(
            self.myob.purchase_bills.get_service,
            {"uid": UID},
            "GET",
            f"/{BID}/Purchase/Bill/Service/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.purchase_bills.put_service,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{BID}/Purchase/Bill/Service/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.purchase_bills.post_service,
            {"data": DATA},
            "POST",
            f"/{BID}/Purchase/Bill/Service/",
        )
        self.assertEndpointReached(
            self.myob.purchase_bills.delete_service,
            {"uid": UID},
            "DELETE",
            f"/{BID}/Purchase/Bill/Service/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.purchase_bills.miscellaneous,
            {},
            "GET",
            f"/{BID}/Purchase/Bill/Miscellaneous/",
        )
        self.assertEndpointReached(
            self.myob.purchase_bills.get_miscellaneous,
            {"uid": UID},
            "GET",
            f"/{BID}/Purchase/Bill/Miscellaneous/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.purchase_bills.put_miscellaneous,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{BID}/Purchase/Bill/Miscellaneous/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.purchase_bills.post_miscellaneous,
            {"data": DATA},
            "POST",
            f"/{BID}/Purchase/Bill/Miscellaneous/",
        )
        self.assertEndpointReached(
            self.myob.purchase_bills.delete_miscellaneous,
            {"uid": UID},
            "DELETE",
            f"/{BID}/Purchase/Bill/Miscellaneous/{UID}/",
        )

    def test_supplier_payments(self):
        self.assertEqual(
            repr(self.myob.supplier_payments),
            (
                "Purchase_SupplierPaymentManager:\n"
                "             all() - Return all purchase supplier payments for a business.\n"
                "       delete(uid) - Delete selected purchase supplier payment.\n"
                "          get(uid) - Return selected purchase supplier payment.\n"
                "        post(data) - Create new purchase supplier payment.\n"
                "    put(uid, data) - Update selected purchase supplier payment."
            ),
        )
        self.assertEndpointReached(
            self.myob.supplier_payments.all,
            {},
            "GET",
            f"/{BID}/Purchase/SupplierPayment/",
        )
        self.assertEndpointReached(
            self.myob.supplier_payments.get,
            {"uid": UID},
            "GET",
            f"/{BID}/Purchase/SupplierPayment/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.supplier_payments.put,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{BID}/Purchase/SupplierPayment/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.supplier_payments.delete,
            {"uid": UID},
            "DELETE",
            f"/{BID}/Purchase/SupplierPayment/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.supplier_payments.post,
            {"data": DATA},
            "POST",
            f"/{BID}/Purchase/SupplierPayment/",
        )

    def test_debit_refunds(self):
        self.assertEqual(
            repr(self.myob.debit_refunds),
            (
                "Purchase_DebitRefundManager:\n"
                "          all() - Return all purchase debit refunds for a business.\n"
                "    delete(uid) - Delete selected purchase debit refund.\n"
                "       get(uid) - Return selected purchase debit refund.\n"
                "     post(data) - Create new purchase debit refund."
            ),
        )
        self.assertEndpointReached(
            self.myob.debit_refunds.all,
            {},
            "GET",
            f"/{BID}/Purchase/DebitRefund/",
        )
        self.assertEndpointReached(
            self.myob.debit_refunds.get,
            {"uid": UID},
            "GET",
            f"/{BID}/Purchase/DebitRefund/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.debit_refunds.delete,
            {"uid": UID},
            "DELETE",
            f"/{BID}/Purchase/DebitRefund/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.debit_refunds.post,
            {"data": DATA},
            "POST",
            f"/{BID}/Purchase/DebitRefund/",
        )

    def test_debit_settlements(self):
        self.assertEqual(
            repr(self.myob.debit_settlements),
            (
                "Purchase_DebitSettlementManager:\n"
                "          all() - Return all purchase debit settlements for a business.\n"
                "    delete(uid) - Delete selected purchase debit settlement.\n"
                "       get(uid) - Return selected purchase debit settlement.\n"
                "     post(data) - Create new purchase debit settlement."
            ),
        )
        self.assertEndpointReached(
            self.myob.debit_settlements.all,
            {},
            "GET",
            f"/{BID}/Purchase/DebitSettlement/",
        )
        self.assertEndpointReached(
            self.myob.debit_settlements.get,
            {"uid": UID},
            "GET",
            f"/{BID}/Purchase/DebitSettlement/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.debit_settlements.delete,
            {"uid": UID},
            "DELETE",
            f"/{BID}/Purchase/DebitSettlement/{UID}/",
        )
        self.assertEndpointReached(
            self.myob.debit_settlements.post,
            {"data": DATA},
            "POST",
            f"/{BID}/Purchase/DebitSettlement/",
        )

    def test_company(self):
        self.assertEqual(
            repr(self.myob.company),
            (
                "CompanyManager:\n"
                "    preferences() - Return all company data file preferences for a business."
            ),
        )
        self.assertEndpointReached(
            self.myob.company.preferences,
            {},
            "GET",
            f"/{BID}/Company/Preferences/",
        )

    def test_timeout(self):
        self.assertEndpointReached(
            self.myob.contacts.all,
            {"timeout": 5},
            "GET",
            f"/{BID}/Contact/",
            timeout=5,
        )

    def test_exceptions(self):
        self.assertExceptionHandled(400, {}, MyobBadRequest)
        self.assertExceptionHandled(401, {}, MyobUnauthorized)
        self.assertExceptionHandled(403, {"Errors": [{"Name": "Something"}]}, MyobForbidden)
        self.assertExceptionHandled(
            403, {"Errors": [{"Name": "RateLimitError"}]}, MyobRateLimitExceeded
        )
        self.assertExceptionHandled(404, {}, MyobNotFound)
        self.assertExceptionHandled(504, {}, MyobGatewayTimeout)
        self.assertExceptionHandled(418, {}, MyobExceptionUnknown)
