import base64
from datetime import datetime, timedelta
from typing import Any

from requests_oauthlib import OAuth2Session

from .constants import ACCESS_TOKEN_URL, AUTHORIZE_URL, MYOB_PARTNER_BASE_URL


class PartnerCredentials:
    """An object wrapping the 3-step OAuth2 process for Partner MYOB API access."""

    def __init__(
        self,
        consumer_key: str,
        consumer_secret: str,
        callback_uri: str,
        verified: bool = False,
        companyfile_credentials: dict[str, str] = {},  # noqa: B006
        oauth_token: str | None = None,
        refresh_token: str | None = None,
        oauth_expires_at: datetime | None = None,
        scope: None = None,  # TODO: Review if used.
        state: str | None = None,
    ) -> None:
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.callback_uri = callback_uri

        self.verified = verified
        self.companyfile_credentials = companyfile_credentials
        self.oauth_token = oauth_token
        self.refresh_token = refresh_token

        if oauth_expires_at is not None:
            if not isinstance(oauth_expires_at, datetime):
                raise ValueError("'oauth_expires_at' must be a datetime instance.")
        self.oauth_expires_at = oauth_expires_at

        self._oauth = OAuth2Session(consumer_key, redirect_uri=callback_uri)
        url, _ = self._oauth.authorization_url(MYOB_PARTNER_BASE_URL + AUTHORIZE_URL, state=state)
        self.url = url + "&scope=CompanyFile"

    # TODO: Add `verify` kwarg here, which will quickly throw the provided credentials at a
    # protected endpoint to ensure they are valid. If not, raise appropriate error.
    def authenticate_companyfile(self, company_id: str, username: str, password: str) -> None:
        """Store hashed username-password for logging into company file."""
        userpass = base64.b64encode(bytes(f"{username}:{password}", "utf-8")).decode("utf-8")
        self.companyfile_credentials[company_id] = userpass

    @property
    def state(self) -> dict[str, Any]:
        """Get a representation of this credentials object from which it can be reconstructed."""
        return {
            attr: getattr(self, attr)
            for attr in (
                "consumer_key",
                "consumer_secret",
                "callback_uri",
                "verified",
                "companyfile_credentials",
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

    def verify(self, code: str) -> None:
        """Verify an OAuth session, retrieving an access token."""
        token = self._oauth.fetch_token(
            MYOB_PARTNER_BASE_URL + ACCESS_TOKEN_URL,
            code=code,
            client_secret=self.consumer_secret,
            include_client_id=True,
        )
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
