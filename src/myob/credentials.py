from datetime import datetime, timedelta
from typing import Any
from urllib.parse import quote

from requests_oauthlib import OAuth2Session

from .constants import ACCESS_TOKEN_URL, AUTHORIZE_URL, MYOB_PARTNER_BASE_URL, AuthScope


class PartnerCredentials:
    """An object wrapping the 3-step OAuth2 process for Partner MYOB API access.

    Consent is granted per business, so a set of credentials covers exactly one. Its
    `business_id` is handed back on the authorisation redirect, and `state` carries it, so
    rebuilding from a persisted `state` gives you everything needed to make calls.
    """

    def __init__(
        self,
        consumer_key: str,
        consumer_secret: str,
        callback_uri: str,
        business_id: str | None = None,
        verified: bool = False,
        oauth_token: str | None = None,
        refresh_token: str | None = None,
        oauth_expires_at: datetime | None = None,
        scopes: tuple[AuthScope, ...] = (),
        state: str | None = None,
    ) -> None:
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.callback_uri = callback_uri
        self.business_id = business_id

        self.verified = verified
        self.oauth_token = oauth_token
        self.refresh_token = refresh_token

        if oauth_expires_at is not None:
            if not isinstance(oauth_expires_at, datetime):
                raise ValueError("'oauth_expires_at' must be a datetime instance.")
        self.oauth_expires_at = oauth_expires_at

        self.scopes = scopes
        self._oauth = OAuth2Session(consumer_key, redirect_uri=callback_uri)
        url, _ = self._oauth.authorization_url(MYOB_PARTNER_BASE_URL + AUTHORIZE_URL, state=state)
        # `prompt=consent` is what makes the authorisation redirect carry the `businessId` of
        # the business the user picked, which is how every subsequent call identifies it.
        self.url = f"{url}&scope={quote(' '.join(self.scopes))}&prompt=consent"

    @property
    def state(self) -> dict[str, Any]:
        """Get a representation of this credentials object from which it can be reconstructed."""
        return {
            attr: getattr(self, attr)
            for attr in (
                "consumer_key",
                "consumer_secret",
                "callback_uri",
                "business_id",
                "verified",
                "oauth_token",
                "refresh_token",
                "oauth_expires_at",
            )
            if getattr(self, attr) is not None
        }

    def expired(self, now: datetime | None = None) -> bool:
        """Determine whether the current access token has expired."""
        # Expiry might be unset if the user hasn't finished authenticating.
        if self.oauth_expires_at is None:
            return False

        # Allow a bit of time for clock differences and round trip times
        # to prevent false negatives. If users want the precise expiry,
        # they can use self.oauth_expires_at
        CONSERVATIVE_SECONDS = 30  # noqa: N806

        now = now or datetime.now()
        return self.oauth_expires_at <= (now + timedelta(seconds=CONSERVATIVE_SECONDS))

    def verify(self, code: str, business_id: str) -> None:
        """Verify an OAuth session, retrieving an access token.

        Both arguments come off the authorisation redirect, which is the only place MYOB
        identifies the business the user consented to.
        """
        token = self._oauth.fetch_token(
            MYOB_PARTNER_BASE_URL + ACCESS_TOKEN_URL,
            code=code,
            client_secret=self.consumer_secret,
            include_client_id=True,
        )
        self.business_id = business_id
        self.save_token(token)

    def refresh(self) -> None:
        """Refresh an expired token."""
        token = self._oauth.refresh_token(
            MYOB_PARTNER_BASE_URL + ACCESS_TOKEN_URL,
            refresh_token=self.refresh_token,
            client_id=self.consumer_key,
            client_secret=self.consumer_secret,
        )
        self.save_token(token)

    def save_token(self, token: dict) -> None:
        self.oauth_token = token.get("access_token")
        self.refresh_token = token.get("refresh_token")

        self.oauth_expires_at = datetime.fromtimestamp(token.get("expires_at"))  # type: ignore[arg-type]
        self.verified = True
