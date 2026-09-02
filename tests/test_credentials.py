from datetime import datetime
from unittest import TestCase
from unittest.mock import patch
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
    def test_business_survives_a_round_trip_through_state(self):
        # The authorisation redirect is the only place the business id is handed over, so
        # `state` has to carry it for credentials rebuilt later to be able to make any calls.
        credentials = PartnerCredentials(
            consumer_key="KeyToTheKingdom",
            consumer_secret="TellNoOne",  # noqa: S106
            callback_uri="CallOnlyWhenCalledTo",
            business_id="DummyBusinessId",
        )
        self.assertEqual(PartnerCredentials(**credentials.state).business_id, "DummyBusinessId")


class VerificationTests(TestCase):
    @patch("myob.credentials.OAuth2Session.fetch_token")
    def test_the_business_from_the_redirect_is_recorded(self, mock_fetch_token):
        mock_fetch_token.return_value = {
            "access_token": "AnAccessToken",
            "refresh_token": "ARefreshToken",
            "expires_at": datetime(1992, 11, 14).timestamp(),
        }
        credentials = PartnerCredentials(
            consumer_key="KeyToTheKingdom",
            consumer_secret="TellNoOne",  # noqa: S106
            callback_uri="CallOnlyWhenCalledTo",
        )

        credentials.verify("AVerifier", "DummyBusinessId")

        self.assertEqual(credentials.business_id, "DummyBusinessId")
