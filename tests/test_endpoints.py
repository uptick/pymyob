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
CID = "DummyCompanyId"
UID = "DummyResourceUid"
DATA = {"dummy": "data"}


class EndpointTests(TestCase):
    maxDiff = None

    def setUp(self):
        cred = PartnerCredentials(
            consumer_key="KeyToTheKingdom",
            consumer_secret="TellNoOne",  # noqa: S106
            callback_uri="CallOnlyWhenCalledTo",
            companyfile_credentials={CID: "!encoded-userpass="},
        )
        self.myob = Myob(cred)
        self.companyfile = self.myob.companyfiles.get(CID, call=False)
        self.expected_request_headers = {
            "Authorization": "Bearer None",
            "x-myobapi-cftoken": "!encoded-userpass=",
            "x-myobapi-key": "KeyToTheKingdom",
            "x-myobapi-version": "v2",
        }

    @patch("myob.managers.requests.request")
    def assertEndpointReached(self, func, params, method, endpoint, mock_request, timeout=None):  # noqa: N802
        mock_request.return_value.status_code = 200
        if endpoint == f"/{CID}/":
            mock_request.return_value.json.return_value = {"CompanyFile": {"Id": CID}}
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
        self.assertEqual(repr(self.myob), ("Myob:\n" "    companyfiles\n" "    info"))
        # Don't expect companyfile credentials here as this endpoint is not companyfile specific.
        del self.expected_request_headers["x-myobapi-cftoken"]
        self.assertEndpointReached(self.myob.info, {}, "GET", "/Info/")

    @patch("myob.managers.requests.request")
    def test_json_error(self, mock_request):
        mock_request.return_value.status_code = 200

        def response_json():
            raise JSONDecodeError("Some error message", "", 0)

        mock_request.return_value.json = response_json

        # Empty response to DELETE returns empty dict
        mock_request.return_value.content = b""
        result = self.companyfile.banking.delete_transfermoneytxn(uid=UID)
        self.assertEqual(result, {})

        # JSON error from non-empty DELETE response gets raised
        mock_request.return_value.content = "{"
        with self.assertRaises(ValueError):
            self.companyfile.banking.delete_transfermoneytxn(uid=UID)

        # JSON error from non-DELETE request gets raised, regardless of content
        mock_request.return_value.content = b""
        with self.assertRaises(ValueError):
            self.companyfile.banking.all()

        with self.assertRaises(ValueError):
            self.companyfile.banking.post_spendmoneytxn(data=DATA)

        with self.assertRaises(ValueError):
            self.companyfile.banking.put_transfermoneytxn(uid=UID, data=DATA)

        mock_request.return_value.content = "{"
        with self.assertRaises(ValueError):
            self.companyfile.banking.all()

        with self.assertRaises(ValueError):
            self.companyfile.banking.post_spendmoneytxn(data=DATA)

        with self.assertRaises(ValueError):
            self.companyfile.banking.put_transfermoneytxn(uid=UID, data=DATA)

    def test_companyfiles(self):
        self.assertEqual(
            repr(self.myob.companyfiles),
            (
                "CompanyFileManager:\n"
                "      all() - Return a list of company files.\n"
                "    get(id) - List endpoints available for a company file."
            ),
        )
        self.assertEndpointReached(self.myob.companyfiles.get, {"id": CID}, "GET", f"/{CID}/")
        # Don't expect companyfile credentials here as the next endpoint is not companyfile specific.
        del self.expected_request_headers["x-myobapi-cftoken"]
        self.assertEndpointReached(self.myob.companyfiles.all, {}, "GET", "/")

    def test_companyfile(self):
        self.assertEqual(
            repr(self.companyfile),
            (
                "CompanyFile:\n"
                "    banking\n"
                "    company\n"
                "    contacts\n"
                "    credit_refunds\n"
                "    credit_settlements\n"
                "    customer_payments\n"
                "    debit_refunds\n"
                "    debit_settlements\n"
                "    general_ledger\n"
                "    inventory\n"
                "    invoices\n"
                "    orders\n"
                "    purchase_bills\n"
                "    purchase_orders\n"
                "    quotes\n"
                "    supplier_payments"
            ),
        )

    def test_banking(self):
        self.assertEqual(
            repr(self.companyfile.banking),
            (
                "BankingManager:\n"
                "                              all() - Return all banking types for an AccountRight company file.\n"
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
                "                  receivemoneytxn() - Return all receive money transactions for an AccountRight company file.\n"
                "                    spendmoneytxn() - Return all spend money transactions for an AccountRight company file.\n"
                "                 transfermoneytxn() - Return all transfer money transactions for an AccountRight company file."
            ),
        )
        self.assertEndpointReached(self.companyfile.banking.all, {}, "GET", f"/{CID}/Banking/")
        self.assertEndpointReached(
            self.companyfile.banking.spendmoneytxn,
            {},
            "GET",
            f"/{CID}/Banking/SpendMoneyTxn/",
        )
        self.assertEndpointReached(
            self.companyfile.banking.get_spendmoneytxn,
            {"uid": UID},
            "GET",
            f"/{CID}/Banking/SpendMoneyTxn/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.banking.put_spendmoneytxn,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{CID}/Banking/SpendMoneyTxn/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.banking.post_spendmoneytxn,
            {"data": DATA},
            "POST",
            f"/{CID}/Banking/SpendMoneyTxn/",
        )
        self.assertEndpointReached(
            self.companyfile.banking.delete_spendmoneytxn,
            {"uid": UID},
            "DELETE",
            f"/{CID}/Banking/SpendMoneyTxn/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.banking.receivemoneytxn,
            {},
            "GET",
            f"/{CID}/Banking/ReceiveMoneyTxn/",
        )
        self.assertEndpointReached(
            self.companyfile.banking.get_receivemoneytxn,
            {"uid": UID},
            "GET",
            f"/{CID}/Banking/ReceiveMoneyTxn/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.banking.put_receivemoneytxn,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{CID}/Banking/ReceiveMoneyTxn/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.banking.post_receivemoneytxn,
            {"data": DATA},
            "POST",
            f"/{CID}/Banking/ReceiveMoneyTxn/",
        )
        self.assertEndpointReached(
            self.companyfile.banking.delete_receivemoneytxn,
            {"uid": UID},
            "DELETE",
            f"/{CID}/Banking/ReceiveMoneyTxn/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.banking.transfermoneytxn,
            {},
            "GET",
            f"/{CID}/Banking/TransferMoneyTxn/",
        )
        self.assertEndpointReached(
            self.companyfile.banking.get_transfermoneytxn,
            {"uid": UID},
            "GET",
            f"/{CID}/Banking/TransferMoneyTxn/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.banking.put_transfermoneytxn,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{CID}/Banking/TransferMoneyTxn/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.banking.post_transfermoneytxn,
            {"data": DATA},
            "POST",
            f"/{CID}/Banking/TransferMoneyTxn/",
        )
        self.assertEndpointReached(
            self.companyfile.banking.delete_transfermoneytxn,
            {"uid": UID},
            "DELETE",
            f"/{CID}/Banking/TransferMoneyTxn/{UID}/",
        )

    def test_contacts(self):
        self.assertEqual(
            repr(self.companyfile.contacts),
            (
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
            ),
        )
        self.assertEndpointReached(self.companyfile.contacts.all, {}, "GET", f"/{CID}/Contact/")
        self.assertEndpointReached(
            self.companyfile.contacts.customer, {}, "GET", f"/{CID}/Contact/Customer/"
        )
        self.assertEndpointReached(
            self.companyfile.contacts.get_customer,
            {"uid": UID},
            "GET",
            f"/{CID}/Contact/Customer/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.contacts.put_customer,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{CID}/Contact/Customer/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.contacts.post_customer,
            {"data": DATA},
            "POST",
            f"/{CID}/Contact/Customer/",
        )
        self.assertEndpointReached(
            self.companyfile.contacts.delete_customer,
            {"uid": UID},
            "DELETE",
            f"/{CID}/Contact/Customer/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.contacts.employee, {}, "GET", f"/{CID}/Contact/Employee/"
        )
        self.assertEndpointReached(
            self.companyfile.contacts.get_employee,
            {"uid": UID},
            "GET",
            f"/{CID}/Contact/Employee/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.contacts.put_employee,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{CID}/Contact/Employee/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.contacts.post_employee,
            {"data": DATA},
            "POST",
            f"/{CID}/Contact/Employee/",
        )
        self.assertEndpointReached(
            self.companyfile.contacts.delete_employee,
            {"uid": UID},
            "DELETE",
            f"/{CID}/Contact/Employee/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.contacts.supplier, {}, "GET", f"/{CID}/Contact/Supplier/"
        )
        self.assertEndpointReached(
            self.companyfile.contacts.get_supplier,
            {"uid": UID},
            "GET",
            f"/{CID}/Contact/Supplier/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.contacts.put_supplier,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{CID}/Contact/Supplier/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.contacts.post_supplier,
            {"data": DATA},
            "POST",
            f"/{CID}/Contact/Supplier/",
        )
        self.assertEndpointReached(
            self.companyfile.contacts.delete_supplier,
            {"uid": UID},
            "DELETE",
            f"/{CID}/Contact/Supplier/{UID}/",
        )

    def test_invoices(self):
        self.assertEqual(
            repr(self.companyfile.invoices),
            (
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
            ),
        )
        self.assertEndpointReached(
            self.companyfile.invoices.all, {}, "GET", f"/{CID}/Sale/Invoice/"
        )
        self.assertEndpointReached(
            self.companyfile.invoices.item, {}, "GET", f"/{CID}/Sale/Invoice/Item/"
        )
        self.assertEndpointReached(
            self.companyfile.invoices.get_item,
            {"uid": UID},
            "GET",
            f"/{CID}/Sale/Invoice/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.invoices.put_item,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{CID}/Sale/Invoice/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.invoices.post_item,
            {"data": DATA},
            "POST",
            f"/{CID}/Sale/Invoice/Item/",
        )
        self.assertEndpointReached(
            self.companyfile.invoices.delete_item,
            {"uid": UID},
            "DELETE",
            f"/{CID}/Sale/Invoice/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.invoices.service,
            {},
            "GET",
            f"/{CID}/Sale/Invoice/Service/",
        )
        self.assertEndpointReached(
            self.companyfile.invoices.get_service,
            {"uid": UID},
            "GET",
            f"/{CID}/Sale/Invoice/Service/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.invoices.put_service,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{CID}/Sale/Invoice/Service/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.invoices.post_service,
            {"data": DATA},
            "POST",
            f"/{CID}/Sale/Invoice/Service/",
        )
        self.assertEndpointReached(
            self.companyfile.invoices.delete_service,
            {"uid": UID},
            "DELETE",
            f"/{CID}/Sale/Invoice/Service/{UID}/",
        )

    def test_customer_payments(self):
        self.assertEqual(
            repr(self.companyfile.customer_payments),
            (
                "Sale_CustomerPaymentManager:\n"
                "          all() - Return all sale customer payments for an AccountRight company file.\n"
                "    delete(uid) - Delete selected sale customer payment.\n"
                "       get(uid) - Return selected sale customer payment.\n"
                "     post(data) - Create new sale customer payment."
            ),
        )
        self.assertEndpointReached(
            self.companyfile.customer_payments.all,
            {},
            "GET",
            f"/{CID}/Sale/CustomerPayment/",
        )
        self.assertEndpointReached(
            self.companyfile.customer_payments.get,
            {"uid": UID},
            "GET",
            f"/{CID}/Sale/CustomerPayment/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.customer_payments.delete,
            {"uid": UID},
            "DELETE",
            f"/{CID}/Sale/CustomerPayment/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.customer_payments.post,
            {"data": DATA},
            "POST",
            f"/{CID}/Sale/CustomerPayment/",
        )

    def test_credit_refunds(self):
        self.assertEqual(
            repr(self.companyfile.credit_refunds),
            (
                "Sale_CreditRefundManager:\n"
                "          all() - Return all sale credit refunds for an AccountRight company file.\n"
                "    delete(uid) - Delete selected sale credit refund.\n"
                "       get(uid) - Return selected sale credit refund.\n"
                "     post(data) - Create new sale credit refund."
            ),
        )
        self.assertEndpointReached(
            self.companyfile.credit_refunds.all, {}, "GET", f"/{CID}/Sale/CreditRefund/"
        )
        self.assertEndpointReached(
            self.companyfile.credit_refunds.get,
            {"uid": UID},
            "GET",
            f"/{CID}/Sale/CreditRefund/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.credit_refunds.delete,
            {"uid": UID},
            "DELETE",
            f"/{CID}/Sale/CreditRefund/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.credit_refunds.post,
            {"data": DATA},
            "POST",
            f"/{CID}/Sale/CreditRefund/",
        )

    def test_credit_settlements(self):
        self.assertEqual(
            repr(self.companyfile.credit_settlements),
            (
                "Sale_CreditSettlementManager:\n"
                "          all() - Return all sale credit settlements for an AccountRight company file.\n"
                "    delete(uid) - Delete selected sale credit settlement.\n"
                "       get(uid) - Return selected sale credit settlement.\n"
                "     post(data) - Create new sale credit settlement."
            ),
        )
        self.assertEndpointReached(
            self.companyfile.credit_settlements.all,
            {},
            "GET",
            f"/{CID}/Sale/CreditSettlement/",
        )
        self.assertEndpointReached(
            self.companyfile.credit_settlements.get,
            {"uid": UID},
            "GET",
            f"/{CID}/Sale/CreditSettlement/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.credit_settlements.delete,
            {"uid": UID},
            "DELETE",
            f"/{CID}/Sale/CreditSettlement/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.credit_settlements.post,
            {"data": DATA},
            "POST",
            f"/{CID}/Sale/CreditSettlement/",
        )

    def test_quotes(self):
        self.assertEqual(
            repr(self.companyfile.quotes),
            (
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
            ),
        )
        self.assertEndpointReached(self.companyfile.quotes.all, {}, "GET", f"/{CID}/Sale/Quote/")
        self.assertEndpointReached(
            self.companyfile.quotes.item, {}, "GET", f"/{CID}/Sale/Quote/Item/"
        )
        self.assertEndpointReached(
            self.companyfile.quotes.get_item,
            {"uid": UID},
            "GET",
            f"/{CID}/Sale/Quote/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.quotes.put_item,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{CID}/Sale/Quote/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.quotes.post_item,
            {"data": DATA},
            "POST",
            f"/{CID}/Sale/Quote/Item/",
        )
        self.assertEndpointReached(
            self.companyfile.quotes.delete_item,
            {"uid": UID},
            "DELETE",
            f"/{CID}/Sale/Quote/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.quotes.service, {}, "GET", f"/{CID}/Sale/Quote/Service/"
        )
        self.assertEndpointReached(
            self.companyfile.quotes.get_service,
            {"uid": UID},
            "GET",
            f"/{CID}/Sale/Quote/Service/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.quotes.put_service,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{CID}/Sale/Quote/Service/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.quotes.post_service,
            {"data": DATA},
            "POST",
            f"/{CID}/Sale/Quote/Service/",
        )
        self.assertEndpointReached(
            self.companyfile.quotes.delete_service,
            {"uid": UID},
            "DELETE",
            f"/{CID}/Sale/Quote/Service/{UID}/",
        )

    def test_orders(self):
        self.assertEqual(
            repr(self.companyfile.orders),
            (
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
            ),
        )
        self.assertEndpointReached(
            self.companyfile.invoices.all, {}, "GET", f"/{CID}/Sale/Invoice/"
        )
        self.assertEndpointReached(
            self.companyfile.invoices.item, {}, "GET", f"/{CID}/Sale/Invoice/Item/"
        )
        self.assertEndpointReached(
            self.companyfile.invoices.get_item,
            {"uid": UID},
            "GET",
            f"/{CID}/Sale/Invoice/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.invoices.put_item,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{CID}/Sale/Invoice/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.invoices.post_item,
            {"data": DATA},
            "POST",
            f"/{CID}/Sale/Invoice/Item/",
        )
        self.assertEndpointReached(
            self.companyfile.invoices.delete_item,
            {"uid": UID},
            "DELETE",
            f"/{CID}/Sale/Invoice/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.invoices.service,
            {},
            "GET",
            f"/{CID}/Sale/Invoice/Service/",
        )
        self.assertEndpointReached(
            self.companyfile.invoices.get_service,
            {"uid": UID},
            "GET",
            f"/{CID}/Sale/Invoice/Service/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.invoices.put_service,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{CID}/Sale/Invoice/Service/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.invoices.post_service,
            {"data": DATA},
            "POST",
            f"/{CID}/Sale/Invoice/Service/",
        )
        self.assertEndpointReached(
            self.companyfile.invoices.delete_service,
            {"uid": UID},
            "DELETE",
            f"/{CID}/Sale/Invoice/Service/{UID}/",
        )

    def test_general_ledger(self):
        self.assertEqual(
            repr(self.companyfile.general_ledger),
            (
                "GeneralLedgerManager:\n"
                "                        account() - Return all accounts for an AccountRight company file.\n"
                "           accountingproperties() - Return all accounting property settings for an AccountRight company file.\n"
                "                accountregister() - Return all account registers for an AccountRight company file.\n"
                "                       category() - Return all cost center tracking categories for an AccountRight company file.\n"
                "              delete_account(uid) - Delete selected account.\n"
                "             delete_category(uid) - Delete selected cost center tracking category.\n"
                "       delete_generaljournal(uid) - Delete selected general journal.\n"
                "                  delete_job(uid) - Delete selected job.\n"
                "              delete_taxcode(uid) - Delete selected tax code.\n"
                "                 generaljournal() - Return all general journals for an AccountRight company file.\n"
                "                 get_account(uid) - Return selected account.\n"
                "                get_category(uid) - Return selected cost center tracking category.\n"
                "          get_generaljournal(uid) - Return selected general journal.\n"
                "                     get_job(uid) - Return selected job.\n"
                "      get_journaltransaction(uid) - Return selected transaction journal.\n"
                "                 get_taxcode(uid) - Return selected tax code.\n"
                "                            job() - Return all jobs for an AccountRight company file.\n"
                "             journaltransaction() - Return all transaction journals for an AccountRight company file.\n"
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
                "                        taxcode() - Return all tax codes for an AccountRight company file."
            ),
        )
        self.assertEndpointReached(
            self.companyfile.general_ledger.taxcode,
            {},
            "GET",
            f"/{CID}/GeneralLedger/TaxCode/",
        )
        self.assertEndpointReached(
            self.companyfile.general_ledger.get_taxcode,
            {"uid": UID},
            "GET",
            f"/{CID}/GeneralLedger/TaxCode/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.general_ledger.put_taxcode,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{CID}/GeneralLedger/TaxCode/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.general_ledger.post_taxcode,
            {"data": DATA},
            "POST",
            f"/{CID}/GeneralLedger/TaxCode/",
        )
        self.assertEndpointReached(
            self.companyfile.general_ledger.delete_taxcode,
            {"uid": UID},
            "DELETE",
            f"/{CID}/GeneralLedger/TaxCode/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.general_ledger.account,
            {},
            "GET",
            f"/{CID}/GeneralLedger/Account/",
        )
        self.assertEndpointReached(
            self.companyfile.general_ledger.get_account,
            {"uid": UID},
            "GET",
            f"/{CID}/GeneralLedger/Account/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.general_ledger.put_account,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{CID}/GeneralLedger/Account/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.general_ledger.post_account,
            {"data": DATA},
            "POST",
            f"/{CID}/GeneralLedger/Account/",
        )
        self.assertEndpointReached(
            self.companyfile.general_ledger.delete_account,
            {"uid": UID},
            "DELETE",
            f"/{CID}/GeneralLedger/Account/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.general_ledger.category,
            {},
            "GET",
            f"/{CID}/GeneralLedger/Category/",
        )
        self.assertEndpointReached(
            self.companyfile.general_ledger.get_category,
            {"uid": UID},
            "GET",
            f"/{CID}/GeneralLedger/Category/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.general_ledger.put_category,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{CID}/GeneralLedger/Category/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.general_ledger.post_category,
            {"data": DATA},
            "POST",
            f"/{CID}/GeneralLedger/Category/",
        )
        self.assertEndpointReached(
            self.companyfile.general_ledger.delete_category,
            {"uid": UID},
            "DELETE",
            f"/{CID}/GeneralLedger/Category/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.general_ledger.journaltransaction,
            {},
            "GET",
            f"/{CID}/GeneralLedger/JournalTransaction/",
        )
        self.assertEndpointReached(
            self.companyfile.general_ledger.accountregister,
            {},
            "GET",
            f"/{CID}/GeneralLedger/AccountRegister/",
        )
        self.assertEndpointReached(
            self.companyfile.general_ledger.accountingproperties,
            {},
            "GET",
            f"/{CID}/GeneralLedger/AccountingProperties/",
        )

    def test_inventory(self):
        self.assertEqual(
            repr(self.companyfile.inventory),
            (
                "InventoryManager:\n"
                "                      adjustment() - Return all inventory adjustments for an AccountRight company file.\n"
                "            delete_adjustment(uid) - Delete selected inventory adjustment.\n"
                "                  delete_item(uid) - Delete selected inventory item.\n"
                "              delete_location(uid) - Delete selected inventory location.\n"
                "               get_adjustment(uid) - Return selected inventory adjustment.\n"
                "                     get_item(uid) - Return selected inventory item.\n"
                "          get_itempricematrix(uid) - Return selected inventory item price matrix.\n"
                "                 get_location(uid) - Return selected inventory location.\n"
                "                            item() - Return all inventory items for an AccountRight company file.\n"
                "                 itempricematrix() - Return all inventory item price matrices for an AccountRight company file.\n"
                "                        location() - Return all inventory locations for an AccountRight company file.\n"
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
            self.companyfile.inventory.item, {}, "GET", f"/{CID}/Inventory/Item/"
        )
        self.assertEndpointReached(
            self.companyfile.inventory.get_item,
            {"uid": UID},
            "GET",
            f"/{CID}/Inventory/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.inventory.put_item,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{CID}/Inventory/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.inventory.post_item,
            {"data": DATA},
            "POST",
            f"/{CID}/Inventory/Item/",
        )
        self.assertEndpointReached(
            self.companyfile.inventory.delete_item,
            {"uid": UID},
            "DELETE",
            f"/{CID}/Inventory/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.inventory.itempricematrix,
            {},
            "GET",
            f"/{CID}/Inventory/ItemPriceMatrix/",
        )
        self.assertEndpointReached(
            self.companyfile.inventory.get_itempricematrix,
            {"uid": UID},
            "GET",
            f"/{CID}/Inventory/ItemPriceMatrix/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.inventory.put_itempricematrix,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{CID}/Inventory/ItemPriceMatrix/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.inventory.location,
            {},
            "GET",
            f"/{CID}/Inventory/Location/",
        )
        self.assertEndpointReached(
            self.companyfile.inventory.get_location,
            {"uid": UID},
            "GET",
            f"/{CID}/Inventory/Location/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.inventory.put_location,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{CID}/Inventory/Location/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.inventory.post_location,
            {"data": DATA},
            "POST",
            f"/{CID}/Inventory/Location/",
        )
        self.assertEndpointReached(
            self.companyfile.inventory.delete_location,
            {"uid": UID},
            "DELETE",
            f"/{CID}/Inventory/Location/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.inventory.adjustment,
            {},
            "GET",
            f"/{CID}/Inventory/Adjustment/",
        )
        self.assertEndpointReached(
            self.companyfile.inventory.get_adjustment,
            {"uid": UID},
            "GET",
            f"/{CID}/Inventory/Adjustment/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.inventory.put_adjustment,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{CID}/Inventory/Adjustment/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.inventory.post_adjustment,
            {"data": DATA},
            "POST",
            f"/{CID}/Inventory/Adjustment/",
        )
        self.assertEndpointReached(
            self.companyfile.inventory.delete_adjustment,
            {"uid": UID},
            "DELETE",
            f"/{CID}/Inventory/Adjustment/{UID}/",
        )

    def test_purchase_orders(self):
        self.assertEqual(
            repr(self.companyfile.purchase_orders),
            (
                "Purchase_OrderManager:\n"
                "                  all() - Return all purchase order types for an AccountRight company file.\n"
                "       delete_item(uid) - Delete selected item type purchase order.\n"
                "          get_item(uid) - Return selected item type purchase order.\n"
                "                 item() - Return all item type purchase orders for an AccountRight company file.\n"
                "        post_item(data) - Create new item type purchase order.\n"
                "    put_item(uid, data) - Update selected item type purchase order."
            ),
        )
        self.assertEndpointReached(
            self.companyfile.purchase_orders.all, {}, "GET", f"/{CID}/Purchase/Order/"
        )
        self.assertEndpointReached(
            self.companyfile.purchase_orders.item,
            {},
            "GET",
            f"/{CID}/Purchase/Order/Item/",
        )
        self.assertEndpointReached(
            self.companyfile.purchase_orders.get_item,
            {"uid": UID},
            "GET",
            f"/{CID}/Purchase/Order/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.purchase_orders.put_item,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{CID}/Purchase/Order/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.purchase_orders.post_item,
            {"data": DATA},
            "POST",
            f"/{CID}/Purchase/Order/Item/",
        )
        self.assertEndpointReached(
            self.companyfile.purchase_orders.delete_item,
            {"uid": UID},
            "DELETE",
            f"/{CID}/Purchase/Order/Item/{UID}/",
        )

    def test_purchase_bills(self):
        self.assertEqual(
            repr(self.companyfile.purchase_bills),
            (
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
            ),
        )
        self.assertEndpointReached(
            self.companyfile.purchase_bills.all, {}, "GET", f"/{CID}/Purchase/Bill/"
        )
        self.assertEndpointReached(
            self.companyfile.purchase_bills.item,
            {},
            "GET",
            f"/{CID}/Purchase/Bill/Item/",
        )
        self.assertEndpointReached(
            self.companyfile.purchase_bills.get_item,
            {"uid": UID},
            "GET",
            f"/{CID}/Purchase/Bill/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.purchase_bills.put_item,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{CID}/Purchase/Bill/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.purchase_bills.post_item,
            {"data": DATA},
            "POST",
            f"/{CID}/Purchase/Bill/Item/",
        )
        self.assertEndpointReached(
            self.companyfile.purchase_bills.delete_item,
            {"uid": UID},
            "DELETE",
            f"/{CID}/Purchase/Bill/Item/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.purchase_bills.service,
            {},
            "GET",
            f"/{CID}/Purchase/Bill/Service/",
        )
        self.assertEndpointReached(
            self.companyfile.purchase_bills.get_service,
            {"uid": UID},
            "GET",
            f"/{CID}/Purchase/Bill/Service/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.purchase_bills.put_service,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{CID}/Purchase/Bill/Service/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.purchase_bills.post_service,
            {"data": DATA},
            "POST",
            f"/{CID}/Purchase/Bill/Service/",
        )
        self.assertEndpointReached(
            self.companyfile.purchase_bills.delete_service,
            {"uid": UID},
            "DELETE",
            f"/{CID}/Purchase/Bill/Service/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.purchase_bills.miscellaneous,
            {},
            "GET",
            f"/{CID}/Purchase/Bill/Miscellaneous/",
        )
        self.assertEndpointReached(
            self.companyfile.purchase_bills.get_miscellaneous,
            {"uid": UID},
            "GET",
            f"/{CID}/Purchase/Bill/Miscellaneous/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.purchase_bills.put_miscellaneous,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{CID}/Purchase/Bill/Miscellaneous/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.purchase_bills.post_miscellaneous,
            {"data": DATA},
            "POST",
            f"/{CID}/Purchase/Bill/Miscellaneous/",
        )
        self.assertEndpointReached(
            self.companyfile.purchase_bills.delete_miscellaneous,
            {"uid": UID},
            "DELETE",
            f"/{CID}/Purchase/Bill/Miscellaneous/{UID}/",
        )

    def test_supplier_payments(self):
        self.assertEqual(
            repr(self.companyfile.supplier_payments),
            (
                "Purchase_SupplierPaymentManager:\n"
                "             all() - Return all purchase supplier payments for an AccountRight company file.\n"
                "       delete(uid) - Delete selected purchase supplier payment.\n"
                "          get(uid) - Return selected purchase supplier payment.\n"
                "        post(data) - Create new purchase supplier payment.\n"
                "    put(uid, data) - Update selected purchase supplier payment."
            ),
        )
        self.assertEndpointReached(
            self.companyfile.supplier_payments.all,
            {},
            "GET",
            f"/{CID}/Purchase/SupplierPayment/",
        )
        self.assertEndpointReached(
            self.companyfile.supplier_payments.get,
            {"uid": UID},
            "GET",
            f"/{CID}/Purchase/SupplierPayment/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.supplier_payments.put,
            {"uid": UID, "data": DATA},
            "PUT",
            f"/{CID}/Purchase/SupplierPayment/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.supplier_payments.delete,
            {"uid": UID},
            "DELETE",
            f"/{CID}/Purchase/SupplierPayment/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.supplier_payments.post,
            {"data": DATA},
            "POST",
            f"/{CID}/Purchase/SupplierPayment/",
        )

    def test_debit_refunds(self):
        self.assertEqual(
            repr(self.companyfile.debit_refunds),
            (
                "Purchase_DebitRefundManager:\n"
                "          all() - Return all purchase debit refunds for an AccountRight company file.\n"
                "    delete(uid) - Delete selected purchase debit refund.\n"
                "       get(uid) - Return selected purchase debit refund.\n"
                "     post(data) - Create new purchase debit refund."
            ),
        )
        self.assertEndpointReached(
            self.companyfile.debit_refunds.all,
            {},
            "GET",
            f"/{CID}/Purchase/DebitRefund/",
        )
        self.assertEndpointReached(
            self.companyfile.debit_refunds.get,
            {"uid": UID},
            "GET",
            f"/{CID}/Purchase/DebitRefund/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.debit_refunds.delete,
            {"uid": UID},
            "DELETE",
            f"/{CID}/Purchase/DebitRefund/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.debit_refunds.post,
            {"data": DATA},
            "POST",
            f"/{CID}/Purchase/DebitRefund/",
        )

    def test_debit_settlements(self):
        self.assertEqual(
            repr(self.companyfile.debit_settlements),
            (
                "Purchase_DebitSettlementManager:\n"
                "          all() - Return all purchase debit settlements for an AccountRight company file.\n"
                "    delete(uid) - Delete selected purchase debit settlement.\n"
                "       get(uid) - Return selected purchase debit settlement.\n"
                "     post(data) - Create new purchase debit settlement."
            ),
        )
        self.assertEndpointReached(
            self.companyfile.debit_settlements.all,
            {},
            "GET",
            f"/{CID}/Purchase/DebitSettlement/",
        )
        self.assertEndpointReached(
            self.companyfile.debit_settlements.get,
            {"uid": UID},
            "GET",
            f"/{CID}/Purchase/DebitSettlement/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.debit_settlements.delete,
            {"uid": UID},
            "DELETE",
            f"/{CID}/Purchase/DebitSettlement/{UID}/",
        )
        self.assertEndpointReached(
            self.companyfile.debit_settlements.post,
            {"data": DATA},
            "POST",
            f"/{CID}/Purchase/DebitSettlement/",
        )

    def test_company(self):
        self.assertEqual(
            repr(self.companyfile.company),
            (
                "CompanyManager:\n"
                "    preferences() - Return all company data file preferences for an AccountRight company file."
            ),
        )
        self.assertEndpointReached(
            self.companyfile.company.preferences,
            {},
            "GET",
            f"/{CID}/Company/Preferences/",
        )

    def test_timeout(self):
        self.assertEndpointReached(
            self.companyfile.contacts.all,
            {"timeout": 5},
            "GET",
            f"/{CID}/Contact/",
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
