from unittest import TestCase
from urllib.parse import parse_qs, urlparse

from myob.constants import AuthScope
from myob.credentials import PartnerCredentials


class AuthorisationUrlTests(TestCase):
    def query_params(self, **kwargs):
        credentials = PartnerCredentials(
            consumer_key="KeyToTheKingdom",
            consumer_secret="TellNoOne",  # noqa: S106
            callback_uri="CallOnlyWhenCalledTo",
            **kwargs,
        )
        return parse_qs(urlparse(credentials.url).query)

    def test_requested_scopes_are_space_delimited(self):
        params = self.query_params(scopes=(AuthScope.COMPANY_FILE, AuthScope.SALES))
        self.assertEqual(params["scope"], ["sme-company-file sme-sales"])

    def test_consent_is_prompted_for(self):
        # Without this, the redirect comes back without the `businessId` identifying the business
        # the user picked, leaving nothing to make subsequent calls against.
        params = self.query_params(scopes=(AuthScope.COMPANY_FILE,))
        self.assertEqual(params["prompt"], ["consent"])


class PersistedStateTests(TestCase):
    def test_state_from_an_earlier_version_is_accepted_and_shed(self):
        credentials = PartnerCredentials(
            consumer_key="KeyToTheKingdom",
            consumer_secret="TellNoOne",  # noqa: S106
            callback_uri="CallOnlyWhenCalledTo",
            companyfile_credentials={"a-company-file": "!encoded-userpass="},
        )
        self.assertNotIn("companyfile_credentials", credentials.state)
