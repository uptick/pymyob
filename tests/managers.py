from unittest import TestCase

from myob.constants import DEFAULT_PAGE_SIZE
from myob.credentials import PartnerCredentials
from myob.managers import Manager


class QueryParamTests(TestCase):
    def setUp(self):
        cred = PartnerCredentials(
            consumer_key='KeyToTheKingdom',
            consumer_secret='TellNoOne',
            callback_uri='CallOnlyWhenCalledTo',
        )
        self.manager = Manager('', credentials=cred)

    def assertParamsEqual(self, raw_kwargs, expected_params, method='GET'):
        self.assertEqual(
            self.manager.build_request_kwargs(method, {}, **raw_kwargs)['params'],
            expected_params
        )

    def test_filter(self):
        self.assertParamsEqual({'Type': 'Customer'}, {'$filter': "Type eq 'Customer'"})
        self.assertParamsEqual({'Type': ['Customer', 'Supplier']}, {'$filter': "Type eq 'Customer' or Type eq 'Supplier'"})
        self.assertParamsEqual({'DisplayID__gt': '5-0000'}, {'$filter': "DisplayID gt '5-0000'"})
        self.assertParamsEqual({'DateOccurred__lt': '2013-08-30T19:00:59.043'}, {'$filter': "DateOccurred lt '2013-08-30T19:00:59.043'"})
        self.assertParamsEqual({'Type': ['Customer', 'Supplier'], 'DisplayID__gt': '5-0000'}, {'$filter': "Type eq 'Customer' or Type eq 'Supplier' and DisplayID gt '5-0000'"})

    def test_orderby(self):
        self.assertParamsEqual({'orderby': 'Date'}, {'$orderby': "Date"})

    def test_pagination(self):
        self.assertParamsEqual({'page': 7}, {'$skip': 6 * DEFAULT_PAGE_SIZE})
        self.assertParamsEqual({'limit': 20}, {'$top': 20})
        self.assertParamsEqual({'limit': 20, 'page': 7}, {'$top': 20, '$skip': 120})

    def test_format(self):
        self.assertParamsEqual({'format': 'json'}, {'format': 'json'})

    def test_templatename(self):
        self.assertParamsEqual({'templatename': 'InvoiceTemplate - 7'}, {'templatename': 'InvoiceTemplate - 7'})

    def test_returnBody(self):
        self.assertParamsEqual({}, {'returnBody': 'true'}, method='PUT')
        self.assertParamsEqual({}, {'returnBody': 'true'}, method='POST')

    def test_combination(self):
        self.assertParamsEqual(
            {
                'Type': ['Customer', 'Supplier'],
                'DisplayID__gt': '3-0900',
                'orderby': 'Date',
                'page': 5,
                'limit': 13,
                'format': 'json',
            },
            {
                '$filter': "Type eq 'Customer' or Type eq 'Supplier' and DisplayID gt '3-0900'",
                '$orderby': 'Date',
                '$skip': 52,
                '$top': 13,
                'format': 'json'
            },
        )
